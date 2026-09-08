"""render_cover_letter: CoverLetter.md -> .docx normalizes stray Markdown to plain text."""

from docx import Document

from src.render_cover_letter import render


def _paragraphs(docx_path):
    doc = Document(str(docx_path))
    return [p for p in doc.paragraphs]


def test_heading_marker_stripped_from_name(tmp_path):
    md = tmp_path / "CoverLetter.md"
    md.write_text(
        "# Alex Example\n\n"
        "Lisbon, Portugal | alex@example.com\n\n"
        "Dear team,\n\n"
        "Body text here.\n\n"
        "Sincerely,\nAlex\n",
        encoding="utf-8",
    )
    out = render(md)
    paras = _paragraphs(out)
    name_para = paras[0]
    assert name_para.text == "Alex Example"
    assert "#" not in name_para.text


def test_bold_re_line_becomes_bold_run_no_asterisks(tmp_path):
    md = tmp_path / "CoverLetter.md"
    md.write_text(
        "Alex Example\n\n"
        "Lisbon, Portugal | alex@example.com\n\n"
        "**Re: Senior Frontend Engineer (Contract), Roofr**\n\n"
        "Dear Roofr team,\n\n"
        "Body text here.\n\n"
        "Sincerely,\nAlex\n",
        encoding="utf-8",
    )
    out = render(md)
    paras = _paragraphs(out)
    re_para = next(p for p in paras if "Re:" in p.text)
    assert re_para.text == "Re: Senior Frontend Engineer (Contract), Roofr"
    assert "*" not in re_para.text
    assert re_para.runs
    assert all(r.bold for r in re_para.runs if r.text)


def test_mixed_inline_bold_in_body_paragraph(tmp_path):
    md = tmp_path / "CoverLetter.md"
    md.write_text(
        "Alex Example\n\n"
        "Lisbon, Portugal | alex@example.com\n\n"
        "Dear team,\n\n"
        "I built a **pricing dashboard** and an *inventory admin* for the team.\n\n"
        "Sincerely,\nAlex\n",
        encoding="utf-8",
    )
    out = render(md)
    paras = _paragraphs(out)
    body_para = next(p for p in paras if "pricing dashboard" in p.text)
    assert body_para.text == "I built a pricing dashboard and an inventory admin for the team."
    assert "*" not in body_para.text
    runs_by_text = {r.text: r for r in body_para.runs if r.text}
    assert runs_by_text["pricing dashboard"].bold is True
    assert runs_by_text["inventory admin"].italic is True
    assert not runs_by_text["I built a "].bold


def test_plain_text_letter_unchanged(tmp_path):
    md = tmp_path / "CoverLetter.md"
    md.write_text(
        "Alex Example\n"
        "Lisbon, Portugal\n"
        "alex@example.com | +351-900-000-000\n\n"
        "Dear team,\n\n"
        "This is a plain paragraph with no markup at all.\n\n"
        "Sincerely,\nAlex Example\n",
        encoding="utf-8",
    )
    out = render(md)
    paras = _paragraphs(out)
    texts = [p.text for p in paras if p.text]
    assert texts[0] == "Alex Example"
    assert "Lisbon, Portugal  |  alex@example.com | +351-900-000-000" in texts
    assert "Dear team," in texts
    assert "This is a plain paragraph with no markup at all." in texts
    assert "Sincerely, Alex Example" in texts


def test_horizontal_rule_block_skipped(tmp_path):
    md = tmp_path / "CoverLetter.md"
    md.write_text(
        "Alex Example\n\n"
        "Lisbon, Portugal\n\n"
        "---\n\n"
        "Dear team,\n\n"
        "Body.\n",
        encoding="utf-8",
    )
    out = render(md)
    paras = _paragraphs(out)
    texts = [p.text for p in paras if p.text]
    assert "---" not in texts
