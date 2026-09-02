# Sardine: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-24
Target posting: "Forward Deployed AI Engineer" (job id 6525), Sardine careers via Ashby,
https://jobs.ashbyhq.com/sardine/4ff32b5d-13c6-4024-826c-04ed2881d688/application

## Location flag (read first)

The posting's structured location field on Sardine's own Ashby job board API is "Remote -
United States or Canada" only; benefits like health insurance and 401k/RRSP matching are marked
"US and Canada specific" in the posting text itself
[api.ashbyhq.com/posting-api/job-board/sardine, jobs.ashbyhq.com posting]. Sardine is genuinely
remote-first company-wide, with hubs in the Bay Area, NYC, Austin, Toronto, and Sao Paulo, and
third-party salary data shows at least one Sardine software engineer based in Brazil
[jobs.ashbyhq.com posting culture section; levels.fyi/companies/sardine/salaries]. But this
specific requisition is scoped to US or Canada, not worldwide remote, and does not mention
Mexico or LATAM eligibility anywhere. Confirmed live: `isListed: true` on the Ashby job board API,
published 2026-06-11 [api.ashbyhq.com/posting-api/job-board/sardine]. Santiago is TN-visa
eligible for US employment, so a US-based remote arrangement is workable in principle, but TN
status requires an actual US work location and the posting gives no indication Sardine sponsors
or supports TN-visa relocation; this should be raised directly with the recruiter rather than
assumed, and flagged in the profile as a genuine open question rather than a clean fit.

## 1. Snapshot

Sardine is a Series C fintech risk-management company building an "agentic risk platform" for
fraud prevention, AML/KYC compliance, and fincrime operations, founded in 2020 by Soups Ranjan
(CEO), Aditya Goel, and Zahid Shaikh [sardine.ai/blog/series-c-announcement; tracxn.com/sardine].
Raised a $70M Series C in February 2025 led by Activant Capital (with Google Ventures, Moody's
Analytics, Cross Creek Capital, and NAventures), bringing disclosed funding to $145M at that time;
a third-party aggregator (Tracxn) shows total funding around $171M as of 2026, a discrepancy this
dossier flags rather than resolves [businesswire.com/news/home/20250211169372;
fintechfutures.com/venture-capital-funding/fraud-prevention-platform-sardine-secures-70m-series-c;
tracxn.com/d/companies/sardine-technologies]. Company reports serving 300+ to 450+ enterprise
customers across 70+ countries as of 2025-2026, with headcount estimated around 330 employees
across six continents as of May 2026 (third-party estimate) [sardine.ai/about via WebFetch
summary; tracxn.com/d/companies/sardine-technologies]. Headquarters location is inconsistent
across public sources (some list San Francisco, some list Miami); treat as unverified precisely,
but the company operates as remote-first with named hubs in the Bay Area, NYC, Austin, Toronto,
and Sao Paulo [jobs.ashbyhq.com posting culture section].

## 2. Core narrative

Sardine's founders (former risk/compliance leaders from PayPal, Revolut, Uber, and Coinbase) built
the company around a specific insight: fraud, AML, and onboarding risk teams were each buying
point solutions and stitching together siloed data, so Sardine's pitch is a single "agentic risk
platform" that unifies device intelligence, behavioral biometrics, transaction data, and a
cross-institution fraud consortium ("Sonar") into one system, then increasingly hands off the
repetitive parts of that system to production AI agents rather than dashboards for humans to
click through [businesswire.com/news/home/20250211169372; sardine.ai/blog/series-c-announcement].
The Series C thesis, explicitly, is that 2025-2026 is the moment to convert this data advantage
into autonomous agents (KYC Agent, Sanctions Screening Agent, Merchant Risk Agent, Disputes Agent)
that resolve real cases with an audit trail, not just flag them for a human, and the company
reports early production numbers (88% automated resolution on KYC edge cases, "4X ROI") to back
that bet [sardine.ai/blog/series-c-announcement]. The Forward Deployed AI Engineer role exists
because that bet requires engineers embedded with individual clients to turn ambiguous fincrime
workflows into deployed, evaluated agents, not just a platform team building generic features
[jobs.ashbyhq.com posting].

## 3. Mission & product

- Product: an "agentic risk platform" spanning fraud prevention, AML/KYC compliance, cybersecurity
  signals, and onboarding, built on device profiling, transaction monitoring, identity
  verification, and behavioral biometrics [sardine.ai/about via WebFetch; jobs.ashbyhq.com
  posting].
- Data moat: the "Sonar" consortium network shares anonymized fraud intelligence across member
  financial institutions; company reports 6+ billion profiled devices, 800 million consumers, and
  3 million businesses in the network as of mid-2026 postings [jobs.ashbyhq.com posting;
  sardine.ai/about via WebFetch].
- Named enterprise customers: FIS, GoDaddy, Intuit, Edward Jones, ZoomInfo, Checkout.com, Deel,
  and Ascensus [jobs.ashbyhq.com posting; fintechnews.am/fintech-usa coverage of the Series C].
- AI agent product line launched around the Series C: KYC Agent (88% automated resolution rate on
  onboarding edge cases), Sanctions Screening Agent (proposes decisions with audit trail for human
  validation), Merchant Risk Agent (industry classification and fraud-behavior drift monitoring),
  and Disputes Agent (automates chargeback evidence prep) [sardine.ai/blog/series-c-announcement].
- Recent self-serve/investigator-facing product direction (2026): user-scoped private AI research
  spaces for investigators, a "Rule Assistant" embedded in workflows, signal-level AML resolution
  (Sanctions/PEP/Adverse Media handled independently rather than bundled), a searchable Customer
  Profiles page, and "SardineQL," a read-only SQL preview for technical users to query
  transaction/session data directly [sardine.ai/blog/product-updates-february-2026].
- Business model: enterprise B2B SaaS/API sold to banks, fintechs, and large consumer platforms;
  partnership integrations extend distribution (see Recent news).

## 4. Culture & voice

- Explicitly remote-first ("#WorkFromAnywhere") despite maintaining hubs in the Bay Area, NYC,
  Austin, Toronto, and Sao Paulo; company language emphasizes "extreme ownership," performance
  over hours worked, and not missing family commitments for a fixed schedule
  [jobs.ashbyhq.com posting culture section].
- Benefits signal a startup-generous, US/Canada-centric package: early exercise on all options
  (including pre-vested), uncapped/flexible PTO plus a year-end break, 100% health coverage for
  employees, monthly meal and wellness stipends, an annual learning stipend, and a MacBook Pro
  shipped to new hires [jobs.ashbyhq.com posting; sardine.ai/careers via WebFetch summary].
- Employee sentiment on Glassdoor: 4.2 out of 5 aggregate rating (15 reviews); recurring positive
  theme is high ownership/fast pace, recurring caution is a steep learning curve and some
  work-life-balance strain; separate anecdote describes a rough candidate experience in the
  recruiting pipeline (automated rejection sent without cancelling a scheduled interview)
  [glassdoor.com/Overview/Working-at-Sardine-EI_IE7044956.11,18.htm search summary;
  glassdoor.com/Reviews/Sardine-team-Reviews search summary].
- Engineering voice: a public engineering blog post (attributed to engineer Kazuki Nishiura)
  describes deliberately redesigning technical interviews around AI-assisted work: candidates use
  their own IDE and are encouraged to use Claude, GitHub Copilot, and search engines during a
  live, evolving "build a payment-risk-scoring API" exercise rather than a Leetcode-style puzzle,
  on the stated philosophy that AI is "a productivity multiplier rather than a threat"
  [sardine.ai/engineering/reimagining-technical-interviews-in-the-age-of-ai].

## 5. Recent news (last ~12 months)

- February 11, 2025: closed $70M Series C led by Activant Capital (Google Ventures, Moody's
  Analytics, Cross Creek Capital, NAventures participating), reported 130% ARR growth and a
  doubled customer base year over year at announcement
  [businesswire.com/news/home/20250211169372; sardine.ai/blog/series-c-announcement].
- February 2026 (published March 11, 2026): product update ships user-scoped AI investigator
  conversations, SardineQL self-serve SQL (preview), signal-level AML resolutions, a new Customer
  Profiles page, and expanded IP allowlisting (CIDR/IPv6)
  [sardine.ai/blog/product-updates-february-2026].
- April 2026: partnership with Modulr, embedding Sardine's fraud/AML detection into Modulr's Risk
  & Compliance Hub for card and real-time payment channels [modulrfinance.com/newsroom/
  sardine-modulr-partnership].
- June 2026 (published July 1, 2026): product update ships embedded dashboard iframes, structured
  alert checklists, Business (corporate entity) CDD workflows, transaction-level screening
  if/then rules, checkpoint execution analytics, and EMVCo 3DS 2.x ACS certification (enabling
  PSD2 Strong Customer Authentication coverage in EEA/APAC) [sardine.ai/blog/
  product-updates-june-2026].
- June 2026: partnership with Modern Treasury to add Sardine's real-time fraud detection across
  ACH, Wire, RTP, FedNow, Push-to-Card, and stablecoin rails inside Modern Treasury's platform
  [fintech.global/2026/06/25/sardine-integration-arms-modern-treasury-against-fraud;
  thepaypers.com Modern Treasury/Sardine coverage].
- July 3, 2026: two-way integration launched with Infinite (a stablecoin compliance startup
  founded by ex-Sardine employees), feeding Sardine's live risk signals into Infinite's compliance
  workflows and giving Sardine clients access to Infinite's account infrastructure, aimed at the
  stablecoin risk gap [fintech.global/2026/07/03/sardine-and-infinite-integration-targets-
  stablecoin-risk-gap; prnewswire.com/news-releases/infinite-and-sardine-launch-two-way-
  integration].

## 6. Engineering & AI direction

- Core hiring bar for this role: 5+ years in Data Science or Applied AI, proficient in Python and
  SQL for pipeline building and model integration; the posting frames the job as equal parts
  "seasoned data scientist" rigor and client-facing solution ownership, not a pure software
  engineering role [jobs.ashbyhq.com posting].
- Stated responsibilities: embed directly with clients to turn ambiguous operational problems into
  technical architecture; train and deploy custom AI agents into production for fraud/AML/complex
  workflow automation; use prompt engineering, fine-tuning, and evaluation frameworks to optimize
  agent accuracy, safety, and reliability; build and evolve AI risk metrics, datasets, and
  evaluation pipelines to measure causal agent impact; work with internal engineering/product to
  scale custom models into production [jobs.ashbyhq.com posting].
- Product-level AI direction: four named production agents (KYC, Sanctions Screening, Merchant
  Risk, Disputes) built around explainability and audit trails as a selling point, not black-box
  automation, plus a 2026 push toward self-serve, investigator-facing AI tooling (scoped
  conversations, a Rule Assistant, SardineQL) rather than only backend model work
  [sardine.ai/blog/series-c-announcement; sardine.ai/blog/product-updates-february-2026].
- Engineering culture signal: the team publicly reworked its own technical interview format around
  AI-assisted development (candidates use Claude/Copilot live during a realistic, evolving
  payment-risk-scoring exercise), suggesting the internal engineering org treats AI tools as
  standard workflow rather than a novelty
  [sardine.ai/engineering/reimagining-technical-interviews-in-the-age-of-ai].
- Compliance/security engineering surface: recent shipped work includes EMVCo 3DS 2.x
  certification (regulatory-grade payment authentication) and CIDR/IPv6-based IP allowlisting,
  indicating the engineering org operates under real regulatory and security constraints, not just
  a typical SaaS product surface [sardine.ai/blog/product-updates-june-2026;
  sardine.ai/blog/product-updates-february-2026].

## 7. Comp signals

- The posting itself lists no salary range or equity band; states "generous compensation in cash
  and equity" with early exercise on all options (including pre-vested) [jobs.ashbyhq.com
  posting].
- Third-party aggregated data (Glassdoor, Levels.fyi; self-reported, not verified by Sardine or
  this dossier) shows a wide spread: a Levels.fyi sample lists a Sardine Software Engineer in
  Brazil at roughly $93,000 total comp versus a Data Scientist in the United States at roughly
  $184,000, and a separate Levels.fyi Canada sample shows a median Software Engineer total comp
  around CA$248,500; general market data for "Forward Deployed Engineer" roles industry-wide
  (not Sardine-specific) clusters around $205,000 median, with wide variance by level and company
  [levels.fyi/companies/sardine/salaries; glassdoor.com/Salary/Sardine-Salaries-E7044956.htm
  search summary; levels.fyi/t/software-engineer/title/forward-deployed-engineer search summary].
  Treat all of the above as directional, not a quoted offer; ask the recruiter directly for the
  actual band tied to a US or Canada location before assuming any of these numbers.

## 8. Interview process signals

- Glassdoor accounts describe an initial roughly 30-minute video screen, followed by a technical
  interview built around a realistic, evolving problem (example cited: given an API, accept a list
  of payment transactions and return a risk score) rather than algorithm puzzles
  [glassdoor.com/Interview/Sardine-Interview-Questions-E7044956.htm search summary].
- Sardine's own engineering blog confirms and elaborates this format: candidates bring their own
  IDE, are explicitly encouraged to use AI assistants (Claude, GitHub Copilot) and search engines,
  start from a provided basic server implementation, and work through requirements that evolve
  live while screen-sharing; the stated goal is assessing human judgment and communication under
  realistic, AI-assisted conditions rather than raw algorithm recall
  [sardine.ai/engineering/reimagining-technical-interviews-in-the-age-of-ai].
- Candidate experience feedback is mixed: some describe the process as straightforward though
  "scripted"; a separate, non-engineering candidate reported poor recruiter communication
  (automated rejection sent without cancelling a scheduled interview). Sample size on public
  reviews is small; treat as anecdote, not a pattern [glassdoor.com Sardine reviews search
  summary].

## 9. Why-fit angles for Santiago

Best hook to lead with: the role is explicitly framed as sitting "at the intersection of client
consulting, advanced machine learning, and hands-on engineering," embedding with clients to turn
an ambiguous operational problem into a deployed, evaluated AI agent
[jobs.ashbyhq.com posting]. That is close to Santiago's actual operating pattern as co-founder of
Pragma AI: diagnosing a client's operational bottleneck, then shipping a scoped AI system (a RAG
"company brain" with deterministic no-answer and citation gating, agent workflows for quoting,
reporting, onboarding, collections) directly into that client's operations
[resume/master_resume.yaml]. The forward-deployed motion (own the full lifecycle from ambiguous
client ask to production system, with extreme ownership and no generic playbook) is also how he
ran Eugenia.ai's on-site B2B deployments (onboarding HOAs and property administrators, translating
conflicting requirements into a working product) [resume/master_resume.yaml].

Concrete transferable evidence:
- Built and operated an authenticated MCP "brain" service and 15 agent definitions for Pragma's
  own internal operations, plus a RAG system with scoped retrieval, deterministic no-answer/
  citation gating, and LLM-at-ingest sensitivity labeling, direct evidence of building agents that
  need explainability and guardrails, which mirrors Sardine's stated emphasis on agent decisions
  being "fully explainable, with clear audit trails" [resume/master_resume.yaml;
  sardine.ai/blog/series-c-announcement].
- Plutus pairs a Python/Postgres backend with an LLM research agent and rule-based screener exposed
  through an MCP control plane, demonstrating the "data science plus production engineering"
  combination the posting asks for (Python/SQL pipeline work plus agent evaluation), though
  Sardine's domain (fincrime/transaction risk) is new territory for Santiago and should be named
  as a learning curve, not assumed expertise [resume/master_resume.yaml; jobs.ashbyhq.com
  posting].
- Founder-level client ownership (raised capital, ran a 7-person team, owned P&L at Online Basics;
  bootstrapped and exited Eugenia.ai) is direct evidence of the "extreme ownership" and end-to-end
  solution-lifecycle ownership language the posting and Sardine's culture section both use
  [resume/master_resume.yaml; jobs.ashbyhq.com posting].

Honest concerns and watch-outs:
- Location is the biggest open question, not a minor detail: this specific requisition is
  structured for US or Canada remote only, with no stated Mexico/LATAM eligibility, despite
  Sardine being remote-first company-wide with a Sao Paulo hub. This should be raised directly
  with the recruiter before investing heavily in the process (see Location flag above).
- Domain gap: Santiago has no direct fraud, AML, or KYC/compliance experience; his AI-agent and
  RAG work is real but in different verticals (PropTech, e-commerce operations, personal finance,
  investment research). This is a legitimate gap to prep for, not something to paper over.
- The role explicitly wants 5+ years "in Data Science or Applied AI" specifically; Santiago's
  background is founder-engineer and full-stack, with strong applied-AI project evidence but not a
  formal data science title or classical ML/stats background. Worth being ready to address how his
  experience maps to "data science rigor" (evaluation pipelines, causal-impact measurement) versus
  pure software engineering.
- Compensation is unlisted and third-party data shows wide variance ($93K to $248K+ depending on
  role/location in aggregator samples); this needs a direct conversation with the recruiter rather
  than assuming it clears Santiago's 65K USD floor comfortably, though it likely does for a
  US/Canada-based senior role.

## 10. Application-question angles

- Why this company: lead with the forward-deployed motion itself, embedding with a client to turn
  an ambiguous operational problem into a production AI agent, since that is functionally what
  Pragma AI already does for Mexican SMB clients. Frame it as wanting to run that same motion
  against a harder, higher-stakes problem (real-time fincrime, regulated financial institutions)
  with a company that has already proven the agent-plus-audit-trail model works (KYC Agent at 88%
  automated resolution, reported 4X ROI). Avoid restating the fraud/AML product list; anchor on
  the operating model match.
- Why you fit: point to concrete built systems, not job titles: an authenticated MCP agent service
  with explainability and access controls built for Pragma's own operations, an LLM research agent
  exposed through MCP in Plutus, and founder-level ownership of full client deployments at
  Eugenia.ai. Be direct that the fincrime domain itself is new and frame the pitch as "fast domain
  learner with a demonstrated pattern of shipping trustworthy, auditable AI systems into real
  operations," not domain expertise he does not have.
- Anything else: if location comes up, be upfront and factual rather than hopeful, this posting is
  scoped to US/Canada remote and Santiago is Mexico City based and TN-visa eligible for US
  employment; ask directly whether the role is open to a US-based TN arrangement or whether it is
  strictly US/Canada resident only. Do not raise compensation unprompted; if asked, note the floor
  (65K USD) without over-anchoring, since Sardine's own posting gives no range to react to.

## Sources

- https://jobs.ashbyhq.com/sardine/4ff32b5d-13c6-4024-826c-04ed2881d688 and
  https://jobs.ashbyhq.com/sardine/4ff32b5d-13c6-4024-826c-04ed2881d688/application (target job
  posting, human-facing page)
- https://api.ashbyhq.com/posting-api/job-board/sardine (Sardine's public Ashby job board API;
  used to pull the full structured posting: location field "United States" + secondary location
  "Canada," workplaceType "Remote," isListed true, publishedAt 2026-06-11, full description text,
  responsibilities, requirements, and benefits)
- https://www.sardine.ai/blog/series-c-announcement (Series C amount/date/investors, founding
  year, founder backgrounds, AI agent product launch, ARR/customer growth stats)
- https://www.businesswire.com/news/home/20250211169372/en/Sardine-AI-Raises-$70M-to-Make-Fraud-and-Compliance-Teams-More-Productive
  (Series C press release corroboration: amount, lead investor, participating investors)
- https://www.fintechfutures.com/venture-capital-funding/fraud-prevention-platform-sardine-secures-70m-series-c-invests-in-agentic-ai
  (Series C coverage, agentic AI investment framing)
- https://tracxn.com/d/companies/sardine-technologies (founder names, total funding estimate,
  headcount estimate as of May 2026; third-party aggregator, flagged as such)
- https://www.sardine.ai/about (company snapshot: mission statement, product description, funding
  total, customer/device stats; fetched via WebFetch summary)
- https://www.sardine.ai/careers (remote-first culture description, benefits detail; fetched via
  WebFetch summary)
- https://www.sardine.ai/blog/product-updates-february-2026 (Feb 2026 product update: AI
  investigator conversations, SardineQL, signal-level AML resolutions, Customer Profiles page)
- https://www.sardine.ai/blog/product-updates-june-2026 (June 2026 product update: dashboards,
  alert checklists, Business CDD, EMVCo 3DS 2.x certification)
- https://www.modulrfinance.com/newsroom/sardine-modulr-partnership (April 2026 Modulr
  partnership)
- https://fintech.global/2026/06/25/sardine-integration-arms-modern-treasury-against-fraud and
  https://thepaypers.com/fraud-and-fincrime/news/modern-treasury-and-sardine-partner-on-fraud-detection
  (June 2026 Modern Treasury partnership)
- https://fintech.global/2026/07/03/sardine-and-infinite-integration-targets-stablecoin-risk-gap
  and https://www.prnewswire.com/news-releases/infinite-and-sardine-launch-two-way-integration-linking-compliance-risk-and-payments-302816365.html
  (July 3 2026 Infinite partnership)
- https://www.sardine.ai/engineering/reimagining-technical-interviews-in-the-age-of-ai (engineering
  blog: reworked technical interview format, AI-assisted interview philosophy, engineering culture
  signal)
- https://www.glassdoor.com/Interview/Sardine-Interview-Questions-E7044956.htm (interview process
  anecdotes: video screen, realistic technical exercise)
- https://www.glassdoor.com/Overview/Working-at-Sardine-EI_IE7044956.11,18.htm and
  https://www.glassdoor.com/Reviews/Sardine-team-Reviews-EI_IE7044956.0,7_KH8,12.htm (aggregate
  rating, employee sentiment themes, candidate-experience anecdote)
- https://www.levels.fyi/companies/sardine/salaries (third-party self-reported compensation data
  points, including a Brazil-based Software Engineer sample, used as directional comp signal and
  as evidence Sardine does employ engineers outside the US/Canada in other roles)
- https://www.glassdoor.com/Salary/Sardine-Salaries-E7044956.htm and
  https://www.levels.fyi/t/software-engineer/title/forward-deployed-engineer (general/aggregated
  comp signals, flagged as directional not Sardine-specific where noted)
- https://www.mckinsey.com/industries/financial-services/our-insights/talking-with-soups-ranjan-cofounder-and-ceo-of-sardineai
  and https://www.amlintelligence.com/speakers/soups-ranjan/ (CEO Soups Ranjan background: PhD
  Rice University, Head of Financial Crime at Revolut, Head of Risk at Coinbase)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience: Online
  Basics, Eugenia.ai, Pragma AI, Plutus, Kairos, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile, location rule,
  and salary floor, used to frame the location and comp watch-outs)

Note for Santiago: this is a draft dossier, please review before it feeds a cover letter or
application answers. The single most important open item is the location scoping: this specific
requisition reads as US/Canada remote only on Sardine's own job board API, despite the company
being remote-first with a Sao Paulo hub elsewhere. Confirm directly with a recruiter whether a
Mexico City, TN-visa-track arrangement is workable before assuming this role is a clean geographic
fit. Headquarters location and total funding figures also vary slightly across sources; both are
flagged above rather than resolved to a single number.
