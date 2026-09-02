# Handle (usehandle.ai)

## Snapshot
Early-stage (seed, $6M led by Andreessen Horowitz, closed March 2026) startup building AI agents that automate insurance back-office operations for brokers, MGAs, and carriers. HQ/founding market is Mexico City; the team is remote-friendly and hiring across the US, Mexico, and Brazil. Reported roughly $1M ARR within two months of launch and 75+ broker customers in Mexico as of the funding announcement.

## Core narrative
Handle was founded by Alfonso de los Rios, the Mexican entrepreneur who co-founded and ran Nowports (a Mexican logistics unicorn, $1.1B valuation) and was Mexico's first Thiel Fellow. He is building Handle around the same pattern he saw at Nowports: enterprise operations that run on fragmented systems (email, WhatsApp, CRMs, insurer portals) forcing armies of people into manual, repetitive work. Handle's bet is "vertical AI agents" that use computer-use style automation to operate inside those fragmented systems directly, starting with insurance, one of the most fragmented, least digitized, highest-volume back-office industries in Latin America.

## Mission & product
Handle builds a two-layer platform: a System of Record that centralizes broker/carrier data pulled from insurer portals and internal systems, and Vertical Agents that autonomously execute workflows such as quoting, reconciliation, collections, and claims handling. The agents use "computer use" style automation to navigate 100+ insurer portals the way a human operator would (filling forms, gathering documents), escalating to a human when judgment is needed, with full activity logging. A separate operational layer called Signal integrates channels like email, WhatsApp, Salesforce, HubSpot, Oracle, and NetSuite so agents can act across a broker's existing tools rather than replacing them.

Pricing is usage-based (charged per task executed) rather than seat-based SaaS licensing, explicitly designed so Handle's revenue scales with agent activity. Target customers are insurance brokers, MGAs, and carriers; named customers include Inter.mx, Genomma Lab, De Acero, and Qualitas. Reported customer outcomes: quoting time cut from 2-5 business days to under 2 hours for complex policies, 94% faster claims registration, 40% faster email response, about 8 hours/week returned per executive, and a case study (Brove) saving 189 hours of manual work in 5 weeks.

## Culture & voice
Public-facing tone is direct and outcome-obsessed: usage-based pricing, "value within 48 hours," 6-8x ROI claims within the first 90 days. Founder de los Rios talks about purpose-driven company building ("never started companies just to start them, but to solve something that interested me") and frames Handle as a continuation of the operational-chaos problem he saw at Nowports. Customer-facing language from a case study emphasizes "openness to listening to our needs, and the flexibility of the product" and framing automation as additive to human relationships, not a replacement for them. No dedicated engineering blog was found (usehandle.ai/blog redirects to the marketing homepage; blog.usehandle.ai returns an empty client-rendered shell), so culture signal here is mostly founder-voice and customer testimonials rather than an engineering-team voice.

## Recent news (last ~12 months)
- March 2026: Closed a $6M seed round led by Andreessen Horowitz to expand the AI agent platform for enterprise operations, with initial focus on insurance brokers in Mexico (theaiinsider.tech, elespanol.com, startupslatam.com, Forbes).
- Around the same period: reported ~$1M ARR within two months of commercial launch and dozens of enterprise clients (emprendedor.com).
- The company describes itself (per founder social posts) as building "the System of Intelligence for Insurance," now serving brokers and multiple carriers on back-office automation, and frames the vertical-AI-agent thesis as playing out fast in one of the largest, messiest back-offices in the world.

## Engineering & AI direction
Handle's stack, per its own product description, centers on "computer use" style AI agents that operate insurer web portals directly (form-filling, document retrieval) rather than relying solely on API integrations, since most insurer systems are not API-accessible. The platform layers a System of Record (data centralization from portals and internal systems) under Vertical Agents (workflow execution) and an integration layer, Signal, connecting to common enterprise tools (email, WhatsApp, Salesforce, HubSpot, Oracle, NetSuite). The open Sr. Software Engineer (Mexico) posting confirms a TypeScript/React/Next.js/Python stack and explicitly values "experience building with LLMs, agent frameworks, or AI-native products, side projects count," plus production ownership and on-call. No public engineering blog, so deeper stack detail (model providers, eval/observability tooling, deployment infra) is unverified.

## Why-fit angles for Santiago
Strongest hook: Santiago ran an $8M multi-marketplace ecommerce operation (Online Basics) that lived inside exactly the kind of fragmented, non-API, manual-workflow problem Handle sells against, and he built the internal tooling (pricing dashboard, inventory admin, ETL pipelines syncing 10+ third-party APIs hourly) to fix it himself before AI agents existed as a category. That is a genuine, specific parallel to Handle's insurance-broker pitch (disconnected systems, repetitive manual work, need for real-time operational visibility), not a generic "I like AI" pitch.

Secondary hooks:
- Forward Deployed Engineer fit: Santiago has done hands-on client deployment work (Eugenia.ai on-site HOA/property-administrator onboarding, Pragma AI client AI consulting and diagnostics) plus the customer-facing Spanish fluency Handle's Mexico postings require.
- Sr. Software Engineer fit: production LLM/agent work (Pragma AI's RAG "company brain," MCP tool layers, Claude Agent SDK integration in Kairos) directly answers Handle's "experience building with LLMs, agent frameworks, or AI-native products" qualification, and his React/Next.js/TypeScript/Python range matches their stated stack.
- Founder-to-founder resonance: Santiago is also a founder-engineer (Online Basics, Eugenia.ai, Pragma AI) who has raised outside capital and shipped 0-to-1 products, which maps to a de los Rios-style "high ownership, ambiguity-comfortable" bar mentioned in both Mexico postings.

Honest concerns/watch-outs:
- No compensation is listed on either Mexico posting; Handle's US postings show real bands ($200k-$340k+equity) but the Mexico and Brazil listings all show blank compensation, so pay needs to be established directly in the email exchange, not assumed.
- This is a very early-stage company (seed, ~5 months post-funding at time of writing) with no public engineering blog and no verified headcount; equity/stability risk is real and unverified, and should be treated as an open question rather than glossed over.
- The Sr. Software Engineer bar is explicitly 6+ years professional software engineering; Santiago's total experience supports this, but it's less "hands-on for 6 years at one company" and more founder-generalist, worth being upfront about in how he frames the "6+ years" line.

## Application-question angles
- Why this company: lead with the ecommerce-to-insurance parallel (Online Basics as a first-hand case of fragmented systems and manual busywork he had to solve with internal tooling before AI agents existed as an off-the-shelf option) rather than a generic "AI agents are exciting" framing. Handle is solving, at platform scale, a version of the exact operational problem he solved once, alone, for one business.
- Why you fit: for the Forward Deployed Engineer role, lean on direct client deployment experience (Eugenia.ai on-site onboarding, Pragma AI client diagnostics) plus bilingual client communication. For the Sr. Software Engineer role, lean on shipped, production LLM/agent systems (Pragma AI's RAG brain, MCP tool layers) and the React/Next.js/TypeScript/Python range, not a checklist of every skill in the posting.
- Anything else: the founder-to-founder note (Santiago has built and exited/scaled his own companies, raised capital, and owns 0-to-1 product decisions) is worth a brief, honest mention since Handle's founder explicitly built this company out of his own operational-chaos experience running Nowports, a resonance that is specific to this company rather than transferable boilerplate.

## Applying by email
Handle has no ATS. Both Mexico roles apply by emailing jobs@usehandle.ai. The site's own apply links auto-fill a subject line in the format "Application: {Job Title} - {Location} ({job id})":
- Forward Deployed Engineer, Mexico: subject "Application: Forward Deployed Engineer - Mexico (Country) (eng-015)"
- Sr. Software Engineer, Mexico: subject "Application: Sr. Software Engineer - Mexico (Country) (eng-012)"
The site's only stated instruction beyond that is the general contact CTA: "Send us your resume or schedule a conversation." No specific attachment format, cover-letter requirement, or additional instructions are stated anywhere on the jobs page or in the underlying page code.

## Sources
- https://usehandle.ai/jobs (job data embedded in page JS bundle: role details, subject-line format, apply mechanism; captured 2026-08-27)
- https://usehandle.ai (mission/product description, agent capabilities, reported metrics, culture language)
- https://theaiinsider.tech/2026/03/16/handle-closes-6m-funding-round-to-expand-ai-agent-platform-for-enterprise-operations/ (funding amount, investor, founder, date, product/customer detail)
- https://www.startupresearcher.com/news/handle-raises-usd6-million-to-bring-enterprise-ai-agents-to-mexico (funding, founder background, customer names, product mechanics, claims-registration/email-response speed stats)
- https://emprendedor.com/handle-alfonso-de-los-rios-agentes-ia-empresas-mexico/ (founder origin story, mission, usage-based pricing model, ARR/traction, founder philosophy quote)
- https://www.elespanol.com/invertia/disruptores-americas/20260317/handle-nueva-startup-emprendedor-poncho-rios-nace-millones-dolares-inversion/1003744170791_0.html (funding announcement, press corroboration)
- https://startupslatam.com/handle-levanta-us6-millones-con-andreessen-horowitz-para-lanzar-sus-agentes-de-ia-empresarial-en-mexico/ (funding announcement, founder Thiel Fellow detail, customer list)
- https://x.com/ponchodelosrios/status/2057619077300940957 (founder public framing: "System of Intelligence for Insurance," vertical AI agent thesis; quote surfaced via search snippet, full tweet not independently fetched due to access restriction)

researched: 2026-08-27
