"""python -m src.onboard linkedin (docs/spec-pre-release.md PR 5 story 5): the opt-in read of a
public profile page. The page is a hand-written fixture for Alex Example in the public page's
shape; the request is a fake, and no test reaches LinkedIn."""
from __future__ import annotations

from pathlib import Path

import pytest

from src import onboard

PAGE = (Path(__file__).resolve().parent / "fixtures" / "onboard" / "linkedin_public.html").read_text()
URL = "https://www.linkedin.com/in/alexexample/"


class Page:
    def __init__(self, status: int = 200, text: str = PAGE, url: str = URL) -> None:
        self.status_code, self.text, self.url = status, text, url


@pytest.fixture
def gets(tmp_path, monkeypatch):
    monkeypatch.setattr(onboard, "ONBOARD_DIR", tmp_path / "onboard")
    seen: list[str] = []
    answer: dict[str, Page] = {"page": Page()}

    def fake(url):
        seen.append(url)
        return answer["page"]

    monkeypatch.setattr(onboard, "_get_page", fake)
    return seen, answer


def test_the_public_page_becomes_a_document_with_the_warning_first(gets, capsys):
    seen, _ = gets
    assert onboard.main(["linkedin", "https://linkedin.com/in/alexexample?trk=public_profile"]) == 0
    out = capsys.readouterr().out
    assert out.index("public LinkedIn page only, with no login") < out.index("linkedin-alexexample")
    assert seen == [URL]                                         # one GET, the clean URL
    doc = {d.id: d for d in onboard.load_manifest()}["linkedin-alexexample"]
    assert doc.kind == "linkedin-public" and doc.source == URL
    text = (onboard.ONBOARD_DIR / Path(doc.text).name).read_text()
    assert "Name: Alex Example" in text and "Headline: Software Engineer at Ledgerly" in text
    assert "Location: Lisbon, PT" in text
    assert "- Ledgerly (2023-04): Built the merchant checkout flow" in text
    assert "- Brightpath Studio (2021-02 to 2023-03)" in text
    assert "Education:\n- Universidade de Lisboa (2017 to 2020)" in text
    assert "Languages: Portuguese, English, Spanish" in text
    assert "Awards" not in text and "312" not in text            # nothing beyond the profile facts


def test_the_document_can_be_cited_as_provenance(gets):
    onboard.linkedin(URL)
    assert "linkedin-alexexample" in onboard.document_ids()


@pytest.mark.parametrize("page", [
    Page(status=999, text=""),
    Page(url="https://www.linkedin.com/authwall?trk=bf&sessionRedirect=x"),
    Page(text="<html><body>Sign in to see Alex's full profile</body></html>"),
])
def test_a_login_wall_reads_nothing(gets, capsys, page):
    _, answer = gets
    answer["page"] = page
    assert onboard.main(["linkedin", URL]) == 1
    out = capsys.readouterr().out
    assert "login wall" in out and ("Save to PDF" in out or "data export" in out)
    assert onboard.load_manifest() == []


def test_only_a_profile_url_is_fetched(gets, capsys):
    seen, _ = gets
    for url in ("https://www.linkedin.com/company/ledgerly", "https://evil.example/in/alex", "alexexample"):
        assert onboard.main(["linkedin", url]) == 1
    assert "is not a public profile URL" in capsys.readouterr().out
    assert seen == []


def test_a_network_failure_is_reported(gets, monkeypatch, capsys):
    def boom(url):
        raise ConnectionError("down")

    monkeypatch.setattr(onboard, "_get_page", boom)
    assert onboard.main(["linkedin", URL]) == 1
    assert "the request failed (ConnectionError)" in capsys.readouterr().out


def test_the_fixture_matches_the_example_resume():
    """The page says nothing the example resume does not."""
    import yaml

    master = yaml.safe_load((Path(__file__).resolve().parent / "fixtures" / "master_resume.yaml").read_text())
    companies = {e["company"].split(" (")[0] for e in master["cv"]["sections"]["experience"]}
    person = onboard._person(PAGE)
    assert person is not None
    assert {o["name"] for o in person["worksFor"]} <= companies
    assert person["name"] == master["cv"]["name"]
