"""The app's selection as plain data (src/tui/selection.py): what a table load may prune."""
from src.tui.data import JobRow
from src.tui.selection import Selection


def _row(job_id: int, status: str = "shortlisted") -> JobRow:
    return JobRow(job_id, f"Co{job_id}", "Engineer", "Remote", "t", status, 80, None, None, False)


def test_a_load_prunes_only_the_marks_it_looked_up():
    """Cursor's residual note on PR #30: a worker that started before a mark was made comes back
    without that row, in the other jobs section's table, and must not take the mark with it."""
    sel = Selection()
    sel.set({1, 2}, set(), [1, 2], {1: _row(1), 2: _row(2)})
    asked = frozenset(sel.selected)                       # the board's load starts: it looks up 1 and 2
    sel.set({1, 2, 3}, set(), [3], {3: _row(3, "applied")})    # meanwhile, a mark made in follow-ups

    sel.loaded([], [_row(1)], [1], asked)                 # the board's load lands: 2 left the listed statuses
    assert sel.selected == {1, 3}                         # 2 was looked up and not found; 3 never was
    assert [r.id for r in sel.selected_rows] == [1, 3] and sel.rows[3].status == "applied"

    sel.loaded([], [_row(1)], [1], frozenset(sel.selected))    # the next load looks 3 up and does not find it
    assert sel.selected == {1}
    sel.loaded([], [], [])                                # no snapshot given: every mark is checked
    assert sel.selected == set()


def test_toggle_puts_back_the_kind_of_mark_a_row_had():
    sel = Selection()
    sel.loaded([7], [_row(7), _row(8)], [7, 8])
    sel.set({8}, set(), [7, 8], {8: _row(8)})
    sel.toggle(_row(7), pick=True)
    sel.toggle(_row(8), pick=False)
    assert sel.marked == set() and sel.dismissed == {7}
    sel.toggle(_row(7), pick=True)
    sel.toggle(_row(8), pick=False)
    assert sel.preselected == {7} and sel.selected == {8} and sel.kind(7) == "pick"
