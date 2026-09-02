# Coinbase: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: "Senior Software Engineer, Full Stack (Coinbase Advisor, Agentic Trading)" (job id
14345), listed on WeWorkRemotely as "Anywhere in the World"
https://weworkremotely.com/remote-jobs/coinbase-senior-software-engineer-full-stack-coinbase-advisor-agentic-trading
(page 403s automated fetchers). Primary req found and fetched directly from Coinbase's own
Greenhouse job board: https://www.coinbase.com/careers/positions/8070574?gh_jid=8070574 and its
structured API record at https://boards-api.greenhouse.io/v1/boards/coinbase/jobs/8070574.

## VERDICT: NOT ELIGIBLE

The req's own structured location field, pulled directly from Coinbase's Greenhouse job board API
for this exact posting (job 8070574), is:

> `"location": {"name": "Remote - USA"}`
[boards-api.greenhouse.io/v1/boards/coinbase/jobs/8070574]

This is Coinbase's own primary-source data for this specific requisition, not a third-party
aggregator's generic tag. It contradicts WeWorkRemotely's "Anywhere in the World" listing, which is
WWR's own generic remote label, not authoritative. The posting text itself only says "Coinbase is a
remote-first, but not remote-only company," which describes the surge/travel cadence, not the
country-eligibility scope; the location field is the actual scope
[coinbase.com/careers/positions/8070574]. The posting also links US-specific compliance documents
(Employee Rights, EEOC Know Your Rights, E-Verify) in its footer, consistent with a US-resident
hire [static-assets.coinbase.com/e-verify.pdf, linked from the posting].

For contrast: Coinbase does hire in Mexico for other functions, for example "Country Manager,
Mexico, Remote - Mexico City" is explicitly scoped that way in its own req
[coinbase.com/careers/positions/6891831], which shows Coinbase's job board is capable of scoping a
role to Mexico when it intends to. This engineering req was not; it was scoped "Remote - USA."
Per the location_rule in config/profile.yaml, a remote role that requires a US work location and
excludes Mexico-based candidates is a hard dealbreaker regardless of Santiago's TN-visa eligibility
for future US-based employment; TN eligibility supports business travel and a hypothetical US-based
hire, not a Mexico-City-remote arrangement against a US-scoped req. This dossier is kept short per
the task instructions since the role is not usable as posted.

## 1. Snapshot (brief, for context only)

Coinbase Global, Inc. (NASDAQ: COIN) is a publicly traded (IPO'd 2021) cryptocurrency exchange and
financial infrastructure company, remote-first with quarterly in-person "surge" sessions, widely
reported base salary bands in the $127K-$300K+ range depending on role and scope
[coinbase.com/careers; efinancialcareers.com/news/coinbase-remote-jobs-pay]. The target req sits on
the "Coinbase Advisor" team inside the Consumer & Business group, building AI-powered agentic
trading experiences (conversational interfaces for trade discovery, execution, and portfolio
management) across web and React Native mobile, backed by Go services, with a base range of
$186,065 to $218,900 USD (excluding equity/bonus), scoped "Remote - USA"
[boards-api.greenhouse.io/v1/boards/coinbase/jobs/8070574].

## 2. Why this dossier stops here

Per instructions, when a role is NOT ELIGIBLE this dossier stays short rather than building out
full culture/news/engineering sections, since the role cannot be used for an application. The one
worthwhile note for Santiago's own record: Coinbase Advisor's mission (agentic, conversational
trading interfaces) is genuinely close to his interests (personal crypto investor since 2017,
built Plutus, a self-hosted investment research and discovery platform with an LLM research agent
exposed via MCP) [resume/master_resume.yaml]. If Santiago becomes open to a real relocation, or if
Coinbase later posts a Mexico-scoped or Americas-scoped engineering req, that domain match would be
worth revisiting; as posted, this specific requisition is out of scope.

## Sources

- https://boards-api.greenhouse.io/v1/boards/coinbase/jobs/8070574 (primary source: structured
  location field "Remote - USA", full job description, salary range $186,065-$218,900, application
  limit language, fetched directly via curl)
- https://www.coinbase.com/careers/positions/8070574?gh_jid=8070574 (human-facing posting, same
  req, remote-first/surge language, US compliance document links)
- https://weworkremotely.com/remote-jobs/coinbase-senior-software-engineer-full-stack-coinbase-advisor-agentic-trading
  (WWR mirror listing, labeled "Anywhere in the World"; flagged as contradicted by the primary
  source above and not authoritative)
- https://www.coinbase.com/careers/positions/6891831 (Country Manager, Mexico req, explicitly
  scoped "Remote - Mexico City"; used as contrast evidence that Coinbase's job board does scope
  roles to Mexico when intended)
- https://www.coinbase.com/blog/The-Next-Phase-of-Remote-First-at-Coinbase and
  https://www.coinbase.com/blog/post-covid-19-coinbase-will-be-a-remote-first-company (Coinbase's
  own remote-first policy history: "surges," decentralized office strategy)
- https://www.efinancialcareers.com/news/coinbase-remote-jobs-pay (third-party aggregate salary
  range context, used only for general snapshot, not for the eligibility verdict)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (location_rule, cited for the dealbreaker
  determination)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Plutus project, crypto domain
  interest, cited only in the closing note)

Note for Santiago: this is a draft dossier, please review. The verdict rests on Coinbase's own
Greenhouse API data for this exact requisition ("Remote - USA"), which is the strongest kind of
primary source available and directly contradicts the WWR aggregator listing you flagged. If you
want a second opinion, ask a recruiter directly whether this specific req has any flexibility for a
non-US remote hire, but do not treat that as likely given the explicit US-only location field.
