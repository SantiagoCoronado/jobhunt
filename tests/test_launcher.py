"""bin/jobhunt and scripts/install_launcher.sh: one word opens the TUI from any directory."""
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
LAUNCHER = ROOT / "bin" / "jobhunt"
INSTALLER = ROOT / "scripts" / "install_launcher.sh"


@pytest.fixture
def box(tmp_path):
    """A bin dir for the symlink and a stub interpreter that reports how it was called."""
    stub = tmp_path / "python-stub"
    stub.write_text('#!/bin/sh\necho "cwd=$(pwd -P)"\necho "args=$*"\n')
    stub.chmod(0o755)
    bin_dir = tmp_path / "bin"
    env = {**os.environ, "JOBHUNT_BIN_DIR": str(bin_dir), "JOBHUNT_PYTHON": str(stub),
           "PATH": f"{bin_dir}:/usr/bin:/bin"}
    return bin_dir, env, tmp_path


def _run(cmd, env, cwd=None):
    return subprocess.run([str(c) for c in cmd], env=env, cwd=cwd, capture_output=True, text=True)


def test_launcher_runs_the_tui_module_from_the_repo_through_a_symlink(box):
    bin_dir, env, tmp = box
    assert _run([INSTALLER], env).returncode == 0
    link = bin_dir / "jobhunt"
    assert link.is_symlink() and Path(os.readlink(link)) == LAUNCHER

    elsewhere = tmp / "elsewhere"
    elsewhere.mkdir()
    got = _run(["jobhunt", "--flag"], env, cwd=elsewhere)        # by name, off PATH, from another dir
    assert got.returncode == 0, got.stderr
    assert got.stdout.splitlines() == [f"cwd={ROOT}", "args=-m src.tui --flag"]

    # A relative link in the chain resolves too.
    hop = tmp / "hop"
    hop.symlink_to(os.path.relpath(link, tmp))
    assert _run([hop], env, cwd=elsewhere).stdout.splitlines()[0] == f"cwd={ROOT}"


def test_launcher_says_what_to_do_without_a_venv(box):
    _bin, env, tmp = box
    got = _run([LAUNCHER], {**env, "JOBHUNT_PYTHON": str(tmp / "missing")})
    assert got.returncode == 1 and "setup.sh" in got.stderr


def test_installer_takes_a_name_is_idempotent_and_uninstalls(box):
    bin_dir, env, _tmp = box
    for _ in range(2):
        got = _run([INSTALLER, "hunt"], env)
        assert got.returncode == 0 and "installed: hunt" in got.stdout
    assert (bin_dir / "hunt").is_symlink() and not (bin_dir / "jobhunt").exists()
    assert _run([INSTALLER, "--uninstall", "hunt"], env).returncode == 0
    assert not (bin_dir / "hunt").exists()


def test_installer_never_replaces_a_foreign_command(box):
    bin_dir, env, _tmp = box
    bin_dir.mkdir()
    foreign = bin_dir / "espresso"
    foreign.write_text("#!/bin/sh\necho coffee\n")
    foreign.chmod(0o755)

    got = _run([INSTALLER, "espresso"], env)
    assert got.returncode == 1 and "not this launcher" in got.stderr
    assert foreign.read_text().endswith("coffee\n")
    got = _run([INSTALLER, "--uninstall", "espresso"], env)
    assert got.returncode == 1 and foreign.exists()

    got = _run([INSTALLER, "ls"], env)                           # taken elsewhere on PATH
    assert got.returncode == 1 and "already runs" in got.stderr
    for bad in ("two words", "../up", "-x"):
        assert _run([INSTALLER, bad], env).returncode == 2
