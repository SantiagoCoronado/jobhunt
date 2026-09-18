"""The hunt orchestrator (docs/spec-hunt-orchestrator.md): a Python state machine over the
stage registry, one harness process per unit of model work, one run ledger under
`data/hunt/<run_id>/`. Harness-neutral by design (decision 1): the same run works on claude,
codex, opencode, pi or agy, chosen in `config/hunt.toml`.

    python -m src.hunt run|status|report|runs|models|doctor|sync-agents

`config.py` reads hunt.toml, `ledger.py` reads and writes the run folder, `cli.py` is the
entry point. The stages, the pool and the harness adapters arrive in later stories of this PR.
"""
