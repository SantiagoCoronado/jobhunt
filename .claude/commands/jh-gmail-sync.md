---
description: Read every configured mailbox for status signals on open applications; propose changes, apply only after approval
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

4. **Classify** each manifest line into exactly one signal:
   - rejection -> propose `rejected`
   - interview invite / scheduling link -> advance ONE stage: applied -> `screen`,
     screen -> `interview`; already interview -> a contact touch, no status change
   - assessment / take-home link -> `screen` if currently applied, else a touch
   - offer letter / verbal-offer recap -> `offer`
   - human reply with no stage change (ack, "we'll get back to you") -> touch only
   - automated receipt, product mail, anything not about my application -> `ignore`
     (write it to the file with `proposed_status: null` and no `contact_date`; the applier
     records it as seen so it never comes back)
   - anything unclear, or conflicting with the current status -> `ambiguous`
   Settle a line from the manifest only when the lead itself contains the decision
   sentence. A hint (`reject?`, `schedule?`, `assessment?`, `offer?`, `receipt?`,
   `human?`) is never enough on its own. For every unsettled line, and for every
   `offer?` line regardless, run `python -m src.mail_fetch show <id> <id> ...` ONCE with
   all the ids you need (25 per call), then classify from the snippets. Lines flagged
   `weak` propose only touches, `ignore`, or `ambiguous` unless the text names the role.
   NEVER propose ghosted, withdrawn, or accepting/declining an offer; those are my calls.

5. **Write `data/gmail_pull.json`**: a JSON array of
   `{"manifest_id": <the line id>, "sweep": "<the sweep: stamp the fetcher printed>", "signal",
   "proposed_status" (null for touches/ignore)}`. The stamp ties the ids to the manifest they
   came from; the applier refuses a proposal whose stamp does not match the manifest on disk.
   The applier copies the evidence headers (from, subject, date, message_id, thread_id,
   account), the job id and the contact date from that manifest line itself, so you never
   need the ids. Add `"job_id"` only when the line lists several jobs. Evidence is HEADERS
   ONLY; never copy snippet text into the file, the DB, or your report.

6. **Dry run**: `python -m src.gmail_pull data/gmail_pull.json` with Bash. Show me the
   proposed batch exactly as printed (status changes, touches, ambiguous pile, skipped,
   ignored count) and WAIT for my explicit approval. Do not proceed without it.

7. **Only after I approve**: re-run with `--apply`. Report what changed and how many ids
   were recorded as seen. For the ambiguous pile suggest the manual path
   (`python -m src.query set-status` or `/jh-debrief` if there was an interview), and say
   it plainly: after `--apply` those ambiguous messages will not come back in a future
   sweep (only that message; later replies on the thread still surface), so they have to
   be handled now or noted for follow-up. Name the account each signal came from; a reply
   has to go out from that mailbox.

The applier enforces the guardrails (forward-only moves, evidence requirements, backlog
holds untouched); your job is honest classification, not persuasion. If in doubt,
classify as ambiguous. Zero em-dashes in anything you write.
