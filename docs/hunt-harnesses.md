# Hunt harnesses

The hunt orchestrator (`python -m src.hunt`, spec `docs/spec-hunt-orchestrator.md`) runs every
unit of model work as one process of an agent CLI. A **harness** is the small adapter that
knows how to build that command line and read what the CLI prints. Nothing else about a CLI
leaks into the hunt, so the same run works on any of them.

Pick one in `config/hunt.toml`:

```toml
[harness]
default = "opencode"            # claude | codex | opencode | pi | agy | a [harness.<name>] below

[stages.research]
harness = "claude"              # one stage on another harness; research must grant "web"
```

or for one run: `python -m src.hunt run --harness pi`. Then, before the first hunt on it:

```
python -m src.hunt doctor --harness NAME     # binary, version, sign-in, catalog, each stage's model, a smoke prompt, a read probe
python -m src.hunt models --harness NAME     # the live catalog, to pick each stage's model from
```

A harness whose catalog exists but cannot be read (agy signed out, a CLI offline) fails the run
before it starts, without spending a call; only a harness with honestly no catalog (claude, a
template) is validated by the smoke prompt.

A model id means something only to the harness whose catalog it came from. The shipped
`hunt.toml` names claude aliases; on another harness `doctor` fails those at minute zero and
`hunt models` shows what to write instead. Leave `model` out to take the harness default.

## What each adapter runs

Tools are the orchestrator's own words (`read`, `write`, `edit`, `bash`, `web`); `bash` always
means "python only" where the CLI can express that. Every line below is pinned by a test in
`tests/test_hunt_harness*.py`.

### claude (reference)

```
claude -p [--bare] --output-format json --no-session-persistence --strict-mcp-config
       --permission-mode acceptEdits --permission-prompts none [--model M] --system-prompt S
       --tools Read,Write,Edit,Bash[,WebSearch,WebFetch]
       --allowedTools Read Write Edit "Bash(python:*)" "Bash(.venv/bin/python:*)" [WebSearch WebFetch]
       [--json-schema SCHEMA]                                   prompt on stdin
```

Grants all five tools. `--bare` only with `ANTHROPIC_API_KEY` set. No catalog command: models
are validated by a 10-token smoke prompt. Verified with real calls (2.1.276).

### codex

```
codex exec --json -o LAST_MSG_FILE [-m M] --sandbox (workspace-write | read-only)
      [--output-schema SCHEMA_FILE] --ephemeral --skip-git-repo-check -
                                                  role body + prompt on stdin
```

No system-prompt flag and no tool allowlist: the sandbox is the grant (`workspace-write` when
the unit may write, edit or run python). `bash` cannot be narrowed to python by a flag; that is
an execpolicy `.rules` file, yours to write. Catalog: `codex debug models`. Does not claim
`web`. **Verified on a real failed call only** (0.153.4, not logged in): the success stream is
parsed from the CLI's documented events. Run the smoke test below once you are logged in.

### opencode

```
opencode run --format json [-m PROVIDER/MODEL] --agent ROLE PROMPT
```

`run` has no tool flags. `.opencode/agents/ROLE.md` (generated, see below) carries the
permissions and the role body, and `--agent` applies them, so the prompt is the task alone.
Where the hunt's stage grants less than the role file, `sync-agents` also writes
`hunt-ROLE.md` with the stage's grant and the unit runs on that one: today only
`hunt-job-matcher`, because the matcher keeps `bash` for interactive ingest and under the
orchestrator ingest is Python's. A
refused tool call goes back to the model as an error; nothing prompts. `--auto` is never
passed. No schema flag: a schema rides in the prompt. Usage is one `step_finish` per step,
summed. Catalog: `opencode models`. Claims `web` only with `OPENCODE_ENABLE_EXA` set (the
`websearch` tool exists only there or on the opencode provider). Verified with real calls
(1.18.29), including a probe agent that was granted a read and refused a write.

### pi

```
pi -p --mode json --no-session --no-context-files --no-skills --no-prompt-templates --no-approve
   [--model PROVIDER/ID] --system-prompt S (--tools read,write,edit,bash | --no-tools)
                                                  prompt on stdin
```

The prompt is on stdin because an argument starting with `@` is a file and one starting with
`-` is an option. Context files, skills and project-local files are off (the role body is the
system prompt); extensions stay on, a provider may come from one. No web tool; `bash` cannot be
narrowed to python. Catalog: `pi --list-models`, ids are `provider/model`. Verified with real
calls (0.85.1).

### agy (Antigravity)

```
agy --output-format json [--model M] [--mode accept-edits] [--json-schema SCHEMA]
    --print-timeout Ns --print=ROLE_BODY_AND_PROMPT
```

`-p` takes the prompt as its own value, so the prompt is attached to `--print=` and goes last
(`agy -p --output-format json ... PROMPT` exits 2). No `--agent`: the role body is prepended.
Two things to do by hand, both checked by `doctor` before it spends a call:

1. **Sign in**: launch `agy` once with no arguments. A signed-out headless call prints a login
   URL and waits, past `--print-timeout`.
2. **Allow python**: headless mode auto-denies any shell command that `permissions.allow` in
   `~/.gemini/antigravity-cli/settings.json` does not cover. Add `"command(python)"` and
   `"command(.venv/bin/python)"`, or the inbox, research and tailor units cannot run it.

Does not claim `web`. `--dangerously-skip-permissions` is never passed. Catalog: `agy models`.
Verified with real calls (1.1.27, 2026-09-22): a smoke prompt, a schema unit (the object comes
back under `structured_output`), a model it does not know (an `ERROR` envelope carrying the
catalog). `output_tokens` counts thinking tokens; no cost is reported.

### Anything else: a command template

```toml
[harness.gemini]
command = "gemini -m {model} --approval-mode auto_edit -o json -p {prompt}"
envelope = "json"                                   # or "text" (the default)
capabilities = ["read", "write", "edit", "bash", "web"]
```

The command is split once with shell rules and never runs through a shell, so a placeholder is
always exactly one argument, whatever the prompt contains.

| Placeholder | Becomes |
|---|---|
| `{prompt}` / `{prompt_file}` | the unit's prompt, as text or as a file path |
| `{system}` / `{system_file}` | the role body, as text or as a file path |
| `{schema_file}` | the unit's JSON schema, as a file path |
| `{model}` | the stage's model |

- No system placeholder: the role body is prepended to the prompt.
- No prompt placeholder: the prompt goes on stdin.
- `{model}` with no model set, or `{schema_file}` on a unit with no schema: that argument is
  dropped, and the flag before it too when it starts with `-`, so `-m {model}` vanishes whole
  (`--model={model}` is its own flag and goes alone).
  A schema the command has no place for rides in the prompt.
- A literal brace is `{{` or `}}`.
- `envelope = "json"`: the last JSON object printed. The reply is the first string among
  `result`, `response`, `text`, `output`, `message`; `is_error`, a non-empty `error` or a bad
  exit is a failure; usage is read from `usage` when it uses common token names, null
  otherwise. `envelope = "text"`: stdout is the reply, usage is null.
- `capabilities` is what YOU say the CLI can do (default `read, write, edit, bash`). A template
  cannot grant or withhold a tool; that is your command line's job (`--approval-mode`,
  a sandbox flag, the CLI's own settings).
- No catalog: the model is passed through unvalidated and the smoke prompt is the check.
- A template cannot take the name of a shipped adapter.

A bad block (unknown key, unknown placeholder, a command that does not split) fails when the
config loads, never mid-hunt.

## Native agent files (`sync-agents`)

`prompts/agents/<role>.md` is the one place a role's system prompt lives.
`python -m src.hunt sync-agents` renders it for every harness, the files are committed so
interactive use works after a clone, and CI runs `sync-agents --check`. Never edit a generated
file.

| Folder | Format | Read by the hunt? | Checked against a loader? |
|---|---|---|---|
| `.claude/agents/*.md` | claude frontmatter, tools by claude names | no (body goes in `--system-prompt`) | yes |
| `.opencode/agents/*.md` (plus `hunt-<role>.md` where the stage grants less) | `mode: all`, `permission:` rules | **yes**, `--agent` | yes, `opencode agent list` |
| `.pi/agents/*.md` | `name`, `description`, `tools`, `model` | no | no extension installed |
| `.gemini/agents/*.md` | `kind: local`, tools by Gemini names | no | gemini has no list command |
| `.codex/agents/*.toml` | `developer_instructions`, `sandbox_mode` | no | codex not logged in |

A generated file carries a stage's `model` only when that stage runs on that file's harness.
agy has no generated file: its `agent.md` layout could not be confirmed.

## Commands on every harness (`sync-agents`)

The `/jh-*` commands follow the same pattern (`docs/spec-pre-release.md` decision 4):
`prompts/commands/<name>.md` is the one source (`description`, optional `argument-hint`,
`tools` from `read, write, edit, bash, web, glob, agent, gmail-read, gmail-draft`; the body in
harness-neutral words, "your shell tool", "the resume-tailor agent", `$ARGUMENTS` for what the
user typed after the name). `sync-agents` renders it for every harness that has a project
command format, and the same `--check` covers the renders. Never edit a render.

| Harness | Render | Format | Checked against |
|---|---|---|---|
| claude | `.claude/commands/<name>.md` | `description`, `argument-hint`, `allowed-tools` by claude names | the files it replaced, byte for byte, before they became renders |
| opencode | `.opencode/commands/<name>.md` | `description` only (no hint, no tool list: the session's permissions apply); `$ARGUMENTS` | `opencode debug config` on 1.18.29 lists all 13 under `command` |
| gemini | `.gemini/commands/<name>.toml` | `description`, `prompt`; `$ARGUMENTS` becomes `{{args}}`; a body with `!{` or `@{` is refused (gemini would inject a shell or a file) | the loader source, `FileCommandLoader` in the 0.46.0 bundle (no list command); loaded only in a trusted folder when folder trust is on |
| pi | `.pi/prompts/<name>.md` (prompt templates) | `description`, `argument-hint`; `$ARGUMENTS` | pi 0.85.1's own `loadPromptTemplates` and `substituteArgs`; project templates load once the project is trusted |
| codex | `AGENTS.md` `## Commands` | say `jh-tailor 123`; the agent reads `prompts/commands/jh-tailor.md` | `codex debug prompt-input` on 0.153.4 carries `AGENTS.md` |
| agy | `AGENTS.md` `## Commands` | as codex | agy 1.2.8 documents `AGENTS.md` as its rules file; not checked against a loader (no list command, a signed-out call waits on a login) |

`AGENTS.md` is read by opencode and pi too, so it stays short and names the harnesses with
native commands. The hunt never runs a command: pi units start with `--no-prompt-templates`
and `--no-context-files`.

`./setup.sh` (`python -m src.setup`) asks which of claude, codex, opencode, pi, gemini and agy you
run, writes the first one with a shipped adapter as `[harness] default`, runs `hunt doctor
--harness H` for each, and ends with the next step in that harness's words: `/jh-setup` where
there are slash commands, the name to say on codex and agy (`jh-discover` until the onboarding
interview lands). It never renders a per-user file.

Opt-in home copy (codex): `python -m src.setup` offers to write one skill per command into
`~/.codex/skills/<name>/SKILL.md`, so `$jh-tailor 123` works in any codex session started in the
checkout. Each skill only points at `prompts/commands/<name>.md`, so it never goes stale, and
carries the installer's mark; the installer updates or removes only files with that mark and
never touches a skill it did not write. Checked: `codex debug prompt-input` on 0.153.4 lists a
skill in that folder; codex's older custom-prompts folder (`~/.codex/prompts/`) could not be
found in that build.

Not rendered, recorded for later: codex 0.153.4 also loads project skills from
`.agents/skills/<name>/SKILL.md` (checked with `debug prompt-input`), and agy 1.2.8 documents
the same folder with `/<name>` slash support and calls its older `.agents/workflows/` deprecated.
Both are skills (a model may invoke one unasked), not commands, so the spec's `AGENTS.md` path
stays the default for codex and agy.

## `web` and research

Only `research` needs `web`. Of the shipped adapters claude grants it always and opencode with
`OPENCODE_ENABLE_EXA`; codex, pi and agy do not claim it. When the stage's harness lacks it,
the hunt runs research on the first configured harness that has it, with that harness's
default model, and says so in the run's output. To choose instead:
`[stages.research] harness = "claude"`.

## Smoke tests

One real 10-token call per shipped adapter, opt-in three ways because it spends real tokens and
is the one test allowed to start a real agent CLI:

```
HUNT_SMOKE=1 .venv/bin/python -m pytest tests/test_hunt_harness_smoke.py -m harness_smoke
```

A CLI that is not installed skips; one that is installed but signed out fails with its own
message, the same one `hunt doctor --harness NAME` gives.

## Adding a shipped adapter

Try a command template first. Write Python only when the CLI needs what a template cannot do:
a catalog command, an event stream to sum, files to generate, its own doctor checks.

1. `src/hunt/harness/<name>.py`: a class with `name`, `binary`, `capabilities`, `version_argv`,
   `argv`, `stdin`, `parse`, `models`, `smoke` (the `Harness` protocol in
   `src/hunt/harness/__init__.py`). `_common.py` has the JSON-lines reader, the rate-limit
   wording, `granted` (refuse a tool you cannot grant, never drop it) and the catalog runner.
   Optional `checks()` returns `(name, status, detail)` rows `doctor` prints before spending a
   call; a `FAIL` stops it.
2. One line in `_ADAPTERS`. `SHIPPED`, the fallback order and the TUI's harness list follow.
3. Capture a real success and a real failure into `tests/fixtures/hunt/` (strip local paths)
   and pin `argv` per tool set. If you could not see a success, say so in the module docstring.
4. If the CLI has native agent files, a renderer plus one row in `prompts.NATIVE`.
5. Add the binary to `AGENT_CLIS` in `tests/conftest.py` so no ordinary test can start it. The
   smoke test needs nothing: it reads `SHIPPED`.
