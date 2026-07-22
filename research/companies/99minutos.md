# 99minutos (99minutos.com)

*Draft dossier for Santiago. Researched for the "Lead AI Product Engineer" role, Miguel Hidalgo,
Ciudad de Mexico (job id 10478, Adzuna). Review before use; re-check anything time-sensitive.*

## 1. Snapshot

99minutos is a Mexico City founded (2014) last-mile and full-stack logistics company for Latin
American e-commerce, operating in Mexico, Colombia, Chile, and Peru, backed by $128.7M in total
funding including an $82M Series C (2022, led by Oak HC/FT, with Kaszek and Prosus Ventures) and
a Y Combinator W20 alum [YC company page; PRNewswire, Mar 2 2022]. Headcount estimates vary by
source and date: self-reported ~5,000 at the time of the Series C (2022) with a stated target of
8,000 to 10,000 by year end, versus third-party aggregator estimates of roughly 900 to 5,000 as
of 2025 [PRNewswire, Mar 2 2022; Tracxn 2025 profile; EasyLeadz, accessed 2025]. HQ is Mexico
City; this role is listed as on-site/hybrid in Miguel Hidalgo, CDMX [job 10478].

## 2. Core narrative

99minutos started as a same-day courier and has grown into a five-vertical logistics operating
system for LATAM e-commerce (last-mile delivery, 3PL fulfillment, freight/middle-mile, custom
operations, and a pickup-point network), serving enterprise shippers like Amazon, Mercado Libre,
Liverpool, Walmart, and CEVA Logistics [99minutos.com, fetched 2026]. What makes it distinctive
for this role specifically: the company is not talking about AI in the abstract, its own CTO and
data leadership have already shipped agentic AI into production twice in late 2025, an internal
project called "Sherlock" that uses AI agents to validate delivery evidence and catch fraud
(correcting over 92% of suspicious delivery cases, cutting unrecognized-delivery call center
contacts by 18%), and an AI-driven operator-validation and anomaly-detection engine inside the
new Freight99 freight vertical [IT Masters Mag, Nov 24 2025; T21, Aug 26 2025]. The Lead AI
Product Engineer opening reads as a formalization of that existing, homegrown AI practice into a
dedicated product role, not a first foray into AI.

## 3. Mission & product

- Positioning: "your logistics partner in Latin America," built on "technology, operation and
  accompaniment" (tecnologia, operacion y acompanamiento) [99minutos.com, fetched 2026].
- Five product verticals: envios99 (last-mile express delivery), fulfill99 (3PL warehousing and
  fulfillment), freight99 (cargo/middle-mile transport, launched as a formal vertical Aug 26,
  2025), tailor99 (custom logistics operations), and punto99 (pickup/collection point network)
  [99minutos.com, fetched 2026; T21, Aug 26 2025].
- Business model: B2B logistics-as-a-service, integrating directly with e-commerce platforms
  (Shopify, WooCommerce, Magento, TikTok Shop) to automate shipping and fulfillment for online
  retailers [99minutos.com, fetched 2026].
- Customers named on the company site include Amazon, Mercado Libre, Liverpool, Walmart, and CEVA
  Logistics [99minutos.com, fetched 2026].
- Scale at time of Series C: 15M+ packages annually, operating in roughly 60 markets across
  Mexico, Colombia, Chile, and Peru [PRNewswire, Mar 2 2022].

## 4. Stage / funding

- Founded 2014 in Mexico City by Alexis Patjane (CEO) [YC company page].
- Y Combinator Winter 2020 (W20) batch [YC company page].
- Series B: $40M, May 2021 (Prosus, Kaszek) [PRNewswire, Mar 2 2022, referenced as prior round].
- Series C: $82M, announced March 2, 2022, led by Oak HC/FT, with existing investors Kaszek and
  Prosus Ventures participating, bringing total funding to ~$128.7M [PRNewswire, Mar 2 2022;
  TechCrunch, Mar 2 2022]. Oak HC/FT principal Allen Miller described 99minutos as having
  "impressively expanded beyond its core last-mile offering to become the leading technology
  logistics and fulfillment company in the region" [TechCrunch, Mar 2 2022].
- No funding round has been found publicly reported since the 2022 Series C; treat the company as
  a well-capitalized, scaling Series C startup rather than a recently-funded one.

## 5. Tech stack (engineering & AI direction)

- General stack, per a third-party aggregator (StackShare, not independently verified against a
  first-party engineering blog, treat as directional): PHP/Laravel, Python, Java, Flask, Go,
  Node.js, and Android SDK on the backend; JavaScript/TypeScript, Dart/Flutter, React, and NestJS
  on the front end/mobile; PostgreSQL and MongoDB for data; AWS-heavy infrastructure (Lambda,
  EC2, S3, CloudWatch, SES, Route 53, ECS) plus Docker and Kubernetes [StackShare aggregator page,
  via search, direct fetch blocked].
- Production AI in the field, named systems:
  - "Sherlock": an internal agentic AI project that analyzes contextual, historical, operational,
    and visual data in real time to flag altered, erroneous, or fabricated delivery evidence,
    generating what CTO Jonathan Andrade called "una huella digital unica por cada entrega" (a
    unique digital fingerprint per delivery). Reported results: over 92% of suspicious delivery
    cases corrected, an 18% cut in call-center contacts for unrecognized deliveries. CDO Santiago
    Savinon on the initiative: "Innovar es romper el molde y traer al mercado cosas que antes no
    existian" [IT Masters Mag, Nov 24 2025].
  - Freight99's AI layer: automatic bill-of-lading generation, integration with 60+ GPS systems,
    AI-based operator/credential validation, anomaly detection for theft prevention, and an
    AI-mediated WhatsApp channel between shippers and operators. CTO Jonathan Andrade: "We're not
    looking to replace WhatsApp, but optimize it with AI to make it more efficient." Executive
    named as Chief Growth Officer in this piece, Santiago Savinon, on the underlying opportunity:
    "The industry continues to grow at 5% annually, but faces a huge tech gap" [T21, Aug 26 2025].
    Note: Santiago Savinon is titled Chief Data Officer in the IT Masters Mag piece and Chief
    Growth Officer in the T21 piece; the discrepancy is unresolved across the two sources.
- The open role itself asks for someone who can "disenar, construir y desplegar agentes de IA de
  extremo a extremo," has product sense to prioritize initiatives and read operations, can pick
  the right LLM per problem, and can communicate with the C-level, explicitly framed against
  transforming logistics operations with generative AI [job 10478, description]. This lines up
  directly with the Sherlock/Freight99 pattern above: in-house agentic AI, owned by
  technical/data leadership, aimed at operational fraud and efficiency problems.

## 6. Culture (public signal)

- Glassdoor aggregate (self-reported employee reviews, unverifiable independently): 3.5/5 overall
  from 70 reviews, 65% would recommend to a friend; commonly cited pros are culture, management,
  and coworkers; compensation and benefits rated lower at 2.7/5, with reviews citing payment
  delays ("Don't count on getting paid your salary on time, even after the considerable
  investment that the company received") and limited transparency in some internal processes
  ("Administracion totalmente vertical, no hay mucha visibilidad...") [Glassdoor, 99minutos.com
  reviews page, accessed via search].
- Startup-speed signal: Y Combinator alum (W20), still framed on its own careers/company material
  as "the fastest shipping for online shopping" [YC company page].
- Innovation-forward internal voice, per CDO Santiago Savinon on the Sherlock launch: "Innovar es
  romper el molde y traer al mercado cosas que antes no existian" [IT Masters Mag, Nov 24 2025].

## 7. Recent news (last ~12 months)

- Aug 26, 2025: Freight99 launched as a formal middle-mile/freight vertical (port towing, full
  truck load), starting with 400+ owned units and 40 strategic partners in Mexico, with AI-based
  operator validation and anomaly detection; phase two expansion planned to Colombia, Chile, and
  Peru [T21, Aug 26 2025].
- Nov 24, 2025: Company detailed "Sherlock," its production agentic AI system for validating
  delivery evidence, reporting a 92%+ correction rate on suspicious deliveries and an 18%
  reduction in unrecognized-delivery call center contacts [IT Masters Mag, Nov 24 2025].
- No additional funding, leadership change, or expansion news dated within the last 12 months was
  found in this research pass; the most recent funding event on record remains the March 2022
  Series C.

## 8. Why-it-fits hooks for Santiago

Best hook to lead with: Santiago has already built, at founder scale, the exact pattern 99minutos
is now running in production. Sherlock is an agentic AI system that ingests messy real-world
signal (delivery evidence) and makes an automated trust decision with a measurable business
result; Santiago's Hermes project is a function-calling/tool-use agent, Plutus is an MCP-based
research agent that turns natural language into structured, evidence-backed output, and Pragma
Brain is a RAG "company brain" built to answer questions and generate reports from a company's
own data. He is not pitching AI enthusiasm, he is describing the same shape of system 99minutos
already shipped, at a different scale.

Supporting angles:
- Founder-to-C-level fluency: the JD explicitly wants someone who is not "solo en el prototipo"
  and who can prioritize initiatives and communicate with the C-level. As a 3x founder (Online
  Basics to $8M revenue, Eugenia.ai built and sold, Pragma AI ongoing) who raised capital, ran
  client deployments, and reported to investors and stakeholders directly, Santiago has been the
  person in that conversation, not adjacent to it.
- Operational-data pattern match: at Online Basics he built an LLM workflow with a multi-stage
  validation pipeline processing 100K+ daily data points, the same "high-volume, needs guardrails"
  shape as Sherlock's per-delivery evidence check.
- CDMX based, bilingual (Spanish native, English fluent), matches the on-site/hybrid CDMX
  location and a company whose leadership communicates publicly in Spanish.

Honest concerns / watch-outs:
- Stack overlap is partial, not full. Santiago's production stack is Python/FastAPI, TypeScript,
  React, Node.js, and AWS; 99minutos's broader engineering stack (per the StackShare aggregator,
  unverified) leans PHP/Laravel, Go, Java, and Flutter/Dart in places. There is real overlap
  (Python, Node.js, TypeScript, AWS, Docker) but this should not be overstated as a full match if
  an interview loop probes the non-Python parts of the stack.
- Compensation and process concerns appear in public Glassdoor reviews (payment delays, low
  transparency rating). These are self-reported and unverifiable, but worth a direct, low-key
  diligence question in process rather than assuming they no longer apply.
- No direct prior experience in physical/last-mile logistics operations specifically; Santiago's
  operational depth is e-commerce (Amazon/Mercado Libre selling operations at Online Basics) and
  proptech (Eugenia.ai), which is adjacent but not identical to parcel delivery and freight. Worth
  naming as a fast-learning gap rather than pretending it is not a gap.
- Full requirements/qualifications text of job 10478 could not be fetched directly (source page
  returned an access error); the dossier is grounded in the truncated description captured in the
  local job record plus public company research, not a complete requirements list.

## 9. Application-question angles

- Why this company: do not lead with "LATAM logistics is exciting," lead with the fact that
  99minutos already proved out agentic AI in a hard, physical-world domain (Sherlock's 92%
  correction rate on suspicious deliveries) before this role even existed, so joining means
  extending a system that already has real production metrics behind it, not evangelizing AI from
  zero.
- Why you fit: anchor on one concrete proof point, ideally Hermes (function-calling agent) or
  Plutus (MCP research agent), and describe it as the same shape of problem Sherlock solves:
  ingest messy signal, make an automated call, measure and improve it. Pair that with the founder
  background (client-facing, C-level-facing, has owned the P&L consequences of a shipped decision)
  to answer the "product sense plus C-level comms" half of the ask directly.
- Anything else: be candid that the stack overlap is partial (strong in Python/TypeScript/AWS, no
  claimed depth in Go/PHP/Flutter) and frame it as fast ramp-up rather than full prior mastery;
  this is more credible than implying a perfect stack match.

## 10. Sources

researched: 2026-07-14

- local job record, job id 10478 (`.venv/bin/python -m src.query job 10478`)
  - title, location (Miguel Hidalgo, CDMX), truncated Spanish job description, Adzuna source URL
    (direct fetch of the Adzuna landing page returned a 403 and could not be read in full).
- https://www.ycombinator.com/companies/99minutos/jobs
  - founded 2014, YC W20 batch, Mexico City HQ, founder Alexis Patjane, self-reported team size.
- https://www.prnewswire.com/news-releases/99minutos-raises-82-million-series-c-round-led-by-oak-hcft-301493845.html
  - Series C details: $82M led by Oak HC/FT, Kaszek and Prosus Ventures participating, total
    funding ~$128.7M, prior $40M Series B (May 2021), headcount (~5,000, target 8,000-10,000),
    15M+ annual packages, ~60 markets across Mexico/Colombia/Chile/Peru.
- https://techcrunch.com/2022/03/02/99minutos-logistics-infrastructure-latin-america/
  - Series C coverage, Oak HC/FT principal Allen Miller quote, use-of-funds detail (EV fleet,
    Punto99 pickup hub expansion target).
- https://99minutos.com (home/product pages, fetched 2026)
  - five product verticals (envios99, fulfill99, freight99, tailor99, punto99), business model,
    integration partners, named enterprise customers, "technology, operation, and accompaniment"
    positioning language.
- https://www.itmastersmag.com/inteligencia-artificial/99minutos-usa-agentic-ai-para-prevenir-entregas-erroneas/
  - Nov 24, 2025: "Sherlock" agentic AI project detail, 92%+ correction rate, 18% call-center
    reduction, CTO Jonathan Andrade and CDO Santiago Savinon quotes and titles.
- https://t21.us/freight99-99minutos-new-venture-into-freight-trucking/
  - Aug 26, 2025: Freight99 launch detail, AI features (anomaly detection, operator validation,
    GPS integrations, WhatsApp-mediated comms), CTO Jonathan Andrade and Santiago Savinon
    (titled Chief Growth Officer here) quotes, fleet/partner counts, phase-two expansion plan.
- https://stackshare.io/99minutos/99minutos
  - crowd-sourced tech stack listing (direct WebFetch returned 403; content summarized via
    search index only, treat as lower-confidence/unverified).
- https://www.glassdoor.com/Reviews/99minutos-com-Reviews-E2739596.htm
  - aggregate employee review ratings (overall, compensation, culture), pros/cons themes including
    payment-delay and transparency complaints; self-reported, unverifiable independently.

Lower-confidence items (surfaced via search-index summaries rather than a directly fetched primary
page, or internally inconsistent across sources): the StackShare tech-stack listing; Santiago
Savinon's exact title (Chief Data Officer per IT Masters Mag vs. Chief Growth Officer per T21);
current headcount (estimates range from roughly 900 to 5,000 depending on source and date, none
more recent than 2025 aggregator snapshots). No funding, leadership, or major news items dated
within the last 12 months were found beyond the two AI/product items above; the most recent
capital raise on record is the March 2022 Series C.
