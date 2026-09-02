---
description: Pull fresh jobs from all enabled sources into the local DB
allowed-tools: Bash, Write, mcp__claude_ai_Google_Drive__read_file_content
---

Run the discovery pipeline and report the summary.

0. **Refresh the dream sheet first.** The hand-curated dream-company sheet is a private
   Google Sheet; its file id is `dreamsheet.file_id` in `config/sources.yaml`. Read it with
   the Google Drive `read_file_content` tool and save the returned markdown table, verbatim,
   to `data/dream_sheet.md` (the `dreamsheet` adapter parses that file; header row must keep
   the Company / Role / Apply URL columns). If the Drive tool is unavailable, say so and keep
   the previous file; discover never blocks on this step.

A full sweep makes hundreds of sequential HTTP calls (all the Greenhouse tokens and Ashby
clients alone) and takes well over 2 minutes, so NEVER run it through the inline `!` command
syntax or a default-timeout Bash call; both kill it at 2 minutes mid-run. Instead run it with
the Bash tool in the background:

```
cd "$CLAUDE_PROJECT_DIR" && .venv/bin/python -m src.discover
```

(run_in_background: true). When it finishes, read the output and tell me how many new jobs
landed per source and in total, flag any source line marked FAILED, and remind me to run
`/jh-match` next. Partial progress is safe: discover commits after each source, so a killed
run keeps what it already pulled.
