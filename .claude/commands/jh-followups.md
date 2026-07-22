---
description: Show applications due for follow-up and draft nudges
allowed-tools: Read, Bash, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__create_draft
---

Help me stay on top of follow-ups.

1. List active applications: run `python -m src.query followups` with Bash.
2. For each one whose `next_followup_at` is due (on or before today) or that has no reply yet,
   optionally check Gmail for a recent thread from that company (search by company name).
3. Record what you learn, so the next run starts from truth instead of re-deriving it:
   - Found a reply from the company? `python -m src.query touch <id> --date <reply-date>`.
     If the reply moves the pipeline (recruiter screen booked, rejection), also
     `python -m src.query set-status <id> screen|rejected --note "..."`.
   - No reply and you drafted a nudge (step 4)? After drafting, run
     `python -m src.query touch <id> --bump` so the follow-up date pushes out
     instead of nagging again tomorrow.
4. For the ones genuinely worth a nudge, draft a short, warm, specific follow-up email
   (Gmail draft, do NOT send). Reference the role and one concrete point of interest.
5. Close out dead roles: anything ghosted past 3 weeks with no reply gets
   `python -m src.query set-status <id> ghosted --note "no reply after N nudges"`.
   Don't nag on roles already rejected or ghosted.
6. Give me a tight summary table: company, role, days since applied, last contact, action taken.
