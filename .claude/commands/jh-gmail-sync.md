---
description: Read Gmail for status signals on open applications; propose changes, apply only after approval
allowed-tools: Bash, Write, Read, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__get_message
---

Read my Gmail for signals on my open applications and bring the pipeline up to date.
This skill is STRICTLY read-only on the mailbox: never label, draft, or send anything.
If the Gmail tools are unavailable, say so and stop; nothing else depends on this.

1. **Get the open applications** with Bash: `python -m src.query crm`, keep only rows
   with status `applied`/`screen`/`interview`/`offer`. Note each id, company,
   applied_at, last_contact_at, url.

2. **Search Gmail per application**: quoted company name, plus a `from:(@domain)`
   variant when the job url yields a company domain (the domain query is the trusted
   one; bare-name hits for generically-named companies classify conservatively).
   Window: `after:` the later of applied_at and last_contact_at, minus 2 days.
   Cap at 10 threads per application. Read only threads that plausibly concern
   my application.

3. **Classify** each relevant message into exactly one signal:
   - rejection -> propose `rejected`
   - interview invite / scheduling link -> advance ONE stage: applied -> `screen`,
     screen -> `interview`; already interview -> a contact touch, no status change
   - assessment / take-home link -> `screen` if currently applied, else a touch
   - offer letter / verbal-offer recap -> `offer`
   - human reply with no stage change (ack, "we'll get back to you") -> touch only
   - automated application receipt -> ignore entirely
   - anything unclear, or conflicting with the current status -> `ambiguous`
   NEVER propose ghosted, withdrawn, or accepting/declining an offer; those are my
   calls, not the inbox's.

4. **Write `data/gmail_pull.json`**: a JSON array of
   `{"job_id", "signal", "proposed_status" (null for touches), "contact_date",
   "evidence": {"from", "subject", "date", "message_id"}}`.
   Evidence is HEADERS ONLY; never copy email body text into the file, the DB,
   or your report.

5. **Dry run**: `python -m src.gmail_pull data/gmail_pull.json` with Bash. Show me
   the proposed batch exactly as printed (status changes, touches, ambiguous pile,
   skipped) and WAIT for my explicit approval. Do not proceed without it.

6. **Only after I approve**: re-run with `--apply`. Report what changed, and for the
   ambiguous pile suggest the manual path (`python -m src.query set-status` or
   `/jh-debrief` if there was an interview).

The applier enforces the guardrails (forward-only moves, evidence requirements,
backlog holds untouched); your job is honest classification, not persuasion. If in
doubt, classify as ambiguous. Zero em-dashes in anything you write.
