"""python -m src.onboard extract / check (docs/spec-pre-release.md PR 5 story 1): the text of
Alex Example's resume as PDF and docx, md, txt, csv, LinkedIn's data-export zip, the size lines,
and the resume and profile checks. Everything lands in a temp dir."""
from __future__ import annotations

import copy
import json
import sys
import zipfile
from pathlib import Path

import pytest
import yaml

from src import onboard

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ROOT = FIXTURES.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import gen_fixtures  # noqa: E402

PDF = FIXTURES / "onboard" / "alex-example-resume.pdf"
DOCX = FIXTURES / "onboard" / "alex-example-resume.docx"


@pytest.fixture(autouse=True)
def onboard_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(onboard, "ONBOARD_DIR", tmp_path / "onboard")
    return tmp_path / "onboard"


def _master() -> dict:
    return yaml.safe_load((FIXTURES / "master_resume.yaml").read_text())


def test_the_pdf_and_docx_fixtures_carry_the_example_resume(onboard_dir, capsys):
    assert onboard.main(["extract", str(PDF), str(DOCX)]) == 0
    out = capsys.readouterr().out
    assert "alex-example-resume.pdf" in out and "1 page" in out and "tokens" in out
    assert "extracted 2 of 2 documents" in out
    docs = {d.id: d for d in onboard.load_manifest()}
    assert set(docs) == {"alex-example-resume.pdf", "alex-example-resume.docx"}
    for doc in docs.values():
        text = (onboard_dir / Path(doc.text).name).read_text()
        for fact in ("Alex Example", "Ledgerly", "Brightpath Studio", "Shelfmate", "Universidade de Lisboa"):
            assert fact in text, (doc.id, fact)
        assert doc.chars == len(text.rstrip("\n")) and doc.tokens == onboard.tokens(doc.chars)
    assert docs["alex-example-resume.pdf"].pages == 1 and docs["alex-example-resume.docx"].pages is None


def test_md_txt_and_csv_documents(tmp_path):
    (tmp_path / "letter.md").write_text("# Cover letter\n\nI built Shelfmate.\n")
    (tmp_path / "notes.txt").write_text("Portfolio: shelfmate.example\n")
    (tmp_path / "roles.csv").write_text("Company,Title,Notes\nLedgerly,Software Engineer,\nBrightpath,Frontend,agency\n")
    docs, errors = onboard.extract([tmp_path / "letter.md", tmp_path / "notes.txt", tmp_path / "roles.csv"])
    assert errors == []
    kinds = {d.id: d.kind for d in docs}
    assert kinds == {"letter.md": "md", "notes.txt": "txt", "roles.csv": "csv"}
    csv_text = Path(onboard.ONBOARD_DIR / "roles-csv.txt").read_text()
    assert "Company: Ledgerly\nTitle: Software Engineer" in csv_text
    assert "Notes: \n" not in csv_text                       # an empty cell is left out
    assert "Notes: agency" in csv_text


def _linkedin_zip(path: Path) -> Path:
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("Profile.csv", "First Name,Last Name,Headline,Geo Location\nAlex,Example,Full-stack engineer,Lisbon\n")
        z.writestr("Positions.csv", "Company Name,Title,Started On,Finished On\nLedgerly,Software Engineer,Apr 2023,\n")
        z.writestr("Skills.csv", "Name\nReact\nTypeScript\n")
        z.writestr("messages.csv", "FROM,TO,CONTENT\nsomeone,Alex,a private message\n")
        z.writestr("Connections.csv", "Notes:\nFirst Name,Last Name\nPat,Person\n")
    return path


def test_the_linkedin_export_reads_only_the_resume_csvs(tmp_path):
    docs, errors = onboard.extract([_linkedin_zip(tmp_path / "Basic_LinkedInDataExport.zip")])
    assert errors == []
    doc = docs[0]
    assert doc.kind == "linkedin-export"
    text = (onboard.ONBOARD_DIR / Path(doc.text).name).read_text()
    assert "## Profile" in text and "## Positions" in text and "## Skills" in text
    assert "Company Name: Ledgerly" in text and "Name: TypeScript" in text
    assert "private message" not in text and "Pat" not in text
    assert "read Profile, Positions, Skills; skipped 2 other csv files" == doc.note


def test_a_zip_without_profile_csvs_is_refused(tmp_path):
    with zipfile.ZipFile(tmp_path / "photos.zip", "w") as z:
        z.writestr("a.txt", "x")
    docs, errors = onboard.extract([tmp_path / "photos.zip"])
    assert docs == [] and "no LinkedIn profile csv" in errors[0]


def test_unsupported_missing_and_scanned_files(tmp_path, capsys):
    (tmp_path / "old.doc").write_bytes(b"\xd0\xcf")
    (tmp_path / "scan.pdf").write_bytes(gen_fixtures.resume_pdf([""]))
    rc = onboard.main(["extract", str(tmp_path / "old.doc"), str(tmp_path / "nope.pdf"), str(tmp_path / "scan.pdf")])
    out = capsys.readouterr().out
    assert rc == 1
    assert "old.doc: unsupported type .doc" in out and "nope.pdf: no such file" in out
    assert "no text layer" in out
    assert "extracted 1 of 3 documents" in out


def test_a_large_document_says_to_ask_for_the_pages(tmp_path, capsys):
    (tmp_path / "thesis.txt").write_text("word " * (onboard.LARGE_TOKENS + 10))
    onboard.main(["extract", str(tmp_path / "thesis.txt")])
    assert "! large: over 15,000 tokens; ask for the pages that matter" in capsys.readouterr().out


def test_extracting_again_replaces_and_a_second_file_of_that_name_gets_its_own_id(tmp_path):
    (tmp_path / "a").mkdir()
    (tmp_path / "b").mkdir()
    (tmp_path / "a" / "cv.txt").write_text("first\n")
    (tmp_path / "b" / "cv.txt").write_text("other\n")
    onboard.extract([tmp_path / "a" / "cv.txt"])
    (tmp_path / "a" / "cv.txt").write_text("first, edited\n")
    onboard.extract([tmp_path / "a" / "cv.txt"])
    onboard.extract([tmp_path / "b" / "cv.txt"])
    docs = {d.id: d for d in onboard.load_manifest()}
    assert set(docs) == {"cv.txt", "cv-2.txt"}
    assert docs["cv.txt"].chars == len("first, edited")
    raw = json.loads((onboard.ONBOARD_DIR / "manifest.json").read_text())
    assert len(raw["documents"]) == 2


# ---- check ----------------------------------------------------------------------------------

def test_check_resume_passes_the_example_and_counts_it(capsys):
    assert onboard.main(["check", "resume", "--file", str(FIXTURES / "master_resume.yaml")]) == 0
    assert "resume ok: 3 roles, 2 projects" in capsys.readouterr().out


def _errors(mutate) -> list[str]:
    data = _master()
    mutate(data)
    return onboard.resume_errors(data)


def test_resume_errors_name_the_entry():
    assert onboard.resume_errors({"name": "x"}) == ["the file needs a top-level `cv:` mapping"]
    exp = "cv.sections.experience"
    assert any(f"{exp}[0].start_date must be YYYY-MM" in e
               for e in _errors(lambda d: d["cv"]["sections"]["experience"][0].update(start_date="April 2023")))
    assert f"{exp}[1] needs `company`" in _errors(lambda d: d["cv"]["sections"]["experience"][1].pop("company"))
    assert any("unknown section(s) hobbies" in e for e in _errors(lambda d: d["cv"]["sections"].update(hobbies=["x"])))
    assert any("em-dash" in e and "highlights[0]" in e for e in _errors(
        lambda d: d["cv"]["sections"]["experience"][0]["highlights"].__setitem__(0, "Built it — fast")))
    assert "cv.location is required" in _errors(lambda d: d["cv"].pop("location"))
    assert any("at least one experience or project" in e for e in _errors(
        lambda d: [d["cv"]["sections"].pop(k) for k in ("experience", "projects")]))
    assert _errors(lambda d: d["cv"]["sections"]["experience"][0].update(end_date="present")) == []


def test_the_renderer_is_the_last_check():
    data = _master()
    broken = copy.deepcopy(data)
    broken["cv"]["sections"]["skills"][0]["details"] = 42      # passes the schema, the renderer cannot join it
    assert any("src.render_docx could not build it" in e for e in onboard.resume_errors(broken))


def test_check_resume_reports_a_missing_or_broken_file(tmp_path, capsys):
    assert onboard.main(["check", "resume", "--file", str(tmp_path / "none.yaml")]) == 1
    (tmp_path / "bad.yaml").write_text("cv: [unclosed\n")
    assert onboard.main(["check", "resume", "--file", str(tmp_path / "bad.yaml")]) == 1
    out = capsys.readouterr().out
    assert "does not exist" in out and "is not valid YAML" in out


def test_check_profile_passes_the_example_and_names_what_is_still_the_example(capsys):
    assert onboard.main(["check", "profile", "--file", str(FIXTURES / "profile.yaml")]) == 0
    out = capsys.readouterr().out
    assert "still the example's value: name, target_titles" in out and "profile ok" in out


def test_profile_errors():
    prof = yaml.safe_load((FIXTURES / "profile.yaml").read_text())
    assert onboard.profile_errors(prof) == []
    bad = dict(prof, name="", shortlist_threshold="seventy")
    bad["role_families"] = [dict(prof["role_families"][0], strength="best")]
    errors = onboard.profile_errors(bad)
    assert "name is required" in errors and "shortlist_threshold must be a whole number" in errors
    assert any("strength must be one of" in e for e in errors)
    missing = {k: v for k, v in prof.items() if k != "candidate_line"}
    assert any("candidate_line is missing" in e for e in onboard.profile_errors(missing))
