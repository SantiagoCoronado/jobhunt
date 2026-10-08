"""Section 4, the stats screen (pre-release PR 6 story 2): the pure renderers without the app,
then the screen on a temp DB."""
from datetime import date

import pytest
from rich.text import Text
from tui_fakes import CAPTURED, _add, _key, _run, _settle

from src import db
from src.tui import data
from src.tui.app import JobhuntApp
from src.tui.screens.stats import StatsScreen
from src.tui.widgets import stats_view as view

pytestmark = pytest.mark.usefixtures("tmp_db")

DAY = date(2026, 10, 6)


def _snap(**over) -> data.StatsSnapshot:
    base = dict(today=DAY, last_discover=None, hunt=None, applications=0, replied=0, waiting=0, interviewing=0,
                applied_7d=0, applied_28d=0, reply_days=(), funnel=tuple((s, 0) for s in data.FUNNEL), bands=(), sources=())
    return data.StatsSnapshot(**{**base, **over})  # type: ignore[arg-type]


def _funnel(**counts: int) -> tuple[tuple[str, int], ...]:
    return tuple((s, counts.get(s, 0)) for s in data.FUNNEL)


def _line(t: Text, start: str) -> str:
    found = [ln for ln in t.plain.splitlines() if ln.startswith(start)]
    assert found, f"no line starts with {start!r} in:\n{t.plain}"
    return found[0]


def _styles(t: Text, piece: str) -> set[str]:
    at = t.plain.index(piece)
    return {str(s.style) for s in t.spans if s.start <= at < s.end}


AUTHOR = _snap(
    last_discover="2026-09-07", hunt=data.HuntLine("20260919-1702", "failed", 0, 0, None, None),
    applications=121, replied=52, waiting=63, interviewing=5, reply_days=(20,),
    funnel=_funnel(found=49_727, scored=13_366, shortlisted=881, applied=121, replied=52, screen=20, interview=8),
    bands=(data.ScoreBand("90+", 25, 14), data.ScoreBand("80-89", 80, 30), data.ScoreBand("70-79", 9, 3),
           data.ScoreBand("<70", 2, 0)),
    sources=(data.SourceStat("remotive", 5, 0, 0, 0, 0, True), data.SourceStat("adzuna", 5, 11_723, 2_618, 24, 10, False)))


# the pure renderers

def test_bar_draws_eighths_never_hides_a_small_count_and_caps_at_the_width():
    assert view.bar(0, 100) == "" and view.bar(5, 0) == ""
    assert view.bar(100, 100, 10) == "█" * 10
    assert view.bar(500, 100, 10) == "█" * 10                 # over the scale stays inside the column
    assert view.bar(55, 100, 10) == "█████" + "▌"             # 44 eighths: 5 full and a half
    assert view.bar(1, 49_727) == "▏"                         # one row in fifty thousand still shows


def test_tile_is_label_bold_value_and_a_dim_note():
    t = view.tile("any reply", "43%", "(rejections count)")
    assert t.plain == "any reply 43% (rejections count)"
    assert "bold" in _styles(t, "43%") and "dim" in _styles(t, "(rejections")


def test_table_aligns_columns_and_keeps_a_cell_style():
    t = view.table(["source", "pulled"], [["adzuna", "11,723"], ["lever", Text("7", style="red")]], frozenset({1}))
    assert t.plain.splitlines() == ["source  pulled", "adzuna  11,723", "lever        7"]
    assert "dim" in _styles(t, "source") and "red" in {str(sp.style) for sp in t.spans if sp.end == len(t.plain)}


def test_tokens_and_cost_show_a_dash_for_none():
    assert [view.tokens(n) for n in (None, 950, 85_000, 3_240_000)] == ["-", "950", "85k", "3.2M"]
    assert (view.cost(None), view.cost(1.2)) == ("-", "$1.20")


# the screen as a whole, from a snapshot

def test_the_author_numbers_read_like_the_design():
    t = view.render(AUTHOR)
    head = t.plain.splitlines()[0]
    assert head.startswith("last discover 2026-09-07, 29 days ago")
    assert "last hunt 20260919-1702: failed, 0 units, context -, cost -" in head
    assert "yellow" in _styles(t, "last discover")                 # past 7 days: a warning
    assert ("applications 121  any reply 43% (rejections count)  median reply 20d  waiting 63  "
            "in interviews 5  applied 7d 0 / 28d 0") in t.plain
    assert all(len(ln) <= 120 for ln in t.plain.splitlines())     # one column at 120
    found, applied = _line(t, "found"), _line(t, "applied")
    assert found.count("█") == 40 and applied.count("█") == 40     # two scales: 121 is not a sliver
    assert _line(t, "shortlisted").endswith("▊")
    assert _line(t, "replied").endswith("43%") and _line(t, "screen").endswith("38%")
    assert _line(t, "interview").endswith("40%") and _line(t, "offer").endswith("0%")
    assert "%" not in found and "%" not in applied                 # a percent from replied on only
    assert "56%  n=25" in t.plain and "38%  n=80" in t.plain
    assert "dim" in _styles(t, "<70") and "dim" not in _styles(t, "90+ ")
    rows = t.plain.split("source ")[1].splitlines()
    assert rows[1].split()[0] == "remotive" and rows[1].endswith("dead")        # dead first
    assert rows[2].split() == ["adzuna", "11,723", "2,618", "24", "10", "42%", "ok"]


def test_day_1_is_found_then_next_steps():
    t = view.render(_snap(last_discover="2026-10-06", funnel=_funnel(found=1_214),
                          sources=(data.SourceStat("adzuna", 1, 900, 900, 0, 0, False),)))
    assert t.plain.startswith("last discover 2026-10-06, today   no hunt yet")
    assert "yellow" not in _styles(t, "last discover")
    assert _line(t, "found").count("█") == 40
    assert _line(t, "scored").split(None, 2) == ["scored", "0", "run match in section 5"]
    assert "run match in section 5" in _line(t, "shortlisted")
    assert "apply by hand" in _line(t, "applied") and "run inbox in section 5" in _line(t, "offer")
    assert "applications 0  any reply - (rejections count)  median reply -" in t.plain
    assert _line(t, "score vs reply").endswith("shows from 20 applications (0 so far)")
    assert _line(t, "source").split() == ["source", "pulled", "new", "health"]       # pulled and new only
    assert _line(t, "adzuna").split() == ["adzuna", "900", "900", "ok"]


def test_an_empty_db_names_the_first_step_everywhere():
    t = view.render(_snap())
    assert t.plain.startswith("no discover yet: run discover in section 5")
    assert _line(t, "found").split(None, 2) == ["found", "0", "run discover in section 5"]
    assert "sources: no discover runs yet" in t.plain


def test_score_vs_reply_waits_for_20_applications_and_a_zero_offer_after_interviews_is_a_rate():
    few = _snap(applications=19, bands=(data.ScoreBand("90+", 19, 5),), funnel=_funnel(found=50, applied=19, replied=5))
    assert _line(view.render(few), "score vs reply").endswith("(19 so far)")
    t = view.render(_snap(applications=20, bands=(data.ScoreBand("90+", 20, 5),),
                          funnel=_funnel(found=50, applied=20, replied=5, screen=2)))
    assert "25%  n=20" in _line(t, "score vs reply") and "dimmed" not in t.plain
    assert _line(t, "interview").endswith(" 0%")                              # 0 of 2 screens: a rate
    assert _line(t, "offer").split(None, 2)[2].startswith("run inbox")        # the bar above is 0 too: a step
    assert _line(t, "screen").endswith("40%")


# the pilot

def _text(screen) -> str:
    return str(screen.query_one("#stats-text").render())


def _seed() -> None:
    for i in range(60):
        _add(status="discovered", source="adzuna", title=f"Engineer {i}")
    for i in range(22):
        _add(status="applied" if i % 2 else "rejected", source="adzuna", match_score=70 + i, applied_at="2026-09-01")
    conn = db.connect(db.DB_PATH)
    conn.execute("INSERT INTO runs (ts, source, pulled, new, ok) VALUES ('2026-10-01T09:00:00+00:00','adzuna',82,82,1)")
    conn.commit()
    conn.close()


def test_section_4_draws_the_snapshot_in_process_and_scrolls(monkeypatch):
    _seed()
    calls: list[int] = []
    real = data.stats
    monkeypatch.setattr(data, "stats", lambda today=None: (calls.append(1), real(today))[1])

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 24)) as pilot:
            await pilot.press(_key("stats"))
            await _settle(app, pilot)
            screen = app.screen
            assert isinstance(screen, StatsScreen)
            shown = _text(screen)
            assert "applications 22" in shown and "any reply 50%" in shown
            assert "score vs reply   90+" in shown or "score vs reply   80-89" in shown   # 22 applications: the bands show
            assert "adzuna" in shown and "placeholder" not in shown
            assert CAPTURED == []                                            # no subprocess
            pane = screen.query_one("#stats-scroll")
            assert pane.max_scroll_y > 0
            await pilot.press("j", "j")
            await pilot.pause()
            assert pane.scroll_y > 0
            await pilot.press("g")
            await pilot.pause()
            assert pane.scroll_y == 0
            before = len(calls)
            await pilot.press("r")
            await _settle(app, pilot)
            assert len(calls) == before + 1
    _run(scenario())


def test_section_4_on_a_fresh_db_shows_the_day_0_steps():
    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 40)) as pilot:
            await pilot.press(_key("stats"))
            await _settle(app, pilot)
            shown = _text(app.screen)
            assert "no discover yet: run discover in section 5" in shown
            assert "shows from 20 applications (0 so far)" in shown
    _run(scenario())


def test_a_failing_snapshot_says_why_in_a_toast(monkeypatch):
    def boom(today=None):
        raise RuntimeError("no such table: runs")
    monkeypatch.setattr(data, "stats", boom)

    async def scenario():
        app = JobhuntApp()
        async with app.run_test(size=(120, 30)) as pilot:
            await pilot.press(_key("stats"))
            await _settle(app, pilot)
            notes = [str(n.message) for n in app._notifications]
            assert any("stats did not load" in n and "no such table" in n for n in notes)
            assert not app.screen.busy.active                               # the indicator never stays on
    _run(scenario())
