"""answers_export: approved entries only, templates under a TAILOR marker."""
from __future__ import annotations

from src.answers_export import TEMPLATE_IDS, render

JOB = {"id": 1, "company": "Acme", "title": "Engineer"}


def test_template_entries_render_under_a_tailor_marker_with_their_own_hint():
    entries = [
        {"id": "why-company", "question": "Why {company}?", "answer": "TEMPLATE: why", "draft": False},
        {"id": "what-do-you-know-about-us", "question": "What do you know about {company}?",
         "answer": "TEMPLATE: three facts", "draft": False},
        {"id": "plain", "question": "Remote?", "answer": "Yes, from Mexico City.", "draft": False},
        {"id": "pending", "question": "Consulting?", "answer": "It winds down.", "draft": True},
    ]
    text, drafts = render(JOB, entries)
    assert text.count("<!-- TAILOR:") == 2
    assert "three specific dossier facts" in text and "3-sentence answer" in text
    assert "## What do you know about Acme?" in text
    assert "It winds down." not in text and drafts == ["pending"]
    assert set(TEMPLATE_IDS) >= {"why-company", "what-do-you-know-about-us"}
