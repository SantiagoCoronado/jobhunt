---
description: Mirror the job pipeline into a Notion database (your phone-friendly CRM)
allowed-tools: Bash, mcp__claude_ai_Notion__notion-search, mcp__claude_ai_Notion__notion-create-database, mcp__claude_ai_Notion__notion-create-pages, mcp__claude_ai_Notion__notion-query-data-sources, mcp__claude_ai_Notion__notion-update-page
---

Sync my job pipeline to Notion so I can track it from my phone.

1. Get the trackable jobs: run `python -m src.query crm` with Bash (JSON of every job past
   'discovered').
2. Find or create a Notion database named **"Job Hunt"** with properties: Company (title),
   Role, Status (select: shortlisted/applied/screen/interview/offer/rejected), Match (number),
   Location, URL, Applied, Follow-up (date), Notes.
3. Upsert: for each job, match on Company+Role. Update the row if it exists, else create it.
   Use the DB `status`/`match_score`/`next_followup_at`/`notes` as the source of truth.
4. **Star the top 10.** Rank the synced applications by Match (highest first) and take the top 10.
   Set the Notion page icon to a star (⭐) on those 10, and remove the icon from every other synced
   page, so exactly the current top 10 are starred. Break ties at the cutoff in favor of the more
   AI-forward or better-located role.
5. Report rows created vs updated, which 10 are starred, and the Notion database URL.

The local SQLite DB is canonical; Notion is a read/update mirror for convenience.
