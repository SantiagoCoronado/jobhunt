"""python -m src.onboard sources / verify-token (docs/spec-pre-release.md PR 5 story 3): the
proposal from the profile's coverage with the keyed sources marked, and one live request per
ATS token, answered here by a fake. No test touches the network."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from src import config, onboard

FIXTURES = Path(__file__).resolve().parent / "fixtures"


class Resp:
    def __init__(self, status: int, body=None, text: bool = False) -> None:
        self.status_code = status
        self._body = body
        self._text = text

    def json(self):
        if self._text:
            raise ValueError("Expecting value")
        return self._body


@pytest.fixture
def calls(tmp_path, monkeypatch):
    """The fake board: answers by token, records every request."""
    shutil.copyfile(FIXTURES / "sources.local.yaml", tmp_path / "sources.local.yaml")
    monkeypatch.setitem(config.USER_FILES, "sources_local", tmp_path / "sources.local.yaml")
    monkeypatch.setattr(onboard, "ONBOARD_DIR", tmp_path / "onboard")
    for key in ("ADZUNA_APP_ID", "ADZUNA_APP_KEY", "FINDWORK_TOKEN", "CAREERJET_AFFID", "THEMUSE_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    seen: list[tuple[str, dict]] = []
    answers = {
        "examplecorp": Resp(200, {"jobs": [{"id": 1}, {"id": 2}]}),
        "quietco": Resp(200, {"jobs": []}),
        "gone": Resp(404, {"error": "not found"}),
        "htmlco": Resp(200, text=True),
        "ledgerly": Resp(200, [{"id": "a"}]),                    # lever answers with the list itself
    }

    def fake_get(url, params):
        seen.append((url, params))
        token = url.rstrip("/").split("/")[-2 if url.endswith("/jobs") else -1]
        if token == "down":
            raise ConnectionError("no route")
        return answers.get(token, answers["examplecorp"])

    monkeypatch.setattr(onboard, "_get", fake_get)
    return seen


def test_the_proposal_follows_the_profile_coverage_and_marks_the_keyed_sources(calls):
    lines = onboard.proposal()
    text = "\n".join(lines)
    assert lines[0].startswith("coverage: ") and "europe" in lines[0]
    assert "off  getonbrd" in text and "off by region" in text          # [latam], the profile is in Lisbon
    assert "on   arbeitnow" in text
    adzuna = next(ln for ln in lines if "adzuna" in ln and ln.lstrip().startswith("on"))
    assert "needs ADZUNA_APP_ID, ADZUNA_APP_KEY (unset): https://developer.adzuna.com" in adzuna
    assert "targeting: countries|country" in adzuna
    assert "optional key THEMUSE_API_KEY" in text
    assert "ats " in text and "greenhouse (tokens: 0 listed)" in text
    assert lines[-1].endswith("need a key (adzuna, findwork, careerjet)")
    assert calls == []                                                    # the proposal asks nobody


def test_a_key_set_in_env_takes_the_source_off_the_need_list(calls):
    config.set_env("ADZUNA_APP_ID", "id")
    config.set_env("ADZUNA_APP_KEY", "key")
    lines = onboard.proposal()
    assert "adzuna" not in lines[-1]
    assert not any("ADZUNA_APP_ID" in ln for ln in lines)


def test_verify_token_makes_one_request_and_records_the_answer(calls, capsys):
    assert onboard.main(["verify-token", "greenhouse", "examplecorp"]) == 0
    assert "ok       greenhouse examplecorp: 2 open roles" in capsys.readouterr().out
    assert calls == [("https://boards-api.greenhouse.io/v1/boards/examplecorp/jobs", {})]
    assert onboard.main(["verify-token", "lever", "ledgerly"]) == 0
    assert calls[-1] == ("https://api.lever.co/v0/postings/ledgerly", {"mode": "json"})
    rec = onboard._verified()
    assert rec["greenhouse"]["examplecorp"]["jobs"] == 2 and rec["lever"]["ledgerly"]["ok"] is True


@pytest.mark.parametrize(("token", "note"), [
    ("quietco", "0 open roles"), ("gone", "HTTP 404"), ("htmlco", "not JSON"), ("down", "request failed"),
])
def test_a_board_that_fails_or_is_empty_is_not_ok(calls, capsys, token, note):
    assert onboard.main(["verify-token", "greenhouse", token]) == 1
    assert note in capsys.readouterr().out
    assert len(calls) == 1                                                # no retry
    assert onboard._verified()["greenhouse"][token]["ok"] is False


def test_a_token_that_is_not_a_slug_is_refused_before_any_request(calls, capsys):
    assert onboard.main(["verify-token", "greenhouse", "../../etc"]) == 1
    assert "a board token is letters" in capsys.readouterr().out
    assert calls == []


def test_write_sources_takes_only_verified_tokens(calls):
    onboard.verify_token("greenhouse", "examplecorp")
    onboard.verify_token("greenhouse", "quietco")
    with pytest.raises(onboard.Refused) as e:
        onboard.write("sources", {"greenhouse": {"tokens": ["examplecorp", "quietco", "never"]}})
    msg = str(e.value)
    assert "greenhouse quietco: 0 open roles" in msg and "leave it out" in msg
    assert "greenhouse never: not verified; run python -m src.onboard verify-token greenhouse never" in msg
    onboard.write("sources", {"greenhouse": {"tokens": ["examplecorp"]}, "workday": {"sites": []}})
    assert config.sources()["greenhouse"]["tokens"] == ["examplecorp"]


def test_the_env_catalog_reads_names_hints_and_urls_from_the_example():
    cat = {e["name"]: e for e in config.env_catalog()}
    assert list(cat)[:2] == ["ADZUNA_APP_ID", "ADZUNA_APP_KEY"]
    assert cat["ADZUNA_APP_KEY"]["url"] == "https://developer.adzuna.com"
    assert cat["THEMUSE_API_KEY"]["optional"] and not cat["FINDWORK_TOKEN"]["optional"]
    assert cat["MAIL_APPS_PASS"]["optional"] and "app" in cat["MAIL_APPS_PASS"]["hint"].lower()
    assert cat["MAIL_APPS_HOST"]["url"] == "" and cat["MAIL_APPS_HOST"]["hint"].startswith("Optional per label")
