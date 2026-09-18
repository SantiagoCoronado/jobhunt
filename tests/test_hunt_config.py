"""src/hunt/config.py: hunt.toml says HOW the hunt runs; defaults, the harness-default model,
and the errors a typo must raise before a run starts (spec decision 6, section 6)."""
from __future__ import annotations

import pytest

from src.hunt import config as hc


def test_shipped_file_loads_with_the_spec_values():
    cfg = hc.load()
    assert cfg.source == hc.HUNT_TOML
    assert cfg.harness == "claude" and cfg.global_concurrency == 8
    assert [s for s in cfg.stages] == list(hc.STAGES)
    assert cfg.stage("triage").model == "haiku" and cfg.stage("triage").option("chunk") == 100
    assert cfg.stage("match").model == "opus" and cfg.stage("match").option("second_pass_min_bucket") == 2
    assert cfg.stage("tailor").model == "fable" and cfg.stage("tailor").attempts == 2
    assert cfg.stage("research").harness is None and cfg.harness_for("research") == "claude"
    assert cfg.pick_n == 5 and cfg.pick_dream_slots == 2
    for name in hc.PYTHON_STAGES:
        s = cfg.stage(name)
        assert not s.fanned and s.model is None and s.options == {}


def test_defaults_when_the_file_is_absent_or_empty(tmp_path):
    cfg = hc.load(tmp_path / "hunt.toml")
    assert cfg.source is None and cfg.harness == "claude"
    for name in hc.FANNED:
        assert cfg.stage(name).model is None, "no file: every fanned stage takes the harness default"
    assert cfg.stage("triage").concurrency == 8 and cfg.stage("triage").option("min_pile") == 200
    assert cfg.stage("inbox").timeout_s == 600 and cfg.stage("inbox").retries == 1
    assert hc.parse({}).snapshot() == hc.defaults().snapshot()


def test_missing_or_blank_model_means_the_harness_default():
    cfg = hc.parse({"stages": {"triage": {"concurrency": 2}, "match": {"model": ""}}})
    assert cfg.stage("triage").model is None and cfg.stage("triage").concurrency == 2
    assert cfg.stage("match").model is None
    assert cfg.stage("match").option("chunk") == 60          # untouched knobs keep their defaults


def test_per_stage_harness_override_and_generic_templates():
    raw = {"harness": {"default": "codex", "gemini": {"command": "gemini -p {prompt_file}", "envelope": "text"}},
           "stages": {"research": {"harness": "claude"}}}
    cfg = hc.parse(raw)
    assert cfg.harness == "codex" and cfg.harness_for("research") == "claude" and cfg.harness_for("tailor") == "codex"
    assert list(cfg.harness_templates) == ["gemini"]
    snap = cfg.snapshot()
    assert snap["harness"]["templates"] == ["gemini"] and snap["stages"]["research"]["harness"] == "claude"
    assert snap["stages"]["discover"] == {"kind": "python", "model": None, "harness": "codex"}


@pytest.mark.parametrize("raw,needle", [
    ({"stages": {"triag": {}}}, "unknown stage(s) triag"),
    ({"stages": {"discover": {"model": "opus"}}}, "Python stage and takes no options"),
    ({"stages": {"triage": {"chnk": 50}}}, "unknown key(s) chnk"),
    ({"stages": {"triage": {"concurrency": 0}}}, "concurrency must be at least 1"),
    ({"stages": {"triage": {"retries": "2"}}}, "retries must be an integer"),
    ({"stages": {"triage": {"model": 3}}}, "model must be a string"),
    ({"harness": {"default": "claude", "gemini": {}}}, "needs a `command` template"),
    ({"harness": {"defualt": "claude"}}, "[harness] unknown key(s) defualt"),
    ({"pick": {"n": 2, "dream_slots": 3}}, "dream_slots (3) exceeds n (2)"),
    ({"stage": {}}, "unknown table(s) stage"),
])
def test_typos_fail_on_load_not_mid_hunt(raw, needle):
    with pytest.raises(ValueError, match=__import__("re").escape(needle)):
        hc.parse(raw)


def test_unknown_stage_lookup_and_bad_toml(tmp_path):
    with pytest.raises(ValueError, match="unknown stage 'foo'"):
        hc.defaults().stage("foo")
    bad = tmp_path / "hunt.toml"
    bad.write_text("[stages.triage\nmodel = 'x'\n")
    with pytest.raises(ValueError, match="not valid TOML"):
        hc.load(bad)
