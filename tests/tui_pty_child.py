"""The real app on a real terminal, for the pty test (test_tui_pty.py): `run()`, the Linux
driver, suspend and resume, none of which `run_test` exercises. A child process sees no
monkeypatch, so the same redirections the pilot fixture makes are made here by hand, before the
app starts: nothing in this process reads the real DB, config or clipboard.

    python tests/tui_pty_child.py <tmp dir> <editor command>
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import config, db, reconcile, research  # noqa: E402
from src.hunt import config as hunt_config  # noqa: E402
from src.hunt import ledger as hunt_ledger  # noqa: E402
from src.tui import commands, settings  # noqa: E402
from src.tui.app import JobhuntApp  # noqa: E402


def main(tmp: Path, editor: str) -> int:
    fixtures = ROOT / "tests" / "fixtures"
    for key, name in (("profile", "profile.yaml"), ("notify", "notify.yaml"), ("sources_local", "sources.local.yaml"),
                      ("master_resume", "master_resume.yaml"), ("answers", "answers.yaml")):
        config.USER_FILES[key] = fixtures / name
    db.DB_PATH = tmp / "jobs.db"
    reconcile.APPS_DIR = tmp / "applications"
    research.COMPANIES_DIR = tmp / "companies"
    settings.TUI_TOML = tmp / "config" / "tui.toml"
    hunt_config.HUNT_TOML = tmp / "config" / "hunt.toml"
    hunt_ledger.HUNT_DIR = tmp / "hunt"
    commands.launch = lambda target: None
    commands.pbcopy = lambda text: None
    commands.capture = lambda argv, timeout=600: (0, "captured")
    settings.save(settings.Settings(editor=editor))
    JobhuntApp().run()
    print("CHILD-EXITED-CLEAN", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1]), sys.argv[2]))
