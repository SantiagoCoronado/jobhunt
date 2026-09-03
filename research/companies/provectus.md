# Provectus

Draft dossier for Santiago's review. Researched: 2026-09-02.

## Snapshot
AI-first systems integrator founded 2010, privately held and founder-led, HQ San Francisco
(447 Sutter Street), 400+ AI builders, 100+ customers in production, offices across North
America, LATAM (Medellin, Bogota, San Jose; Barranquilla also referenced), and EMEA. Premier
AWS Partner and Select Anthropic Partner. [provectus.com, careers.provectus.com/about]

## Core narrative
Provectus does not sell AI advice, it embeds engineers inside a client's operation as
Forward Deployed Engineers/Executives who do the operator's actual job (underwriter, claims
clinician, RCM specialist) for weeks before writing code, then rebuild that function from
first principles using one of five pre-built "AI Blueprints" for financial services/insurance
and healthcare/life sciences. The pitch is that most AI engagements fail at the
requirements-gathering step, so Provectus removes that step entirely and measures its people
on whether the business unit's number moved, not hours or scope delivered. This is reinforced
by a formal multi-year AWS Strategic Collaboration Agreement (announced June 2025) and status
as an Anthropic launch partner for Claude for Healthcare and Life Sciences (January 2026),
positioning Provectus as one of the more deeply embedded implementation partners in the
Anthropic ecosystem rather than a generic consultancy layering a chatbot on top of existing
workflows. [job 37377 posting; provectus.com/blog/provectus-aws-strategic-collaboration-accelerate-enterprise-ai-transformation; provectus.com/news/provectus-joins-the-launch-of-anthropics-claude-for-healthcare-and-life-sciences]

## Mission & product
- Builds and operates production AI and data systems for enterprises, two verticals only:
  Financial Services & Insurance, and Healthcare & Life Sciences. [provectus.com]
- Five "AI Blueprints", pre-built systems tuned per client: Submission Flow, Portfolio Lens,
  Asset Flow (FSI); Revenue Flow, Evidence Lens (HCLS). [job 37377 posting; provectus.com]
- Three engagement models: Sprint (baseline measurement), Enable (8-14 week deployment),
  Realize (ongoing, outcome-based pricing). [provectus.com]
- Also runs an "Agentic Executive" program for C-suite leaders and co-delivers Anthropic's
  Agentic SDLC and Cowork Activation programs. [provectus.com; job 37377 posting]
- Notable client outcomes cited on the company site: a biotech genomics platform saving $10M
  in licensing costs; Convex Insurance GenAI document intelligence turning 100-page risk
  reports into structured summaries in about 10 minutes; Johnson Lambert audit process
  accelerated nearly 4x; PepsiCo AI/ML marketing platform with 2x ROI improvement across 25+
  brands in 100+ countries. [provectus.com]
- Business model: bespoke applications, managed services, and advisory engagements sold to
  enterprise FSI and HCLS clients, not a horizontal SaaS product. [job 37377 posting]

## Culture & voice
- Site language is terse and outcome-obsessed ("The catalog is small on purpose. Every
  blueprint exists because we have shipped it enough times to start day one with working
  code.") and explicitly anti-consulting-theater: "learn the work, ship the system, own the
  outcome" versus staying at arm's length as a vendor. [careers.provectus.com/about]
- Describes itself as "distributed by design," "local presence across three continents, one
  way of working." [careers.provectus.com/about]
- The job posting's voice matches: short declarative sentences, explicit "engineers who need
  to stay in the IDE should not apply," measured on whether the business unit's KPI moved. This
  is a consistent, deliberate brand voice, not just one recruiter's phrasing. [job 37377 posting]

## Recent news (last ~12 months)
- January 12, 2026: Provectus named a launch partner for Anthropic's expanded Claude for
  Healthcare and Claude for Life Sciences offering, designing compliant AI architectures and
  embedding agent-based workflows for healthcare clients.
  [provectus.com/news/provectus-joins-the-launch-of-anthropics-claude-for-healthcare-and-life-sciences]
- Background (just outside the 12-month window but structurally relevant): June 2025,
  Provectus and AWS signed a multi-year Strategic Collaboration Agreement covering financial
  services, healthcare/life sciences, and retail/CPG; CEO Stepan Pushkarev framed it as helping
  clients "execute [AI/ML, GenAI, cloud, and data decisions] with speed and precision."
  [provectus.com/blog/provectus-aws-strategic-collaboration-accelerate-enterprise-ai-transformation]
- Active hiring push into GenAI/Claude-focused Forward Deployed roles as of September 2026
  (this posting and sibling Senior/Middle AI-ML Engineer, Forward Deployed Executive, and
  Solutions Architect roles all live simultaneously), consistent with scaling the Anthropic
  and AWS partnerships into delivery headcount. [WebSearch job listings on jobs.lever.co/provectus]

## Engineering & AI direction
- Team holds 100+ AWS certifications (careers page separately cites 150+ AWS and Anthropic
  Certified Architects) and is Claude Code certified; co-delivers Anthropic's Agentic SDLC
  program, Cowork Activation, and AI Blueprint engagements. [job 37377 posting; provectus.com]
- Stack emphasis per the target role: Python and/or TypeScript as the delivery languages
  (chosen per customer, not per resume), AWS-native delivery (containers, Kubernetes/ECS, IaC,
  CI/CD), with GCP/Azure as a plus. Nice-to-haves include data lakes/warehouses/streaming,
  data mesh and contracts, MLOps (PyTorch, SageMaker, MLflow), fine-tuning/distillation/serving
  optimization, graph databases (Neo4j, AWS Neptune), and IaC depth (CDK, CloudFormation,
  Terraform). [job 37377 posting]
- Explicit AI bet: production GenAI/agentic systems, not demos or notebooks, with a hard
  requirement to have built or owned an eval suite for a non-deterministic system before
  shipping the feature. Heavy, repeated emphasis on evals as a first-class engineering
  discipline. [job 37377 posting]
- AWS Marketplace listing exists for "Generative AI by Provectus with Anthropic," indicating a
  packaged, purchasable Claude-based offering rather than only bespoke engagements.
  [aws.amazon.com/marketplace/pp/prodview-pktyrp57ep7ls, surfaced via WebSearch]

## Why-fit angles for Santiago
Best hook to lead with: Santiago has already run the "own the outcome, do the operator's job,
ship the system" loop for himself, not as a hired-in FDE but as the founder who did every one
of those roles at Online Basics ($8M multi-marketplace ecommerce business) and Eugenia.ai
(PropTech, on-site client deployments, requirements gathering collapsed into building).
Provectus's entire pitch, that requirements-gathering-then-handoff is the bug and embedding is
the fix, is exactly the operating model he ran solo for seven years: he was the underwriter,
the analyst, and the engineer at once, then built the internal platform (pricing dashboard,
inventory admin, ETL pipelines) that the business ran on. That is a rare, honest match to "you
do the job before you automate it."

Supporting angles:
- Shipped production GenAI systems end to end, not demos: the LLM listing-generation pipeline
  with a multi-stage validation gate at Online Basics, and the Pragma AI RAG "company brain"
  with deterministic no-answer/citation gating and an automated eval harness, directly answers
  the "built or owned an eval suite for a non-deterministic system" requirement.
- Founder-to-IC framing: the posting explicitly wants people who "have led before, as a
  founder, a CTO, a staff engineer" and chose to stay hands-on; Santiago is a two-time founder
  who still writes the code himself (Plutus, Kairos, Pragma AI's internal MCP platform).
- Credible with senior stakeholders on both sides of a room: he raised $500K from investors and
  banking partners, led a 7-person team, and personally ran client deployments at Eugenia.ai,
  matching "credible with a BU head and a CTO."

Honest concerns and watch-outs:
- The posting lists United States as the location and the matcher flags location as unresolved
  for a Mexico City hire; Provectus does have real LATAM offices (Medellin, Bogota, San Jose)
  and a distributed model, but nothing found confirms this specific US-titled role is open to a
  Mexico-based hire, or whether non-US hires are W-2 employees, B2B contractors, or something
  else. The posting itself offers "B2B contract model or full-time model," which is compatible
  with a Mexico-based contractor arrangement but is not confirmed either way for this req.
  [job 37377 posting; careers.provectus.com/about, no employment-classification detail found]
- Domain depth: the role explicitly prizes financial services, insurance, healthcare, or asset
  management experience as a plus. Santiago's ecommerce and PropTech domain background is
  adjacent, not a direct match; this is a real gap, not just a keyword gap (the matcher already
  flags it).
- The role wants someone willing to spend two to four weeks literally doing an unfamiliar
  operator's job (claims processing, underwriting) before writing code, and functions on client
  sites/embedded time; confirm expected travel cadence and whether any of it requires physical
  US presence beyond periodic trips, since the location rule allows travel but not a required
  US work location.

## Application-question angles
- Why this company: lead with the operating-model match, not the AWS/Anthropic partner
  logos. Santiago has already lived the "do the job, then rebuild the function, then own the
  number" loop as a founder; Provectus is one of the few places that hires for that loop
  explicitly rather than asking him to translate it into a normal engineering title.
- Why you fit: anchor on the eval-suite and production-GenAI requirement using Pragma AI's RAG
  brain (deterministic no-answer/citation gating, automated eval harness) and the Online Basics
  LLM listing pipeline, then bridge to the founder-who-stayed-hands-on framing the posting asks
  for directly. Do not try to claim financial services or healthcare depth he does not have;
  name the ecommerce/PropTech domain honestly and pivot to the transferable skill (fast domain
  immersion, building the internal system a small team actually runs the business on).
- Anything else: if asked, raise the location/employment-classification question directly
  rather than guessing (Mexico City, TN-eligible, open to the B2B contract model Provectus
  itself offers in the posting) rather than letting it surface later as a surprise.

## Sources
- researched: 2026-09-02
- https://provectus.com/ (mission, services, engagement models, notable client outcomes, HQ,
  founding year, headcount)
- https://careers.provectus.com/about/ (culture language, LATAM office locations, "distributed
  by design" positioning; no employment-classification detail found)
- https://provectus.com/blog/provectus-aws-strategic-collaboration-accelerate-enterprise-ai-transformation/
  (AWS Strategic Collaboration Agreement, June 2025, verticals, CEO quote)
- https://provectus.com/news/provectus-joins-the-launch-of-anthropics-claude-for-healthcare-and-life-sciences/
  (Claude for Healthcare/Life Sciences launch partner, January 12, 2026)
- https://aws.amazon.com/marketplace/pp/prodview-pktyrp57ep7ls (AWS Marketplace listing,
  "Generative AI by Provectus with Anthropic", surfaced via WebSearch, not independently
  fetched)
- WebSearch results for "Provectus AI AWS Premier partner Anthropic Strategic Partner GenAI"
  and "Provectus AI careers LATAM remote contractor employees Mexico Brazil" (sibling job
  listings on jobs.lever.co/provectus, LATAM city list, hybrid-model language)
- `.venv/bin/python -m src.query job 37377` (full job description, canonical apply URL, salary
  band, posted date, matcher notes): apply link
  https://himalayas.app/companies/provectus/jobs/forward-deployed-ai-architect-genai-aws

## Target role
Forward Deployed AI Architect (GenAI, AWS), job id 37377. Posted 2026-09-01. Listed location
"United States", remote flag set, OTE $150k to $180k USD, B2B contract or full-time model
offered. Two verticals (Financial Services & Insurance, Healthcare & Life Sciences), five AI
Blueprints, 8+ years building production software, shipped GenAI/LLM systems to production
with an owned eval suite, Python and/or TypeScript, AWS-native delivery, prior
founder/CTO/staff-engineer background explicitly welcomed. Hiring process: intro call, two
live engineering sessions (LLM assistants allowed, autocomplete/agentic tools off), an
unfamiliar-business-function redesign session (no LLMs), then a team/practice conversation.
Canonical apply link: https://himalayas.app/companies/provectus/jobs/forward-deployed-ai-architect-genai-aws
[job 37377 posting]

## Hiring signal (2026-09-02)

The Forward Deployed AI Architect (GenAI, AWS) application form refused a Mexico-based applicant as location-ineligible: this req is US-only despite the LATAM offices. Do not tailor for Provectus US listings from Mexico; only a req that names Mexico or LATAM explicitly is worth the time.
