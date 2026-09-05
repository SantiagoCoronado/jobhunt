"""Stage 4 (push): HTML email digest of new high-match jobs via Apprise.

Dedupes by canonical_key so the same role never appears twice in one digest.
Run:  python -m src.notify
Config: config/notify.yaml (Apprise URLs). Falls back to plain text if no channel.
"""
from __future__ import annotations

import json

from .db import connect
from .config import load_yaml, shortlist_threshold


def _digest_rows(conn, threshold: int):
    # MAX(match_score) + GROUP BY canonical_key returns the best-scoring row per role.
    # MAX() + GROUP BY is SQLite's documented bare-column special case: the
    # other columns come from the max-scoring row, deterministically.
    return conn.execute(
        "SELECT id, company, title, location, url, MAX(match_score) AS match_score, match_verdict "
        "FROM jobs WHERE notified=0 AND match_score >= ? "
        "AND status NOT IN ('irrelevant', 'expired') "
        "GROUP BY canonical_key ORDER BY match_score DESC LIMIT 40",
        (threshold,),
    ).fetchall()


def _unscored_count(conn) -> int:
    """Discovered jobs no stage has scored yet: the digest's honesty line.
    The digest can only show what was SCORED since the last send; this is the
    pile that hasn't been looked at."""
    return conn.execute(
        "SELECT COUNT(*) FROM canonical_jobs "
        "WHERE status='discovered' AND match_score IS NULL"
    ).fetchone()[0]


def _dead_sources(conn, window: int = 3) -> list[str]:
    """Enabled sources whose last `window` runs all pulled nothing or failed.
    Needs at least `window` recorded runs before flagging, so a newly added
    source isn't declared dead on day one."""
    dead = []
    sources = [r[0] for r in conn.execute("SELECT DISTINCT source FROM runs")]
    for s in sources:
        last = conn.execute(
            "SELECT pulled, ok FROM runs WHERE source=? ORDER BY id DESC LIMIT ?",
            (s, window),
        ).fetchall()
        if len(last) == window and all(r["pulled"] == 0 or not r["ok"] for r in last):
            dead.append(s)
    return sorted(dead)


def _shade(score: int) -> str:
    # Monochrome hierarchy: darker numeral = stronger match. No color.
    if score >= 85:
        return "#111111"
    if score >= 75:
        return "#3d3d3d"
    return "#8a8a8a"


def _esc(s) -> str:
    # Quotes escaped too: values land inside HTML attributes (href="...").
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _reason(verdict) -> str:
    try:
        return json.loads(verdict).get("reasons", "") if verdict else ""
    except Exception:  # noqa: BLE001, malformed verdict JSON just means no reason line
        return ""


_MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
_SANS = "-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"


def _status_line(unscored: int, dead: list[str]) -> str:
    parts = []
    if unscored:
        parts.append(f"{unscored} discovered jobs not yet scored (run /jh-triage + /jh-match)")
    if dead:
        parts.append(f"sources gone quiet: {', '.join(dead)}")
    return " · ".join(parts)


def _html(rows, threshold: int, status: str = "") -> str:
    items = []
    for i, r in enumerate(rows):
        sh = _shade(r["match_score"])
        reason = _reason(r["match_verdict"])
        reason_html = (
            f'<div style="font-size:13px;color:#555555;line-height:1.5;margin-top:6px;">{_esc(reason)}</div>'
            if reason else ""
        )
        rule = "border-top:1px solid #e6e6e6;" if i else ""
        items.append(f"""
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="{rule}">
 <tr>
  <td valign="top" width="56" style="padding:20px 0;font-family:{_MONO};font-size:26px;font-weight:700;color:{sh};line-height:1;">{r['match_score']}</td>
  <td valign="top" style="padding:20px 0 20px 4px;font-family:{_SANS};">
    <div style="font-size:16px;font-weight:700;color:#111111;line-height:1.3;">{_esc(r['title'])}</div>
    <div style="font-size:11px;letter-spacing:1.3px;text-transform:uppercase;color:#9a9a9a;font-family:{_MONO};margin-top:5px;">{_esc(r['company'])} &nbsp;/&nbsp; {_esc(r['location'] or 'Location n/a')}</div>
    {reason_html}
    <div style="margin-top:11px;"><a href="{_esc(r['url'])}" style="font-size:11px;letter-spacing:1.3px;text-transform:uppercase;color:#111111;text-decoration:none;border-bottom:1.5px solid #111111;padding-bottom:2px;">View posting &rarr;</a></div>
  </td>
 </tr>
</table>""")
    return f"""<div style="background:#ffffff;margin:0;padding:0;">
 <div style="max-width:600px;margin:0 auto;padding:36px 26px;font-family:{_SANS};color:#111111;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0"><tr>
   <td style="font-size:12px;letter-spacing:3px;text-transform:uppercase;font-weight:700;color:#111111;">Job Hunt / Daily</td>
   <td align="right" style="font-size:11px;letter-spacing:1px;color:#9a9a9a;font-family:{_MONO};">{len(rows)} scored since last digest &middot; score {threshold}+</td>
  </tr></table>
  <div style="border-top:2px solid #111111;margin-top:12px;"></div>
  {''.join(items)}
  <div style="border-top:2px solid #111111;"></div>
  {f'<div style="margin-top:14px;font-size:12px;color:#555555;font-family:{_SANS};">{_esc(status)}</div>' if status else ''}
  <div style="margin-top:18px;font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#bcbcbc;font-family:{_MONO};">Local jobhunt pipeline &middot; run /jh-match then python -m src.crm.viewer</div>
 </div>
</div>"""


def _text(rows, threshold: int, status: str = "") -> str:
    lines = [f"{len(rows)} matches scored since last digest (score >= {threshold}):", ""]
    for r in rows:
        lines.append(f"[{r['match_score']}] {r['title']} @ {r['company']} ({r['location'] or 'n/a'})")
        lines.append(f"    {r['url']}")
        lines.append("")
    if status:
        lines.append(f"Pipeline: {status}")
    return "\n".join(lines)


def main() -> None:
    try:
        cfg = load_yaml("notify.yaml")
    except FileNotFoundError:
        cfg = {}
    # min_score is an optional override; the default is THE shortlist threshold
    # (profile.yaml), so the digest can never silently disagree with the shortlist.
    threshold = cfg.get("min_score") or shortlist_threshold()

    conn = connect()
    rows = _digest_rows(conn, threshold)
    status = _status_line(_unscored_count(conn), _dead_sources(conn))
    if not rows:
        print("No newly scored matches above threshold.")
        if status:
            print(f"Pipeline: {status}")
        return

    urls = cfg.get("apprise_urls") or []
    placeholder = any(
        any(tok in u for tok in ("APP_PASSWORD_HERE", "BOT_TOKEN", "CHAT_ID", "your-secret-topic"))
        for u in urls
    )
    sent = False
    if urls and not placeholder:
        try:
            import apprise
            ap = apprise.Apprise()
            for u in urls:
                ap.add(u)
            sent = bool(ap.notify(
                title=f"Job hunt: {len(rows)} matches scored",
                body=_html(rows, threshold, status),
                body_format=apprise.NotifyFormat.HTML,
            ))
            print("Sent digest." if sent else "Digest send FAILED (check config/notify.yaml credentials).")
        except ImportError:
            print("apprise not installed; printing digest instead:\n")
            print(_text(rows, threshold, status))
    else:
        if placeholder:
            print("config/notify.yaml still has a placeholder credential; printing digest instead:\n")
        print(_text(rows, threshold, status))

    # Only mark notified if the digest actually went out, so nothing is lost before setup is done.
    if sent:
        conn.execute(
            "UPDATE jobs SET notified=1 WHERE notified=0 AND match_score >= ?", (threshold,)
        )
        conn.commit()
        print("Marked those matches as notified.")
    else:
        print("Not marking notified (nothing sent); will retry on the next run.")


if __name__ == "__main__":
    main()
