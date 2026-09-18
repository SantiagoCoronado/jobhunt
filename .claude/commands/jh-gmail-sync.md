---
description: Read every configured mailbox for status signals on open applications; classify, dry-run, apply (auto-apply since 2026-09-04)
allowed-tools: Bash, Write, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__get_message
---

Bring the pipeline up to date with what the inbox says about my open applications.
This skill is STRICTLY read-only on every mailbox: never label, draft, or send anything.
Token discipline is part of the job: the fetcher prints a manifest sized to be read
directly; you never read the files behind it.

1. **Run the fetcher**: `python -m src.mail_fetch` with Bash (`.venv/bin/python` if
   plain `python` is not on PATH). It prints one summary line per account/folder with
   noise counts, any `tune:` lines, a legend (one line per job with mail: id, company,
   title, status, applied date), and page 1 of the manifest (one line per thread: id,
   account, job, date, sender, hints, subject | lead). Show me the summary lines and
   every `tune:` line verbatim; those are my only prompt to edit `config/mail_hints.yaml`.
   Say which mailboxes the sweep covered, and say it plainly when that is zero.

2. **The printed legend and manifest are the whole input.** Hard rules:
   - NEVER run `python -m src.query crm` or `python -m src.query job` here. The legend is
     the job context; those two commands cost more tokens than the entire sweep.
   - NEVER `cat`, Read, `grep`, `jq`, or `python -c` over anything under `data/mail_`.
     The snippet file holds bodies and the manifest file is the archive, not the input.
   - Do NOT search Gmail through the MCP tools when any account reported `ok`.
   - Work page by page: a manifest over 80 lines prints a footer; finish page 1
     (classify, `show`, write proposals) before `python -m src.mail_fetch manifest --page 2`.
     Never spawn a sub-agent for this step.

3. **Fallback only when no account is configured** (the run printed the
   "no mail accounts configured" hint) AND the Gmail MCP tools are available: search per
   open application (quoted company name plus `from:(@domain)` when the job url yields a
   domain; window `after:` the later of applied_at and last_contact_at minus 2 days; cap 10
   threads per application), read only threads that plausibly concern my application, and
   take `message_id` from the RFC 822 Message-ID header with the angle brackets stripped.
   For this path only, `python -m src.query crm` is allowed to get the open rows. If neither
   the fetcher nor the MCP is usable, say so and stop; nothing else depends on this.

4. **Classify** each manifest line into exactly one signal by the rules in
   `prompts/agents/inbox-classifier.md` (read it once; it is the same system prompt the hunt
   orchestrator gives the inbox unit). The `signal` values are the applier's, and it skips any
   other word: `rejection`, `interview_invite` (advance ONE stage), `assessment`, `offer`,
   `reply` (a contact touch), `ignore`, `ambiguous`. Settle a line from the manifest only when the lead itself
   carries the decision sentence; for every unsettled line, and for every `offer?` line
   regardless, run `python -m src.mail_fetch show <id> <id> ...` ONCE with all the ids you
   need (25 per call). NEVER propose ghosted, withdrawn, or accepting/declining an offer;
   those are my calls.

5. **Write `data/gmail_pull.json`**: a JSON array, one object per proposal.
   - Manifest path (step 1 ran): `{"manifest_id": <the line id>, "sweep": "<the sweep: stamp
     the fetcher printed>", "signal", "proposed_status" (null for touches/ignore)}`. The stamp
     ties the ids to the manifest they came from; the applier refuses the whole file when the
     stamp does not match the manifest on disk, and skips (and reports) a single line it
     cannot resolve. The applier copies the evidence headers (from, subject, date,
     message_id, thread_id, account), the job id and the contact date from that manifest
     line itself, so you never need the ids. Add `"job_id"` only when the line lists several
     jobs.
   - Fallback path (step 3, no manifest, so no `manifest_id` and no `sweep`): write every
     field yourself: `{"job_id": <int>, "signal", "proposed_status" (null for
     touches/ignore), "contact_date": "YYYY-MM-DD" (omit for ignore), "evidence": {"from",
     "subject", "date", "message_id", "thread_id", "account"}}`. Rejections and offers
     without both `subject` and `from` are skipped, and a touch without a date is skipped.
   Evidence is HEADERS ONLY on both paths; never copy snippet text into the file, the DB,
   or your report.

6. **Dry run, then apply** (auto-apply, the standing decision of 2026-09-04: the
   applier's guardrails are the gate, not a chat approval). Run
   `python -m src.gmail_pull data/gmail_pull.json` with Bash and read its output; if it
   printed nothing surprising (no `Skipped` line you cannot explain, no stamp error),
   re-run at once with `--apply`. Stop and ask ONLY when a proposal names a different role
   or company than the DB row (a rejection for "GTM AI Engineer" against an SDK Engineer
   row), when a mailbox reported `error`, or when the dry run itself refused the file.

7. **Report** the applied batch exactly as printed (status changes, touches, ambiguous
   pile, skipped, ignored count), what changed and how many ids were recorded as seen,
   in plain words: which company moved where and why, one line each, the good news first.
   For the ambiguous pile suggest the manual path
   (`python -m src.query set-status` or `/jh-debrief` if there was an interview), and say
   it plainly: after `--apply` those ambiguous messages will not come back in a future
   sweep (only that message; later replies on the thread still surface), so they have to
   be handled now or noted for follow-up. Name the account each signal came from; a reply
   has to go out from that mailbox.

The applier enforces the guardrails (forward-only moves, evidence requirements, backlog
holds untouched); your job is honest classification, not persuasion. If in doubt,
classify as ambiguous. Zero em-dashes in anything you write.
