"""One real 10-token call per shipped adapter (spec section 12, PR 4 story 1): the only tests
that start a real agent CLI, so they are opt-in three ways: the `harness_smoke` marker (the
conftest guard lets nothing else through), `HUNT_SMOKE=1`, and the binary on PATH.

    HUNT_SMOKE=1 .venv/bin/python -m pytest tests/test_hunt_harness_smoke.py -m harness_smoke

A harness that is installed but not signed in fails here with the CLI's own message, which is
the point: `hunt doctor --harness NAME` says the same thing."""
from __future__ import annotations

import os
import shutil

import pytest

from src.hunt import doctor, harness

pytestmark = pytest.mark.harness_smoke

SMOKED = [n for n in harness.SHIPPED if n != "claude"]      # claude's smoke is `hunt doctor`, run by hand since PR 2


@pytest.mark.parametrize("name", SMOKED)
def test_the_real_cli_answers_the_smoke_prompt(name, tmp_path):
    h = harness.get(name)
    if os.environ.get("HUNT_SMOKE") != "1":
        pytest.skip("set HUNT_SMOKE=1 to spend a real call")
    if shutil.which(h.binary) is None:
        pytest.skip(f"{h.binary} is not on PATH")
    res, err, _secs = doctor.smoke(h, None, cwd=tmp_path)
    assert err is None, err
    assert res is not None and "ok" in (res.text or "").lower()
