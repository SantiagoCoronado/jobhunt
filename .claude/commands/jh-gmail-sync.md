---
description: Read every configured mailbox for status signals on open applications; classify, dry-run, apply (auto-apply since 2026-09-04)
allowed-tools: Bash, Write, Task, mcp__claude_ai_Gmail__search_threads, mcp__claude_ai_Gmail__get_thread, mcp__claude_ai_Gmail__get_message
---

Bring the pipeline up to date with what the inbox says about my open applications.
This flow is STRICTLY read-only on every mailbox: never label, draft, or send anything.
It has the single-unit shape: Python fetches, one inbox-classifier agent classifies, Python
applies. Token discipline is part of the job: you never hold the manifest yourself, and you
never read the files behind it.

1. **Run the fetcher**: `python -m src.mail_fetch --summary` with your shell tool
   (`.venv/bin/python` if plain `python` is not on PATH). It prints the `sweep:` stamp, one
   summary line per account/folder with noise counts, any `tune:` lines, and the thread and
   page count of the manifest it wrote. Show me the summary lines and every `tune:` line
   verbatim; those are my only prompt to edit `config/mail_hints.yaml`. Say which mailboxes the
   sweep covered, and say it plainly when that is zero. With 0 threads, stop here: nothing to
   classify.

2. **Hard rules for this session**:
   - NEVER run `python -m src.query crm` or `python -m src.query job` here, and never print the
     manifest yourself (`mail_fetch manifest`, `show`); the agent reads it.
   - NEVER `cat`, read, `grep`, `jq`, or script over anything under `data/mail_`.
   - Do NOT search Gmail through the mail connector when any account reported `ok`.

3. **Fallback only when no account is configured** (the run printed the
   "no mail accounts configured" hint) AND a Gmail connector is available to you: search per
   open application (quoted company name plus `from:(@domain)` when the job url yields a
   domain; window `after:` the later of applied_at and last_contact_at minus 2 days; cap 10
   threads per application), read only threads that plausibly concern my application, and
   take `message_id` from the RFC 822 Message-ID header with the angle brackets stripped.
   For this path only, `python -m src.query crm` is allowed to get the open rows, and you
   classify by the rules in `prompts/agents/inbox-classifier.md` yourself. If neither the
   fetcher nor a connector is usable, say so and stop; nothing else depends on this.

4. **Classify**: hand the manifest to the **inbox-classifier** agent (your harness's native
   agent file supplies its prompt, tools and model). The prompt is two lines:
   `Classify sweep <the stamp>. The manifest is on disk: <P> page(s), print each with
   python -m src.mail_fetch manifest --page N. Reply with the proposals as a bare JSON array.`
   The agent runs `show` for the lines it cannot settle and replies with one proposal per
   manifest line: `{"manifest_id", "sweep", "signal", "proposed_status"}` (plus `"job_id"` when
   a line lists several jobs, `"needs_human"` where it would have asked). The `signal` values
   are the applier's: `rejection`, `interview_invite`, `assessment`, `offer`, `reply`,
   `ignore`, `ambiguous`. It never proposes ghosted, withdrawn, or accepting/declining an
   offer; those are my calls.

5. **Write `data/gmail_pull.json`**: the agent's JSON array exactly as it replied (or, on the
   fallback path, your own array where every object carries `{"job_id": <int>, "signal",
   "proposed_status" (null for touches/ignore), "contact_date": "YYYY-MM-DD" (omit for
   ignore), "evidence": {"from", "subject", "date", "message_id", "thread_id", "account"}}`;
   rejections and offers without both `subject` and `from` are skipped, and a touch without a
   date is skipped). The applier refuses the whole file when the stamp does not match the
   manifest on disk, and copies the evidence headers, the job id and the contact date from the
   manifest line itself. Evidence is HEADERS ONLY; never copy snippet text into the file, the
   DB, or your report. If the reply is not a JSON array, ask the agent once more for the bare
   array; do not classify yourself.

6. **Dry run, then apply** (auto-apply, the standing decision of 2026-09-04: the
   applier's guardrails are the gate, not a chat approval). Run
   `python -m src.gmail_pull data/gmail_pull.json` with your shell tool and read its output; if it
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
holds untouched); the classifier's job is honest classification, not persuasion. If in
doubt, it classifies as ambiguous. Zero em-dashes in anything you write.

For a batch, `python -m src.hunt run --only inbox` runs this stage under the hunt orchestrator (ledger, retries, coverage checks, `--resume`); this prose flow is for a single interactive use.
