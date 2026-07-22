---
description: Two-way sync between the job pipeline and Notion (your phone-friendly CRM)
allowed-tools: Bash, Write, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-create-database, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-query-data-sources, mcp__claude_ai_Notion__notion-update-page
---

Sync my job pipeline with Notion. Notion is where I update statuses from my phone,
so PULL its edits into SQLite first, then PUSH the full pipeline back out.

## Phase 1: pull (Notion -> DB)

1. Find the Notion database **"Job Hunt"** (search, then fetch to get its
   `collection://` data source URL).
2. Query every row that carries a decision or a date, via SQL mode:
   `SELECT url, Company, Role, Status, "date:Applied:start" AS applied,
   "date:Follow-up:start" AS followup, Match, Notes, Link FROM "collection://..."
   WHERE Status NOT IN ('shortlisted','discovered') OR followup IS NOT NULL`
3. Write the rows to `data/notion_pull.json` as a JSON array of
   `{company, role, status, applied, followup, notes, link}` objects.
4. Run `python -m src.notion_pull data/notion_pull.json` (dry run), sanity-check
   the diff, then re-run with `--apply`. The script maps Notion's
   `declined`/`Not Found` to DB `withdrawn`, never downgrades a more advanced DB
   status, never overwrites a `backlog` hold, and moves application folders.
   Rows with no DB match: re-run with `--create-missing` if they are real
   applications; otherwise report them.

## Phase 2: push (DB -> Notion)

5. Get the trackable jobs: run `python -m src.query crm` with Bash.
6. Upsert into the same database (Company title, Role, Status select, Match number,
   Location, Link, Applied date, Follow-up date, Notes): match on Link first,
   else Company+Role. Update existing rows, create missing ones.
   Status mapping DB -> Notion: `withdrawn` -> `declined`, `backlog` -> `shortlisted`
   (keep the "Backlog:" note prefix); everything else maps 1:1.
7. **Star exactly the top 5 `shortlisted` rows by Match** (same rule as /jh-hunt):
   set the page icon to ⭐ on those 5 and remove it everywhere else. Break ties
   in favor of the more AI-forward or better-located role.
8. Report: pull changes applied, rows created vs updated, the 5 starred, DB URL.

The local SQLite DB is canonical after a pull; between syncs, Notion edits are
treated as the freshest human intent.
