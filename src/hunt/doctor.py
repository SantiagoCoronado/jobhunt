"""`hunt models`, `hunt doctor` and the run-start model check (spec section 5 "Live model
catalog", decision 6).

A stage's model is validated against the harness's LIVE catalog, never a table in the repo:
`models()` asks the CLI. The one exception is claude, whose CLI has no list command; there the
check is a 10-token smoke prompt per distinct configured model, the same call `doctor` makes,
so a retired alias fails at minute zero instead of mid-hunt. `doctor` also runs the binary,
reads its version, and probes that the tool grants work by asking the model to read a file
with a nonce in it (a diagnostic; inside a hunt the reply is never parsed, decision 4).
"""
from __future__ import annotations

import secrets
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from ..config import ROOT
from . import harness as harness_mod
from .config import STAGES, HuntConfig
from .harness import Harness, Invocation, Model, Result


@dataclass(frozen=True)
class Check:
    name: str
    status: str            # ok | warn | FAIL
    detail: str

    def line(self) -> str:
        return f"  {self.name:<9} {self.status:<5} {self.detail}"


@dataclass
class Exec:
    rc: int
    stdout: str
    stderr: str
    timed_out: bool
    elapsed: float


def execute(h: Harness, inv: Invocation) -> Exec:
    """One harness process, no log streaming (the pool has its own runner)."""
    started = time.monotonic()
    try:
        cp = subprocess.run(h.argv(inv), input=h.stdin(inv), capture_output=True, text=True, encoding="utf-8",
                            errors="replace", cwd=inv.cwd, timeout=inv.timeout_s, check=False)
    except subprocess.TimeoutExpired as e:
        out = e.stdout.decode("utf-8", "replace") if isinstance(e.stdout, bytes) else (e.stdout or "")
        err = e.stderr.decode("utf-8", "replace") if isinstance(e.stderr, bytes) else (e.stderr or "")
        return Exec(-1, out, err, True, time.monotonic() - started)
    except OSError as e:
        return Exec(-1, "", str(e), False, time.monotonic() - started)
    return Exec(cp.returncode, cp.stdout, cp.stderr, False, time.monotonic() - started)


def smoke(h: Harness, model: str | None, cwd: Path = ROOT) -> tuple[Result | None, str | None, float]:
    """(result, error, seconds) of the smoke prompt on one model; error is None when it answered."""
    inv = h.smoke(model, cwd) if hasattr(h, "smoke") else Invocation(
        "Reply with the single word ok", "You are a smoke test.", model, frozenset(), cwd, 60)
    ex = execute(h, inv)
    if ex.timed_out:
        return None, f"timeout after {inv.timeout_s}s", ex.elapsed
    res = h.parse(ex.stdout, ex.stderr, ex.rc)
    return res, res.error, ex.elapsed


def catalog(h: Harness) -> tuple[list[Model] | None, str | None]:
    """(models, reason it could not be read)."""
    try:
        models = h.models()
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        return None, f"{type(e).__name__}: {e}"[:200]
    return models, None


def _nearest(model: str, ids: list[str], n: int = 3) -> list[str]:
    key = model.lower()
    hits = [i for i in ids if key in i.lower() or i.lower() in key]
    return hits[:n] or ids[:n]


def validate_models(cfg: HuntConfig, stages: list[str], harness_default: str,
                    get: Callable[[str], Harness] | None = None, smoke_fn=smoke) -> list[Check]:
    """One Check per fanned stage in `stages`: its model is in the harness's live catalog, or
    (no catalog) answered the smoke prompt. Same harness + same model is checked once."""
    # resolved at call time (tests swap the registry); the templates are this config's
    get = get or (lambda name: harness_mod.get(name, templates=cfg.harness_templates))
    checks: list[Check] = []
    cats: dict[str, tuple[list[Model] | None, str | None]] = {}
    smoked: dict[tuple[str, str | None], tuple[str, str]] = {}
    for name in stages:
        s = cfg.stage(name)
        if not s.fanned:
            continue
        hname = s.harness or harness_default
        try:
            h = get(hname)
        except ValueError as e:
            checks.append(Check(name, "FAIL", str(e)))
            continue
        if hname not in cats:
            cats[hname] = catalog(h)
        models, reason = cats[hname]
        label = s.model or "harness default"
        if models is not None:
            ids = [m.id for m in models]
            if s.model is None or s.model in ids:
                checks.append(Check(name, "ok", f"{label} ({hname}, in the catalog of {len(ids)})"))
            else:
                checks.append(Check(name, "FAIL", f"{s.model!r} is not in the {hname} catalog ({len(ids)} models; "
                                                  f"nearest: {', '.join(_nearest(s.model, ids))}); pick one from `hunt models`"))
            continue
        key = (hname, s.model)
        if key not in smoked:
            _res, err, secs = smoke_fn(h, s.model)
            why = f"no catalog on {hname}" + (f" ({reason})" if reason else "")
            smoked[key] = ("ok", f"{label} ({hname}, smoke prompt ok in {secs:.1f}s, {why})") if err is None else \
                          ("FAIL", f"{label} ({hname}): smoke prompt failed, {err}")
        status, detail = smoked[key]
        checks.append(Check(name, status, detail))
    return checks


def tool_probe(h: Harness, model: str | None, cwd: Path = ROOT) -> Check:
    """Can the model use the granted Read tool? A nonce in a temp file must come back."""
    if "read" not in h.capabilities:
        return Check("tools", "warn", f"{h.name} grants no read tool; the probe is skipped")
    nonce = secrets.token_hex(6)
    probe_dir = cwd / "data" / "hunt"
    probe_dir.mkdir(parents=True, exist_ok=True)
    path = probe_dir / f".doctor-probe-{nonce}.txt"
    path.write_text(f"probe {nonce}\n", encoding="utf-8")
    try:
        inv = Invocation(f"Use the Read tool on {path} and reply with exactly the text it contains, nothing else.",
                         "You are a tool probe.", model, frozenset({"read"}), cwd, 90)
        ex = execute(h, inv)
        if ex.timed_out:
            return Check("tools", "FAIL", "read probe timed out after 90s")
        res = h.parse(ex.stdout, ex.stderr, ex.rc)
        if res.error:
            return Check("tools", "FAIL", f"read probe: {res.error}")
        if nonce in (res.text or ""):
            return Check("tools", "ok", f"Read granted and used ({ex.elapsed:.1f}s)")
        return Check("tools", "FAIL", f"read probe: the reply did not carry the file's nonce ({(res.text or '')[:80]!r})")
    finally:
        path.unlink(missing_ok=True)


def doctor(cfg: HuntConfig, harness_name: str | None = None, get: Callable[[str], Harness] | None = None,
           smoke_fn=smoke, probe_fn=tool_probe, cwd: Path = ROOT) -> tuple[list[Check], int]:
    """Every check for one harness; (checks, exit code: 0 ok, 2 any FAIL)."""
    get = get or (lambda name: harness_mod.get(name, templates=cfg.harness_templates))
    hname = harness_name or cfg.harness
    checks: list[Check] = []
    try:
        h = get(hname)
    except ValueError as e:
        return [Check("harness", "FAIL", str(e))], 2
    found = shutil.which(h.binary)
    if not found:
        return [Check("binary", "FAIL", f"{h.binary!r} is not on PATH")], 2
    checks.append(Check("binary", "ok", found))
    try:
        cp = subprocess.run(h.version_argv(), capture_output=True, text=True, timeout=30, check=False)
        ver = (cp.stdout.strip() or cp.stderr.strip()).splitlines()[0] if (cp.stdout.strip() or cp.stderr.strip()) else ""
        checks.append(Check("version", "ok" if cp.returncode == 0 and ver else "FAIL", ver or f"exit {cp.returncode}"))
    except (OSError, subprocess.SubprocessError) as e:
        checks.append(Check("version", "FAIL", f"{type(e).__name__}: {e}"))
    if hasattr(h, "checks"):
        # what an adapter can find out before a call is spent (agy: signed in, and whether the
        # user's settings let python run headless). A FAIL stops here: the smoke prompt on a
        # signed-out agy would wait for a login until its timeout.
        own = [Check(*row) for row in h.checks()]
        checks += own
        if any(c.status == "FAIL" for c in own):
            return checks, 2
    models, reason = catalog(h)
    if models is None:
        aliases = h.aliases() if hasattr(h, "aliases") else []
        extra = f"; aliases from --help: {', '.join(aliases)}" if aliases else ""
        checks.append(Check("catalog", "warn", (reason or f"no catalog on {hname}") + extra +
                            "; models are validated by the smoke prompt"))
    else:
        checks.append(Check("catalog", "ok", f"{len(models)} models"))
    stage_checks = validate_models(cfg, [s for s in STAGES if cfg.stage(s).fanned and (cfg.stage(s).harness or cfg.harness) == hname],
                                   hname, get=lambda n: h, smoke_fn=smoke_fn)
    if not stage_checks:
        checks.append(Check("stages", "warn", f"no stage runs on {hname}"))
    checks += stage_checks
    if models is not None or not any(c.status == "FAIL" for c in stage_checks):
        fanned = [cfg.stage(s) for s in STAGES if cfg.stage(s).fanned and (cfg.stage(s).harness or cfg.harness) == hname]
        probe_model = next((s.model for s in fanned if s.model), None)
        if models is not None and stage_checks and all(c.status == "ok" for c in stage_checks) or models is None:
            checks.append(probe_fn(h, probe_model, cwd))
    rc = 2 if any(c.status == "FAIL" for c in checks) else 0
    return checks, rc


def render(hname: str, checks: list[Check], rc: int) -> str:
    fails = sum(1 for c in checks if c.status == "FAIL")
    tail = "ok" if rc == 0 else f"{fails} problem(s)"
    return "\n".join([f"doctor: {hname}", *(c.line() for c in checks), f"result: {tail}"])


def render_models(hname: str, models: list[Model] | None, reason: str | None, grep: str | None,
                  aliases: list[str] | None = None) -> str:
    if models is None:
        why = reason or f"{hname} has no model catalog"
        lines = [f"{hname}: {why}."]
        if aliases:
            lines.append(f"aliases named by `{hname} --help`: {', '.join(aliases)} (any full model id is also accepted)")
        lines.append("validation: a smoke prompt per configured model before every run and in `hunt doctor`")
        return "\n".join(lines)
    rows = [m for m in models if not grep or grep.lower() in m.id.lower() or grep.lower() in m.note.lower()]
    if not rows:
        return f"{hname}: no model matches {grep!r} ({len(models)} in the catalog)"
    width = max(len(m.id) for m in rows)
    return "\n".join([f"{hname}: {len(rows)} of {len(models)} models" if grep else f"{hname}: {len(models)} models",
                      *(f"  {m.id:<{width}}  {m.note}".rstrip() for m in rows)])
