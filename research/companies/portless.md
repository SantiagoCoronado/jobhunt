# Portless (portless.com)

Draft dossier for Santiago Coronado, prepared for the "AI Engineer (Founding seat)" role, job id
10272 ($180k-$230k, remote North America). This is a draft for Santiago to review before use in
application materials.

## 1. Snapshot

Portless is a Toronto-based, venture-backed 3PL and direct-fulfillment platform that lets e-commerce
brands ship straight from manufacturing hubs in China (and soon Vietnam/India) to end customers in
75+ countries, skipping the traditional "buy a container, warehouse it domestically" model
(portless.com/about; betakit.com). Founded May 2023 by Izzy Rosenzweig (also founder of Browze,
2012), it raised an $18M USD ($24.7M CAD) Series A in February 2025 led by Commerce Ventures, with
FJ Labs, eGateway Capital, Red Swan Ventures, and Ground Up Ventures participating
(betakit.com; prweb.com). Reported 300% YoY growth as of that raise, serving mostly $5M-$150M
revenue DTC brands (betakit.com). Headcount is small: Built In lists the company at 42 employees,
Crunchbase brackets it 11-50 (builtin.com/job/engineering-manager/9768814; crunchbase.com). Fully
remote engineering org of roughly 10 people spanning US, Canada, EU, UK, and China
(builtin.com/job/engineering-manager/9768814).

## 2. Core narrative

Portless is a logistics operator that grew out of one DTC brand's own supply-chain pain (its
founders ran a $50M+/year DTC business and built their own Shenzhen fulfillment center to fix it,
then opened that infrastructure to other brands) and is now scaling straight into the biggest
regulatory shock this industry has seen in years: the elimination of the U.S. de minimis exemption
(gone for China/Hong Kong since May 2025, for every country since August 2025, reaffirmed February
2026) and the EU's own de minimis rollback starting July 2026 (fulfill.com/about via WebFetch
summary of portless.com/about; federalregister.gov; portless.com/blogs/the-eu-is-ending-de-minimis-exemptions-what-your-brand-needs-to-know).
Every package now needs a full formal customs entry: commercial invoice, correct HS code, proof of
origin, VAT verification (portless.com/blogs/the-eu-is-ending-de-minimis-exemptions-what-your-brand-needs-to-know).
That is precisely the operational load the AI Engineer posting's example project targets: an agent
that reads an inbound invoice question, pulls the right invoice, and drafts a context-aware reply in
about 30 seconds instead of an hour (job 10272 / HN posting). In other words, this isn't a generic
"add AI to the product" mandate; it's a founding AI seat arriving at the exact moment the company's
core compliance and documentation surface area exploded, with a CEO (Rosenzweig) who is publicly
writing about tariff engineering and trade complexity as his day job (forbes.com/sites/izzyrosenzweig;
npr.org transcript).

## 3. Mission & product

- Mission line on the company site: "At the Intersection of Technology and Logistics, We're
  Redefining Global Delivery for E-Commerce" (portless.com/careers).
- Core product: consolidates brand inventory near origin (Shenzhen fulfillment center, expanding to
  Vietnam and India), then ships direct-to-consumer using domestic-feeling last-mile carriers in
  75+ countries, so brands hold less inventory, get paid back faster, and cut lead times (betakit.com;
  fulfill.com/about via portless.com/about summary).
- Reported outcomes it markets: 2.9M+ packages shipped, 99.8% pick-and-pack accuracy, 98% on-time
  delivery, up to 90% lead-time reduction and 3x faster cash-flow conversion for customers
  (portless.com; portless.com/about).
- Customer base: named clients/case studies include MrBeast, Craft Club, The Woobles, Memobottle,
  Privacy Clo, and Cosara; core segment is $5M-$150M revenue DTC brands (portless.com; betakit.com).
- Product surface is expanding beyond pure fulfillment into adjacent fintech/insurance/compliance:
  "Portless Capital" (invoice financing via Kanmon partnership, 30/60/90-day terms, April 2026),
  "Portless Protect" (package insurance via Onward, March 2026), and an OpenBorder partnership for
  Merchant-of-Record/tax compliance across 180+ countries (April 2026) (updates.portless.com/changelog).
- Platform/portal itself is actively being built out: a new self-serve Inbound Management Portal
  (live shipment status, per-SKU receiving visibility) shipped July 6, 2026, and an "Advanced
  Filtering & Reporting" upgrade to the merchant portal shipped February 2026
  (updates.portless.com/changelog). This is the same portal surface the AI Engineer role is meant to
  build agentic features and reusable APIs/MCP tools on top of.
- Integrations: Shopify, WooCommerce, SellerCloud, X-Cart on the merchant side; internal stack (per
  a separate Senior Software Engineer posting) is Node.js/Express/TypeScript on Google Cloud
  Platform, with Cloud SQL/PostgreSQL, Firestore, ClickHouse, and BigQuery, plus a React/Vite
  frontend, integrating with Order/Warehouse/Transportation Management Systems
  (builtin.com/job/senior-software-engineer/9230702).

## 4. Culture & voice

- Stated values (careers page): "Extreme Ownership" (own outcomes as part of a "kind-and-caring
  team"), "Strategic Boldness" (know when to think outside the box to drive measured merchant
  value), "Operational Precision" (meticulous attention to detail in a fast-paced "0-to-1"
  environment) (portless.com/careers).
- Founder-led public voice: CEO Izzy Rosenzweig writes and speaks constantly in his own name about
  tariffs, trade policy, and supply-chain strategy (Forbes contributor, NPR's The Indicator, multiple
  podcasts), not just through a branded company account (forbes.com/sites/izzyrosenzweig;
  npr.org/transcripts/nx-s1-5515756; dynamo.vc podcast page).
- Company blog tone is practical and urgency-driven: regulatory explainers (de minimis, EU customs
  changes) written with clear deadlines, tables, and concrete cost/timeline breakdowns rather than
  abstract brand marketing (portless.com/blogs/the-eu-is-ending-de-minimis-exemptions-what-your-brand-needs-to-know).
- Explicit internal embrace of AI-assisted engineering: the Engineering Manager posting asks the hire
  to "standardize and optimize the team's usage of modern AI development tools (e.g., Cursor,
  Copilot, Claude Code)" and to "champion AI-augmented development" as a stated responsibility, not a
  nice-to-have (builtin.com/job/engineering-manager/9768814).
- Work style: remote-first, documentation-first, asynchronous-by-default across US/Canada/EU/UK/
  China time zones, with DORA metrics used to track delivery health
  (builtin.com/job/engineering-manager/9768814; builtin.com/job/senior-software-engineer/9230702).

## 5. Recent news (last ~12 months, dated)

- February 2025: closes $18M USD ($24.7M CAD) Series A led by Commerce Ventures, with FJ Labs,
  eGateway Capital, Red Swan Ventures, Ground Up Ventures; announcement frames it explicitly against
  the incoming Trump tariff executive orders (betakit.com; prweb.com; finsmes.com).
- May 2025 and August 2025: U.S. de minimis exemption eliminated first for China/Hong Kong, then for
  all countries, directly hitting the low-value cross-border shipping model Portless's customers rely
  on (federalregister.gov; smartasset.com).
- August 2025: Rosenzweig discusses "tariff engineering" (country-of-origin component strategies) on
  NPR's The Indicator (npr.org/transcripts/nx-s1-5515756).
- February 2026: White House confirms continuing suspension of de minimis treatment for all countries
  (whitehouse.gov presidential action, Feb 2026), and EU Council gives final approval to end its own
  de minimis exemption starting July 1, 2026 (federalregister.gov; EU de minimis coverage cited in
  portless.com blog post).
- February-July 2026: rapid product expansion beyond fulfillment: advanced portal filtering/reporting
  (Feb 22), Portless Protect package insurance with Onward (Mar 3), OpenBorder Merchant-of-Record
  partnership for 180+ country expansion (Apr 2), Portless Capital invoice financing with Kanmon
  (Apr 8), and a new self-serve Inbound Management Portal (Jul 6) (updates.portless.com/changelog).
- June 30, 2026: Rosenzweig publishes a Forbes piece arguing that shifting final assembly to Vietnam
  does not actually reduce China dependence, reinforcing his public role as an industry voice on
  supply-chain/trade strategy (forbes.com/sites/izzyrosenzweig/2026/06/30).
- July 2026: posts the "AI Engineer (Founding seat)" role on Hacker News "Who is hiring?" and on its
  own Workable/Built In job boards, its first dedicated AI hire (job 10272 / HN item 48889875;
  builtin.com/job/ai-engineer/9551393). A separate Engineering Manager posting (also open now)
  confirms the engineering org is ~10 people and reports up to a VP of Engineering
  (builtin.com/job/engineering-manager/9768814).

## 6. Engineering & AI direction

- Today's AI usage is explicitly described by the company itself as basic: "decks, spreadsheets, a
  few people vibe-coding dashboards. No real agentic workflows yet" (job 10272 / HN posting). This
  role exists to change that.
- Mandate: ship agentic workflows directly (first example: an inbound-invoice-question agent that
  reads the question, retrieves the right invoice, and drafts a context-aware reply, cutting an hour
  of manual work to about 30 seconds) and, in parallel, build reusable building blocks (APIs, MCP
  tools, documentation) so other teams at Portless can build their own AI features afterward (job
  10272 / HN posting). This is a platform mandate, not a single-feature build.
- A fuller version of the role posted on Built In elaborates the same job: design AI features across
  B2B merchant portals and internal tools, translate business problems into scoped AI solutions with
  prompt engineering and agentic workflows, run experiment-driven evals on quality/latency/cost,
  build internal AI tooling for non-technical teams, and integrate third-party AI APIs securely
  (builtin.com/job/ai-engineer/9551393).
- Named stack/tools in that fuller posting: Claude and GPT APIs, LangChain or LlamaIndex, vector
  databases (Pinecone, Weaviate, pgvector), and, as a "nice to have," Model Context Protocol (MCP)
  and multi-step agent orchestration (builtin.com/job/ai-engineer/9551393) - directly matching the
  MCP-tools language in the founding-seat posting (job 10272).
- Required background: 3+ years SWE, 1-2+ years shipping production AI, 10+ real agentic/LLM
  workflows built end-to-end, a genuine platform mindset (built tools/infra for others, not just
  yourself), strong Python and/or TypeScript, and e-commerce/3PL/logistics/B2B sector background as a
  plus (job 10272 / HN posting).
- Broader engineering org runs Node.js/Express/TypeScript on GCP (Cloud SQL/Postgres, Firestore,
  ClickHouse, BigQuery) with a React/Vite frontend, fault-tolerant international shipping workflows
  (retries, idempotency keys, dead-letter queues), and elite DORA metrics as a stated bar
  (builtin.com/job/senior-software-engineer/9230702). The concurrently open Engineering Manager role
  confirms leadership already actively "champions AI-augmented development" and standardizes on
  Cursor, GitHub Copilot, and Claude Code across the team (builtin.com/job/engineering-manager/9768814),
  meaning the founding AI engineer is not evangelizing AI-assisted coding into a skeptical org, that
  part is already assumed.
- No dedicated public engineering/AI blog was found; Portless's public blog is customer/market-facing
  (case studies, tariff and de minimis explainers), not technical (portless.com/case-studies-blog).
  Flag this: AI/engineering culture had to be pieced together from job postings, not a blog, so it is
  thinner and more inference-based than an ideal source set.

## 7. Why-fit angles for Santiago

Best single hook to lead with: Santiago has already built the exact shape of thing this role
describes, an agent that turns a slow manual document/reply workflow into a fast automated one, plus
the reusable plumbing (APIs, MCP tools) so it is not a one-off. His Plutus project ships an MCP
control plane exposing an LLM research agent and autonomous discovery engine as reusable tools, not
just a personal script, which is close to the "shipping agentic workflows yourself, plus reusable
building blocks (APIs, MCP tools, docs) so any team can build their own" mandate almost line for line
(resume/master_resume.yaml; job 10272).

Supporting angles:
- Production LLM workflow experience is real and dated, not a hobby project: at Online Basics he
  designed an LLM workflow on the Anthropic and OpenAI APIs with custom prompt engineering and a
  multi-stage validation pipeline, generating 100+ product listings a month and cutting
  content-creation time 70% at $8M revenue scale on Amazon and Mercado Libre, an e-commerce
  operations context that overlaps with Portless's own DTC/e-commerce customer base
  (resume/master_resume.yaml).
- Platform mindset, not just personal tooling: Kairos exposes the same 18 tools through both an
  in-app Claude Agent SDK integration and a standalone MCP server from one typed tool-definition
  layer, i.e. built once, reusable by multiple surfaces, which is the specific "platform mindset
  (built tools/infra for others, not just yourself)" bar the posting calls out (resume/master_resume.yaml;
  job 10272).
- RAG and eval-adjacent experience: "Pragma Brain" is a RAG company-brain product built and shipped
  to clients, and Plutus's discovery engine includes vectorized signal scans and an evidence-backed
  ranking pipeline, both relevant to the posting's RAG/vector-DB/eval nice-to-haves
  (resume/master_resume.yaml; builtin.com/job/ai-engineer/9551393).
- Python and TypeScript both show up as daily-driver languages across FastAPI/SQLAlchemy backends and
  React/TypeScript frontends (Plutus, Kairos, Eugenia.ai), matching "strong Python and/or TypeScript"
  as a hard requirement, not a stretch (resume/master_resume.yaml; job 10272).
- Founder pattern: three ventures (Online Basics, Eugenia.ai, Pragma AI) each involved 0-to-1 build
  and product ownership under real operational pressure, a natural match for a literal "founding
  seat" with no existing AI playbook to follow (resume/master_resume.yaml; job 10272).

Honest concerns / watch-outs:
- Direct e-commerce/3PL/logistics sector depth is thinner than a specialist candidate's: Santiago's
  e-commerce experience is running his own Amazon/Mercado Libre brand (demand side), not building
  fulfillment, customs, or warehouse-management software (supply side); the JD lists sector
  background as "a plus," not a hard requirement, but this is worth naming honestly rather than
  overselling (resume/master_resume.yaml; job 10272).
- The "10+ real agentic/LLM workflows built end-to-end" bar is specific and countable; Santiago's
  resume names a handful of distinct systems (Online Basics listing pipeline, Pragma Brain RAG,
  Hermes finance agent, Plutus research agent, Kairos agent/MCP layer). This is a real, defensible
  list, but it should be prepared as an explicit, countable inventory before an interview rather than
  left implicit, since the JD explicitly screens on a number.
- Company is small (roughly 42 people, ~10 engineers) and only 2-3 years past founding on a single
  Series A; no evidence of a Series B or larger raise was found, so runway and stability are
  reasonable questions to ask directly rather than assume (builtin.com/job/engineering-manager/9768814;
  betakit.com).
- No public salary band beyond what the HN posting itself states ($180k-$230k); no equity, benefits,
  or visa-sponsorship language was found in any public posting, so U.S. work authorization (TN
  eligibility) and remote-from-Mexico logistics should be raised early, not assumed
  (job 10272; config/profile.yaml notes TN-visa eligibility, not U.S. citizenship).
- Compliance/customs-documentation depth (HS codes, proof of origin, VAT) is a real domain the
  invoice-agent example project touches; this is learnable but is a genuine knowledge gap today, not
  something on the resume (portless.com/blogs/the-eu-is-ending-de-minimis-exemptions-what-your-brand-needs-to-know).

## 8. Application-question angles (narrative-led, not full answers)

- Why this company: lean on timing, not the fulfillment-industry label in the abstract. Portless is
  hitting the exact moment its core compliance and documentation load exploded (de minimis gone in
  the U.S. and now the EU, every package needing a full formal customs entry) at the same time it is
  making its first dedicated AI hire, with a CEO who is personally out front on trade-policy
  complexity. That is a company where an AI agent for invoice/customs questions is not a nice demo,
  it is load-bearing on day one.
- Why you fit: lead with the MCP/reusable-tooling overlap, not a skills checklist. Santiago has
  already shipped the "agent plus reusable building blocks so other people can build on it" pattern
  (Plutus's MCP control plane, Kairos's shared typed tool layer across an app and Claude Code), which
  is close to a rehearsal of this exact founding-seat mandate, on top of dated production LLM-workflow
  experience in e-commerce operations at Online Basics.
- Anything else: worth surfacing plainly that his e-commerce background is demand-side (ran his own
  Amazon/Mercado Libre brand) rather than 3PL/logistics-software-side, and naming that as something he
  is ready to ramp on fast rather than hoping it goes unnoticed; also worth flagging TN-visa status
  and remote-from-Mexico City logistics early given no visa/location language appears in the public
  posting.

## Sources

- https://www.portless.com/about , founding story (own $50M+ DTC brand, Shenzhen fulfillment center),
  mission language, scale metrics (2.9M packages, 75+ countries, 99.8% accuracy), investor names.
- https://www.portless.com/ , product/value proposition, named clients (MrBeast, Craft Club, The
  Woobles, Memobottle, Privacy Clo, Cosara), case-study metrics, platform integrations.
- https://www.portless.com/careers , mission tagline, stated values (Extreme Ownership, Strategic
  Boldness, Operational Precision).
- https://www.portless.com/case-studies-blog , confirms public blog is customer/market-facing, not a
  technical engineering blog.
- https://www.portless.com/blogs/the-eu-is-ending-de-minimis-exemptions-what-your-brand-needs-to-know ,
  EU de minimis rollback details, documentation/invoice complexity (HS codes, proof of origin, VAT),
  company tone/voice.
- https://updates.portless.com/changelog , dated 2026 product releases: Inbound Management Portal
  (Jul 6), Portless Capital/Kanmon (Apr 8), OpenBorder (Apr 2), Portless Protect/Onward (Mar 3),
  portal filtering upgrade (Feb 22).
- https://betakit.com/portless-raises-24-7-million-to-be-retailers-port-in-a-trade-storm/ , Series A
  details (amount, date, investors), founder background (Izzy Rosenzweig, Browze), HQ, growth metrics
  (300% YoY), customer revenue band ($5M-$150M).
- https://www.prweb.com/releases/portless-secures-18m-funding-to-revolutionize-global-e-commerce-and-dtc-fulfillment-302469087.html
  and https://www.finsmes.com/2025/06/portless-raises-18m-in-funding.html , corroborating Series A
  announcement, investor quotes, use-of-funds language.
- https://www.npr.org/transcripts/nx-s1-5515756 , Rosenzweig on NPR's The Indicator discussing tariff
  engineering (August 2025).
- https://www.forbes.com/sites/izzyrosenzweig/2026/06/30/why-moving-production-to-vietnam-doesnt-end-china-dependence/ ,
  Rosenzweig's Forbes contributor piece (June 30, 2026), confirms his ongoing public trade-policy
  voice.
- https://www.federalregister.gov/documents/2026/06/24/2026-12670/indefinite-suspension-of-the-de-minimis-exemption-for-merchandise-arriving-through-all-modes-other-than-the-international-postal-network
  and https://www.whitehouse.gov/presidential-actions/2026/02/continuing-the-suspension-of-duty-free-de-minimis-treatment-for-all-countries/ ,
  primary U.S. government confirmation of de minimis elimination timeline (2025-2026).
- https://news.ycombinator.com/item?id=48889875 , primary source, full text of the "AI Engineer
  (Founding seat)" posting as ingested (job id 10272): mandate, example project, requirements,
  compensation, remote North America.
- https://builtin.com/job/ai-engineer/9551393 , fuller/parallel version of the AI Engineer posting:
  detailed responsibilities, named tools (LangChain/LlamaIndex, Pinecone/Weaviate/pgvector, MCP),
  company headcount (42 employees).
- https://builtin.com/job/engineering-manager/9768814 , concurrently open Engineering Manager role:
  confirms ~10-person globally distributed engineering team, VP of Engineering reporting line,
  existing internal use of Cursor/GitHub Copilot/Claude Code, DORA metrics culture.
- https://builtin.com/job/senior-software-engineer/9230702 , broader engineering stack (Node.js,
  Express, TypeScript, GCP, Cloud SQL/Postgres, Firestore, ClickHouse, BigQuery, React/Vite),
  engineering practices (fault tolerance, DORA metrics, async-first).
- https://www.crunchbase.com/organization/portless , corroborating headcount bracket (11-50) and
  Series A round record.
- Job id 10272 in this pipeline's database (`.venv/bin/python -m src.query job 10272`), the ingested
  posting text used as the primary JD source for this dossier.
- Note: the application/apply link (https://uctalent.io/referral/Huynh_Nhu_Bao_Nhan221138/DNwhgw) is
  a JS-rendered referral page that could not be fetched for additional content; the HN posting (job
  10272) was used as the authoritative full-text source instead.

researched: 2026-07-14
