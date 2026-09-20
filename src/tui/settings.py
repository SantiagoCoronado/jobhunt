"""`config/tui.toml`: how the TUI looks and opens (spec section 6). Never how a hunt runs, which
is `config/hunt.toml`, and never what counts as a fit, which is `config/profile.yaml`.

Loading never raises: the TUI must open on a missing file, a typo or a theme that is gone. A
value that does not pass falls back to its default and leaves one line in `Settings.warnings`,
which the app toasts on launch. `save` writes the whole file back, comments included.
"""
from __future__ import annotations

import os
import shlex
import string
import tomllib
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

from rich.errors import StyleSyntaxError
from rich.style import Style
from textual.theme import BUILTIN_THEMES, Theme

from ..config import CONFIG_DIR
from .presets import PRESETS

TUI_TOML = CONFIG_DIR / "tui.toml"

KANAGAWA = "kanagawa"
# Kanagawa "wave" (rebelot/kanagawa.nvim): sumiInk grounds, fujiWhite text, crystalBlue lead.
KANAGAWA_THEME = Theme(
    name=KANAGAWA, dark=True,
    primary="#7E9CD8",        # crystalBlue
    secondary="#957FB8",      # oniViolet
    accent="#FFA066",         # surimiOrange
    warning="#E6C384",        # carpYellow
    error="#E82424",          # samuraiRed
    success="#98BB6C",        # springGreen
    foreground="#DCD7BA",     # fujiWhite
    background="#1F1F28",     # sumiInk3
    surface="#2A2A37",        # sumiInk4
    panel="#363646",          # sumiInk5
    variables={
        "footer-key-foreground": "#7FB4CA",           # springBlue
        "input-selection-background": "#2D4F67 60%",  # waveBlue2
        "block-cursor-background": "#7E9CD8",
        "block-cursor-foreground": "#1F1F28",
        "border": "#54546D",                          # sumiInk6
    },
)
THEMES: tuple[str, ...] = (*BUILTIN_THEMES, KANAGAWA)
SECTIONS: tuple[str, ...] = tuple(PRESETS)           # a launch section is one of the jobs presets
OVERDUE_STYLES: tuple[str, ...] = ("red", "bold red", "yellow", "magenta", "reverse")
EDITORS: tuple[str, ...] = ("$EDITOR", "code -w", "cursor -w", "zed -w", "nvim", "vim", "nano")
FALLBACK_EDITOR = "vi"                               # what `$EDITOR` means when it is unset
FILE_FIELD = "file"                                  # the one placeholder an editor template takes


@dataclass(frozen=True)
class Settings:
    theme: str = KANAGAWA
    default_section: str = "board"
    detail_pane: bool = True                         # false = the detail is always an overlay
    followup_days: int = 7                           # display only (the `f` prompt's hint)
    overdue_style: str = "red"
    editor: str = "$EDITOR"
    warnings: tuple[str, ...] = ()                   # what `load` could not take, never saved


DEFAULTS = Settings()


def check_editor(template: str) -> None:
    """An editor template is a command line: `$VARS` expand, `{file}` is where the path goes
    (appended when absent). Raises ValueError for one that could never run."""
    if not template.strip():
        raise ValueError("the editor command is empty")
    try:
        fields = [name for _text, name, _spec, _conv in string.Formatter().parse(template) if name is not None]
    except ValueError as e:
        raise ValueError(f"bad editor command {template!r}: {e}") from None
    stray = sorted({f for f in fields if f != FILE_FIELD})
    if stray:
        raise ValueError(f"bad editor command {template!r}: unknown placeholder "
                         f"{', '.join('{' + f + '}' for f in stray)} (only {{file}} is filled)")
    try:
        shlex.split(template)
    except ValueError as e:
        raise ValueError(f"bad editor command {template!r}: {e}") from None


def editor_argv(template: str, path: Path, env: dict[str, str] | None = None) -> list[str]:
    """The argv that opens `path`. An unset `$EDITOR` means `vi`, as it does for git."""
    check_editor(template)
    env = dict(os.environ if env is None else env)
    env["EDITOR"] = env.get("EDITOR", "").strip() or FALLBACK_EDITOR
    slot = "{" + FILE_FIELD + "}"
    argv: list[str] = []
    for part in shlex.split(template):
        expanded = string.Template(part).safe_substitute(env)
        if slot in part:                  # the path goes in after the split: a space in it
            argv.append(expanded.replace(slot, str(path)))      # never makes a second argument
        elif expanded != part:            # `$EDITOR` may itself be "code -w"
            argv.extend(shlex.split(expanded))
        else:
            argv.append(part)
    return argv if slot in template else [*argv, str(path)]


def _style_ok(style: str) -> bool:
    try:
        Style.parse(style)
    except StyleSyntaxError:
        return False
    return bool(style.strip())


def _table(raw: dict[str, Any], name: str, warnings: list[str]) -> dict[str, Any]:
    block = raw.get(name, {})
    if not isinstance(block, dict):
        warnings.append(f"[{name}] must be a table; defaults used")
        return {}
    return block


def parse(raw: dict[str, Any]) -> Settings:
    """A decoded tui.toml to Settings; every value that does not pass becomes its default."""
    w: list[str] = []
    theme_t, sections_t = _table(raw, "theme", w), _table(raw, "sections", w)
    follow_t, editor_t = _table(raw, "followups", w), _table(raw, "editor", w)

    theme = theme_t.get("name", DEFAULTS.theme)
    if theme not in THEMES:
        w.append(f"unknown theme {theme!r}; using {DEFAULTS.theme}")
        theme = DEFAULTS.theme

    section = sections_t.get("default", DEFAULTS.default_section)
    if section not in SECTIONS:
        w.append(f"sections.default {section!r} is not one of {', '.join(SECTIONS)}; using {DEFAULTS.default_section}")
        section = DEFAULTS.default_section

    detail_pane = sections_t.get("detail_pane", DEFAULTS.detail_pane)
    if not isinstance(detail_pane, bool):
        w.append(f"sections.detail_pane must be true or false, got {detail_pane!r}")
        detail_pane = DEFAULTS.detail_pane

    days = follow_t.get("days", DEFAULTS.followup_days)
    if isinstance(days, bool) or not isinstance(days, int) or days < 1:
        w.append(f"followups.days must be a whole number of days, got {days!r}")
        days = DEFAULTS.followup_days

    overdue = follow_t.get("overdue_style", DEFAULTS.overdue_style)
    if not isinstance(overdue, str) or not _style_ok(overdue):
        w.append(f"followups.overdue_style {overdue!r} is not a style; using {DEFAULTS.overdue_style}")
        overdue = DEFAULTS.overdue_style

    editor = editor_t.get("command", DEFAULTS.editor)
    try:
        if not isinstance(editor, str):
            raise ValueError(f"editor.command must be a string, got {editor!r}")
        check_editor(editor)
    except ValueError as e:
        w.append(f"{e}; using {DEFAULTS.editor}")
        editor = DEFAULTS.editor

    return Settings(theme, section, detail_pane, days, overdue, editor, tuple(w))


def load(path: Path | None = None) -> Settings:
    """Read tui.toml (the shipped file by default). A missing file is the defaults, silently;
    a file that is not TOML is the defaults with a warning."""
    path = path or TUI_TOML
    if not path.exists():
        return DEFAULTS
    try:
        raw = tomllib.loads(path.read_text(encoding="utf-8"))
    except (tomllib.TOMLDecodeError, OSError) as e:
        return replace(DEFAULTS, warnings=(f"{path.name}: unreadable ({e}); defaults used",))
    return parse(raw)


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def render(s: Settings) -> str:
    return f"""# How the TUI looks and opens (docs/spec-tui.md section 6). Written by the settings modal
# (`,` inside `python -m src.tui`), which rewrites the whole file: values edited by hand are
# kept, comments added by hand are not.

[theme]
name = {_quote(s.theme)}           # any Textual built-in or "kanagawa" (custom)

[sections]
default = {_quote(s.default_section)}           # section opened on launch: {', '.join(SECTIONS)}
detail_pane = {str(s.detail_pane).lower()}          # false = always overlay

# No [harness] block: the harness and per-stage models live in config/hunt.toml
# (docs/spec-hunt-orchestrator.md section 6) and the settings modal edits that file.

[followups]
days = {s.followup_days}                    # display only; config.followup_days() stays the pipeline authority
overdue_style = {_quote(s.overdue_style)}

[editor]
command = {_quote(s.editor)}         # $VARS expand; {{file}} marks where the path goes (appended when absent)
"""


def save(s: Settings, path: Path | None = None) -> Path:
    """Atomic, like the ledger: the new file is whole before it takes the old one's name."""
    path = path or TUI_TOML
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(render(replace(s, warnings=())), encoding="utf-8")
    os.replace(tmp, path)
    return path
