---
description: Generate and open the offline HTML dashboard from the pipeline DB. Usage: /jh-report
allowed-tools: Bash
---

Regenerate my job-hunt dashboard.

1. Run `python -m src.report --open` with Bash (use `.venv/bin/python` if plain
   `python` is not on PATH). The script writes `data/report.html` (self-contained,
   offline, gitignored) and opens it in the browser.
2. Relay the headline line the script prints (applications, response rate, median
   response, interviews, offers) as plain text.

That is the whole job. Do NOT add your own analysis or estimate any number; the
report is deterministic and interpretation lives in `/jh-review`.
