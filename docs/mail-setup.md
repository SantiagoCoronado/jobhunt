# Inbox pull setup: reading every mailbox you apply from

`/jh-gmail-sync` reads your mail for signals on open applications (interview invites,
rejections, assessments, offers). The read happens in Python (`python -m src.mail_fetch`),
over plain IMAP, for as many mailboxes as you list in `.env`. Nothing is ever written to a
mailbox: folders are opened read-only and every fetch is a peek, so nothing gets marked
read. Design and budget: `docs/spec-mail-fetch.md`.

Why not the Gmail connector? It sees exactly one Google account. If you apply from a
second address, a sweep that looks clean is meaningless. It stays available only as a
fallback when no account is configured here.

## 1. Add your accounts to `.env`

Copy `.env.example` to `.env` if you have not already, then fill the `MAIL_*` block:

```
MAIL_ACCOUNTS=personal,apps
MAIL_PERSONAL_USER=you@gmail.com
MAIL_PERSONAL_PASS=abcd efgh ijkl mnop
MAIL_APPS_USER=you.applications@gmail.com
MAIL_APPS_PASS=abcd efgh ijkl mnop
```

- One label per mailbox, letters, digits and underscores only. The label becomes the
  `account` tag on every signal, and `/jh-followups` uses it to tell you which mailbox a
  reply has to go out from.
- `PASS` is an **app password**, never your login password (section 2). Spaces are fine;
  they are stripped.
- Optional per label: `MAIL_<LABEL>_HOST` (default `imap.gmail.com`, may carry `:port`),
  `MAIL_<LABEL>_FOLDERS` (comma list, default `INBOX`), `MAIL_<LABEL>_ALIASES` (other
  addresses that are you, so your own replies are recognized), `MAIL_<LABEL>_REPLY_AS`
  (only for a forwarding target, section 4).
- Gmail users: set `MAIL_<LABEL>_FOLDERS=INBOX,[Gmail]/Spam`. First-contact mail from an
  unfamiliar ATS domain lands in Spam more often than you would think. `[Gmail]/All Mail`
  also works if you archive aggressively; it is larger and includes sent mail.
- An account with a blank USER or PASS is reported as skipped, never as an error, and never
  breaks the run.

Then run it:

```
python -m src.mail_fetch
```

The first lines are one per account and folder. `ok` plus counts means it worked.
`error: ...` names the problem without ever printing the password.

## 2. Minting an app password, per provider

An app password is a second password scoped to one client. It grants the same mailbox
access as your real one, so treat it like one: keep it in `.env` (gitignored), prefer a
dedicated applications mailbox, and revoke it from the provider's security page when you
stop using this tool.

| provider | prerequisite | where | IMAP host |
|---|---|---|---|
| Gmail, Google Workspace | 2-Step Verification on (the app-passwords page does not appear without it) | myaccount.google.com/apppasswords | `imap.gmail.com` |
| iCloud Mail | two-factor authentication on | appleid.apple.com, Sign-In and Security, App-Specific Passwords | `imap.mail.me.com` |
| Fastmail | none | Settings, Privacy and Security, Integrations, New app password (choose Mail / IMAP) | `imap.fastmail.com` |
| Yahoo Mail | none | Account Security, Generate app password | `imap.mail.yahoo.com` |
| Zoho Mail | two-factor authentication on | My Account, Security, App Passwords | `imap.zoho.com` (US data center; EU is `imap.zoho.eu`, and `.in`, `.com.au`, `.jp` exist) |

All of these use port 993 with implicit TLS, which is the default. Google Workspace: an
admin can disable IMAP or app passwords for the domain; if the page is missing or the
login fails with `AUTHENTICATIONFAILED`, ask the admin or use forwarding (section 4).

**Outlook.com, Hotmail, Live, and Microsoft 365** do not work with this tool. Microsoft
removed basic authentication for IMAP on personal accounts in September 2024 (tenants
earlier), and app passwords are basic authentication, so third-party IMAP clients must use
OAuth, which this tool does not implement. Use forwarding (section 4).

Sources: [Microsoft support, apps unable to connect to Outlook.com with basic
authentication](https://support.microsoft.com/en-us/office/outlook-and-other-apps-are-unable-to-connect-to-outlook-com-when-using-basic-authentication-f4202ebf-89c6-4a8a-bec3-3d60cf7deaef),
[Microsoft, modern authentication now needed in non-Microsoft mail
apps](https://support.microsoft.com/en-US/Support/known-issues/modern-authentication-methods-now-needed-to-continue-syncing-outlook-email-in-non-microsoft-email-ap),
[Nylas, Gmail app passwords setup and gotchas](https://cli.nylas.com/guides/gmail-app-password-setup).

## 3. Tuning, organized by symptom

`config/mail_hints.yaml` is the one file to edit. You rarely have to go looking: the run
prints a `tune:` line naming the exact key when it detects the symptom, and the sync skill
repeats those lines to you.

**Product notifications show up as `weak` lines.** A company you applied to writes from one
or two domains; a dictionary word or a product you use shows up from many. The fetcher
demotes such a name for the run and prints:

```
tune: "Google" matched mail from 9 sender domains, treated as weak this run.
      Make it permanent: add google to weak_names in config/mail_hints.yaml
```

```yaml
weak_names: [google, linear, kraken]
```

**A company I know wrote to me is missing.** They probably write from another name or
domain than the job posting shows. Add an alias; both names and domains are matched:

```yaml
aliases:
  "Framework Computer": {names: ["Framework"], domains: ["frame.work"]}
```

To see what was cut, run `python -m src.mail_fetch --keep-noise`; the account summary
also prints counts per noise category (`seen`, `ignored`, `own`, `autoreply`, `alerts`,
`echoes`, `receipts`, `collapsed`). After three sweeps of every mailbox with no candidate for an open
job, the run prints a `tune:` line pointing here.

**Mail from a company I am a customer of keeps appearing.** Never match that sender:

```yaml
ignore_senders: [kraken.com, notifications@linear.app]
```

**Recruiters write to me in another language.** The `hints` block is per language; English
and Spanish ship. Add a block with the same four categories (`reject`, `schedule`,
`assessment`, `offer`) and the receipt subjects for your language under `receipts`. A hint
only tags a line for the model; it never decides a status.

## 4. Forwarding fallback

If your provider cannot do IMAP with an app password (Outlook, a locked-down Workspace
domain, Exchange), set up a forwarding rule from that mailbox into one that can (a Gmail
account works), configure the target here, and set `MAIL_<LABEL>_REPLY_AS` on the target to
the original address so `/jh-followups` tells you to reply from the right place. Replies
to ATS relay addresses (Greenhouse `bf-j-...`, Lever, Ashby) must go out from the address
the thread was sent to, or the threading breaks.

## 5. What the model reads, and what it does not

The run prints a legend (one line per job with mail) and a manifest (one line per thread:
sender, hints, subject, and a short lead centered on the decisive sentence). That is all the
model reads. Full snippets live in `data/mail_snippets.jsonl` and come out only through
`python -m src.mail_fetch show <id>` for the few lines the manifest cannot settle. Bodies
never enter the database, `data/gmail_pull.json`, or any report; the applier stores
headers plus the classification signal.

Budget, projected for a 91-application pipeline (the spec derives it; Phase D replaces it with measured numbers): roughly 250 tokens per surviving email,
6k to 10k per weekly sweep, 25k to 35k for a first run over two months of mail. Every sweep
prints its own thread counts so you can check it.

## 6. Commands

```
python -m src.mail_fetch                       # sweep every account, print summary + legend + manifest page 1
python -m src.mail_fetch --account apps        # one label only
python -m src.mail_fetch --full                # ignore the seen list (re-surface already classified mail)
python -m src.mail_fetch --keep-noise          # disable the noise cuts to debug a missed email
python -m src.mail_fetch --scan-all            # header pull instead of per-job search (servers with no text search)
python -m src.mail_fetch --since 2026-07-01    # override the horizon
python -m src.mail_fetch manifest --page 2     # next page of a long manifest
python -m src.mail_fetch show 7 12 15          # cleaned snippets for those ids (25 max)
python -m src.gmail_pull data/gmail_pull.json  # dry run of the classified batch
python -m src.gmail_pull data/gmail_pull.json --apply
```

State lives in `data/mail_state.json`: per-account sweep times, the `seen` ids (pruned past
`--max-days`, default 120), and the zero-candidate counters behind the aliases hint.
Delete the file to start clean.
