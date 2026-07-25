---
description: Show applications due for follow-up and draft nudges
allowed-tools: Read, Bash, Write, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__get_message, mcp__claude_ai_Gmail__create_draft
---

Help me stay on top of follow-ups.

1. **Pull email reality first**: run the `/jh-gmail-sync` flow (search Gmail for
   signals on open applications, propose the batch, apply after my approval).
   That flow owns ALL email classification and status writes; do not re-derive
   replies ad hoc here. If Gmail is unavailable, continue from DB state.

2. List active applications: run `python -m src.query followups` with Bash.
   After step 1 this reflects the inbox: replies already bumped
   `last_contact_at`, rejections already closed their rows.

3. For each one whose `next_followup_at` is due (on or before today), decide if
   it genuinely deserves a nudge: skip anything that got a reply in step 1,
   anything nudged twice already, and anything rejected or ghosted.

4. For the ones worth a nudge, draft a short, warm, specific follow-up email
   (Gmail draft, do NOT send). Reference the role and one concrete point of
   interest. Voice rules: `docs/writing-voice.md`. After drafting, run
   `python -m src.query touch <id> --bump` so the follow-up date pushes out
   instead of nagging again tomorrow.

5. Close out dead roles: anything silent past 3 weeks and 2+ nudges gets
   `python -m src.query set-status <id> ghosted --note "no reply after N nudges"`.
   (Ghosted is a human call made HERE, never by the gmail sync.)

6. Give me a tight summary table: company, role, days since applied, last contact,
   action taken.
