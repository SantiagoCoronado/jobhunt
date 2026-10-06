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
| ① Discover | Pull free, ToS-safe ATS APIs + aggregators → SQLite (auto-expires vanished postings) | `python -m src.discover` |
| ② Triage | Cheap Haiku junk-cut when the pile is large; keepers get a 0-3 fit bucket | `/jh-triage` |
| ③ Match | Score each surviving job vs your profile | `/jh-match` → `job-matcher` agent |
| ④ Research | Cited company dossier, reused across applications | `/jh-research <company\|id>` → `company-researcher` agent |
| ⑤ Tailor | Per-job resume + cover letter (truthful, ATS-clean) | `/jh-tailor <id>` → `resume-tailor` agent |
| ⑥ Apply | You review the draft and submit | manual, always |
| ⑦ Track | Local CRM, follow-up nudges, inbox sync | `python -m src.tui` · `/jh-followups` · `/jh-gmail-sync` |

`/jh-hunt` runs the whole loop end to end and tailors the top 5 shortlisted.

Sources with **zero setup**: RemoteOK, Remotive, We Work Remotely, HN "Who is Hiring",
Get on Board (LatAm). Add your target companies' **Greenhouse/Lever/Ashby** tokens for the
highest-signal listings.

## Setup

```bash
cd ~/projects/jobhunt
./setup.sh                       # one command: venv + deps + `python -m src.init` (your files from the examples)
# ...or manually:
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1. Edit your yardstick + resume (keep everything true):
#    config/profile.yaml, target roles, real skills, locations, salary floor
#    resume/master_resume.yaml, your master resume (RenderCV schema)
#    config/sources.local.yaml, your Greenhouse/Lever/Ashby tokens and countries (see the .example)
python -m src.init               # creates profile.yaml, master_resume.yaml, answers.yaml, sources.local.yaml, notify.yaml, .env from the examples
```

## Daily use

```bash
python -m src.discover   # pull fresh jobs into data/jobs.db
python -m src.notify     # optional digest of already-scored matches (config/notify.yaml)
```
Then, in Claude Code from this folder:
```
/jh-triage               # Haiku junk-cut when the discovered pile is large
/jh-match                # score newly discovered jobs
/jh-research 42          # cited company dossier (reused by tailor)
/jh-tailor 42            # tailor resume + cover letter for job id 42 (review before sending!)
/jh-followups            # draft nudges for applications due a follow-up
/jh-hunt                 # or run the whole loop end to end
```
Record a submission (moves the folder AND schedules the follow-up):
```bash
python -m src.query set-status 42 applied
```
Local CRM, a terminal UI (`docs/spec-tui.md`): board and follow-ups over one
three-pane screen, `s` status, `n` notes, `f` follow-up, `/` search, `>` `<` `-` sort, `?` every key;
the `dream list` entry shows the rows at your dream companies (`a` adds one, `x` removes one;
`python -m src.query dream {list|add|rm}` does the same from a shell);
`3` the application folders, `4` the funnel, `5` runs a stage or the whole hunt with its log beside it,
`6` the config files (`e` edits one), `,` the settings (theme, launch section, harness and models, editor):
```bash
python -m src.tui
```
One word from any directory (a symlink to `bin/jobhunt` in `~/.local/bin`; pass another name if
you would rather type something else, `--uninstall` removes it):
```bash
scripts/install_launcher.sh          # then: jobhunt
```

## Run it on a second machine (macOS / Linux)

The repo is portable and the `.claude/` skills travel with it. Local state (`data/`,
`applications/`, `config/notify.yaml`) is git-ignored and stays per-machine; SQLite on the
machine that runs the hunt is the CRM.

```bash
git clone https://github.com/<you>/jobhunt.git
cd jobhunt
./setup.sh                       # venv + deps + scaffolds config/notify.yaml
# paste your Gmail app password into config/notify.yaml (git-ignored, never committed)
python -m src.discover           # first discovery run on this machine
```
Recommended split: keep any scheduled run on one always-on machine; use the other
as an **interactive** client (`/jh-match`, `/jh-tailor` by hand) to avoid double emails. Sync code changes with plain `git pull` / `git push`.

## Schedule it

Nothing is installed for you. `docs/scheduling.md` shows the one cron or launchd line that runs
`python -m src.hunt run --to match` and then the digest.

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
config/        profile.yaml (incl. location_rule + shortlist_threshold) · sources.yaml · notify.yaml
resume/        master_resume.yaml   (single source of truth)
src/           discover · triage · match · notify · query · research · reconcile · pick
               · maintain · render_docx · db · models · adapters/ · tui/
.claude/       agents/ (job-matcher, resume-tailor, company-researcher)
               commands/ (/jh-hunt /jh-discover /jh-triage /jh-match /jh-research /jh-tailor …)
research/      companies/<slug>.md   cited dossiers (committed, reusable)
applications/  {pending,applied,other}/<company>-<id>/  tailored output (git-ignored)
tests/         pytest suite (`.venv/bin/python -m pytest tests/`)
data/          jobs.db + queue files (git-ignored)
```

Not legal advice. Respect each site's Terms of Service; you're responsible for how you use this.
