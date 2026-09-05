"""db.connect sets the concurrency pragmas the TUI relies on (docs/spec-tui.md, decision 20)."""
import sqlite3

from src.db import connect


def test_connect_sets_wal_and_busy_timeout(tmp_path):
    conn = connect(tmp_path / "jobs.db")
    assert conn.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    assert conn.execute("PRAGMA busy_timeout").fetchone()[0] == 5000


def test_reader_sees_committed_rows_while_writer_holds_a_transaction(tmp_path):
    db = tmp_path / "jobs.db"
    writer = connect(db)
    writer.execute("INSERT INTO jobs (source, external_id, canonical_key, company, title) "
                   "VALUES ('t', 'x1', 'k1', 'Acme', 'Engineer')")
    writer.commit()
    writer.execute("INSERT INTO jobs (source, external_id, canonical_key, company, title) "
                   "VALUES ('t', 'x2', 'k2', 'Acme', 'Engineer II')")   # open write txn, not committed
    reader = sqlite3.connect(db)
    assert reader.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 1   # WAL: no lock error
    writer.commit()
    assert reader.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == 2
