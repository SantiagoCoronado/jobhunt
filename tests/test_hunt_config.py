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


# ---- writing: the TUI's harness tab edits the file in place ------------------------------

# A file of its own, not the shipped one: the TUI rewrites config/hunt.toml on the user's machine.
SAMPLE = """# How the hunt RUNS.

[harness]
default = "claude"                # any [harness.<name>] below or a shipped adapter
global_concurrency = 8

[stages.triage]
model = "haiku"                   # claude rolling alias; `hunt models` shows the alternatives
chunk = 100

[stages.match]
model = "opus"                    # calibration continuity with the existing shortlist

[stages.tailor]
model = "fable"                   # the tailor stays on the strongest writer available
retries = 1                       # the one fix round

[pick]
n = 5
"""


def _shipped_copy(tmp_path):
    path = tmp_path / "hunt.toml"
    path.write_text(SAMPLE, encoding="utf-8")
    return path


def test_set_stage_model_changes_one_line_and_keeps_every_comment(tmp_path):
    path = _shipped_copy(tmp_path)
    before = path.read_text(encoding="utf-8").splitlines()
    cfg = hc.set_stage_model("tailor", "opus", path)
    after = path.read_text(encoding="utf-8").splitlines()
    assert cfg.stage("tailor").model == "opus" and hc.load(path).stage("tailor").model == "opus"
    changed = [(b, a) for b, a in zip(before, after, strict=True) if b != a]
    assert len(changed) == 1
    old, new = changed[0]
    assert new.startswith('model = "opus"') and new.endswith("# the tailor stays on the strongest writer available")
    assert new.index("#") == old.index("#")                      # the comment kept its column
    assert not path.with_suffix(".toml.tmp").exists()


def test_a_long_model_name_pushes_the_comment_instead_of_eating_it(tmp_path):
    path = _shipped_copy(tmp_path)
    hc.set_stage_model("triage", "claude-haiku-4-5-20251001-with-a-long-tail", path)
    line = next(ln for ln in path.read_text(encoding="utf-8").splitlines() if "with-a-long-tail" in ln)
    assert '"  # claude rolling alias' in line


def test_clearing_a_model_means_the_harness_default(tmp_path):
    path = _shipped_copy(tmp_path)
    assert hc.set_stage_model("match", None, path).stage("match").model is None
    assert 'model = ""' in path.read_text(encoding="utf-8")


def test_set_default_harness_and_a_stage_with_no_model_line_yet(tmp_path):
    path = tmp_path / "hunt.toml"
    path.write_text('[harness]\nglobal_concurrency = 4\n\n[stages.inbox]\n# model = "x"\nretries = 1\n', encoding="utf-8")
    cfg = hc.set_default_harness("codex", path)
    assert cfg.harness == "codex" and cfg.global_concurrency == 4
    cfg = hc.set_stage_model("inbox", "sonnet", path)
    assert cfg.stage("inbox").model == "sonnet" and cfg.stage("inbox").retries == 1
    assert '# model = "x"' in path.read_text(encoding="utf-8")   # a commented line is not the key
    cfg = hc.set_stage_model("research", "sonnet", path)   # a table the file does not have
    assert cfg.stage("research").model == "sonnet"
    assert path.read_text(encoding="utf-8").rstrip().endswith('[stages.research]\nmodel = "sonnet"')


def test_writing_into_a_missing_file_creates_it(tmp_path):
    path = tmp_path / "config" / "hunt.toml"
    assert hc.set_stage_model("tailor", "fable", path).stage("tailor").model == "fable"
    assert hc.load(path).harness == "claude"


def test_a_python_stage_takes_no_model_and_a_bad_edit_writes_nothing(tmp_path):
    path = _shipped_copy(tmp_path)
    before = path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="runs no model"):
        hc.set_stage_model("pick", "opus", path)
    with pytest.raises(ValueError, match="control character"):
        hc.set_stage_model("tailor", "op\nus", path)
    broken = tmp_path / "broken.toml"
    broken.write_text("[stages.tailor]\nmodel = [\n  'a',\n]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="by hand"):
        hc.set_stage_model("tailor", "opus", broken)
    assert path.read_text(encoding="utf-8") == before
    assert "model = [" in broken.read_text(encoding="utf-8")


def test_an_integer_keeps_its_line_comment_and_a_value_under_the_minimum_writes_nothing(tmp_path):
    path = tmp_path / "hunt.toml"
    text = ('[harness]\ndefault = "claude"\nglobal_concurrency = 8          # rate-limit guard\n\n'
            '[stages.triage]\nmodel = "haiku"\nconcurrency = 8   # chunks at once\n\n[stages.tailor]\nmodel = "fable"\n')
    path.write_text(text, encoding="utf-8")
    cfg = hc.set_stage_concurrency("triage", 12, path)
    assert cfg.stage("triage").concurrency == 12
    after = path.read_text(encoding="utf-8")
    assert "concurrency = 12  # chunks at once" in after           # one line changed, the comment kept
    assert after.replace("concurrency = 12  # chunks at once", "concurrency = 8   # chunks at once") == text
    assert hc.set_global_concurrency(4, path).global_concurrency == 4
    assert "global_concurrency = 4          # rate-limit guard" in path.read_text(encoding="utf-8")
    hc.set_stage_concurrency("tailor", 2, path)                     # a missing key goes in under its table
    assert "[stages.tailor]\nconcurrency = 2\n" in path.read_text(encoding="utf-8")

    before = path.read_text(encoding="utf-8")
    with pytest.raises(ValueError, match="concurrency must be at least 1, got 0"):
        hc.set_stage_concurrency("triage", 0, path)
    with pytest.raises(ValueError, match="global_concurrency must be at least"):
        hc.set_global_concurrency(0, path)
    with pytest.raises(ValueError, match="one Python process"):
        hc.set_stage_concurrency("pick", 2, path)
    with pytest.raises(ValueError, match="must be an integer"):
        hc.set_int(before, "stages.triage", "concurrency", True)
    assert path.read_text(encoding="utf-8") == before
