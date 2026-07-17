# Rhizome AI

Draft dossier for Santiago Coronado, prepared for the "Founding Full Stack AI Engineer" role
(fully remote). Review and refresh before relying on it for an application.

## 1. Snapshot

Rhizome AI is a Y Combinator W26 (Winter 2026) startup building a RAG powered regulatory
intelligence agent for life sciences: teams ask a question about FDA, EMA, MHRA, or PMDA
requirements and get a citation backed answer drawn from a 2.5+ TB corpus of regulatory and
clinical documents, with no hallucinations claimed. Solo founder and CEO Chetan Mishra; the
working team is described as "remote team of 4" with six figure ARR and growing (per the job
listing and a third party writeup, not a primary Rhizome source). HQ listed as Jersey City, New
Jersey; the company is remote first. Funding: participated in YC W26; no funding amount, round, or
investor list was publicly disclosed in any source checked (YC's standard batch investment terms
were not confirmed for this company specifically, so no number is stated here).

## 2. Core narrative

Rhizome is chasing a specific, unglamorous, high stakes bottleneck: regulatory affairs teams in
biotech, pharma, and medtech must manually dig through thousands of pages of FDA/EMA precedent
before they can plan a study or file a submission, and a single missed precedent can delay a
therapy's approval by months. Rhizome's bet is that a citation grounded RAG system, built on a
continuously synced 44 to 46 million document corpus of primary regulatory sources, can compress
that research from weeks to minutes without hallucinating, because in regulatory affairs a
plausible-sounding wrong answer is worse than no answer. The founder is explicitly positioning
against "AI startups that focus on drug discovery" while few address getting a drug through
regulatory approval and to market; the stated long run mission is to "universally organize and
make accessible the world's life science information" so that 10x more therapies can reach
patients.

## 3. Mission & product

- Product: "Rhizome Ask," a research agent that answers regulatory questions with citations to up
  to 1,000 source documents per query, covering FDA, EMA, UK MHRA, Japan's PMDA and global clinical
  trial registries. (rhizomeai.com; YC launch post)
- Data layer: 2.5+ TB of public regulatory and clinical data, described variously as 44 million,
  46.2 million documents, and 59 to 67 datasets across roughly 10 countries or markets (the exact
  figures shift slightly across sources and appear to be updated over time as the corpus grows;
  treat as "tens of millions of documents, several dozen datasets, ~10 markets"). (rhizomeai.com;
  startuphub.ai)
- Architecture (per founder interview): purpose built RAG with dense vector search and
  regulatory specific re ranking; hallucination mitigation via fine tuning on QA pairs plus
  citation grounding at inference time; heavy investment in ingestion/normalization because source
  documents are often scanned PDFs with inconsistent formatting and metadata. (datainnovation.org
  Q&A with Chetan Mishra)
- Business model: usage/seat based SaaS. Pricing tiers cited (with some variation across sources
  and time): roughly $400/month project tier, $3,500 to $4,000/year professional tier, up to
  $20,000 to $30,000/year for a 5 seat business tier, and custom enterprise pricing with an
  on-premise/secure-enclave option for large customers. (startuphub.ai; rhizomeai.com)
- Customers: regulatory affairs managers, directors and VPs at clinical stage biotech, mid-size to
  top-5 pharma, medtech/device companies, and the consultants who serve them; 20+ paying customers
  and 2,800+ answered queries reported as of mid-2026. (rhizomeai.com)
- Company origin: the founder has said Rhizome pivoted from an earlier idea (a healthcare data
  exchange) before landing on regulatory intelligence as the core problem. (LinkedIn founder post)

## 4. Culture & voice

- Solo technical founder, Chetan Mishra, with deep AI infra pedigree: product engineer #1 /
  employee #15 at EvolutionaryScale (the protein design AI company spun out of work related to
  Meta AI's ESM models), where he built and scaled their inference platform to billions of API
  calls; before that, employee #16 at Instabase, technical lead on a $7M banking/insurance document
  processing deal; co-author on a Science magazine cover paper. (YC company page; startuphub.ai;
  LinkedIn)
- Voice is founder led, direct, and metrics forward: launch and social posts lean on concrete
  customer quotes ("Last time we did this research, we spent weeks. Rhizome found the answer
  immediately") rather than marketing copy. (YC launch post; LinkedIn)
- The job listing itself is a strong culture signal: async, written first communication, high
  autonomy, explicit expectation to "hand-write less than 10% of the code that you ship to prod"
  (i.e. AI assisted/agentic coding is the default way of working, not an exception), quarterly
  in-person offsites, and a stated preference for engineers who have worked at small (<50 person),
  VC backed American companies before. (findwork.dev job posting)
- Framing throughout is mission driven around patients and speed to therapy, not just enterprise
  SaaS metrics: "bring more therapies to patients faster" and "10x the number of therapies coming
  to market" are repeated framings. (datainnovation.org; YC company page)

## 5. Recent news (last ~12 months)

- Feb 2026: Rhizome AI publicly launches via Y Combinator's Launch YC program ("Know what the FDA
  thinks"), announcing the W26 batch participation and product. (ycombinator.com/launches;
  LinkedIn founder announcement)
- Feb 2026: Founder Chetan Mishra gives a "5 Questions" interview to the Center for Data
  Innovation covering product architecture, data sources, and accuracy approach.
  (datainnovation.org)
- As of the job posting (found dated roughly mid 2026, "posted 1 month ago" relative to a July
  2026 check) and a May 17, 2026 third party writeup: team has grown to a "remote team of 4," has
  crossed six figures in ARR and is "climbing rapidly," 20+ paying customers, 2,800+ answers
  served, zero hallucinations reported for 2025. (findwork.dev; startuphub.ai; rhizomeai.com)
- No specific funding round, amount, or investor names beyond YC W26 participation were found in
  any source checked (Crunchbase blocked scraping; no press release with a dollar figure was
  located). Treat funding as unconfirmed/unverified beyond "YC W26 batch company."

## 6. Engineering & AI direction

- Stack (from the job posting): Next.js, TypeScript, and Tailwind on the frontend; FastAPI/Python
  on the backend; PostgreSQL plus ParadeDB (Postgres extension for search/analytics) as the data
  layer; DigitalOcean for infra; Clerk for auth; Logfire and Checkly for observability/monitoring;
  PostHog for product analytics; Anthropic and OpenAI as the model providers. (findwork.dev job
  posting)
- Data infrastructure is a first class engineering problem here, not an afterthought: the role
  explicitly scales "data infrastructure pipelines from 55 current pipelines to 125 by year end and
  500 by 2027," alongside OCR accuracy, indexing, retrieval and citation quality work. (findwork.dev
  job posting)
- The role spans the full stack of an AI product: OCR ingestion, retrieval, agent layer, and user
  facing UI, plus building specialized agents to automate regulatory affairs workflows and
  supporting an internal "AI Regulatory Affairs team" with document editing/monitoring tools.
  (findwork.dev job posting)
- AI native engineering culture: the explicit expectation that engineers hand-write under 10% of
  shipped code implies heavy use of AI coding agents (Claude Code class tooling) as the default
  workflow, not a novelty. (findwork.dev job posting)
- Founder's own technical background (inference platforms at scale, document processing for
  regulated industries) suggests the engineering bar and taste come from someone who has personally
  built and scaled production ML infrastructure, not just directed it. (YC company page;
  startuphub.ai)

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago has already built the exact shape of product Rhizome is hiring
for, a RAG "company brain" that ingests messy source data and answers natural language questions
with grounded output, and he did it as a 3x founder shipping 0-to-1, not as a large-company IC
executing someone else's spec. That is a rare, specific match to a "founding engineer" role at a
4 person team.

- Full-stack + RAG "company brain" experience: at Pragma AI he built "Pragma Brain," a RAG system
  that ingests a company's internal data to answer questions and auto-generate reports, plus
  conversational agents and automations; this is structurally the same problem as Rhizome Ask
  (ingest domain documents, answer questions, cite sources), just in a different vertical.
  (resume/master_resume.yaml)
- Founder mindset for a 4-person team: 3x founder (Online Basics to $8M revenue on a 9-person team,
  Eugenia.ai built to acquisition, Pragma AI co-founded now) means he is used to owning outcomes
  end to end with no safety net, which maps directly to Rhizome's "founding engineer, high
  autonomy, own database to UI" framing.
  (resume/master_resume.yaml)
- Full-stack range matches the stack: React/Node/TypeScript (Eugenia.ai), Python/FastAPI backends
  and Postgres (Plutus project), Claude/Anthropic API and agent tooling used daily; this lines up
  closely with Rhizome's Next.js/TypeScript/FastAPI/Postgres/Anthropic stack.
  (resume/master_resume.yaml)
- AI-native workflow fit: Santiago uses Claude Code daily and has built both an in-app Claude
  agent and an MCP server (Kairos project), which is directly relevant to a team that expects
  engineers to ship mostly AI-generated code and build agent layers, not just call an LLM API.
  (resume/master_resume.yaml)
- Remote and timezone: role is fully remote with a 5-hour Pacific Time overlap requirement; Mexico
  City (GMT-6) overlaps essentially all of a Pacific business day, so this is a non-issue logistically.
  (findwork.dev job posting; config/profile.yaml)

Honest concerns / watch-outs:

- Life sciences and FDA/EMA regulatory domain is genuinely new territory for Santiago; his prior
  domains are PropTech, e-commerce, personal finance and general SMB consulting, not pharma or
  regulatory affairs. This is a real learning curve the role itself acknowledges ("learning domain
  expertise in drug development lifecycles and clinical trial phases" is listed as a job
  responsibility), so it is addressable but should be named honestly.
- The posting states a preference for candidates with prior experience at a small (<50 person),
  VC-backed American company. Santiago has founded and run small companies (not been an employee
  at one), which is an adjacent but not identical background; worth acknowledging and reframing as
  "founder-level ownership, not just employee experience at one."
- Extremely early stage and small (roughly 4 people, six figure ARR, no confirmed funding amount
  publicly): high upside but real risk of runway, product-market-fit, and role scope shifting
  quickly. No confirmed funding round was found, so financial runway is unverified.
- Compensation and equity were not disclosed in any source checked; confirm directly before or
  during the process given the stated $65k minimum in Santiago's profile.

## 8. Application-question angles

- Why this company: lead with the "company brain" parallel, not a generic "I love AI startups"
  line. Santiago already built a RAG system that turns a company's messy internal data into
  cited, trustworthy answers (Pragma Brain); Rhizome is solving the same core problem
  (turn a huge, messy corpus of regulatory documents into citation-grounded answers) for a domain
  where a wrong answer has real cost (delayed drug approvals). Name the specific resonance: he is
  not learning what RAG is for this role, he is bringing a system he has already shipped into a
  harder, higher-stakes vertical.
- Why you fit: anchor on founder-level ownership at a founding-engineer scope. Three ventures where
  he owned the full stack (product, infra, and often the client relationship) map directly onto a
  4-person team that wants someone who can go from database to UI with minimal hand holding and is
  fluent in AI-assisted/agentic coding as a default workflow, not an add-on skill.
  Reference his Claude Code fluency and the MCP server he built (Kairos) as evidence he already
  works the way this team expects engineers to work.
- Anything else: be direct about the domain gap (life sciences/regulatory is new) and frame it as
  a fast-learning founder trait rather than avoid it. His track record is repeatedly picking up a
  new domain (PropTech, e-commerce operations, personal finance, SMB consulting) and shipping
  production systems in it within months; that pattern, not prior pharma experience, is the
  relevant signal for a team this early and this small.

## 9. Sources

- researched: 2026-07-13
- https://www.ycombinator.com/companies/rhizome-ai (company overview, founder bio, HQ, batch, team
  size as shown on YC page, primary partner)
- https://www.ycombinator.com/launches/PIq-rhizome-ai-know-what-the-fda-thinks (launch post:
  product description, mission, founder motivation, customer quotes)
- https://findwork.dev/njjN9dn/founding-full-stack-ai-engineer-at-rhizome-ai (full job posting:
  responsibilities, requirements, tech stack, "remote team of 4," six-figure ARR)
- https://www.startuphub.ai/ai-news/claudes-corner/2026/claudes-corner-rhizome-ai-yc-w2026
  (product/technology detail, traction numbers, pricing, dated May 17, 2026)
- https://rhizomeai.com/ (company site: mission statement, product description, pricing tiers,
  customer segments, document/dataset counts as of the site's last update)
- https://datainnovation.org/2026/02/5-qs-with-chetan-mishra-ceo-of-rhizome-ai/ (founder Q&A:
  architecture, data sourcing, accuracy approach, vision)
- https://www.linkedin.com/posts/chemishra_happy-to-announce-rhizome-ai-yc-w26-is-activity-7421997015070486528-9ukf
  (founder's YC announcement post: origin story/pivot, tone, early customer count)
- https://fondo.com/blog/rhizome-ai-launches (third-party summary of the launch, corroborating
  product description, founder background, launch timing)
- https://www.extruct.ai/hub/rhizomeai-com/ (secondary data aggregator: founding year 2025, HQ
  Jersey City NJ, employee count band 1-10)
- Not confirmed / explicitly unverified: total funding raised, investor names, exact current
  headcount beyond "remote team of 4," compensation and equity for the role. Crunchbase returned
  403 (blocked) and no other source disclosed a funding amount.
