"""Stage 4 (push): HTML email digest of new high-match jobs via Apprise.

Dedupes by canonical_key so the same role never appears twice in one digest.
Run:  python -m src.notify
Config: config/notify.yaml (Apprise URLs). Falls back to plain text if no channel.
"""
from __future__ import annotations

import json

from .db import connect
from .config import load_yaml


def _digest_rows(conn, threshold: int):
    # MAX(match_score) + GROUP BY canonical_key returns the best-scoring row per role.
    return conn.execute(
        "SELECT id, company, title, location, url, MAX(match_score) AS match_score, match_verdict "
        "FROM jobs WHERE notified=0 AND match_score >= ? "
        "GROUP BY canonical_key ORDER BY match_score DESC LIMIT 40",
        (threshold,),
    ).fetchall()


def _shade(score: int) -> str:
    # Monochrome hierarchy: darker numeral = stronger match. No color.
    if score >= 85:
        return "#111111"
    if score >= 75:
        return "#3d3d3d"
    return "#8a8a8a"


def _esc(s) -> str:
    return str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _reason(verdict) -> str:
    try:
        return json.loads(verdict).get("reasons", "") if verdict else ""
    except Exception:
        return ""


_MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
_SANS = "-apple-system,BlinkMacSystemFont,'Helvetica Neue',Arial,sans-serif"


def _html(rows, threshold: int) -> str:
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
   <td align="right" style="font-size:11px;letter-spacing:1px;color:#9a9a9a;font-family:{_MONO};">{len(rows)} matches &middot; score {threshold}+</td>
  </tr></table>
  <div style="border-top:2px solid #111111;margin-top:12px;"></div>
  {''.join(items)}
  <div style="border-top:2px solid #111111;"></div>
  <div style="margin-top:18px;font-size:11px;letter-spacing:.8px;text-transform:uppercase;color:#bcbcbc;font-family:{_MONO};">Local jobhunt pipeline &middot; run /match then /notion-sync</div>
 </div>
</div>"""


def _text(rows, threshold: int) -> str:
    lines = [f"{len(rows)} new job matches (score >= {threshold}):", ""]
    for r in rows:
        lines.append(f"[{r['match_score']}] {r['title']} @ {r['company']} ({r['location'] or 'n/a'})")
        lines.append(f"    {r['url']}")
        lines.append("")
    return "\n".join(lines)


def main() -> None:
    try:
        cfg = load_yaml("notify.yaml")
    except FileNotFoundError:
        cfg = {}
    threshold = cfg.get("min_score", 70)

    conn = connect()
    rows = _digest_rows(conn, threshold)
    if not rows:
        print("No new matches above threshold.")
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
                title=f"Job hunt: {len(rows)} new matches",
                body=_html(rows, threshold),
                body_format=apprise.NotifyFormat.HTML,
            ))
            print("Sent digest." if sent else "Digest send FAILED (check config/notify.yaml credentials).")
        except ImportError:
            print("apprise not installed; printing digest instead:\n")
            print(_text(rows, threshold))
    else:
        if placeholder:
            print("config/notify.yaml still has a placeholder credential; printing digest instead:\n")
        print(_text(rows, threshold))

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
