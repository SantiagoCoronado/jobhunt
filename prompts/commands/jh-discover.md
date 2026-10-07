---
description: Pull fresh jobs from all enabled sources into the local DB
tools: [bash]
---

Run the discovery pipeline and report the summary.

A full sweep makes hundreds of sequential HTTP calls (all the Greenhouse tokens and Ashby
clients alone) and takes well over 2 minutes, so NEVER run it inline in your prompt or through
a shell call with a default timeout of a couple of minutes; either kills it mid-run. Instead run
it with your shell tool in the background (or with a timeout of at least 20 minutes when your
shell tool cannot background a command), from the repo root:

```
.venv/bin/python -m src.discover
```

When it finishes, read the output and tell me how many new jobs
landed per source and in total, flag any source line marked FAILED, and remind me to run
`/jh-match` next. Partial progress is safe: discover commits after each source, so a killed
run keeps what it already pulled.
