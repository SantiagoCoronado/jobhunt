---
description: Show applications due for follow-up and draft nudges
allowed-tools: Read, Bash, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__create_draft
---

Help me stay on top of follow-ups.

1. List active applications: run `python -m src.query followups` with Bash.
2. For each one whose `next_followup_at` is due (on or before today) or that has no reply yet,
   optionally check Gmail for a recent thread from that company (search by company name).
3. For the ones genuinely worth a nudge, draft a short, warm, specific follow-up email
   (Gmail draft, do NOT send). Reference the role and one concrete point of interest.
4. Give me a tight summary table: company, role, days since applied, suggested action.

Don't nag on roles already rejected or ghosted past 3 weeks, flag those to close out instead.
