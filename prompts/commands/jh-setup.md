---
description: 'Onboarding interview: read your documents, write the master resume, the profile, the sources, the keys. Usage: /jh-setup [files...]'
argument-hint: '[files...]'
tools: [read, write, bash]
---

Set up jobhunt for me: turn my documents and my answers into `resume/master_resume.yaml`,
`config/profile.yaml`, `config/sources.local.yaml` and `.env`. Files I named: **$ARGUMENTS**

Run every command below with your shell tool from the repo root (`.venv/bin/python` if plain
`python` is not on PATH). `python -m src.onboard` does everything deterministic; you run the
interview. Rules for the whole session:

- **Nothing invented.** The master resume holds only facts that are in my documents or that I
  typed in this chat. Every role, project, school, skill group and additional line gets a
  provenance entry naming the document it came from (or `interview`). Anything you cannot place
  becomes a question to me, never a guess. Dates, numbers and titles are copied, not improved.
- **Every write goes through the helper**: `python -m src.onboard write <what> <payload>`. Never
  edit those four files with your own write or edit tool. Put a payload in a file under
  `data/onboard/` (`payload-resume.json`, ...) and pass its path. Your write tool touches nothing
  outside `data/onboard/`.
- Exit 3 from a writer means the file was edited by hand: show me the diff it printed, ask,
  and repeat the call with `--yes` only if I agree.
- **Token budget**: read each extracted text file once, write each file once, keep the whole
  setup under 0.3M tokens. Do not read the repo's code or docs beyond what this command names.
- Talk to me in the language I write in; write the files in the language of my documents.
- Zero em-dashes in anything you write. Plain voice: read `docs/writing-voice.md` once before
  the first write; it applies to the summary, the candidate line and the notes.

## 1. Documents

Ask for my documents if I named none: resumes, cover letters, a portfolio page saved as text,
LinkedIn's "Save to PDF" or its data-export zip (Settings, Data privacy, Get a copy of your
data). PDF, docx, md, txt, csv or zip. Then:

```
python -m src.onboard extract <file> [<file> ...]
```

It prints one line per document with its size in tokens. A document marked `! large` is not
read: ask me for the pages that matter (or a shorter export) and extract that instead. A PDF
with no text layer needs a text export or pasted text.

Then read each text file the extract printed, once.

## 2. Master resume

Build the resume from those texts in the schema of `resume/master_resume.yaml` (`cv.name`,
`location`, `email`, `phone`, `social_networks`, then `cv.sections` with `summary`,
`experience` (company, position, start_date and end_date as YYYY-MM or `present`, location,
highlights), `projects` (name, date, highlights), `skills` (label, details), `education`
(institution, area, degree, dates) and `additional` (label, details)). Before writing, ask me
in one message about every gap: a role with no dates, a skill no document shows, two documents
that disagree. Then write it with a `provenance` list beside `cv`:

```json
{"cv": {...}, "provenance": [{"what": "experience Ledgerly", "from": ["resume.pdf"]},
                             {"what": "skills Frontend", "from": ["resume.pdf", "interview"]}]}
```

```
python -m src.onboard write resume data/onboard/payload-resume.json
```

A refusal names what is missing (`no provenance for experience 'X'`): ask me, then write again.
Show me the provenance list: one line per role and skill group, the document it came from.

## 3. Profile

Read `config/profile.yaml` once: its comments say what every key means. Ask one section at a
time, proposing values from the resume, and wait for my answer each time:

1. Who I am: `name`, `candidate_line`, `seniority`, `header_location`.
2. What I apply for: `target_titles`, `role_families` (key, name, titles, skills, strength).
3. Where: `locations`, `timezones`, `location_rule`, `work_authorization` (`relocation_regions`
   are region names from `config/geo.yaml`).
4. Pay: `comp`.
5. What I will not take: `dealbreakers`.
6. Skills: `must_have_skills`, `nice_to_have_skills` (only skills the resume shows).
7. Dream companies, if any: name, careers URL, a note. Then `dream_rule` and `relocation_line`.
8. `notes`: a short third-person framing for the matcher.

Write the profile once, with every key you collected, then the dream companies:

```
python -m src.onboard write profile data/onboard/payload-profile.json
python -m src.onboard write dream data/onboard/payload-dream.json
python -m src.onboard check profile
```

Tell me which keys still hold the example's value (`check profile` names them).

## 4. Sources

```
python -m src.onboard sources
```

Show me which sources my regions turn on and what each still needs (targeting, a key). Ask for
the companies I follow and their ATS board token (the slug in `boards.greenhouse.io/<token>`,
`jobs.lever.co/<company>`, `jobs.ashbyhq.com/<client>`, ...). Verify each before it is written:

```
python -m src.onboard verify-token <source> <token>
```

Leave out a token that fails or returns 0 roles and tell me. Then write the targeting the
proposal asked for (queries, countries, the verified tokens) in one call:

```
python -m src.onboard write sources data/onboard/payload-sources.json
```

## 5. Keys and mail

For each keyed source the proposal marked, give me its signup URL and ask for the value or
"skip". Then ask whether I want the inbox pull (`/jh-gmail-sync`): if yes, one label per mailbox
I apply from, the address and an app password (never my login password; `docs/mail-setup.md`).
Write every value once, and never repeat a value back to me:

```
python -m src.onboard write env data/onboard/payload-env.json
```

(`{"ADZUNA_APP_ID": "...", "MAIL_ACCOUNTS": "apps", "MAIL_APPS_USER": "...", "MAIL_APPS_PASS": "..."}`).
Delete `data/onboard/payload-env.json` right after the write succeeds.

## 6. Check and first run

```
python -m src.hunt doctor
python -m src.discover
python -m src.onboard summary
```

`discover` takes minutes: run it in the background (or with a timeout of at least 20 minutes)
and report the rows per source when it ends. Close with the summary: what was written where,
how many roles, projects and skills (each traced to a document), the sources on and the keys
set or skipped, the tokens left out, and the next step: `/jh-hunt`.
