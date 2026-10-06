# Scheduling

Nothing in the tree installs a schedule. If you want the read-only stages to run unattended, point
cron (Linux, WSL) or launchd (macOS) at one line run from the repo folder:
`.venv/bin/python -m src.hunt run --to match && .venv/bin/python -m src.notify`. That discovers,
triages and scores under the hunt orchestrator (ledger in `data/hunt/<run_id>/`, retries, the
models of `config/hunt.toml`), then sends the digest of what scored, if `config/notify.yaml` is
set up. A run that is already going holds the hunt lock, so an overlapping trigger is refused, not
doubled. Research and tailoring stay interactive (`/jh-hunt`, `/jh-tailor`), and nothing ever
submits an application.
