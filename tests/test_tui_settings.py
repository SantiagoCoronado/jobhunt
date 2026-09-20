"""config/tui.toml: defaults, tolerant loading, the round trip, the editor template."""
from dataclasses import replace
from pathlib import Path

import pytest

from src.tui import settings
from src.tui.settings import DEFAULTS, Settings


def _write(path: Path, text: str) -> Path:
    path.write_text(text, encoding="utf-8")
    return path


def test_a_missing_file_is_the_defaults_without_a_warning(tmp_path):
    assert settings.load(tmp_path / "tui.toml") == DEFAULTS
    assert DEFAULTS.warnings == () and DEFAULTS.theme == "kanagawa"


def test_the_shipped_file_parses_clean_and_is_what_save_would_write():
    """config/tui.toml is committed and the settings modal rewrites it, so it may say any valid
    thing; it must never carry a warning or drift from the writer's format."""
    shipped = settings.load(settings.TUI_TOML)
    assert shipped.warnings == ()
    assert settings.TUI_TOML.read_text(encoding="utf-8") == settings.render(shipped)


def test_an_unknown_theme_falls_back_and_says_so(tmp_path):
    s = settings.load(_write(tmp_path / "tui.toml", '[theme]\nname = "vaporwave"\n'))
    assert s.theme == "kanagawa"
    assert len(s.warnings) == 1 and "vaporwave" in s.warnings[0]


def test_a_file_that_still_opens_on_the_removed_shortlist_section_falls_back_to_board(tmp_path):
    s = settings.load(_write(tmp_path / "tui.toml", '[sections]\ndefault = "shortlist"\n'))
    assert s.default_section == "board" and settings.SECTIONS == ("board", "followups")
    assert len(s.warnings) == 1 and "shortlist" in s.warnings[0]


def test_every_builtin_theme_and_kanagawa_pass():
    for name in settings.THEMES:
        assert settings.parse({"theme": {"name": name}}) == replace(DEFAULTS, theme=name)


@pytest.mark.parametrize("command, why", [
    ('code -w "unclosed', "quotation"),
    ("vim {line} {file}", "{line}"),
    ("vim {file", "bad editor command"),
    ("   ", "empty"),
])
def test_a_bad_editor_template_falls_back_and_says_so(tmp_path, command, why):
    s = settings.load(_write(tmp_path / "tui.toml", f"[editor]\ncommand = '{command}'\n"))
    assert s.editor == "$EDITOR"
    assert len(s.warnings) == 1 and why in s.warnings[0]


def test_bad_values_fall_back_one_warning_each(tmp_path):
    s = settings.load(_write(tmp_path / "tui.toml", """
[sections]
default = "apps"
detail_pane = "yes"
[followups]
days = 0
overdue_style = "not a colour at all"
[editor]
command = 7
"""))
    assert replace(s, warnings=()) == DEFAULTS
    assert len(s.warnings) == 5


def test_a_file_that_is_not_toml_is_the_defaults_with_a_warning(tmp_path):
    s = settings.load(_write(tmp_path / "tui.toml", "[theme\nname ="))
    assert replace(s, warnings=()) == DEFAULTS
    assert "unreadable" in s.warnings[0]


def test_a_section_that_is_not_a_table_is_ignored(tmp_path):
    s = settings.load(_write(tmp_path / "tui.toml", 'theme = "nord"\n'))
    assert s.theme == "kanagawa" and "[theme]" in s.warnings[0]


def test_save_then_load_round_trips_and_drops_the_warnings(tmp_path):
    path = tmp_path / "config" / "tui.toml"
    mine = Settings(theme="nord", default_section="followups", detail_pane=False, followup_days=10,
                    overdue_style="bold red", editor='code -w "{file}"', warnings=("stale",))
    assert settings.save(mine, path) == path
    assert settings.load(path) == replace(mine, warnings=())
    assert not path.with_suffix(".toml.tmp").exists()
    assert "—" not in path.read_text(encoding="utf-8")


def test_editor_argv_expands_the_variable_and_places_the_file():
    f = Path("/tmp/my config/profile.yaml")
    assert settings.editor_argv("$EDITOR", f, {"EDITOR": "code -w"}) == ["code", "-w", str(f)]
    assert settings.editor_argv("$EDITOR", f, {}) == ["vi", str(f)]
    assert settings.editor_argv("$EDITOR", f, {"EDITOR": "  "}) == ["vi", str(f)]
    assert settings.editor_argv("nvim +3 {file}", f, {}) == ["nvim", "+3", str(f)]
    assert settings.editor_argv("open -a TextEdit", f, {}) == ["open", "-a", "TextEdit", str(f)]
    assert settings.editor_argv("sh -c 'less {file}'", f, {}) == ["sh", "-c", f"less {f}"]
    with pytest.raises(ValueError):
        settings.editor_argv("vim {nope}", f, {})
