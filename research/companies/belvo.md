# Belvo

Draft dossier for Santiago's review. Researched 2026-08-24.

## 1. Snapshot

Belvo is an open finance API platform for Latin America (data access plus account-to-account
payments), founded in 2019 by Pablo Viguera and Oriol Tintore. Series B stage, roughly 117
employees as of February 2026, offices in Sao Paulo and Mexico City with a large remote workforce
(20+ nationalities). Total funding to date is about $74.3M, including a $15M round closed April
2025 led by new investor Quona Capital alongside Kaszek, Kibo Ventures, Future Positive, Citi
Ventures and Y Combinator. [ycombinator.com/companies/belvo, belvo.com/blog funding post,
tracxn.com]

## 2. Core narrative

Belvo spent its first six years building the unglamorous connective tissue of Latin American
finance (bank-account data access, identity verification, account-to-account payments across
80+ million connected accounts and $1B+ in annualized transaction volume) and in 2026 is
repositioning that infrastructure as the base layer for an "Intelligent Ecosystem": AI-driven
underwriting, fraud, collections and segmentation tools built on top of its own data pipes. The
March 2026 rebrand made this explicit, shifting from generic "open finance for LatAm" language to
an AI-first platform story backed by concrete usage numbers rather than vision statements. [Belvo
blog: rebranding-2026, reaching-80-million-accounts-1b-tpv-2025-recap, funding announcement]

## 3. Mission & product

- Mission (as stated by Belvo): build the technological infrastructure so financial innovators in
  Latin America can focus on building better financial experiences, rather than reinventing data
  and payments plumbing. [belvo.com/about]
- Product surface: three pillars, financial data access (banking, employment, fiscal data),
  AI-powered insights (risk analysis, income verification, transaction categorization), and
  account-to-account payments (direct debit, biometric payments, smart transfers). Integration via
  API or no-code widgets (Connect Widget, Connect Page). [belvo.com]
- Newest product: Smart Collections, launched May 6, 2026, an automated loan-repayment layer that
  debits the moment a borrower has balance, built on Brazil's Open Finance rails and Smart Pix,
  plugging into a client's existing CRM and credit-rules engine rather than replacing it. Belvo is
  a regulated Payment Transaction Initiator (ITP) under the Central Bank of Brazil, ISO 27001
  certified, LGPD compliant. [belvo.com/products/smart-collections, search result citing May 6 2026
  launch]
- Scale: 80+ million connected accounts across Brazil and Mexico, roughly 2 million
  account-to-account transactions processed monthly, $1B+ annualized total payment volume, 150+
  customers including BBVA, Banamex, Bradesco, Santander, Mercado Libre, Creditas, Nubank, Adyen,
  iFood and Banco Inter. [belvo.com, belvo.com/blog funding post, reaching-80-million post]
- Customers span fintech lenders, neobanks, and large traditional financial institutions, i.e. the
  company sells both to disruptors and to the incumbents those disruptors are pressuring.

## 4. Culture & voice

- Distributed team across 20+ nationalities, offices in Mexico City and Sao Paulo, remote-friendly
  with a rule to keep at least 3 overlapping hours a day across time zones. [job posting for
  20564; belvo.com/about]
- Stated values lean on perseverance ("the first answer is almost never the final answer"),
  data-driven decisions, and deliberately investing in in-person connection for a remote-first team
  (annual "work from any office" weeks, offsites). [belvo.com/blog/what-we-learned-3-years-at-belvo]
- Voice is energetic and collaborative, mixes English and Spanish/Portuguese phrasing ("TamoJunto",
  "VamosConTodo") and pairs aspirational language with hard numbers rather than pure vision talk.
  [same source]
- Diversity and flexibility are called out explicitly (birthday PTO, holiday swaps, pet-friendly,
  fitness stipend, laptop refresh every 3 years). [job posting for 20564]
- Engineering-specific culture: the team frames itself as pragmatic and customer-focused,
  prioritizing validating hypotheses early and iterating from customer feedback over big upfront
  designs; weekly all-hands for transparency on company performance and goals. [job posting for
  20564]
- A recurring theme in Belvo's own blog is that Solutions Engineers are treated as real engineers,
  encouraged to contribute directly to the company's open-source repos (not just configure and
  escalate), both to move faster for customers and as a stated path into core Software Engineering
  roles. [belvo.com/blog/how-solutions-engineers-contribute-open-source-projects]

## 5. Recent news (last ~12 months)

- 2025-04-16: Closed a $15M round (new investor Quona Capital, existing Kaszek, Kibo Ventures,
  Future Positive, Citi Ventures, Y Combinator) explicitly earmarked for product (data and
  payments) and to "fuel Belvo's AI strategy." [belvo.com/blog/belvo-secures-15-million...]
- 2026-02: Unveiled the "Intelligent Ecosystem," a suite of AI-driven decision tools (underwriting,
  segmentation, anti-fraud, payment acceptance) sitting on top of its open finance infrastructure.
  [thepaypers.com coverage; belvo.com/blog/stepping-into-ai-powered-era-open-finance]
- 2026-02-28: Reported headcount of 117 employees. [tracxn.com company profile]
- 2026-03-02: Rebranded (AI-generated imagery, bolder typography, deeper Brazil/Mexico focus) to
  position as an "AI-first" open finance partner, publishing 80M+ connected accounts and $1B+
  annualized TPV as proof points. [belvo.com/blog/rebranding-2026]
- 2026-05-06: Launched Smart Collections, an automated loan-repayment product built on Brazil Open
  Finance and Smart Pix rails. [belvo.com/products/smart-collections]

## 6. Engineering & AI direction

- Stack (per Belvo's own engineering blog and third-party tech-stack listings): Python for the
  large majority of backend code (95%+), Django as the primary backend framework, JavaScript on
  the frontend with Nuxt.js, heavy use of managed AWS services (databases, queues, logging,
  monitoring, orchestration). Deliberately keeps the stack small and familiar to keep it
  maintainable long-term rather than chasing new tools. [himalayas.app/companies/belvo/tech-stack;
  belvo.com engineering blog search summary]
- Cross-functional, autonomous engineering teams running continuous delivery; explicitly
  "products built for developers, by developers," with technical excellence framed as core
  identity. [job posting for 20564]
- AI direction in 2026 is customer-facing product, not just internal tooling: applying models to
  "billions of financial data points" for underwriting, segmentation, anti-fraud, and payment
  acceptance (the Intelligent Ecosystem), plus AI-generated design assets used in the March 2026
  rebrand. The Staff Solutions Engineer posting itself asks candidates to be comfortable
  "leveraging AI tools... to enhance daily workflows and decision-making" and rewards having
  "leveraged AI to fundamentally change the way you work." [belvo.com/blog funding post; job
  posting for 20564]
- Solutions Engineers are explicitly encouraged to contribute code to Belvo's open-source
  repositories rather than stay purely on the support/config side, which the company frames as
  both a velocity lever for customers and a growth path toward core engineering roles.
  [belvo.com/blog/how-solutions-engineers-contribute-open-source-projects]

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago has spent his career on exactly the seam this role sits on,
technical enough to own an API integration end to end, commercial enough to run the client
relationship around it. At Online Basics he built and operated integrations across 10+ third-party
APIs (Amazon, Mercado Libre, Inflow) processing 100K+ daily data points, the same kind of
"turn a messy external data source into something a business can act on" work Belvo does for
financial data. At Eugenia.ai he personally ran on-site client deployments, onboarding, and
requirements-gathering for B2B accounts, which maps directly onto the role's pre-sales through
post-launch lifecycle. As a founder he has always owned the customer relationship and the
technical build at the same time, which is unusual for candidates coming from a pure SE or pure
SWE track.

Other angles:
- Bilingual ES/EN and Mexico City based: fits Belvo's CDMX office and LatAm customer base without
  a visa or relocation question.
- Genuine hands-on AI-tool fluency (built RAG systems, LLM workflows, agents at Pragma AI and in
  his own products) answers the posting's explicit ask for candidates who have "leveraged AI to
  fundamentally change the way you work," not just claim familiarity with chatbots.
- REST API depth and technical documentation habit (internal platforms at Online Basics, API
  integrations at Eugenia.ai and Nextia) map to the "deeper knowledge of APIs and documentation"
  requirement.

Honest concerns / watch-outs:
- Belvo lists 5+ years specifically in onboarding, pre-sales, or similar customer-facing technical
  roles as a requirement. Santiago's customer-facing technical experience is real but was mostly
  as a founder running his own accounts, not as a Solutions Engineer inside a larger org; he should
  frame the founder work explicitly as equivalent scope (owning enterprise-style client
  relationships end to end) rather than let the title gap read as a mismatch.
- No direct fintech, open banking, or payments domain experience; the posting flags this as
  "amazing if," not required, but it is a real gap to name rather than paper over.
- Portuguese fluency is called out as a plus given Belvo's large Sao Paulo/Brazil customer base;
  Santiago does not speak Portuguese, worth a brief honest acknowledgment if it comes up.
- Santiago already has an open application at Belvo for Software Engineer, Applied AI (applied
  2026-07-06). Any outreach or cover letter for this Staff Solutions Engineer role should
  acknowledge the existing application rather than read as a duplicate, cold approach.

## 8. Application-question angles

- Why this company: lean on the "connective tissue becoming intelligence layer" narrative. Belvo
  spent years building unglamorous but critical infrastructure (80M+ accounts, $1B+ TPV) and is
  now turning that into an AI decision layer for underwriting, fraud, and collections. That is the
  exact trajectory Santiago has personally lived at smaller scale: build the pipes first (Online
  Basics' data ETL and third-party API integrations), then put AI on top of them (Pragma AI's RAG
  and agent work). Do not restate the funding history or headcount as if reciting a fact sheet;
  use one or two of these as color, not the whole answer.
- Why you fit: center on owning both the technical integration and the client relationship at the
  same time, the founder pattern repeated at Online Basics and Eugenia.ai, which is unusual
  preparation for a role that spans pre-sales through post-launch support. Avoid listing all four
  research areas (product, culture, news, engineering); pick the client-facing-technical-owner
  angle and go deep.
- Anything else: worth naming, briefly and without over-explaining, that Santiago also has an open
  application for the Applied AI Software Engineer role at Belvo, and that this Staff Solutions
  Engineer posting is a genuine second fit rather than a scattershot application; his AI-agent and
  RAG work (Pragma AI, Plutus) is real hands-on evidence for the posting's AI-fluency ask, not
  résumé filler.

## 9. Sources

researched: 2026-08-24

- https://jobs.ashbyhq.com/belvo/d9156c58-6c5e-4852-b9d9-00b8133d1b2d/application (job posting
  20564, full description, requirements, perks, hiring process)
- https://www.ycombinator.com/companies/belvo (founding year, founders, employee count, YC backing)
- https://belvo.com/blog/belvo-secures-15-million-in-new-round-of-funding-open-finance-latin-america/
  (April 2025 funding round detail, investors, use of funds, AI strategy, customer list)
- https://belvo.com/ (product pillars, business model, customer names, scale metrics)
- https://belvo.com/about/ (mission, vision, founding story, founders, offices, team composition)
- https://belvo.com/blog/rebranding-2026/ (March 2026 rebrand, AI-first positioning, scale metrics)
- https://belvo.com/blog/how-solutions-engineers-contribute-open-source-projects/ (Solutions
  Engineer role detail: day-to-day, open-source contribution model, career path)
- https://belvo.com/blog/what-we-learned-3-years-at-belvo/ (culture and values statements, tone of
  voice)
- https://belvo.com/products/smart-collections/ (Smart Collections product detail, regulatory
  status)
- https://himalayas.app/companies/belvo/tech-stack (third-party summary of engineering stack:
  Python/Django backend, JS/Nuxt frontend, AWS)
- Tracxn company profile (tracxn.com/d/companies/belvo) (headcount as of 2026-02-28, total funding
  figure)
