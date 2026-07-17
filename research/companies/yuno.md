# Yuno (y.uno)

Draft dossier for Santiago Coronado. Researched for the Forward Deploy Engineer role
(job id 9853, remote LATAM / Colombia, Commercial team in Brazil). Review before use.

## 1. Snapshot

Yuno is a Bogota-headquartered payment orchestration platform: a single API that connects
merchants to 1,000+ payment methods and 60+ providers across 190+ countries, handling routing,
fraud/risk, tokenization, payouts, and reconciliation. Founded 2021 by ex-Rappi executives Juan
Pablo Ortega (CEO) and Julian Nunez (COO); product launched October 2022. Series A stage: $35M
raised total ($10M seed, March 2022; $25M Series A, March 2024, led by DST Global Partners with
a16z, Tiger Global, Kaszek, Monashees), $150M valuation as of the Series A. Remote-first, offices
across 16 locations on 5 continents including Mexico City and Sao Paulo. Enterprise customers
include McDonald's, Rappi, Uber, inDrive, Netease/Ant Group, Despegar, GoFundMe, and Avianca.
(Sources: y.uno/en/about, y.uno/en, TechCrunch 2024, TechCrunch 2022, Yuno newsroom $25M round.)

## 2. Core narrative

Yuno was built by operators, not outside observers: the founders lived the pain of fragmented,
country-by-country payment integrations while building Rappi, Latin America's largest super app,
and built the orchestration layer they wished they'd had. That founder-market fit plus a
LATAM-to-global expansion arc (Bogota roots, now certified in Saudi Arabia, live in Africa via
Onafriq/Flutterwave, MENA via Tabby, APAC via Singapore) is the throughline: a technical,
credibility-first infrastructure company scaling from emerging markets outward, now layering
autonomous AI agents (Payments Concierge) on top of that infrastructure rather than treating AI
as a bolt-on feature. (Sources: y.uno/en/about, TechCrunch 2024, Yuno newsroom Onafriq/Tabby/
Payments Concierge releases.)

## 3. Mission & product

- Core product: payment orchestration, single API/no-code integration across 1,000+ payment
  methods, smart routing, fraud prevention (risk decisioning, 3DS, tokenization), subscriptions
  and recurring billing, payouts (including stablecoins via a Triple-A partnership), and
  reconciliation/analytics. (y.uno/en)
- Business model: B2B infrastructure sold to large enterprises (not SMBs); pitch is "go live in
  new markets in weeks instead of months" without rewriting integration code for each new
  processor. (y.uno/en, TechCrunch 2024)
- April 2026: launched "Payments Concierge," an always-on AI agent that monitors payment
  operations, flags approval-rate drops and provider outages in real time, surfaces interchange/
  scheme fee visibility, and is reachable via WhatsApp, Telegram, WeChat, or Slack. This is the
  clearest signal of where the product is heading: from orchestration layer to agentic ops
  layer. (Yuno newsroom / GlobeNewswire, April 6 2026)
- Customers named publicly: McDonald's, Rappi, Uber, inDrive, Netease, Ant Group, Despegar,
  GoFundMe, Avianca, Viva Aerobus, Vibra/Petrobras gas stations (5M monthly transactions).
  (y.uno/en, Yuno newsroom, job description for req 9853)

## 4. Stage, funding, footprint

- Seed: $10M, March 2022 (a16z + LatAm VCs). Series A: $25M, March 2024, $150M valuation (DST
  Global Partners lead; a16z, Tiger Global, Kaszek Ventures, Monashees). Total disclosed raise:
  $35M. (TechCrunch 2024, TechCrunch 2022, Yuno newsroom $25M round)
- No Series B has been publicly announced as of this research date; treat any "1,400-1,600
  employees" or "$149.8M ARR" figures from third-party data aggregators (LeadIQ, bitscale.ai,
  Getlatka) as unverified estimates, not confirmed by a primary Yuno source. Do not cite these
  numbers in application materials.
- Footprint: HQ Bogota; offices in Miami, Mexico City, Buenos Aires, Sao Paulo, Shanghai,
  Singapore, London, Paris, Porto, Madrid, Warsaw, Doha, Dubai, San Francisco (16 offices, 5
  continents). Recent expansion moves: Saudi Central Bank (SAMA) payment service provider
  certification (April 2026), Onafriq partnership for Pan-African rails (June 2026), Tabby
  partnership for MENA BNPL (May 2026), Flutterwave partnership for Africa (April 2026).
  (y.uno/en/about, y.uno/en/newsroom)

## 5. Recent news (last ~12 months)

- June 17, 2026: Vibra (Petrobras-branded gas stations, Brazil) adopts an "AI First" strategy on
  Yuno; reported 20% boost in approval rates managing 5M monthly transactions. (y.uno/en/newsroom)
- June 9, 2026: Partnership with Onafriq to integrate a Pan-African payment network into the
  orchestration platform. (y.uno/en/newsroom)
- June 8, 2026: Selected to support payment operations at Web Summit Rio 2026. (y.uno/en/newsroom)
- June 2, 2026: Edwin Poot appointed CTO. Previously Global CTO at Thredd (led a cloud-native,
  AI-first serverless platform rebuild) and VP of Product & Technology at Nubank (Brazil, Mexico,
  Colombia platformization); earlier Chief Architect at Booking.com. He now leads Yuno's global
  engineering org. (GlobeNewswire, June 2 2026; y.uno/en/newsroom/edwin-poot)
- May 7, 2026: Partnership with Triple-A to enable stablecoin acceptance via a single
  integration. (y.uno/en/newsroom)
- May 5, 2026: Partnership with Tabby for BNPL across MENA. (y.uno/en/newsroom)
- April 28, 2026: Partnership with Flutterwave to strengthen African payment capabilities.
  (y.uno/en/newsroom)
- April 22, 2026: Received Payment Technical Service Provider certification from the Saudi
  Central Bank (SAMA). (y.uno/en/newsroom)
- April 6-7, 2026: Launched Payments Concierge (autonomous AI agent for payment ops); CEO Juan
  Pablo Ortega spoke on AI-powered commerce at the HumanX conference. (GlobeNewswire, April 6
  2026)

## 6. Engineering & AI direction

- New CTO (Edwin Poot, joined June 2026) has a track record of moving platforms to cloud-native,
  AI-first, serverless architectures (at Thredd) and of platformization work at Nubank across
  Brazil/Mexico/Colombia, plus chief-architect experience at Booking.com. This suggests active
  investment in scaling and modernizing engineering under new leadership right now. (GlobeNewswire,
  June 2 2026)
- Data platform stack (from a public Yuno Staff Engineer, Data Platform job listing, so treat as
  a snapshot of one team, not the whole company): StarRocks as the analytical layer, Flink for
  stream processing, dbt for transformation, Airflow for orchestration, built to process
  global payment-event volume. (Yuno job posting via search result; original listing returned
  403 on direct fetch, so this is a secondary citation, flagged for verification.)
- AI is positioned as a product layer, not just an internal tool: "agent-first by design" is
  language used on the About page, and Payments Concierge (April 2026) is a shipped, customer-
  facing autonomous agent integrated into Slack/WhatsApp/Telegram/WeChat, reportedly delivering
  "30% recovered revenue" and "90% reduction in development time" per company marketing (y.uno/en;
  treat these specific percentages as company-stated, not independently verified).
  (y.uno/en/about, y.uno/en, Yuno newsroom Payments Concierge release)
- The Forward Deploy Engineer role itself (req 9853) is an explicit technical-feedback-loop
  role: relaying API design friction and missing SDK features from the field back to Product and
  Engineering, which signals a company that treats commercial engineering as a roadmap input, not
  just a sales support function. (job description, req 9853)

## 7. Culture & voice

- Careers page states eight core values: Ambition, Excellence, Resilience, Flexibility,
  Collaboration, Transparency, Diversity, Innovation. Describes a "fast-paced," 100% remote,
  ownership-driven culture with 15+ nationalities represented and 1B+ transactions processed
  yearly. (y.uno/careers)
- Public blog voice (e.g. "Build vs. Buy for Payments: The Math Most CTOs Get Wrong") is
  advisory and evidence-led rather than salesy: it argues in terms of engineering opportunity
  cost ("sprints not shipped") and quantified metrics (an "8% authorization rate uplift" claim)
  rather than hype. This matches what the Forward Deploy Engineer role asks for: turning
  technical depth into a credible, non-salesy story for skeptical engineering stakeholders.
  (y.uno/en/blog/build-vs-buy-for-payments-the-math-most-ctos-get-wrong)
- In payments specifically, the company's own framing is that "trust is built on precision" and
  every demo, RFP response, and line of sample code is a credibility moment. This is stated
  directly in the req 9853 job description, not just inferred. (job description, req 9853)

## 8. Why-fit angles for Santiago

Strongest hook to lead with: Santiago has been the technical-plus-commercial hybrid this role
asks for, twice, as a founder. At Eugenia.ai he personally owned the full product lifecycle
"and led on-site client deployments: onboarding HOAs and property administrators, gathering
requirements, and translating complex, conflicting needs into intuitive mobile and web apps"
while co-building the full-stack platform himself. That is functionally the Forward Deploy
Engineer motion (technical build plus direct client-facing deployment) applied to a different
vertical. Pair this with his current daily use of Claude Code and shipped agent/RAG work
(Pragma Brain, Hermes function-calling agent, Plutus MCP research agent) to speak directly to
Yuno's own "agent-first" product direction (Payments Concierge) and its brand-new CTO mandate to
modernize engineering.

Other angles, in priority order:
- REST APIs, webhooks, and sample-code fluency: his master resume shows hands-on REST API
  integration work (Nextia.mx: "Integrated REST APIs to sync front-end and back-end data,
  reducing user-facing errors by 90%"; Online Basics: orchestrating 10+ third-party APIs) and
  current FastAPI/Python backend work on Plutus, directly matching the role's "REST APIs,
  webhooks, API testing tools (Postman, cURL)" requirement.
- Fintech/payments adjacency: Online Basics scaled to $8M USD revenue on LLM-powered workflows
  and automated data pipelines with real unit-economics and pricing decisions; not payments
  orchestration specifically, but real commercial-plus-technical ownership of revenue-critical
  systems, which is the credibility Yuno wants in front of "skeptical stakeholders."
- Remote LATAM fit: based in Mexico City, which is both one of Santiago's required locations and
  one of Yuno's own office hubs, and the role is explicitly remote LATAM with the commercial team
  based in Brazil, so timezone overlap is workable.

Honest concerns / watch-outs:
- No direct payments-industry experience (PCI DSS, tokenization, 3DS, card-network specifics)
  on his resume; this is a real gap against the "Understanding of payment industry protocols and
  security standards" requirement and should be acknowledged, not glossed over, framing it as
  fast-learner adjacency (Nextia mobile/API work, Online Basics multi-API orchestration) rather
  than claiming direct experience.
- The role is titled and structured as a Sales/Solutions Engineer role embedded in a Commercial
  team (reporting line and success metrics likely tied to sales cycles, RFPs, demos), which is a
  different day-to-day than his recent AI-engineering-first project work (Plutus, Kairos); the
  cover letter should be honest that the pull here is the founder-style hybrid motion, not a pure
  engineering IC role.
- Job listing shows the role split across "Colombia" (Lever location tag) and "Commercial team in
  Brazil" in the description text; worth a direct question in the interview about where the team
  and manager actually sit and what the real timezone expectation is.

## 9. Application-question angles

- Why this company: lead with the founder-market-fit story (Rappi's payment pain built into
  Yuno) and connect it to his own founder pattern of building the tool he needed (Pragma Brain
  as an internal company brain, Hermes as a personal automation agent). Do not recite the full
  funding/customer list; pick one concrete proof point (e.g. the April 2026 Payments Concierge
  launch) to show he researched where the company is now, not just its origin story.
- Why you fit: lead with the Eugenia.ai on-site client deployment plus full-stack build as the
  closest real precedent for Forward Deploy Engineer, then back it with the REST API integration
  history (Nextia, Online Basics). Name the payments-specifics gap plainly and pivot to how fast
  he has picked up regulated/technical domains before (chemical engineering degree into
  self-taught software, then into LLM systems).
- Anything else: use this slot for the honest gap (no direct payments/PCI experience) framed as a
  question he is prepared to close quickly, and optionally mention TN-visa eligibility only if
  the conversation moves toward US-based teams; otherwise keep it about the remote LATAM fit from
  Mexico City.

## 10. Sources

- https://y.uno/en (product overview, AI positioning, customer list)
- https://y.uno/en/about (founding story, values, footprint, leadership names)
- https://y.uno/careers (culture, values, benefits, hiring philosophy)
- https://y.uno/en/newsroom (recent press releases, dated)
- https://y.uno/en/newsroom/edwin-poot (CTO appointment details)
- https://y.uno/en/blog/build-vs-buy-for-payments-the-math-most-ctos-get-wrong (engineering/
  product voice and positioning)
- https://y.uno/newsroom/yunos-25-million-round (Series A round detail)
- https://techcrunch.com/2024/03/05/yunos-payments-orchestration-valuation-fintech/ (Series A,
  valuation, investors, expansion plans)
- https://techcrunch.com/2022/03/10/with-founders-hailing-from-colombian-unicorn-rappi-startup-yuno-raises-10m-from-a16z-and-latam-vcs/
  (seed round, founder background)
- https://www.globenewswire.com/news-release/2026/04/06/3268529/0/en/yuno-launches-payments-concierge-an-always-on-ai-agent-for-payment-operations.html
  (Payments Concierge launch, April 6 2026)
- https://www.globenewswire.com/news-release/2026/06/02/3304823/0/en/yuno-appoints-edwin-poot-as-chief-technology-officer.html
  (CTO appointment, June 2 2026)
- https://jobs.lever.co/yuno/8f2c5253-6927-41ec-b70e-6bec2816b1ee (req 9853, Forward Deploy
  Engineer job description; also loaded via `python -m src.query job 9853`)
- Data platform stack detail (StarRocks/Flink/dbt/Airflow) sourced from a WebSearch summary of a
  public Yuno "Staff Engineer, Data Platform" Lever posting; the direct URL
  (https://jobs.lever.co/yuno/0a1e498f-b0af-4955-bf94-e23b48faec00) returned HTTP 403 on fetch,
  so this detail is flagged as secondary/unverified and should be re-confirmed before quoting it
  directly in application materials.
- config/profile.yaml and resume/master_resume.yaml (candidate background, for fit angles only,
  not company facts)

researched: 2026-07-14
