# Hightouch

Reusable dossier for Santiago Coronado, refreshed for job id 1911 ("Deployment Architect", listed
location "Remote (North America)", posted salary $140,000-$180,000 USD, canonical posting
https://job-boards.greenhouse.io/hightouch/jobs/5762547004). Originally drafted for job id 1947
("Software Engineer, AI Agents"); company-level sections below are shared across all Hightouch
roles, role-specific sections are called out. Draft for review, not a final source of truth.

## Location eligibility verdict: UNVERIFIED, leaning NOT ELIGIBLE (read first)

**No public source states outright that Hightouch excludes Mexico-based candidates from this
req**, so the honest label is UNVERIFIED rather than a confirmed NOT ELIGIBLE. But the weight of
evidence leans against Mexico eligibility, not toward it:

- The posting's own structured location field (pulled directly from Hightouch's Greenhouse job
  board API, not just the human-facing page) is exactly `"location": {"name": "Remote (North
  America)"}`, with associated Greenhouse offices listed as "New York Office," "San Francisco
  Office," and a generic "Remote" (no location string attached)
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004`].
- Hightouch's own live job board (65 open reqs pulled 2026-07-28) shows the company is precise
  about country/region scoping when it intends to hire outside the US: it uses labels like
  `Remote (India)` (Technical Account Manager), `Paris` and `Europe - Austria/Switzerland/
  Netherlands/UKI` (multiple EMEA reqs), and `Australia/Singapore` (Enterprise AE, APAC Japan).
  Across the entire list, **"Mexico" and "LATAM" never appear as a location label on any req**,
  while "Remote (North America)" appears on roughly 25 reqs including this one
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs`, full list pulled 2026-07-28].
- The application form for this req (and, identically, for the "Software Engineer, AI Agents" req
  Santiago already applied to) requires two gating questions before submission: "Are you
  authorized to work for any employer in the U.S?" and "Will you now or in the future require
  sponsorship for employment visa status?" (both `required: true`)
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004?questions=true`]. This is
  boilerplate across their North-America-scoped reqs, so it does not by itself rule out a
  Canada-based hire, but it is oriented around US work authorization, not a Mexico or general-LATAM
  pathway.
- The posting closes with an E-Verify statement: "Hightouch participates in E-Verify. After you
  join the team, we'll verify your eligibility to work in the U.S. by submitting information from
  your Form I-9 to the Social Security Administration..." [posting text, same source as above].
  E-Verify/Form I-9 only applies to actual US employees, so this confirms a US employment pathway
  exists but says nothing directly about Canada or Mexico.
- One piece of circumstantial evidence that "North America" likely means US + Canada in practice:
  a public LinkedIn profile shows a Hightouch software engineer based in Canada (education at
  McMaster University) [LinkedIn search result, `linkedin.com/in/kogand2/`, low confidence, single
  data point]. No equivalent public evidence of a Mexico-based Hightouch employee was found in this
  research pass.
- Hightouch's careers page states only "We're a remote-friendly company with 5+ offices across San
  Francisco, NYC, London, and more" with no company-wide statement of which countries are eligible
  for remote hiring; it defers entirely to each individual job posting's location field
  [hightouch.com/careers].

**Posting is confirmed live**: Greenhouse API returns valid, current data (`first_published:
2026-01-12`, `updated_at: 2026-07-10`), and it remains listed on Hightouch's own live job board
pulled 2026-07-28
[`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004`,
`boards-api.greenhouse.io/v1/boards/hightouch/jobs`]. The jobhunt DB also shows `last_seen:
2026-07-28`, consistent with an active listing.

**Recommendation**: do not assume Mexico eligibility here. If Santiago wants to pursue this role,
the location question should be asked directly and plainly in the recruiter screen or cover note,
rather than assumed from the "North America" label, since Hightouch's own hiring pattern shows they
label requisitions precisely when a country outside the US/Canada core is genuinely in scope, and
Mexico has never appeared in that pattern.

## Concurrent-application flag (read before applying)

Santiago already has two open Hightouch applications: "Software Engineer, AI Agents" (job id 1947,
applied 2026-07-14) and "Staff Engineer, AI Productivity" (job id unlisted here but same company,
applied 2026-07-14). A third simultaneous application is a real judgment call, not a formality:

- The "Software Engineer, AI Agents" posting itself states, in its own text: "We have limited
  inbound applications to one application per candidate. You will be auto-rejected if you apply to
  multiple roles. Please only apply to the position you are most qualified for."
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5542602004`]. Santiago already applied to a
  second role (Staff Engineer, AI Productivity) on the same day, which on a literal reading of that
  clause already put both applications at risk of auto-rejection.
- Neither the "Staff Engineer, AI Productivity" posting nor this "Deployment Architect" posting
  restates that one-application clause anywhere in their own text
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/6020404004`;
  `boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004`]. Whether the policy is enforced
  by an ATS-level dedup rule (checking any Hightouch req) or only applies within the specific req
  that states it is unverified; this dossier cannot confirm which.
- Deployment Architect is also a materially different function (customer-facing deployment and
  enablement, reporting through Customer Success, not Engineering) from the two engineering reqs
  already applied to, which is a legitimate reason a recruiter might view a third application more
  charitably than three interchangeable engineering applications. That said, given the explicit
  auto-reject language already found on one of the two live applications, adding a third
  application before hearing back on the first two carries real risk of tripping a
  dedup/auto-reject rule across all three. This is Santiago's call to make with that risk stated
  plainly, not a decision this dossier makes for him.

## 1. Snapshot

Hightouch is a San Francisco based Composable CDP and Agentic Marketing Platform: it activates
customer data directly from the warehouse (Snowflake, BigQuery, Redshift, Databricks) instead of
copying it into a walled garden, and now layers AI agents on top to research, decide, and execute
marketing campaigns. Founded in 2019 (YC S19) by ex-Segment engineers Tejas Manohar, Josh Curl,
and Kashish Gupta. Series D, raised $150M in April 2026 led by Goldman Sachs Alternatives and Bain
Capital Ventures at a $2.75B valuation, $322M total raised across six rounds. Crossed $100M ARR in
2025 with over 100% revenue growth in each of the past two years. Roughly 400 to 580 employees as
of mid-2026 depending on the tracker, remote-friendly with 5+ offices (San Francisco, NYC, London
and more). Named a Leader in the Gartner Magic Quadrant for Customer Data Platforms (first-time
inclusion, announced January 2026), and named 2026 Snowflake Marketers and Advertisers Product
Partner of the Year (June 2026).
[Adweek funding recap](https://www.adweek.com/dealroom/hightouch-raised-322-million-across-six-rounds-heres-how-the-company-skyrocketed-to-a-275-billion-valuation/),
[PYMNTS Series D](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/),
[YC company page](https://www.ycombinator.com/companies/hightouch),
[Hightouch Gartner page](https://hightouch.com/gartner),
[Deployment Architect posting](https://job-boards.greenhouse.io/hightouch/jobs/5762547004).

## 2. Core narrative

Three Segment engineers who watched companies abandon their SaaS-siloed customer data for
Snowflake/BigQuery/Redshift built the tool to activate that centralized warehouse data instead of
re-copying it. That single architectural bet (warehouse-native, no data replication) took the
company through three re-brandings in six years: reverse ETL (2020) to Composable CDP (2022) to
Agentic Marketing Platform (2025) to "Agentic CDP" (June 2026), each time keeping the same
underlying insight (query the warehouse, act on the result) while pushing further up the stack
from moving data to deciding and acting on it with AI agents. The company's own framing: "the CDP
executes ideas, but it has never had one of its own."
[Contrary/Unusual product-market-fit history](https://www.unusual.vc/hightouchs-product-market-fit-journey/),
[Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp).

## 3. Mission & product

- Product suite: Composable CDP (warehouse-native identity resolution and audience building),
  Reverse ETL (sync warehouse data to 200+ SaaS destinations), AI Decisioning (reinforcement
  learning/contextual bandits that pick the best message, channel, timing, and frequency per
  customer, including whether to send at all), Hightouch Agents (AI agents that research
  opportunities, answer analytics questions, and draft/execute campaigns), plus Ad Studio,
  Lifecycle Studio, Content Assembly, Customer Studio, and Intelligence modules under the
  "Agentic Marketing Platform" (AMP) umbrella.
  [Hightouch homepage](https://hightouch.com/),
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning).
- Business model: enterprise SaaS, warehouse-native (customer's own Snowflake/BigQuery/Databricks
  stays the source of truth, no forced data copy), sold to marketing and data teams jointly.
  [Hightouch Gartner page](https://hightouch.com/gartner).
- Customers: enterprise brands including Domino's, Spotify, Aritzia, Cars.com, Ramp, PetSmart,
  Warner Music Group, Grammarly, DoorDash, DraftKings, WHOOP, Fundrise, and Accor Hotels, per the
  company's own materials and job postings. 1,000+ companies use the platform per Hightouch's site.
  [Deployment Architect posting](https://job-boards.greenhouse.io/hightouch/jobs/5762547004),
  [Hightouch homepage](https://hightouch.com/),
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning).
- Documented results: WHOOP +22% loyalty offer activation, PetSmart +10% cross-sell conversion and
  +52% new customer acquisition, Fundrise 4x increase in investments, Otrium -70% campaign launch
  time, Warner Music Group 1,000+ audiences managed and +200% engagement.
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning),
  [Hightouch homepage](https://hightouch.com/).

## 4. Culture & voice

- Seven stated values: Forever Hungry (ambitious, celebrate wins but keep pushing), Kindness
  ("people who aren't kind aren't tolerated"), Efficient Execution (bias to speed, "most decisions
  are two-way doors"), Compassion, Impact Driven, Raising the Bar (talent and "slope over
  y-intercept" over credentials), Humility.
  [Hightouch careers page](https://hightouch.com/careers).
- Remote-friendly with 5+ physical offices (San Francisco, NYC, London and more); office perks
  include free weekday lunches and a $150/month commuter benefit; benefits include 100%
  employee/80% dependent health premiums, $100/month wellness stipend, flexible PTO, and 16/12
  weeks parental leave.
  [Hightouch careers page](https://hightouch.com/careers).
- Design/product philosophy leans on "craft over shortcuts": a 2025 product redesign write-up
  emphasizes sweating details, "hundreds of design explorations," and building products people
  "actually love to use," plus an explicit shift toward serving marketer (non-technical) users as
  the fastest-growing segment, not just data engineers.
  [Hightouch redesign 2025 blog post](https://hightouch.com/blog/hightouch-redesign-2025).
- No programming interview on at least some engineering reqs: postings state directly they do not
  run coding interviews because they consider them "low signal to noise," instead weighting
  product sense, system design, and values fit. This is an engineering-hiring signal specifically;
  the Deployment Architect posting itself does not describe an interview loop.
  [Software Engineer, AI Agents posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).

## 5. Recent news (last ~12 months)

- **June 10, 2025**: Hightouch named 2025 Databricks Retail and Consumer Goods ISV Partner of the
  Year at the Data + AI Summit.
  [Businesswire](https://www.businesswire.com/news/home/20250610695735/en/Hightouch-Awarded-2025-Databricks-Retail-and-Consumer-Goods-ISV-Partner-of-the-Year-at-Data-AI-Summit).
- **October 8, 2025**: Launched Smart Suppression inside AI Decisioning, predicting per-message
  incremental lift so marketers can suppress low-value or relationship-damaging sends instead of
  relying on static frequency caps.
  [Businesswire](https://www.businesswire.com/news/home/20251008017466/en/Hightouch-Launches-Smart-Suppression-to-Protect-Brand-Relationships-Without-Sacrificing-Conversions).
- **January 26/29, 2026**: Named a Leader (first-time inclusion) in the Gartner Magic Quadrant for
  Customer Data Platforms, credited to early leadership in warehouse-native/composable
  architecture.
  [Hightouch Gartner page](https://hightouch.com/gartner),
  [Businesswire](https://www.businesswire.com/news/home/20260129112125/en/Hightouch-Named-a-Leader-in-the-2025-Gartner-Magic-Quadrant-for-Customer-Data-Platforms).
- **April 27-29, 2026**: Raised $150M Series D led by Goldman Sachs Alternatives and Bain Capital
  Ventures at a $2.75B valuation (Iconiq, Sapphire, Amplify, YC, and The Trade Desk's TD7 also
  participated); over 100% revenue growth each of the past two years.
  [Businesswire](https://www.businesswire.com/news/home/20260427054567/en/Hightouch-Raises-$150-Million-to-Reinvent-How-Marketing-Works-Using-AI),
  [PYMNTS](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/).
- **Around the Series D**: launched "Hightouch Agents," pre-trained AI agents that answer
  marketing/analytics questions directly from warehouse data, surface audience/opportunity
  insights, and can execute actions like A/B tests and budget changes, explicitly compared by CMO
  Brian Kotlyar to how coding agents changed software engineering.
  [CMS Critic](https://cmscritic.com/hightouch-launches-high-performance-agents-to-help-marketers-move-10x-faster).
- **June 2, 2026**: Named 2026 Marketers and Advertisers Snowflake Product Partner of the Year at
  Snowflake Summit 26.
  [Businesswire](https://www.businesswire.com/news/home/20260602248845/en/Hightouch-Named-2026-Marketers-and-Advertisers-Snowflake-Product-Partner-of-the-Year).
- **June 15, 2026**: Published "The Agentic CDP," repositioning the platform around three pillars:
  a long-running agent harness that investigates opportunities over hours without context loss, a
  composable context layer that reads data in place (warehouses, DAMs, Figma, Looker) via open
  standards including MCP rather than centralizing copies, and forward-deployed teams embedded
  with customers to build agent skills and guardrails. Landed the same week as competing "agentic
  CDP" moves from Databricks and a BlueConic acquisition, an active category fight right now.
  [Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp).
- **June 22, 2026**: Recognized as a Leader in Snowflake's "Modern Marketing Data Stack" report,
  Activation and Delivery category (announced around Cannes Lions 2026).
  [Businesswire](https://www.businesswire.com/news/home/20260622288045/en/Hightouch-Recognized-as-a-Leader-in-Snowflakes-Modern-Marketing-Data-Stack-Report-for-Activation-and-Delivery).

## 6. Engineering & AI direction

- Core stack (from current and recent Hightouch job postings, primary source): TypeScript across
  frontend and backend, React on the frontend, some Go in backend services, GraphQL, queueing/
  streaming infra referencing Kafka and Kinesis for distributed data-sync workloads.
  [Full Stack Product Engineer posting](https://job-boards.greenhouse.io/hightouch/jobs/4620430004),
  [Staff Engineer, AI Productivity posting](https://job-boards.greenhouse.io/hightouch/jobs/6020404004).
- AI Decisioning's technical core is a documented, four-part public series: reinforcement learning
  as the foundation, multi-armed bandits for the explore/exploit tradeoff, and contextual bandits
  to personalize the decision using each customer's live and historical data, all connected back
  to the warehouse rather than a duplicated data store. Strong prep material before interviews.
  [Under the hood of AI Decisioning, part one](https://hightouch.com/blog/the-personalization-gap),
  [part two: reinforcement learning](https://hightouch.com/blog/rl-for-marketers),
  [part three: multi-armed bandits](https://hightouch.com/blog/mabs-for-marketers),
  [part four: contextual bandits](https://hightouch.com/blog/contextual-bandits-for-marketers).
- Org signal: Hightouch's live job board (65 open reqs, pulled 2026-07-28) shows a large cluster of
  AI-agent-adjacent and forward-deployed roles hiring in parallel, including Engineering Manager,
  Agents; Staff Engineer, AI Productivity (internal AI-coding-agent tooling); Forward Deployed
  Analytics Engineer; Forward Deployed Marketing Data Scientist; Forward Deployed Creative
  Designer/Strategist; AI Strategy Consultant; Head of Machine Learning; and this Deployment
  Architect req sitting alongside Technical Account Manager and Solutions Engineer roles in
  Customer Success. This is a company simultaneously building the agent product, its own internal
  AI-tooling stack, and a forward-deployed/deployment motion to make the product work for real
  enterprise customers.
  [Full live job list](https://boards-api.greenhouse.io/v1/boards/hightouch/jobs).
- The internal-AI-tooling role itself (Staff Engineer, AI Productivity) is a strong signal of
  engineering culture: Hightouch is building its own `agents.md`-based repo-wide agent guidance,
  MCP server integrations connecting internal AI coding agents to CircleCI/Slack/Datadog/GitHub,
  and cloud dev environments where agents run autonomously, framed as a deliberate investment
  ("companies that invest in making agents truly productive... will have a significant advantage").
  [Staff Engineer, AI Productivity posting](https://job-boards.greenhouse.io/hightouch/jobs/6020404004).
- This Deployment Architect role's own scope (primary source, JD): own the full deployment and
  enablement lifecycle for Hightouch's customers, working alongside an account team; translate
  customer requirements into implementation plans; design and standardize deployment frameworks
  that scale across customer segments; run technical discovery/implementation workshops with
  customer data-engineering teams and business stakeholders; maintain deployment documentation
  (integration specs, data models, best practices). Wants 5-10 years in technical implementation,
  solutions architecture, or similar with enterprise software; data warehouse/ETL/martech
  experience called out as "a plus," not a hard requirement. Salary $140,000-$180,000 USD,
  explicitly "location independent in accordance with our remote-first policy" (see location
  verdict above for what "remote" is actually scoped to here).
  [Deployment Architect posting](https://job-boards.greenhouse.io/hightouch/jobs/5762547004).
- Interview process for engineering-track roles is notably non-standard, no coding interview:
  Recruiter screen, System Design Screen (design a data processing feature end to end), Hiring
  Manager interview on values/operating fit, and (for AI-facing roles) an AI Skills interview plus
  a longer System Design interview to architect a system at a conceptual level. The Deployment
  Architect posting does not itself list an interview loop, so this should not be assumed to carry
  over unmodified; confirm with the recruiter.
  [Staff Engineer, AI Productivity posting](https://job-boards.greenhouse.io/hightouch/jobs/6020404004),
  [Deployment Architect posting](https://job-boards.greenhouse.io/hightouch/jobs/5762547004).

## 7. Why-fit angles for Santiago (Deployment Architect, job id 1911)

Lead hook: **the role's actual job, "own the full deployment and enablement lifecycle, translate
complex customer requirements into actionable implementation plans, and standardize that process
so it scales across the customer base," is functionally the job Santiago already did at Eugenia.ai
and now does inside Pragma AI.** At Eugenia.ai he ran on-site B2B deployments onboarding HOAs and
property administrators, translating conflicting stakeholder requirements into a working, scoped
product. At Pragma AI he owns client-facing AI deployments end to end: diagnosing a client's
operational bottleneck, then shipping and enabling the client on a scoped system (a RAG "company
brain," agent workflows for quoting, reporting, onboarding, collections), the same "technical
discovery to production implementation, with the client as the end user" motion this req describes
[resume/master_resume.yaml]. This matches profile.yaml's own Family B target titles (Deployment
Strategist, Solutions Architect/Engineer) directly, and Santiago has separately flagged this exact
kind of role (deployment/enablement, client-facing, technical) as one of his ideal target shapes
[config/profile.yaml].

Second hook: **the Agentic CDP repositioning explicitly names "forward-deployed teams embedded with
customers to build agent skills and guardrails" as one of its three architectural pillars**, which
gives this specific req a live, current company narrative to anchor on rather than treating
deployment/enablement as a generic back-office function
[hightouch.com/blog/the-agentic-cdp]. Naming that pillar shows the company is being tracked in real
time, not just reading a generic "About" page.

Concrete transferable evidence:
- Founder-level ownership of full client lifecycles (raised capital, ran a 7-person team, owned
  P&L at Online Basics; bootstrapped and exited Eugenia.ai) is direct evidence of end-to-end
  deployment ownership and the "translate ambiguous requirements into a scoped implementation plan"
  skill this req asks for [resume/master_resume.yaml].
- Built and operated an authenticated MCP "brain" service and internal agent workflows for Pragma's
  own operations, demonstrating comfort with the technical integration/data-model side of a
  deployment (APIs, data pipelines, documentation), though this is at founder/SMB scale, not
  enterprise data-warehouse scale [resume/master_resume.yaml].
- Online Basics: built a cloud microservices architecture orchestrating 10+ third-party APIs to
  process 100K+ daily data points with hourly sync, real ETL-adjacent, integration-and-pipeline
  work that is close in kind (not scale) to the "data warehouses, ETL processes" experience this
  posting calls "a plus" [resume/master_resume.yaml].

Honest gaps and watch-outs:
- No enterprise data-warehouse or CDP-category domain experience specifically (Snowflake/BigQuery/
  Redshift/Databricks at enterprise scale, martech ecosystem, marketing-team stakeholders). His
  ETL-adjacent and client-integration experience is real but at founder/SMB scale and in different
  verticals (PropTech, e-commerce ops, personal finance); this is a legitimate gap to name directly,
  not paper over.
- Scale mismatch: this req is scoped to Hightouch's Mid-Market and Enterprise customers at a
  $100M-ARR, 400-580-employee company with named Fortune-500-adjacent clients (Spotify, Domino's,
  Ramp), versus Santiago's own founder-scale deployments (lean teams, SMB clients). Frame as "owned
  deployments end to end at a smaller scale, ready to apply the same pattern at enterprise scale,"
  not as equivalent enterprise experience.
- Location is genuinely unresolved, not a formality: see the verdict above. This should be raised
  directly and plainly, not assumed, before investing further in this specific req.
- Third concurrent Hightouch application: see the Concurrent-application flag above. A real
  literal-reading risk that a third application could trigger an auto-reject rule that may already
  apply to the two engineering applications in flight.

## 8. Application-question angles (Deployment Architect framing)

- **Why this company**: do not lead with "CDP" or "reverse ETL," those are means, not the story.
  Lead with the founder narrative: three Segment engineers who watched the industry move its
  source of truth to the warehouse, built the tool to activate it there instead of copying it
  again, and have re-invented that same bet three times (reverse ETL, Composable CDP, AI
  Decisioning, Agentic CDP) as the ceiling of "warehouse-native" kept rising. For this specific
  role, connect it to the June 2026 Agentic CDP repositioning's "forward-deployed teams" pillar,
  since deployment and enablement is explicitly part of how the company says it will make that bet
  work for real customers, not a side function.
- **Why you fit**: anchor on the actual job description language ("own the full deployment and
  enablement lifecycle," "translate complex customer requirements into actionable implementation
  plans," "standardize and automate implementation processes to scale") mapped to concrete,
  already-run deployments: Eugenia.ai's on-site HOA/property-administrator onboarding and Pragma
  AI's client AI deployments, both requiring the same discovery-to-implementation-to-scale pattern
  at smaller scale. Avoid overclaiming enterprise data-warehouse depth he does not have; name the
  ETL-adjacent integration work from Online Basics as the closest technical analog instead.
- **Anything else**: if location comes up, be upfront and factual: this posting reads "Remote
  (North America)" on Hightouch's own structured job data, with no Mexico or LATAM precedent found
  anywhere on their live job board, so it should not be assumed this covers a Mexico-based hire;
  ask directly. If asked about other applications, be straightforward that he applied to two
  Hightouch engineering roles the same week and is now looking at this one because it is a
  genuinely different function (deployment/enablement vs. engineering), not a volume play; do not
  hide or minimize this if asked, since the postings themselves flag multiple applications as a
  live concern.

## 9. Sources

- [Deployment Architect posting (human page)](https://job-boards.greenhouse.io/hightouch/jobs/5762547004)
  and structured API record
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004`] and questions
  [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5762547004?questions=true`]: full JD text,
  location field, salary band, E-Verify clause, required application questions, publish/update
  timestamps (used for the location verdict and role-scope sections).
- [Full live Hightouch job board](https://boards-api.greenhouse.io/v1/boards/hightouch/jobs) (65
  reqs, pulled 2026-07-28): used to establish Hightouch's country/region-labeling pattern
  (`Remote (India)`, `Paris`, `Europe - ...`, `Australia/Singapore` versus no Mexico/LATAM label
  anywhere), and the cluster of AI-agent-adjacent and forward-deployed roles hiring in parallel.
- [Software Engineer, AI Agents posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004)
  and its API record [`boards-api.greenhouse.io/v1/boards/hightouch/jobs/5542602004`]: source of
  the "one application per candidate... auto-rejected if you apply to multiple roles" clause (used
  in the Concurrent-application flag), interview loop, stack detail, JD comparison.
- [Staff Engineer, AI Productivity posting](https://job-boards.greenhouse.io/hightouch/jobs/6020404004):
  confirms this posting does NOT restate the one-application clause; internal AI-tooling role
  scope and stack (TypeScript/JS monorepo, Go, GraphQL, MCP servers), interview loop.
- Internal: `.venv/bin/python -m src.query job 1911` (jobhunt DB), canonical stored JD and metadata
  for the target Deployment Architect req.
- [Hightouch: careers page](https://hightouch.com/careers), seven values, remote/office policy
  (no country-eligibility statement found), benefits.
- [Adweek: Hightouch funding history](https://www.adweek.com/dealroom/hightouch-raised-322-million-across-six-rounds-heres-how-the-company-skyrocketed-to-a-275-billion-valuation/),
  round-by-round funding and valuation table.
- [PYMNTS: Hightouch valued at $2.75B](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/),
  Series D date, amount, valuation, growth rate, founder/investor quotes.
- [Businesswire: Hightouch Raises $150M Series D](https://www.businesswire.com/news/home/20260427054567/en/Hightouch-Raises-$150-Million-to-Reinvent-How-Marketing-Works-Using-AI),
  Series D announcement.
- [Businesswire: Smart Suppression launch](https://www.businesswire.com/news/home/20251008017466/en/Hightouch-Launches-Smart-Suppression-to-Protect-Brand-Relationships-Without-Sacrificing-Conversions),
  Oct 2025 product launch detail.
- [Businesswire: Gartner Leader announcement](https://www.businesswire.com/news/home/20260129112125/en/Hightouch-Named-a-Leader-in-the-2025-Gartner-Magic-Quadrant-for-Customer-Data-Platforms),
  Gartner recognition date/detail.
- [Businesswire: Databricks ISV Partner of the Year](https://www.businesswire.com/news/home/20250610695735/en/Hightouch-Awarded-2025-Databricks-Retail-and-Consumer-Goods-ISV-Partner-of-the-Year-at-Data-AI-Summit),
  June 2025 partner award.
- [Businesswire: Snowflake Product Partner of the Year 2026](https://www.businesswire.com/news/home/20260602248845/en/Hightouch-Named-2026-Marketers-and-Advertisers-Snowflake-Product-Partner-of-the-Year),
  June 2026 award.
- [Businesswire: Snowflake Modern Marketing Data Stack Leader](https://www.businesswire.com/news/home/20260622288045/en/Hightouch-Recognized-as-a-Leader-in-Snowflakes-Modern-Marketing-Data-Stack-Report-for-Activation-and-Delivery),
  June 2026 recognition.
- [CMS Critic: Hightouch Agents launch](https://cmscritic.com/hightouch-launches-high-performance-agents-to-help-marketers-move-10x-faster),
  Hightouch Agents product detail and CMO quote.
- [Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp), June 15
  2026 repositioning, three architecture pillars including forward-deployed teams, founder quote.
- [Hightouch homepage](https://hightouch.com/), product suite, customer logos, headline metrics.
- [Hightouch: AI Decisioning product page](https://hightouch.com/platform/ai-decisioning), product
  mechanics and customer results.
- [Hightouch: Gartner recognition page](https://hightouch.com/gartner), Leader status, date,
  rationale.
- [Hightouch: 2025 redesign blog post](https://hightouch.com/blog/hightouch-redesign-2025),
  product/design culture and philosophy.
- [Hightouch: Under the hood of AI Decisioning series](https://hightouch.com/blog/the-personalization-gap)
  (parts two through four linked inline), RL/bandit technical detail for interview prep.
- [YC company page: Hightouch](https://www.ycombinator.com/companies/hightouch), founding year,
  batch (S19), founders, one-line description.
- [Full Stack Product Engineer posting](https://job-boards.greenhouse.io/hightouch/jobs/4620430004),
  tech stack (TypeScript, React, Go, Kafka/Kinesis).
- [Unusual VC: Hightouch's product-market-fit journey](https://www.unusual.vc/hightouchs-product-market-fit-journey/),
  founding story, original pivot from customer-dashboard idea to reverse ETL.
- LinkedIn search result (`linkedin.com/in/kogand2/`), single public profile of a Canada-based
  Hightouch software engineer; used only as low-confidence circumstantial evidence in the location
  verdict, not as a primary claim.
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml, Santiago's verified experience (Online
  Basics, Eugenia.ai, Pragma AI, Plutus, Kairos), used for the why-fit section.
- /Users/santiagocoronado/jobhunt/config/profile.yaml, Santiago's target profile, location rule,
  Family B target titles, and the "ideal role shape" note, used to frame the fit angles.

researched: 2026-07-28

---
Draft prepared for Santiago's review; this is not a final source of truth. Two things need direct
confirmation before this role is pursued further: (1) whether "Remote (North America)" on this req
genuinely includes a Mexico-based hire, since no public source confirms or denies this and
Hightouch's own hiring pattern leans against it; (2) whether submitting a third Hightouch
application risks triggering the auto-reject clause found on the "Software Engineer, AI Agents"
posting, which may already apply to the two applications in flight.
