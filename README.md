# jobhunt 🎯

A DIY, **$0**, locally-run job-search copilot that leverages **Claude Code** as its agent engine.
It automates the parts that actually raise your callback rate, **discovery, tailoring, and
tracking**, and deliberately keeps a **human on the submit button**.

> **The reframe that matters:** mass auto-apply gets ~1–3% callbacks (same as manual cold-
> applying) and gets LinkedIn/Indeed accounts banned. Targeted, tailored applications to
> 10–20 good roles/week get ~25%. This tool optimizes for the second thing.

## What it does

| Stage | How | Tool |
|-------|-----|------|
| ① Discover | Pull free, ToS-safe ATS APIs + aggregators → SQLite | `python -m src.discover` |
| ② Match | Score each job vs your profile | `/match` → `job-matcher` agent |
| ③ Tailor | Per-job resume + cover letter (truthful, ATS-clean) | `/tailor <id>` → `resume-tailor` agent |
| ④ Apply | You review the draft and submit (assisted form-fill optional) | manual / Playwright |
| ⑤ Track | Local kanban CRM + follow-ups | `python -m src.crm.viewer` or `/notion-sync` |

Sources with **zero setup**: RemoteOK, Remotive, We Work Remotely, HN "Who is Hiring",
Get on Board (LatAm). Add your target companies' **Greenhouse/Lever/Ashby** tokens for the
highest-signal listings.

## Setup

```bash
cd ~/projects/jobhunt
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Edit your yardstick + resume (keep everything true):
#    config/profile.yaml, target roles, real skills, locations, salary floor
#    resume/master_resume.yaml, your master resume (RenderCV schema)
#    config/sources.yaml, add Greenhouse/Lever/Ashby tokens for target companies
cp config/notify.yaml.example config/notify.yaml   # optional: Telegram/ntfy/email digest
```

## Daily use

```bash
./run.sh                 # discover + queue + digest
```
Then, in Claude Code from this folder:
```
/match                   # score newly discovered jobs
/tailor 42               # tailor resume + cover letter for job id 42 (review before sending!)
/notion-sync             # mirror pipeline to a Notion board (phone-friendly)
/followups               # draft nudges for applications due a follow-up
```
Local CRM instead of Notion:
```bash
python -m src.crm.viewer      # http://localhost:5000
```

## Schedule it (Windows 11 + WSL)

In-WSL cron dies when the VM idles, so trigger from Windows Task Scheduler:
- Program: `wsl.exe`
- Arguments: `-d Ubuntu -e bash -lc "/home/kenpachi/projects/jobhunt/run.sh"`
- Trigger: daily 08:00 (tick "Wake the computer to run this task")

## Ground rules (baked into the agents)

- **Never fabricate** experience, tailoring only reframes what's in your master resume.
  Fabrication → rescinded offers; interviews expose what you can't defend.
- **Never auto-submit** or automate **logged-in LinkedIn/Indeed**, that's the account-ban path
  (LinkedIn User Agreement §8.2) and it converts *worse* than targeted applying anyway.
- Discovery uses **only free, sanctioned** endpoints. `jobspy` (Indeed/LinkedIn scraping) is
  **off by default**; it breaks often and carries ToS/ban risk, enable only for low-volume
  personal use, never while logged in.
- No keyword stuffing / white-text tricks, parsers strip formatting, so it's visible to the
  recruiter and reads as dishonest.

## Layout

```
config/        profile.yaml · sources.yaml · notify.yaml
resume/        master_resume.yaml   (single source of truth)
src/           discover · match · notify · query · db · models · adapters/ · crm/
.claude/       agents/ (job-matcher, resume-tailor) · commands/ (/discover /match /tailor …)
applications/  per-job tailored output (git-ignored)
data/          jobs.db + queue files (git-ignored)
```

Not legal advice. Respect each site's Terms of Service; you're responsible for how you use this.
