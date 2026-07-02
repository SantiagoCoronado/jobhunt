---
description: Pull fresh jobs from all enabled sources into the local DB
allowed-tools: Bash
---

Run the discovery pipeline and report the summary:

!`cd "$CLAUDE_PROJECT_DIR" && python -m src.discover`

Then tell me how many new jobs landed and remind me to run `/match` next.
