# Cryptio

**Role in view:** Applied AI Engineer (Remote), job id 8864, posted 2026-06-18.
https://findwork.dev/nZlpavM/applied-ai-engineer-at-cryptio

## 1. Snapshot

Cryptio builds enterprise-grade financial data transformation and digital-asset ERP software
(accounting, reconciliation, financial reporting, tokenization compliance, loan management) for
regulated institutions holding crypto. Founded 2018, Paris, by CEO Antoine Scalia. Remote-first
international team with hubs in Paris, London and New York; roughly 110 employees. Closed a $45M
Series B in March 2026 (total raised roughly $71.2M), serving 450+ institutional clients including
Circle and Societe Generale's SG Forge, with over $3 trillion in transactions processed.
(Sources: coindesk.com Series B article; fortune.com; cryptio.co)

## 2. Core narrative

Cryptio sits at the point where crypto is being absorbed into regulated finance: its pitch is
literally "financial integrity in tokenized finance," and its Series B lands as institutions
(banks, stablecoin issuers, asset managers) start treating digital assets as auditable balance
sheet items rather than a side bet. The Applied AI Engineer role is the company's first hire on a
brand-new "Advisory Intelligence" line: AI tooling for accounting workflows (close, chart of
accounts benchmarking, policy generation, audit fit-gap) where deterministic logic and LLM layers
are deliberately kept separate because "being wrong has financial consequences." This is a company
betting that AI-assisted accounting only works if it is auditable, not just impressive: a natural
extension of, not a departure from, their existing SOC 1/2 Type II compliance posture.
(Sources: cryptio.co homepage; job description; coindesk.com)

## 3. Mission & product

- Platform ingests on-chain and off-chain crypto activity across 150+ blockchains, exchanges,
  custodians and DeFi protocols, and normalizes it into audit-ready records for accounting,
  treasury, tax, licensing and regulatory reporting. (cryptio.co)
- Serves regulated institutions: banks, exchanges, brokers, treasury companies, asset managers,
  stablecoin issuers, payments firms, miners, DeFi enterprises, accounting firms. Named clients
  include Circle (CRCL) and Societe Generale's SG Forge; also Uniswap, Consensys and 1inch are
  referenced on the careers page as clients/partners. (cryptio.co, cryptio.co/careers)
- Enterprise SaaS, SOC 1 and SOC 2 Type II certified, built for GAAP/IFRS compliance.
  (cryptio.co)
- Business is expanding beyond accounting into loan management and treasury management as
  additional ERP-style modules, funded by the new Series B. (fortune.com Series B article)

## 4. Culture & voice

- Stated values (careers page): "Bias for action," "Build trust with your team," "If it's worth
  doing, it's worth doing well," "Stay curious." (cryptio.co/careers)
- Self-description: remote-first international team, employees can choose fully remote, hybrid,
  or office-based (hubs in Paris, London, New York); high autonomy, "trusted to do your best work."
  (cryptio.co/careers)
- Voice is direct and outcome-focused rather than irreverent: "we eat challenges for breakfast,"
  5x YoY revenue growth cited as a point of pride. (cryptio.co/careers)
- Glassdoor reviews are mixed: some describe supportive teammates and leadership that trusts
  people to own their work; others describe the culture as cliquey with a legacy leadership group
  resistant to change. Treat as an unverified, secondhand signal rather than company narrative.
  (glassdoor.com/Reviews/Cryptio-Reviews-E6912365.htm)

## 5. Recent news (last ~12 months)

- **2026-03-12**: Closed $45M Series B led by BlackFin Capital Partners and Sentinel Global, with
  1kx, BlueYard Capital and Ledger Cathay Capital participating; brings total funding to roughly
  $71.2M. CEO quote: "We started to see what we've been promised since day one, that the
  institutions are coming." Reported headcount ~110, client count 450+.
  (coindesk.com/business/2026/03/12/...; fortune.com/2026/03/12/...; businesswire.com press
  release)
- **2026 (ongoing)**: Actively hiring for a new "Advisory Intelligence" function, including a
  Senior Software Engineer, Intelligence role and this Applied AI Engineer role, its first
  dedicated applied-AI hire. Signals a real, funded push into AI-assisted accounting product,
  not just a single job posting. (jobs.ashbyhq.com/cryptio; job description for id 8864)
- **Prior round**: Series A extended to $25M (date reported as "last year" relative to the March
  2026 Series B coverage), led by Alven with 1kx and Ledger Cathay Capital joining, alongside
  existing backers Point Nine, BlueYard, Tim Draper and Charlie Songhurst.
  (cathaycapital.com Series A press release)

## 6. Engineering & AI direction

- No dedicated public engineering blog was found; direction here is inferred from the job
  description itself (the most detailed primary source available) plus adjacent job postings.
- Stack signaled by the JD: production TypeScript full stack, Node.js backend (REST APIs,
  middleware auth, async pipelines with batching/concurrency/retries), React with Zustand for
  state and Zod for schema validation, Postgres (workflow/run-oriented schemas, append-only
  audit-trail design), exposure to distributed systems. Bonus: Next.js App Router, background job
  infra (BullMQ, pg-boss), AWS, Docker, CI/CD. (job description, job id 8864)
- AI direction: explicitly a hybrid architecture, deterministic logic for anything with financial
  consequences, AI layers on top drawing on a structured library of real client engagements.
  Multi-step AI pipelines (prompt chaining, structured output parsing, confidence scoring,
  failure recovery, audit-trail logging), an AI output evaluation framework (test inputs, expected
  outputs, scoring rubrics), and document ingestion (parsing spreadsheets/structured reports into
  typed data models). Bonus points explicitly list AWS Bedrock, OpenAI, and the Anthropic SDK "at
  real throughput," plus experience debugging AI in production. (job description, job id 8864)
- Team structure for this function is deliberately small: one Applied AI Engineer (this hire)
  working directly with an Advisory Intelligence Product Engineer and a VP of Advisory
  Intelligence, high autonomy, full-stack ownership without handoffs. (job description, job id
  8864)

## 7. Why-fit angles for Santiago

**Best hook to lead with:** Santiago has already built, on his own initiative, the exact shape of
system Cryptio is standing up a team to build: an AI layer over a deterministic domain where being
wrong is costly. Pragma Brain is a RAG "company brain" over real business data; Hermes is a
function-calling agent with tool use; Plutus pairs deterministic backtesting and screening with an
LLM research agent behind an MCP control plane, i.e. exactly the "deterministic core plus AI layer
with structured evaluation" pattern the JD describes for Advisory Intelligence. That is a rare,
specific match, not a generic AI-engineer overlap.

Supporting angles:
- Full-stack ownership from schema to UI: Santiago's whole career (Online Basics, Eugenia.ai,
  Pragma AI, Plutus, Kairos) is 0-to-1, founder-owned, schema-to-UI building, which maps directly
  to "own full-stack feature delivery from Postgres schema through API layer through React UI."
- Fintech/payments adjacency: Online Basics ran on Amazon/Mercado Libre financial and operational
  data pipelines processing 100K+ daily data points; Eugenia.ai handled fee management. Not
  accounting-specific, but real experience with financial data integrity and reconciliation-style
  problems.
- High-autonomy, small-team seat: Santiago is a 3x founder used to working without handoffs,
  which matches "the team is small on purpose."

**Honest gaps / watch-outs:**
- No direct GAAP/IFRS, audit, or accounting-domain experience; the JD lists this as a bonus, not
  a requirement, but it is a real gap worth naming rather than glossing over.
- Postgres experience for workflow/run-oriented, append-only audit-trail schemas at "table scale"
  is not explicitly evidenced in the resume; his Postgres work (Plutus) is closer to
  time-series/market-data schemas than compliance audit trails.
- The JD's core requirement is production TypeScript/Node.js full stack "shipped real systems,
  not side projects." Santiago's production TypeScript work (Eugenia.ai, Kairos) is real but
  smaller-scale than Cryptio's enterprise financial workloads; this should be framed honestly as
  founder-scale production experience, not enterprise-scale.
- Company is Paris-founded with hubs in Paris/London/New York; no explicit confirmation that
  remote hiring extends to Mexico or LATAM specifically. The JD lists "Remote or Hybrid working"
  as a perk without a location restriction, and this specific posting is tagged remote, but
  Santiago should confirm timezone/geo expectations in the application or an early conversation.

## 8. Application-question angles

- **Why this company:** Lead with the Advisory Intelligence narrative, not "crypto is cool" or a
  generic AI-adoption pitch. Cryptio is building the first dedicated AI function on top of a
  compliance-grade financial platform, at the exact moment institutional money is moving into
  digital assets (the Series B thesis). Frame interest around wanting to build AI that has to be
  trustworthy by construction, because the domain punishes hand-waving.
- **Why you fit:** Do not list all of RAG, agents, MCP, fintech, full-stack. Pick the deterministic-
  core-plus-AI-layer pattern (Plutus/Hermes/Pragma Brain) as the single throughline, and connect
  it to the "own it end to end, small team, no handoffs" seat structure. One concrete example
  (e.g. how Plutus separates rule-based screening from the LLM research agent, or how Pragma Brain
  is scoped to real client data rather than generic chat) beats a skills list.
- **Anything else:** Use this to proactively name the accounting-domain gap rather than let it
  surface later, then pivot to what transfers: shipping production financial/operational data
  pipelines solo and fast, and being comfortable learning a new domain's rules (GAAP/IFRS) the way
  he learned e-commerce SEO/marketplace mechanics or property-management workflows before.

## Sources

- Job description (id 8864): https://findwork.dev/nZlpavM/applied-ai-engineer-at-cryptio
- Company site, product/mission/customers: https://cryptio.co/
- Careers page, values and culture: https://cryptio.co/careers
- Series B coverage (funding, headcount, clients, CEO quote):
  https://www.coindesk.com/business/2026/03/12/crypto-accounting-firm-cryptio-raises-usd45-million-in-series-b-funding-round
- Series B coverage (headcount corroboration, investor list, valuation note):
  https://fortune.com/2026/03/12/cryptio-series-b-fundraise-blackfin-capital-partners-sentinel-global/
- Series B press release: https://www.businesswire.com/news/home/20260312303330/en/Cryptio-Raises-$45m-Series-B-as-Digital-Assets-Move-Into-Regulated-Financial-Markets
- Series A extension to $25M, investor list: https://www.cathaycapital.com/leading-financial-data-platform-cryptio-expands-series-a-funding-to-25m/
- Advisory Intelligence / Applied AI Engineer role mirrored posting and related open role
  (Senior Software Engineer, Intelligence): https://jobs.ashbyhq.com/cryptio
- Glassdoor reviews (secondhand culture signal, mixed):
  https://www.glassdoor.com/Reviews/Cryptio-Reviews-E6912365.htm
- Candidate background: /Users/santiagocoronado/jobhunt/config/profile.yaml,
  /Users/santiagocoronado/jobhunt/resume/master_resume.yaml

researched: 2026-07-14
