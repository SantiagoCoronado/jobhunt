"""Core normalization + persistence primitives: Job model and upsert_job."""
from src.db import connect, upsert_job
from src.models import Job, normalize_text, strip_html
from src.notify import _esc


def test_normalize_text():
    assert normalize_text("  Sr. Software Engineer!! ") == "sr software engineer"
    assert normalize_text(None) == ""
    assert normalize_text("A-B_C") == "a b c"


def test_strip_html():
    assert strip_html("<p>Hello <b>world</b></p>") == "Hello world"
    assert strip_html(None) == ""


def test_canonical_key_collapses_cross_source():
    a = Job(source="greenhouse", external_id="1", url="u", company="Acme Inc", title="AI Engineer")
    b = Job(source="remoteok", external_id="99", url="v", company="ACME, Inc.", title="AI  Engineer!")
    assert a.canonical_key == b.canonical_key
    c = Job(source="remoteok", external_id="98", url="w", company="Acme Inc", title="Data Engineer")
    assert a.canonical_key != c.canonical_key


def test_to_row_shapes_for_sqlite():
    j = Job(source="s", external_id="1", url="u", company="Co", title="T",
            remote=True, tags=["a", "b"], posted_at="2026-07-16", raw={"noise": 1})
    row = j.to_row()
    assert row["remote"] == 1
    assert row["tags"] == "a,b"
    assert "raw" not in row
    assert row["posted_at"] == "2026-07-16T00:00:00+00:00"
    assert row["canonical_key"] == j.canonical_key


def test_upsert_inserts_then_refreshes_last_seen(tmp_path):
    conn = connect(tmp_path / "jobs.db")
    row = Job(source="s", external_id="1", url="u", company="Co", title="T").to_row()
    assert upsert_job(conn, row, "2026-07-01T00:00:00") == "new"
    assert upsert_job(conn, row, "2026-07-02T00:00:00") == "seen"
    r = conn.execute("SELECT first_seen, last_seen, COUNT(*) OVER () AS n FROM jobs").fetchone()
    assert r["n"] == 1
    assert r["first_seen"] == "2026-07-01T00:00:00"
    assert r["last_seen"] == "2026-07-02T00:00:00"


def test_esc_covers_attribute_context():
    assert _esc('<a href="x">&') == '&lt;a href=&quot;x&quot;&gt;&amp;'
    out = _esc('"><script>')
    assert '"' not in out and "<" not in out and ">" not in out
