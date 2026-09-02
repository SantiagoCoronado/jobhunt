# CoPlane (coplane.com)

STATUS: DRAFT, not yet human-fact-checked by Santiago. Verify before quoting anything in an
outbound email or application, especially the headcount and comp figures below (comp is
industry-benchmark inference, not a CoPlane-specific number).

Researched for job id 13200, "Design/Product Engineer" (posting labeled "Full Stack Engineer"
in its URL slug), https://coplane.com/careers/full-stack-engineer. Applications go to
founders@coplane.com (email application, not an ATS form).

## 1. Snapshot

CoPlane is an AI-native business process orchestration platform for enterprise back-office
operations (finance, accounts payable/receivable, procurement), founded 2024 by ex-Stripe and
ex-Segment engineers. Seed stage: raised $14M in November 2025 (Ribbit Capital led, with Stripe,
Optum Ventures, and Terrain participating). Headquartered in New York City (133 W 25th Street),
roughly 11-50 employees per LinkedIn (about 21 profiles listed there as of this research).
Hiring for this specific role is scoped "NYC or Remote (North or South America)."
[businesswire via WebFetch cache, LinkedIn company page, coplane.com careers]

## 2. Core narrative

CoPlane pitches itself as replacing the reflex to buy another rigid ERP module with software
that is "contoured to [the enterprise's] own shape." Two Stripe alumni (one of whom also built
Segment's product architecture) are selling the discipline they learned building infrastructure
for "essential enterprises" (industrials, healthcare services, late-stage tech, not just VC-lit
tech companies) back-office reliability: durable workflows that resume exactly where they left
off, full audit trails, human override at the edge cases. The engineering team includes Thiago
de Arruda ("tarruda"), the original creator of Neovim, who is the lead author of their open-source
Python workflow framework, Planar. That is an unusually strong open-source pedigree for a
9-figure-ARR-away seed company. [coplane.com/manifesto, coplane.com/perspectives/unveiling-coplane,
PyPI planar package page, news.ycombinator.com job post via Algolia cache]

## 3. Mission & product

- Product: a business process orchestration platform. Enterprises define business objects
  (invoices, POs, vendors) that sync with source ERP/CRM systems; workflows combine
  deterministic business logic, AI agents, and human-in-the-loop task routing; every action is
  logged, versioned, and reversible. Positioned explicitly against building yet another ERP.
  [coplane.com/platform, coplane.com/perspectives/unveiling-coplane]
- Deployment model: customer-owned infrastructure ("bring your own cloud," and per a founder
  tweet "bring your own data cloud (Snowflake), bring your own edge (Cloudflare)"), SOC 2 Type II
  and ISO 27001 compliant, AES-256 at rest / TLS 1.2+ in transit, VPN/VPC peering/EDI/API
  integration options. [coplane.com/platform, x.com/sperand_io/status/1837280472868737463]
- Customers named publicly: OI Infusion Services (healthcare services, quoted CEO Joe Brunink)
  and Georgia Pacific (quoted "Controller's Transformation Leader" Jeff Grice); the seed
  announcement also references Red Ventures as a design partner/customer. Use cases named:
  invoice exception handling and sales order entry, described as freeing "thousands of hours" of
  manual work. [coplane.com/perspectives/announcing-seed-fundraise, businesswire release via
  WebSearch summary]
- Origin: the company started in 2024 pitching narrower "supply chain finance / AP automation"
  infrastructure (per an August 2024 Hacker News hiring post) and has since broadened its pitch to
  the wider "agentic orchestration for the enterprise" framing used today (May 2025 relaunch post).
  That is a real repositioning, not just marketing copy drift; treat "started in accounts payable,
  broadened the scope" as a fair, sourced characterization. [news.ycombinator.com item 41131010 via
  Algolia cache, coplane.com/perspectives/unveiling-coplane dated 2025-05-06]

## 4. Founders

- Chris Sperandio, Co-founder and CEO. Previously Lead Product Architect at Segment and led
  product acceleration at Stripe. [coplane.com/perspectives/unveiling-coplane, LinkedIn
  in/csperandio via WebSearch]
- Victor Mota, Co-founder. Previously Senior Software Engineer at Stripe, with earlier roles at
  Google, Etsy, and Flatiron Health; B.Eng Electrical and Computer Engineering, University of
  Waterloo (2011-2016). Posted on X in August 2024 that he and Chris "left Stripe in the last few
  months to work together" and were building "a small, world class founding engineering team."
  [LinkedIn in/vimota via WebSearch, x.com/vimota/status/1814020485447106847]
- Scott O'Leary, Co-founder. Previously at Segment, Monte Carlo, and OnRamp; BA Economics,
  Bryant University (2011-2014). [LinkedIn scott-o-leary-78000a43 via WebSearch]
- Unverified: I could not independently confirm Scott O'Leary's exact title/function at CoPlane
  beyond "co-founder" (LinkedIn snippet only, not fetched directly due to auth wall).

## 5. Funding, stage, headcount (read this before writing anything)

This is a small, single-round seed company, not a 30-person Series B shop.

- $14M seed round, announced November 25, 2025, led by Ribbit Capital, with Stripe, Optum
  Ventures, and Terrain participating. No earlier public round found (searches turned up no
  pre-seed/angel announcement; the company self-describes as "well-capitalized" as far back as
  2024, which likely means an earlier unannounced or small pre-seed, but I could not verify
  amount or date, mark this unverified). [businesswire release via WebSearch summary, Terrain's
  own X post confirming the round: x.com/terraincap/status/1993412229337854199]
- Headcount: LinkedIn's company page shows an "11-50 employees" size band with about 21 profiles
  actually listed. GitHub org has 20 public followers (a weak secondary signal, not a headcount
  proxy). No official headcount figure published by the company itself. Treat "roughly 15-25
  people" as the working estimate, not a precise number. [LinkedIn company/coplaneinc via
  WebFetch]
- HQ is listed as New York City on LinkedIn (133 W 25th Street), consistent with the job's "NYC
  or Remote" framing and with the sibling Forward Deployed AI Engineer req's "NYC or US Remote"
  scope. [LinkedIn company page, coplane.com/careers]

## 6. Culture & voice

- Manifesto (coplane.com/manifesto) is opinionated and a little combative in tone: rejects
  vendor-template software, insists "every action should be explainable, auditable, and
  reversible," and frames speed of deployment ("weeks, not years") as the core competitive
  lever. [coplane.com/manifesto]
- Public voice on X leans confident/insider, e.g. Chris Sperandio: "you merely adopted the
  enterprise, coplane was born in it." Founders are personally active posters, not just a
  corporate account. [x.com/sperand_io/status/1944889430374015049, x.com/sperand_io/status/1947683894658289748]
- Hiring copy (HN posts, careers page) repeatedly emphasizes small-team, high-craft signaling:
  "ex-founders, open source contributors (authors of neovim and neverthrow), architects of
  petabyte-scale data platforms" and a philosophy of "doing the work then building the function
  around it" (i.e., new hires do real work before org-chart formalization). [HN job post via
  Algolia cache, coplane.com/careers via WebFetch]
- The blog (coplane.com/perspectives) is aimed at finance/ops buyers, not engineers: recurring
  themes are AI adoption pitfalls in finance, ERP/BPO criticism, and customer-facing "how we
  build" pieces. It posts on a roughly weekly-to-biweekly cadence and was still active as of
  July 30, 2026, the most recent entry found. [coplane.com/perspectives, dated post list fetched
  directly]

## 7. Recent news (last ~12 months)

- November 25, 2025: $14M seed round announced (Ribbit Capital lead; Stripe, Optum Ventures,
  Terrain participating). Named customers OI Infusion Services and Georgia Pacific quoted.
  [coplane.com/perspectives/announcing-seed-fundraise, businesswire release, Terrain's X
  confirmation]
- December 2025 through July 2026: steady blog cadence covering AI adoption patterns in finance,
  a "Localsandbox" open-source sandbox release (January 20, 2026), and continued product
  narrative pieces through July 30, 2026 ("When 90% Isn't Good Enough: The Hidden Cost of
  Out-of-the-Box AP Automation"). No further funding, leadership, or acquisition news found in
  this window. [coplane.com/perspectives post list]
- GitHub activity: the `localsandbox` and `par` repos show recent commit/star activity into
  mid-2026 (localsandbox last updated July 8, 2026 per GitHub), and the core `planar` framework
  on PyPI shipped version 0.35.0 on August 4, 2026, one week before this research. Engineering is
  demonstrably active recently, independent of the specific frontend req's staleness.
  [github.com/coplane org page via WebFetch, pypi.org/project/planar]
- A previously-posted "Framework Engineer" role (coplane.com/careers/framework-engineer) now
  404s, i.e. it existed at some point and was taken down, most likely filled. That is a positive
  hiring-velocity data point for a different req, not this one. [WebFetch on that URL, dated
  during this research session]

## 8. Engineering & AI direction

- Backend: Python, built around their own open-source framework, Planar
  (batteries-included framework for durable agentic workflows and business applications),
  itself built on FastAPI and SQLModel with Alembic migrations, requiring Python 3.12+.
  This is a close match to the FastAPI/SQLAlchemy/Alembic/Postgres stack Santiago used to build
  Plutus. [pypi.org/project/planar, github.com/coplane]
- Frontend (the role in question): React, TypeScript, "modern JavaScript ecosystem," WebSockets
  and Server-Sent Events for real-time sync, complex state management, modern responsive CSS,
  design-system/component work, visual workflow-builder UI, dashboards for AI/analytics
  interfaces. [coplane.com/careers/full-stack-engineer, fetched job description]
- AI stack: agent framework supports OpenAI, Anthropic, and Azure OpenAI as pluggable LLM
  providers inside Planar; separate open-source repos for AI-driven computer-use automation
  (`planar-computer-use`, using VNC + OpenAI agents + OS-ATLAS grounding) and an agent sandbox
  (`localsandbox`, runs bash and Python for agent execution). They also maintain a fork of
  Pydantic AI. [pypi.org/project/planar, github.com/coplane/planar-computer-use,
  github.com/coplane/localsandbox]
- Notable engineer: Thiago de Arruda ("tarruda"), the original author of Neovim, is listed as
  the primary developer of the `planar` PyPI package. This corroborates the "authors of neovim"
  claim made in CoPlane's own hiring copy; it is a real, verifiable credential, not marketing
  fluff. [pypi.org/project/planar package metadata]
- Observability: dedicated `monitoring-stack` repo for OpenTelemetry-based application
  monitoring, and DuckDB (WASM fork) present in their org, suggesting embedded analytics/local
  query use. [github.com/coplane]

## 9. Why the req has been open ~16 months

Working theory, moderately confident, not fully provable from public sources: this reads like a
narrow, hard-to-fill specialist search inside an otherwise actively hiring and actively shipping
company, not a signal the company itself is struggling.

Evidence for "narrow search, not company distress":
- The company has hired and closed at least one other engineering req in the same window (the
  Framework Engineer posting is now gone/404), so hiring is happening, just not for this seat.
- Engineering output (blog cadence, GitHub commit activity, a PyPI release one week before this
  research) is current through August 2026, so this is not a company that went quiet.
- They raised a fresh $14M seven months ago (November 2025), so runway is not an obvious
  constraint on making a senior frontend hire.
- The role's own language ("architect the UI... for both technical and non-technical users,"
  requiring specifically React/TypeScript expertise plus product/UX judgment plus workflow-builder
  domain experience) is a narrow, senior, full-stack-leaning-frontend combination that is
  genuinely hard to source, especially at a company this size where this hire effectively owns
  the entire frontend surface alone.

Evidence that should temper optimism:
- 16 months open for one seat at a ~15-25 person company is long by any normal startup hiring
  cadence; either the bar is unusually high, the role's scope has been redefined more than once
  (the URL slug says "full-stack-engineer" while the live title is "Design/Product Engineer,"
  suggesting the req has been edited/re-scoped since its original posting), or it is a lower
  organizational priority than sales hiring (the Engagement Lead and Forward Deployed AI Engineer
  reqs read as more central to current revenue motion).
- I found no public statement from CoPlane about hiring difficulty, timeline, or why this role
  specifically remains open; everything above is inference from indirect signals, not a
  first-party admission. Flag this honestly in any outreach rather than assuming urgency.
[coplane.com/careers/full-stack-engineer URL vs. live title, coplane.com/careers/framework-engineer
404, coplane.com/careers role list, github.com/coplane commit dates, pypi.org/project/planar
release date]

## 10. Compensation

CoPlane's posting states "competitive compensation and founding team equity" with no number
disclosed. [coplane.com/careers/full-stack-engineer]

No CoPlane-specific salary data (Glassdoor, Levels.fyi, H-1B filings) was found in this research;
this is an unverified gap, not a number to quote. What follows is general market context only,
not a CoPlane figure:

- General NYC "product engineer" market data (Indeed, June 2026 data cited via Wellfound/Indeed
  aggregation) puts the broad market range around $96k-$224k with an average near $158k, but this
  spans all company stages and is not seed-specific. [Indeed/Wellfound salary pages via WebSearch
  summary, unverified primary source, treat as directional only]
- General seed-stage benchmarks found via secondary aggregators suggest seed-stage engineers
  commonly land in the $110k-$190k base range depending on level, with 0.1%-1.0% equity for
  senior hires. [topstartups.io and Cadence blog aggregator summaries via WebSearch, unverified
  primary methodology, directional only]

Given the profile's floor of $70,000 USD/year for LATAM-scoped remote roles and target of
$100,000, this role is plausibly within range for the ask, but there is no company-specific
confirmation. Recommend Santiago state his number early and clearly in the email (per the
profile's comp rule: anchor near or above the likely midpoint) rather than waiting for CoPlane to
name a figure, since informal seed-stage NYC startups often do not have a fixed band and a
LATAM-remote contractor arrangement, per the profile's own contractor_note, should be priced
above the equivalent employee salary, not below it.

## 11. Why-fit angles for Santiago

Lead hook: CoPlane is explicitly not building "another ERP." It is building durable, auditable
workflow orchestration for real operational back offices, exactly the kind of internal tooling
Santiago has built firsthand, not just adjacent to. At Online Basics he built the company's
internal operations platform (React + AWS + SQL + Python ETL) that ran pricing, inventory, and
alerting for a 7-person team scaling to $8M revenue; at Pragma AI he built an MCP-based internal
brain and 15 agent definitions that operators use as day-to-day tools. That is the same shape of
problem CoPlane sells to enterprises: process orchestration that real operators depend on daily,
not a demo.

Supporting angles:
- Stack match: CoPlane's own framework, Planar, is built on FastAPI and SQLModel/Alembic on
  Postgres, the same core backend stack Santiago used to build Plutus (FastAPI, SQLAlchemy 2,
  Alembic, Postgres/TimescaleDB). He can speak to that stack concretely, not just list it as a
  keyword.
- Frontend depth for the specific req: the role wants React/TypeScript expertise, WebSockets/SSE
  real-time sync, and workflow-builder/visual-programming UI. Santiago shipped exactly that shape
  of UI at Plutus (WebSocket quote feed, hand-rolled SSE client, a visual screener rule builder,
  React Flow node-graph canvas at Hydrel) and at Kairos (React 19, complex state, drag-and-drop
  calendar UI). This is a strong, specific match, not a generic "I know React" claim.
- AI agent fluency: CoPlane's Planar framework has a first-class agent-step layer (OpenAI,
  Anthropic providers) and MCP-adjacent tooling ambitions; Santiago has shipped MCP servers and
  Claude Agent SDK integrations on both Plutus and Kairos, so he can talk about agent-in-the-loop
  UI design from direct experience, not theory.
- Founder credibility: he built and sold Eugenia.ai and ran an $8M e-commerce operation as
  founder/CEO. CoPlane is a founder-led company that explicitly wants people who will "do the
  work then build the function around it." That founder instinct (own ambiguity, ship without a
  fully-formed team around you) is a real, honest match, not a resume-padding line.

Honest concerns and watch-outs:
- Work authorization: the posting states no visa sponsorship. This is a non-issue for Santiago
  specifically because he is Mexican and plans to work from Mexico under the role's own "Remote
  (North or South America)" scope, not because the company will sponsor anything. Do not conflate
  the two in the email; be precise that he needs no sponsorship because he is not relocating.
- The req has been open roughly 16 months (see section 9). That is a real yellow flag worth a
  brief, low-key acknowledgment or at minimum awareness going in; it should not be treated as "an
  easy, low-competition opening."
- No public comp band. He will likely need to name his number first (per the profile's comp
  rule), which is a mild negotiating disadvantage in an email application versus an ATS form with
  a posted range.
- Very small team (~15-25 people). This is a single-owner frontend seat: high autonomy, but also
  no existing frontend team or established patterns to lean on, and CoPlane's blog content skews
  heavily finance/ops-buyer-facing rather than engineering-facing, so there is less public
  evidence of engineering process/culture than at a company with an active eng blog.

## 12. Application-question angles (for founders@coplane.com)

This is a direct email to the founders, not an ATS form, so the opening line matters more than
usual: lead with the specific internal-tooling/orchestration parallel (section 11's lead hook),
not a generic "I'm excited about AI." Do not attempt to checklist mission, culture, news, and
engineering in one email; pick the one or two hooks below and go deep.

- Why this company: lead with the "not another ERP" framing and the fact that Santiago has
  personally built the kind of operator-facing internal tooling CoPlane sells to enterprises
  (Online Basics's internal ops platform, Pragma's MCP-based operator brain). Frame it as
  recognition, not admiration: he has stood on the other side of this exact problem as the
  operator who needed the tool, then as the person who built it.
- Why you fit: anchor on the frontend-plus-agent combination the req explicitly asks for
  (React/TypeScript UI for AI-driven workflows, real-time sync, workflow-builder UX), backed by
  concrete, named work (Plutus's WebSocket/SSE real-time layer and visual rule builder, the MCP
  and Claude Agent SDK integrations at Kairos and Pragma). Avoid restating the full resume;
  choose the two or three most load-bearing specifics.
- Anything else: this is the natural place for the founder-credibility angle (built and sold
  Eugenia.ai, scaled Online Basics to $8M as a 7-person team) framed around comfort with
  ambiguity and doing the work before the org chart exists, since that is language CoPlane uses
  about itself. It is also a reasonable place to state his rate expectation plainly, since there
  is no posted band and this is an email, not a form with a required field forcing the issue
  later.
- Keep the email itself short. This is a founder inbox at a roughly 20-person company; a long,
  multi-section email will read as generic-blast rather than targeted.

## 13. Sources

researched: 2026-08-11

- https://coplane.com/careers (roles list, hiring philosophy language) [WebFetch]
- https://coplane.com/careers/full-stack-engineer (the specific req: responsibilities,
  requirements, comp language, how to apply) [WebFetch]
- https://coplane.com/manifesto (values, tone) [WebFetch]
- https://coplane.com/platform (product features, deployment model, security posture) [WebFetch]
- https://coplane.com/perspectives (full dated blog post list, posting cadence) [WebFetch]
- https://coplane.com/perspectives/unveiling-coplane (founding narrative, product description,
  dated 2025-05-06) [WebFetch]
- https://coplane.com/perspectives/announcing-seed-fundraise (funding amount, investors, named
  customers/quotes, dated 2025-11-25) [WebFetch]
- https://www.businesswire.com/news/home/20251125900638/en/CoPlane-Announces-$14M-Seed-Round-to-Rebuild-the-Back-Office-for-Essential-Enterprises
  (funding press release, via WebSearch summary; direct WebFetch failed with DNS error) [WebSearch]
- https://finance.yahoo.com/news/coplane-announces-14m-seed-round-150000010.html (syndicated
  funding release; direct WebFetch returned 404 at time of research) [WebSearch]
- https://pulse2.com/coplane-14-million-seed-funding/ (funding recap: amount, investors, founder
  backgrounds, customers) [WebFetch]
- https://x.com/terraincap/status/1993412229337854199 (Terrain confirming lead investor
  participation in the seed round) [WebSearch]
- https://x.com/vimota/status/1814020485447106847 (Victor Mota, August 2024, founding story: left
  Stripe with Chris, building a small founding engineering team) [WebSearch]
- https://x.com/sperand_io/status/1837280472868737463 (Chris Sperandio on BYOC/BYO Data Cloud
  architecture) [WebSearch]
- https://x.com/sperand_io/status/1944889430374015049 and
  https://x.com/sperand_io/status/1947683894658289748 (founder public voice/tone) [WebSearch]
- https://www.linkedin.com/company/coplaneinc (headcount range, HQ address, company description)
  [WebFetch]
- https://www.linkedin.com/in/csperandio/ , https://www.linkedin.com/in/vimota/ ,
  https://www.linkedin.com/in/scott-o-leary-78000a43/ (founder backgrounds; snippets via
  WebSearch, not directly fetched due to LinkedIn auth wall) [WebSearch]
- https://news.ycombinator.com/item?id=41131010 (August 2024 hiring post: original narrower
  "supply chain finance / AP automation" pitch, "early, well-capitalized," remote US/Canada
  timezones; fetched via Hacker News Algolia API mirror since news.ycombinator.com itself was
  unreachable in this environment) [WebFetch via hn.algolia.com]
- https://news.ycombinator.com/item?id=45146327 (later hiring post: "scale intelligence not
  headcount" framing, team described as including open-source authors of neovim and neverthrow;
  fetched via Hacker News Algolia API mirror) [WebFetch via hn.algolia.com]
- https://github.com/coplane (org repo list, languages, activity dates) [WebFetch]
- https://github.com/coplane/planar-computer-use ,
  https://github.com/coplane/localsandbox , https://github.com/coplane/par (individual repo
  descriptions) [WebSearch/WebFetch]
- https://pypi.org/project/planar/ (Planar framework description, FastAPI/SQLModel/Alembic
  stack, Python 3.12+, current version 0.35.0 released 2026-08-04, primary developer listed as
  "tarruda") [WebFetch]
- https://www.coplane.com/careers/framework-engineer (checked: returns 404, confirming this req
  was posted at some point and has since been removed) [WebFetch]
- config/profile.yaml and resume/master_resume.yaml (Santiago's comp floor/target, location rule,
  stack, and prior work used for the fit-angle section) [Read]

Not found / explicitly unverified:
- No public statement from CoPlane on why the Design/Product Engineer req specifically has stayed
  open ~16 months; section 9's explanation is inference from indirect signals, not a first-party
  claim.
- No CoPlane-specific salary, band, or comp philosophy beyond "competitive compensation and
  founding team equity" was found anywhere public (job post, press, Glassdoor, Levels.fyi). The
  compensation figures in section 10 are general market benchmarks, not CoPlane numbers.
- Scott O'Leary's precise function/title at CoPlane beyond "co-founder" was not confirmed beyond
  a LinkedIn search snippet.
- Any pre-seed or earlier funding round (the "well-capitalized" framing used as early as 2024
  suggests one existed) was not found or verified; do not claim an amount or date.
- CoPlane's public footprint outside its own site, GitHub, X, and funding-press coverage is thin.
  There is no independent engineering blog separate from the finance/ops-facing "Perspectives"
  section, no Glassdoor reviews found, and no third-party engineering culture writeups. This
  itself is a finding: this is a small, seed-stage company whose public presence is almost
  entirely first-party (their own site and founders' own social accounts) plus funding-press
  coverage, not a company with an established independent reputation to research against.
