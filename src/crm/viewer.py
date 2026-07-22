"""Stage ④ (view): a tiny local CRM over jobs.db. Single-user, localhost only.

Run:  python -m src.crm.viewer   then open http://localhost:5000
Columns = pipeline stages. Change a job's status / notes / follow-up date inline.
"""
from __future__ import annotations

from ..config import followup_days
from ..db import connect, STATUSES, set_status
from ..reconcile import sync_folder

try:
    from flask import Flask, request, redirect
except ImportError:  # pragma: no cover
    raise SystemExit("Install Flask:  pip install flask") from None

app = Flask(__name__)

PAGE = """<!doctype html><meta charset=utf-8><title>Job Hunt CRM</title>
<style>
 body{{font:14px/1.4 system-ui,sans-serif;margin:0;background:#111;color:#eee}}
 header{{padding:12px 18px;background:#000;border-bottom:1px solid #333;position:sticky;top:0}}
 .board{{display:flex;gap:12px;padding:16px;overflow-x:auto;align-items:flex-start}}
 .col{{flex:0 0 300px;background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px}}
 .col h2{{font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:#9ad;margin:0;padding:10px 12px;border-bottom:1px solid #2a2a2a}}
 .card{{padding:10px 12px;border-bottom:1px solid #222}}
 .card b{{color:#fff}} .score{{float:right;background:#264;color:#cfc;border-radius:10px;padding:1px 8px;font-size:12px}}
 .muted{{color:#888;font-size:12px}} a{{color:#7bf;text-decoration:none}}
 select,input,textarea{{background:#222;color:#eee;border:1px solid #444;border-radius:4px;padding:2px 4px;font-size:12px;font-family:inherit}}
 form.inline{{margin-top:6px;display:flex;gap:4px;flex-wrap:wrap}}
</style>
<header><b>Job Hunt CRM</b> &nbsp;<span class=muted>{count} jobs · {shortlisted} shortlisted · sorted by match score</span></header>
<div class=board>{cols}</div>"""

COL = "<div class=col><h2>{status} ({n})</h2>{cards}</div>"
CARD = """<div class=card>
 <span class=score>{score}</span><b>{title}</b><br>
 <span class=muted>{company} · {location}</span><br>
 <a href="{url}" target=_blank>open posting ↗</a>
 <form class=inline method=post action=/update>
   <input type=hidden name=id value="{id}">
   <select name=status onchange="this.form.submit()">{opts}</select>
   <input name=next_followup value="{followup}" placeholder="follow-up YYYY-MM-DD" size=12>
   <textarea name=notes placeholder="notes" rows=1 cols=20>{notes}</textarea>
   <button>save</button>
 </form></div>"""


@app.route("/")
def board():
    conn = connect()
    # irrelevant/expired are terminal junk, not pipeline stages: keep them off the board
    rows = conn.execute(
        "SELECT * FROM jobs WHERE (status!='discovered' OR match_score IS NOT NULL) "
        "AND status NOT IN ('irrelevant','expired') "
        "ORDER BY COALESCE(match_score,0) DESC, id DESC"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) c FROM jobs").fetchone()["c"]
    shortlisted = sum(1 for r in rows if r["status"] == "shortlisted")

    cols = []
    for st in (s for s in STATUSES if s not in ("irrelevant", "expired")):
        cards = []
        for r in [x for x in rows if x["status"] == st]:
            opts = "".join(
                f'<option {"selected" if o==r["status"] else ""}>{o}</option>' for o in STATUSES
            )
            cards.append(CARD.format(
                id=r["id"], title=_h(r["title"]), company=_h(r["company"]),
                location=_h(r["location"] or ""), url=_h(r["url"] or "#"),
                score=r["match_score"] if r["match_score"] is not None else "–",
                opts=opts, followup=_h(r["next_followup_at"] or ""),
                notes=_h(r["notes"] or ""),
            ))
        cols.append(COL.format(status=st, n=len(cards), cards="".join(cards) or "<div class=card muted>(none)</div>"))

    return PAGE.format(count=total, shortlisted=shortlisted, cols="".join(cols))


@app.route("/update", methods=["POST"])
def update():
    f = request.form
    conn = connect()
    try:
        changed = set_status(
            conn, f["id"], f["status"],
            notes=f.get("notes", ""),
            next_followup=f.get("next_followup", ""),
            followup_days=followup_days(),
        )
    except ValueError as e:
        return str(e), 400
    conn.commit()
    sync_folder(int(changed["id"]), f["status"])
    return redirect("/")


def _h(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace('"', "&quot;")


if __name__ == "__main__":
    app.run(port=5000, debug=False)
