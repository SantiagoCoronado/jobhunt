# Vitalize

Reusable dossier for Santiago Coronado, drafted for local job id 10645, "Senior Product Engineer,
Deployment Platform" (source: findwork, `https://findwork.dev/Xq2xbLn/senior-product-engineer-deployment-platform-at-vitalize`).
Draft for review, not a final source of truth.

## Identity confirmation (read first)

"Vitalize" is an ambiguous name (a venture fund, a health/wellness app, other unrelated
companies). This dossier is about **Vitalize Care** (`vitalize.care`), the YC-backed hospital
labor and staffing operating system, San Francisco. Confirmed by matching the job posting's own
text against the company's primary sources:

- The job description in our DB opens with: "At Vitalize, we're building toward a future where
  hospital operations are safe, autonomous, fair, and cost-effective. Today, hospitals still run
  their most critical workflows (staffing, labor planning, capacity management) on spreadsheets,
  paper, and gut instinct." [`.venv/bin/python -m src.query job 10645`]
- Vitalize Care's own YC page describes the identical pitch: "Transforming how health systems
  optimize labor," founded 2023 by Sanketh Andhavarapu and Veeraj Shah, San Francisco, YC Winter
  2023 batch [ycombinator.com/companies/vitalize].
- Vitalize Care's own live careers page (Ashby, fetched directly via its public job-board API)
  uses the same framing: "Hospitals run on three things: their people, their beds, and their
  supplies... and all are still managed with spreadsheets, phone calls, and gut instinct"
  [`api.ashbyhq.com/posting-api/job-board/vitalize`].
- The stack named in the req ("Strong proficiency in React, TypeScript, Postgres... Nice to have:
  Experience with Effect") matches Vitalize Care's own stated stack elsewhere: "Stack: Typescript
  + Postgres + Effect" on a Vitalize hiring post on Hacker News, and "Bun, TypeScript, Effect,
  React, TanStack Router, Planetscale" on the current live engineering req
  [news.ycombinator.com/item?id=48749843; `api.ashbyhq.com/posting-api/job-board/vitalize`].

This is not the venture-fund Vitalize or any health/wellness app named Vitalize; identity is
confirmed with high confidence.

## Location eligibility verdict: NOT ELIGIBLE from Mexico, and open status is unconfirmed (read first)

**The req's own text rules out a Mexico-based remote hire.** The posting closes with: "Location
San Francisco HQ (in-person) or hybrid." [`.venv/bin/python -m src.query job 10645`, job body
text]. That is a hybrid/in-person requirement in San Francisco, not a remote grant, and it names
no country-inclusive remote option. Per `config/profile.yaml`'s location rule, any role requiring
a work location outside Mexico, hybrid included, is a dealbreaker. The local matcher scored this
job 86 with `"location_ok": true` and the reasoning "Listed Remote with no country restriction in
the text" [DB `match_verdict` for job 10645]; that reasoning is wrong on this record, since the
description's own closing line was not weighed. **This should be treated as a location fail, not
an 86.**

Corroborating (not contradicting) evidence from the company's other channels:
- Vitalize's currently-live structured job data (Ashby posting-API, pulled directly today) shows
  every current engineering/product req as `workplaceType: "Hybrid"`, `location: "San Francisco
  HQ"`, address San Francisco, California, United States, except one fully-remote non-engineering
  role (Head of Marketing) [`api.ashbyhq.com/posting-api/job-board/vitalize`].
- A Vitalize hiring post on Hacker News (dated 2026-07-01) advertises a general "Full-time
  Engineer" role as "Remote (US, SF in-person preferred)" [news.ycombinator.com/item?id=48749843].
  Read generously, that is still scoped to the US, not Mexico or LATAM; Santiago's profile treats
  "must reside in the United States" style scoping as a dealbreaker too. No source found anywhere
  (careers page, job postings, HN post) mentions Mexico, LATAM, or "worldwide" as an eligible
  remote geography.

**Open status: could not confirm this specific req is still live.** The current Ashby job-board
API for Vitalize (pulled directly today, 2026-08-11) lists 8 open roles; none is titled "Senior
Product Engineer, Deployment Platform." The closest title on the live board, "Senior Product
Engineer" (`ad6831f1-c0a9-4f6a-9a4c-6a78c48a3ce9`, published 2026-06-03), has a materially
different job description (a "decision engine" for staffing recommendations, not a deployment/
configuration platform), so it does not appear to be the same req reworded
[`api.ashbyhq.com/posting-api/job-board/vitalize`]. Our local DB still shows `last_seen:
2026-08-11` for job 10645 via findwork, and findwork's own page still renders it as apparently
active [findwork.dev listing], so this dossier cannot rule out that the req is genuinely open on
some path not surfaced by the public Ashby API pull; it also cannot confirm it. Given both the
hard location fail and the unconfirmed open status, Santiago should not invest further in this
specific req without a direct answer from Vitalize on both points, and should treat the 86 score
as unreliable.

## 1. Snapshot

Vitalize Care is a San Francisco based, YC-backed (W23) startup building an AI operating system
for hospital labor, staffing, and capacity management. Series A stage per a company hiring post
(2026-07-01); ~28-50 employees depending on source and date; has raised over $32M total per the
company's own current careers-page copy; live across 20-30+ hospitals with roughly $10M ARR
achieved in under 2 years as of mid-2026.
[ycombinator.com/companies/vitalize](https://www.ycombinator.com/companies/vitalize),
[Vitalize live careers data](https://api.ashbyhq.com/posting-api/job-board/vitalize),
[HN hiring post](https://news.ycombinator.com/item?id=48749843).

## 2. Core narrative

Vitalize's founders started by building a mental-health platform for healthcare workers, saw weak
adoption, then spent months interviewing hundreds of people across 20+ health systems before
writing a line of code for the current product, under an explicit internal rule: "no code until we
signed multiple health system deals." A Figma prototype landed the first six-figure pilot within
two months and became a multi-million-dollar deal within four weeks of launch. That
customer-development-first, ship-only-what's-validated instinct is now the company's product
thesis at scale: replace hospitals' spreadsheet-and-gut-instinct staffing process with an
"operating system" that increasingly makes staffing decisions itself.
[Substack: Millions in revenue with a 15-person team](https://nextplayso.substack.com/p/millions-in-revenue-with-a-15-person),
[Vitalize: Rebuilding the Foundation of the Healthcare Workforce](https://vitalize.care/blog/rebuilding-the-foundation).

## 3. Mission & product

- Product: an AI-powered "operating system" for hospital workforce operations, covering
  AI-assisted scheduling (automating a large share of schedule creation and load-balancing),
  a staffing "command center" for real-time decisions, patient flow and capacity optimization, and
  predictive workforce-demand analytics [vitalize.care homepage/solutions pages].
- Business model: enterprise SaaS sold directly to health systems; the company states customers
  "pay 5-15x more than legacy incumbents" because the software is mission-critical to hospital
  operations [live Ashby "Senior Product Engineer" posting,
  `api.ashbyhq.com/posting-api/job-board/vitalize`].
- Customers: named health systems include MemorialCare and Hendrick Health, with public
  testimonials from a hospital CEO and a Chief Nurse Executive [vitalize.care homepage].
- Scale claims: live across 20-30+ hospitals, roughly $10M ARR achieved in under 2 years, reported
  by the company itself on a Hacker News hiring post [news.ycombinator.com/item?id=48749843].

## 4. Culture & voice

- Four stated values, each tied to an internal company story: "Push the Car" (step outside your
  role, own problems end to end), "Premier 1K" (customer feedback shapes everything, engineers
  meet customers directly), "Run Towards the Ugly" (name the hardest problem first, candor over
  comfort), "Think Bigger Fridays" (see a gap, fill it, experiment fast)
  [live Ashby posting, `api.ashbyhq.com/posting-api/job-board/vitalize`].
- Hiring philosophy blog post: prioritizes "intelligence over credentials," explicitly optimizing
  for "learning and talent-density rather than titles and promotions"; looks for bias toward action
  (unprompted documentation fixes, demos built before being asked, visiting customer sites before
  an offer) and a willingness to challenge leadership; describes the engineering environment as
  high autonomy with minimal handholding and mission-critical urgency (emergency hospital site
  visits, last-minute travel)
  [vitalize.care: Our thoughts on building a team](https://vitalize.care/blog/our-thoughts-on-building-a-team).
- Perks/benefits across current postings: medical/dental/vision, 401(k) match, flexible or
  unlimited PTO, bi-annual company off-sites, free meals in-office, a travel budget to visit
  customer sites, relocation bonus, desk-setup and commuter reimbursement
  [job 10645 body; live Ashby posting].

## 5. Recent news (last ~12 months)

- **2026-02-23 / published 2026-07-23**: Published "Rebuilding the Foundation of the Healthcare
  Workforce," arguing hospital staffing problems are an infrastructure problem, not a headcount
  problem: "if you fix the infrastructure, you unlock everything built on top of it"
  [vitalize.care/blog/rebuilding-the-foundation](https://vitalize.care/blog/rebuilding-the-foundation).
- **2026-07-01**: Company hiring post on Hacker News states Series A stage, ~50 person team, $10M
  ARR in under 2 years across 30+ hospitals, and a general engineer comp band of $160K-$270K plus
  equity [news.ycombinator.com/item?id=48749843](https://news.ycombinator.com/item?id=48749843).
- **As of 2026-06-03 (live posting publish date)**: the company's own current careers copy states
  "we've raised over $32M from top investors, and even our own customers," a larger, more current
  figure than the $7-7.5M seed total shown on older third-party trackers (Crunchbase/Tracxn), which
  appear not to reflect a later round
  [`api.ashbyhq.com/posting-api/job-board/vitalize`].

No named funding-round announcement (date, lead investor, round size) was found in press; the
$32M+ figure is the company's own unattributed cumulative claim, not a dated press release. Treat
it as directionally true, not press-confirmed.

## 6. Engineering & AI direction

- Stack per the target req itself: React, TypeScript, Postgres, full-stack ownership, "nice to
  have: Effect" [job 10645 body]. Stack per the company's currently-live general engineering req:
  Bun, TypeScript, Effect, React, TanStack Router, Planetscale
  [`api.ashbyhq.com/posting-api/job-board/vitalize`]. Stack per a July 2026 hiring post: "Typescript
  + Postgres + Effect" [news.ycombinator.com/item?id=48749843]. Consistent core (TypeScript, React,
  Effect) across all three sources; the exact database (Postgres vs. Planetscale/MySQL-compatible)
  and runtime (Bun) vary by source/date, so do not over-commit to one specific detail in an
  interview without confirming.
- Company framing of engineering's mandate on the live "Senior Product Engineer" req: "Every
  recommendation Vitalize makes flows through this team... This is where Vitalize evolves from
  software that reports what's happening into software that actively runs hospital operations,"
  i.e. a stated move from decision-support toward autonomous action
  [`api.ashbyhq.com/posting-api/job-board/vitalize`].
- No dedicated public engineering blog was found (only the general company blog at
  `vitalize.care/blog`, which is product/mission-focused, not technical).

## Deployment Platform thesis check (matcher's family D internal-platform read)

The local matcher scored this job 86 on the premise that it is squarely internal-tooling/platform
work matching Santiago's Family D strength. Reading the req's own text confirms that specific
thesis, independent of the location problem above:

- The role exists because "every new customer requires configuration work that is today largely
  manual, bespoke, and engineering-dependent," and the job is to "own the internal platform to
  deploy new health systems to Vitalize": configuration infrastructure, integration tooling that
  removes engineers from the loop, and a self-service configuration portal so hospital IT teams can
  build and validate "digital twins" of their workforce data (org structures, job codes, cost
  centers, scheduling rules) without Vitalize involved [job 10645 body].
- Explicitly framed as an internal-platform-for-operators role, not a customer-surface feature
  role: "You've shipped internal platforms that operators actually depend on... systems that
  replaced the way a team operates," and a stated caution that "the leverage here is real, but it
  lives in deployment metrics and operational efficiency rather than product surfaces" [job 10645
  body]. This is a genuine, well-matched internal-tooling/deployment-enablement role on paper; the
  problem with this req is the location and open-status questions above, not the role's substance.

## 7. Compensation signal vs. the 70K USD floor

- **No salary is disclosed for this specific req** (job 10645 body has no comp line; the current
  live Ashby posting-API record for it does not exist to check).
- Comparable current Vitalize bands (YC job board, pulled today, all San Francisco HQ / Remote
  US scoped, none Mexico/LATAM-scoped): Senior Full-Stack Engineer $180K-$260K plus 0.10%-0.50%
  equity; Deployment Strategist $150K-$240K; Customer Success Manager $180K-$240K; Product Support
  Operations $120K-$250K [ycombinator.com/companies/vitalize/jobs].
- A July 2026 company hiring post lists a general engineer band of $160K-$270K plus equity
  [news.ycombinator.com/item?id=48749843].
- All disclosed Vitalize engineering/product bands sit well above both Santiago's $70K LATAM-scope
  floor and his $100K default US-scope anchor. But every one of these bands is explicitly tied to a
  US-based (SF HQ or US-remote) hire; none confirms what, if anything, Vitalize would offer a
  Mexico-based contractor, and given the hard in-person/hybrid requirement on this specific req,
  comp is moot unless the location question is resolved first.

## 8. Why-fit angles for Santiago

**Lead hook (if location were resolvable):** the req's actual scope, replacing manual,
engineering-dependent customer deployments with self-serve configuration tooling that operators
run without engineering, is close in kind to what Santiago built at Online Basics (an internal
pricing/inventory platform used daily by 4 operators, cutting reporting from hours to minutes) and
at Pragma AI (an internal MCP-based operating platform with 15 agent definitions and 10 reusable
routines that let non-engineers run quoting, diagnostics, and delivery workflows themselves)
[resume/master_resume.yaml]. Both are genuine "built an internal platform operators actually
depend on" stories, which is the exact phrase this req uses to describe what it wants.

Second, weaker hook: Eugenia.ai's on-site B2B deployment work (onboarding HOAs and property
administrators, translating conflicting stakeholder requirements into a working product) maps to
the req's "translate health system context into structured configuration" ask, though at SMB scale
and in a different vertical (PropTech, not healthcare) [resume/master_resume.yaml].

Honest concerns and watch-outs:
- **Location is a hard fail as written**, not a soft concern: the req states "San Francisco HQ
  (in-person) or hybrid" with no remote-from-Mexico option named anywhere across the company's
  postings, and Santiago will not relocate [`config/profile.yaml` location_rule; job 10645 body].
  This alone should override the matcher's 86 score.
- **Open status is unconfirmed**: this exact req does not appear on Vitalize's own live Ashby job
  board as pulled today, only an unrelated "Senior Product Engineer" posting with different scope.
  Applying may be to a stale or already-filled listing.
- No healthcare-vertical experience (hospital operations, clinical workflows, ADT data) anywhere in
  Santiago's background; the req does not require domain experience explicitly, but it would be a
  real gap to name honestly if asked.

## 9. Application-question angles

Given the location and open-status problems above, these angles are provided for completeness and
for reuse if Santiago finds a genuinely remote-eligible or Mexico-scoped Vitalize req later; they
are not a recommendation to apply to job 10645 as currently written.

- **Why this company**: lead with the "no code until we signed multiple health system deals"
  founding discipline (customer development before a line of product code, then a Figma prototype
  turning into a multi-million-dollar deal within weeks) rather than the general healthcare-AI
  pitch. It is a specific, checkable story, not a restatement of the mission.
- **Why you fit**: anchor on the deployment-platform framing itself ("owned the internal platform
  operators depend on") mapped to Online Basics' internal ops platform and Pragma AI's internal MCP
  operating platform, both real examples of building tooling that let non-engineers run a workflow
  themselves. Do not overclaim healthcare-domain knowledge.
- **Anything else**: if asked about location, be direct rather than hopeful: the posting itself
  reads "San Francisco HQ (in-person) or hybrid," Santiago is Mexico City based and not relocating,
  and this should be resolved as a yes/no before either side spends more time on the process.

## 10. Sources

- Internal: `.venv/bin/python -m src.query job 10645` (jobhunt DB), canonical stored job body,
  used for the exact location line, role scope, stack, and benefits.
- [findwork.dev posting](https://findwork.dev/Xq2xbLn/senior-product-engineer-deployment-platform-at-vitalize),
  original source of job 10645; location text, posted-date signal, apparent active status.
- [Vitalize live job-board API](https://api.ashbyhq.com/posting-api/job-board/vitalize) (pulled
  directly, 2026-08-11): authoritative current list of 8 open Vitalize reqs, their workplaceType/
  location fields, full description text for the current "Senior Product Engineer" req (stack,
  values, funding claim, benefits), used to establish that job 10645's exact title/req is not
  currently listed and that current reqs are Hybrid/San Francisco.
- [YC company page: Vitalize](https://www.ycombinator.com/companies/vitalize), meta description
  "Founded in 2023 by Sanketh Andhavarapu and Veeraj Shah, Vitalize has 28 employees based in San
  Francisco," YC Winter 2023 batch, Active status, San Francisco location (primary, authoritative
  source for founding year, founders, headcount as tracked by YC).
- [YC jobs listing for Vitalize](https://www.ycombinator.com/companies/vitalize/jobs), current open
  roles with location and compensation bands, including confirming "Senior Product Engineer,
  Deployment Platform" as a listed title there (San Francisco HQ / Remote (US), 5+ years, no comp
  disclosed) versus other Vitalize reqs' disclosed bands.
- [Hacker News hiring post](https://news.ycombinator.com/item?id=48749843) (2026-07-01, via HN
  Algolia API), company self-description: Series A, ~50 person team, $10M ARR in under 2 years
  across 30+ hospitals, stack (TypeScript + Postgres + Effect), comp band $160K-$270K + equity,
  location "Remote (US, SF in-person preferred)."
- [Substack: Millions in revenue with a 15-person team](https://nextplayso.substack.com/p/millions-in-revenue-with-a-15-person)
  (published 2025-08-10), founding pivot story (mental-health platform to workforce management),
  "no code until we signed multiple health system deals," first pilot and deal timeline, founders
  named (Sanketh Andhavarapu, Veeraj Shah as CEO).
- [Vitalize: Rebuilding the Foundation of the Healthcare Workforce](https://vitalize.care/blog/rebuilding-the-foundation),
  product/mission framing ("fix the infrastructure, unlock everything built on top of it"),
  critique of legacy systems, dates (written 2026-02-23, published 2026-07-23).
- [Vitalize: Our thoughts on building a team](https://vitalize.care/blog/our-thoughts-on-building-a-team),
  hiring philosophy and engineering-culture detail (intelligence over credentials, bias toward
  action, high autonomy).
- [vitalize.care homepage/solutions](https://vitalize.care), product component list, customer
  names and testimonials (MemorialCare, Hendrick Health).
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml, Santiago's verified experience (Online
  Basics, Eugenia.ai, Pragma AI), used for the why-fit section.
- /Users/santiagocoronado/jobhunt/config/profile.yaml, location_rule and comp block, used for the
  location verdict and compensation section.

researched: 2026-08-11

---
Draft prepared for Santiago's review, not a final source of truth. Two things need direct
confirmation before this specific req is pursued further: (1) whether Vitalize would consider a
Mexico-based remote hire for this role at all, since every source found scopes remote eligibility
to the US at most and this req's own text asks for San Francisco in-person or hybrid; (2) whether
job 10645 is still an open, live requisition, since it does not appear on Vitalize's own current
Ashby job-board API under this title.
