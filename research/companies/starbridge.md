# Starbridge

STATUS: DRAFT, not yet human-fact-checked by Santiago. Verify before quoting anything below in an application.

## 1. Snapshot

Starbridge is a New York based, venture-funded startup (founded early 2025) that sells an AI powered go to market intelligence platform to companies selling into government and education (SLED: state, local, education) buyers. It has raised $52M total ($10M seed, October 2025 saw $42M Series A led by Craft Ventures) and reports 150+ to 160+ enterprise customers as of its Series A announcement (October 2025). HQ is 60 Chelsea Piers, Suite 6020, New York, NY. Public headcount figures are unreliable (third-party job boards show stale "1-10 employees," which does not square with a $52M raise and a 10-req open board); treat exact headcount as unverified. [starbridge.ai/about-us, techbuzz.ai, craftventures.com]

## 2. Core narrative

Starbridge is built by a repeat SLED founder (Justin Wenig, who previously founded Coursedog, a higher-ed software company) turning his own first-hand pain, filing FOIA requests and reading council meeting minutes by hand to find government sales prospects, into an AI product that automates that exact workflow: it watches thousands of public sources (council meetings, budget documents, RFPs, purchase orders, FOIA responses) and turns them into a scored, actionable pipeline for enterprise sales teams selling to government and schools. The company is small, fast-moving, and openly leans into founder-market fit and speed as its identity ("Shooting Star Speed," "In the Arena"). [craftventures.com, govtech.com/biz/sled-procurement-firm-starbridge-raises-10m-in-seed-funding, starbridge.ai]

## 3. Mission & product

- What it does: aggregates and monitors public sector procurement signals (council meeting mentions, budget documents, RFPs, grant awards, purchase orders, contract expirations, FOIA responses) across 300k+ public sector entities, scores accounts as "buying signals," enriches contacts, and helps sales teams draft outreach and RFP responses. Integrates with Salesforce/HubSpot. [starbridge.ai, welcome.ai/company/starbridge/technology]
- Notable feature: automated, multi-state FOIA request filing on a customer's behalf (anonymized) to pull competitor contract terms, pricing, and renewal dates; the company states it can "handle FOIA requests in every state" despite some states restricting open-records requests to state residents, without publicly detailing the compliance mechanism. [starbridge.ai/blog/starbridge-foia]
- Who buys it and what for: GTM teams (AEs, SDRs, RevOps, customer success) at companies selling software/services to government and K-12/higher-ed. Named customers include Fortinet, Airtable, Instructure, Clever, Magic School, Aramark, Zencity, Frontline Education, ClearGov, SimpliGov, Mark43, Imagine Learning, and HMH. [starbridge.ai, craftventures.com]
- Market framing: addresses roughly $2 trillion in annual US SLED spend, positioned as "the first GTM intelligence platform designed for government and education deals." [craftventures.com, govtech.com/biz/sled-procurement-firm-starbridge-raises-10m-in-seed-funding]
- Pricing/business model: not publicly disclosed; go-to-market is demo-and-book-a-call, B2B SaaS subscription (implied by "enterprise sales teams" and account-based deal sizes referenced in job postings, e.g. "$25K+ ARR opportunities"). [starbridge.ai, Ashby job board: Solutions Engineer req]

## 4. Culture & voice

- Stated "How We Work" values, repeated verbatim across every job posting: "Build Bridges to Help Customers Win" (obsessively customer-centric), "Shooting Star Speed" (extreme speed, momentum, decisiveness), "Fun Is a Feature" (intentionally energizing, humor and camaraderie), "In the Arena" (best ideas come from living close to the work). [Ashby job board, all reqs]
- Interview process language is consistently urgent: "We move fast, really fast. Getting back to someone today beats tomorrow." All interviews via Google Meet, aiming to finish a process within about a week for at least one engineering req. [Ashby job board]
- In-office NYC culture is explicit for NYC roles: company-provided daily lunch, gym stipend, commuter benefits, "excited to build an in-person culture with us" language on the Senior Product Engineer req; benefits across all reqs include unlimited PTO and "regular offsites (NYC + global locations)." [Ashby job board]
- Public voice: Justin Wenig posts openly on LinkedIn about company building and gave away RFP/contract data for free in one campaign ("Starbridge makes RFPs, Contracts data public for free"), consistent with an evangelist-founder, category-building posture. [linkedin.com/posts/justinwenig, search result title corroborated via WebSearch]

## 5. Recent news (last ~12 months, dated)

- 2025-10-21: Series A, $42M, led by Craft Ventures, bringing total funding to $52M; used for hiring and product/AI infrastructure expansion. [starbridge.ai/blog (Series A post), govtech.com/biz/procurement-ai-tech-provider-starbridge-raises-42m, craftventures.com]
- 2025-10-21 (same announcement window): reported 150+ to 160+ enterprise public-sector sales teams as customers, up from launch roughly 8 months prior. [craftventures.com, govtech.com/biz/procurement-ai-tech-provider-starbridge-raises-42m]
- 2025 (year, exact date unverified, prior to Series A): $10M seed round led by Owl Ventures, with Autotech, Commonweal Ventures, and Avalanche participating. [govtech.com/biz/sled-procurement-firm-starbridge-raises-10m-in-seed-funding]
- Ongoing 2026: actively hiring across Engineering, Revenue, Product, and Legal (Founding General Counsel req posted 2026-07-29), consistent with post-Series-A scaling; job board shows a steady cadence of new reqs from March through August 2026. [Ashby job board, live pull 2026-08-11]

## 6. Engineering & AI direction

From the live req texts (fetched directly from the Ashby posting API, 2026-08-11):

- **Models/providers in production or under evaluation**: OpenAI, Anthropic, Gemini, and Parallel.ai. [job 18701 description; NYC AI Engineer req]
- **AI Engineer scope (both the NYC and EMEA/LATAM reqs use near-identical text)**: building, evaluating, and deploying LLM-driven features in production, specifically AI proposal writing, search/chat experiences, and "deep document analysis" over complex public documents. Responsibilities center on productizing new AI capabilities, evaluating/monitoring model performance through "rigorous testing and experimentation," and building CI/CD practices for AI systems. [job 18701; Ashby job board]
- **Explicitly named tools/frameworks (bonus, not required)**: LangGraph, LiteLLM, Agent Client Protocol, Koog, and depth in RAG implementation; Kotlin proficiency is a listed bonus (Koog is a Kotlin-based agent framework, so this likely reflects one team or one service, not the whole stack). ML lifecycle tooling required in the base qualifications: MLflow, dvc, Weights & Biases; "cloud deployment of ML systems." [job 18701]
- **Frontend stack** (from the separate Senior Product Engineer, New Products req, NYC, $200K-$300K, posted 2026-08-06): React, TypeScript, JavaScript, REST APIs, CSS, GitHub CI/CD; hiring bar of 5+ years specifically in React/TypeScript. [Ashby job board]
- **Backend language** required across AI reqs: Python, "production software and systems design." [job 18701]
- **Customer-facing integration surface**: the Solutions Engineer req (NYC) references customer "integrations with CRM, API support, and MCP access," meaning Starbridge exposes an MCP (Model Context Protocol) interface to customers, not just internal tooling. [Ashby job board, Solutions Engineer req]
- **No GitHub org, public engineering blog, or public eval-methodology writeup was found.** Starbridge's public blog (starbridge.ai/blog) is GTM/product-marketing focused (funding announcements, feature explainers like FOIA automation), not an engineering blog. This is a real gap: there is no external evidence of Starbridge's AI evaluation practices beyond what the job posting itself claims. [starbridge.ai/blog, searched, no dedicated eng blog found]

## 7. Why fit angles for Santiago

**Lead hook**: Santiago has shipped exactly the three things this specific req asks for, RAG over messy real-world documents with citation gating, LLM agent orchestration, and eval harnesses, at Pragma AI's "Pragma Brain" (a RAG "company brain" with deterministic no-answer and citation gating, LLM-at-ingest sensitivity labeling, and an automated eval harness) and Plutus (an LLM research agent over MCP with vectorized signal scanning and evidence-backed candidate output). Both map directly onto Starbridge's stated core work: "deep document analysis," "AI proposal writing & search experiences," and "evaluate and monitor the performance of AI models... through rigorous testing and experimentation." This is a strong, specific, non-generic match, not a "I've used LLMs before" claim. [resume/master_resume.yaml; job 18701]

Supporting angles:
- Founder background (built and sold Eugenia.ai, scaled Online Basics to $8M) matches Starbridge's own founder-led, fast-moving, customer-obsessed self-description ("Shooting Star Speed," "In the Arena," small team with real ownership). A founder-engineer is a legible fit for a 2025-founded, ~10-req company, not an enterprise-process candidate.
- Full-stack range (Python/FastAPI backend, React/TypeScript frontend) matches the fact that Starbridge's AI Engineer works "closely with engineering and product teams" and its own frontend req demands the same React/TypeScript stack, meaning an AI hire who can also touch the UI is plausibly valued here even though it is not explicit in req 18701.
- MCP experience (Kairos exposes 52 tools over MCP; Plutus exposes an MCP control plane) is a concrete, rare match against Starbridge's own MCP-exposed customer integration surface (per the Solutions Engineer req), worth a one-line mention if there is room, but do not overweight it since it is not in the AI Engineer req itself.

Honest concerns / watch outs:
- **Model training gap**: this req's base qualifications list "machine learning algorithms and model development techniques" and ML lifecycle tools (MLflow, dvc, Weights & Biases) as required experience. Santiago has no evidence of model training, fine-tuning, or classic ML model development anywhere in the master resume; his work is entirely applied LLM engineering (RAG, agents, evals, prompting) on top of hosted APIs (Anthropic, OpenAI). This is a real, honest gap. A cover letter should not claim ML model development experience; if asked directly, the honest answer is that his depth is in applied LLM systems and evaluation, not classical ML/model training.
- **Employment mechanism unverified**: the req does not name an EOR, PEO, or any Mexico-specific employment structure. Whether Santiago would be hired directly, as a contractor, or through an employer-of-record is genuinely unknown from public sources; flag this explicitly in any application or first-call question rather than assuming.
- **Compensation gap vs. NYC role**: the LATAM band ($120K-$140K) is meaningfully below the NYC AI Engineer band ($200K-$380K) for what reads as the same role text. That gap almost certainly reflects location-based pay banding common at NYC-headquartered startups hiring internationally, not a lesser scope. See section 6 below for how this should shape negotiation.
- **Public headcount signals are noisy/unreliable** (third-party boards show "1-10 employees," clearly stale). Team size and the maturity of AI infrastructure/eng practices could not be independently verified beyond the job postings themselves; go in expecting a very early-stage engineering org (10 open reqs total company-wide as of 2026-08-11) rather than a mature AI platform team.

## 8. Compensation context

The LATAM/EMEA req (job 18701) is banded $120,000-$140,000 USD. The NYC AI Engineer req (same "About the role" language, published earlier: 2025-10-21) is banded $200,000-$380,000 USD, on-site. [job 18701; Ashby job board, AI Engineer | NYC req]

What the gap likely means: this is standard geography-based pay banding at a NYC-headquartered, in-person-culture startup (see the NYC Senior Product Engineer req's explicit "excited to build an in-person culture with us" language), not a signal that the LATAM role is junior or lower-scope; the responsibilities text is nearly identical between the two reqs. The $200K-$380K NYC band is unusually wide, which suggests Starbridge bands broadly by seniority/experience within a single title rather than tightly scoping the role, and the LATAM band is likely following the same logic scaled down for location.

Negotiation implication for Santiago: his floor is $70,000 (LATAM-scope floor) and target is $100,000; the whole posted band ($120,000-$140,000) clears both, sitting above his target anchor as well as his floor. Given 7+ years of directly relevant experience (RAG, agents, evals) and founder-level ownership, the anchor should be at or above the band's midpoint (approximately $130,000), consistent with `config/profile.yaml`'s band rule (anchor at or above midpoint, never below the floor). There is limited room above $140,000 unless Starbridge treats this LATAM band as flexible on a case-by-case basis, which is unverified; do not assume the NYC band's upper range is reachable for a remote LATAM hire.

## 9. What "AI Engineer" means here, precisely

Based only on the text of job 18701 (and the identical-language NYC counterpart), this role is:
- RAG and document understanding over public/government documents ("deep document analysis," search experiences): YES, explicit.
- Agent/LLM-driven feature orchestration (proposal writing, chat experiences) across multiple model providers (OpenAI, Anthropic, Gemini, Parallel.ai): YES, explicit.
- Evaluation infrastructure for LLM systems ("evaluate and monitor the performance of AI models... through rigorous testing and experimentation," "implement strong testing and CI/CD practices"): YES, explicit, and treated as a core, ongoing responsibility, not a one-off.
- Classical ML model development / training: the base qualifications ask for "machine learning algorithms and model development techniques" and ML lifecycle tooling (MLflow, dvc, Weights & Biases) as required experience, and "professional experience with LLMs and large-scale models" and "distributed product machine learning systems" as a track record. This reads as either (a) a broad ML/AI engineering job description written to cast a wide net that in practice is fulfilled mostly by applied LLM work, given the responsibilities section is 100% LLM/RAG/eval focused, or (b) a genuine expectation of some classical ML background the team currently lacks strong internal evidence for beyond the req text itself. This cannot be resolved from public sources alone.

Practical read for the cover letter: lean hard into RAG, agent orchestration, and eval harnesses, all of which Santiago can back with specifics (Pragma Brain's citation gating and no-answer gate, Plutus's MCP-exposed research agent and backtesting evals). Do not claim or imply model training/fine-tuning experience. If the requirements list is a concern worth raising, it is better raised as a direct question in an early call than finessed in the cover letter.

## 10. Full role requirements (for the tailor agent)

Title: AI Engineer | EMEA/LATAM. Ashby req 80ee1fbc-2de4-4c9a-b62a-be5ae89b0c37. Location field: "Europe/LATAM," workplaceType Remote. Published 2026-06-12. Band $120,000-$140,000 USD plus equity.

Responsibilities:
- Collaborate with the team to productize new AI-powered capabilities (AI proposal writing, search experiences).
- Evaluate and monitor AI model/system performance (OpenAI, Anthropic, Gemini, Parallel.ai) through rigorous testing and experimentation.
- Stay current on AI/ML research and proactively suggest improvements to generative AI capabilities.
- Implement strong testing and CI/CD practices for AI system development.

Required:
- Bachelor's in Computer Science, Engineering, Mathematics, related field, or equivalent experience.
- Startup or small-company experience with real engineering impact.
- 5+ years professional software engineering / AI-ML development experience, including: production Python and systems design; machine learning algorithms and model development techniques; ML lifecycle tools (MLflow, dvc, Weights & Biases); cloud deployment of ML systems; professional experience with LLMs and large-scale models.
- Track record building scalable, distributed product machine learning systems.
- Product thinking: translating product requirements into LLM application strategy.
- Strong communication of complex ideas.

Bonus:
- Experience with LangGraph, LiteLLM, Agent Client Protocol, Koog.
- Depth in RAG implementation and improvements.
- Kotlin proficiency.

Benefits: competitive salary + early-stage equity, unlimited PTO, regular offsites (NYC + global locations). Interview process conducted via Google Meet; company states it moves fast and asks candidates to share timeline expectations. [job 18701; Ashby job board]

## 11. Risks, reputation, recent news context

- Public-sector data products carry inherent exposure around data licensing, records-request compliance, and state-by-state legal variation. Starbridge's own FOIA-automation blog post acknowledges that "a handful of states restrict their public records laws to residents of that state" and states the company can "handle FOIA requests in every state," without publishing the mechanism. This is not evidence of wrongdoing, but it is a real, self-disclosed compliance nuance worth being aware of, not a reason to avoid applying. [starbridge.ai/blog/starbridge-foia]
- No lawsuits, breaches, regulatory actions, or negative press were found in searches covering the company name plus "controversy," "lawsuit," and "FOIA" for 2025-2026. Absence of evidence is not the same as evidence of absence; this is simply what public search surfaced as of 2026-08-11. [WebSearch, no results found]
- Company is young (founded early 2025) and small; normal early-stage-startup risk applies (fewer than a handful of funding events, concentration on a single go-to-market motion, and, per the CEO's own public comments picked up in press, awareness of broader "AI bubble" market chatter around the sector). [govtech.com/biz/procurement-ai-tech-provider-starbridge-raises-42m]
- No LATAM-based Starbridge staff could be confirmed via public LinkedIn search. One New York-based Customer Success hire (Antonio Aguirre) surfaced in search but nothing indicates a LATAM location; this is inconclusive, not a negative signal, the LATAM scoping on the job board itself (per the already-verified context) remains the strongest evidence of employer intent to hire from the region. [WebSearch, LinkedIn search, inconclusive]

## 12. Application-question angles

**Why this company**: lead with the founder-market-fit narrative, Wenig lived the exact pain (manually reading council minutes and filing FOIA requests to find prospects) that Starbridge now automates with AI, and Santiago has built the same category of system (a RAG "brain" with citation gating over messy internal documents, an LLM research agent over MCP) for his own consultancy's clients. The resonance is "I have built the thing you are building," not generic enthusiasm for AI or for government tech.

**Why you fit**: anchor on the three concrete, defensible pieces of evidence, citation-gated RAG (Pragma Brain), agent orchestration with real tool use (Plutus's MCP-exposed research agent, Kairos's 52-tool MCP server), and an actual eval harness (Pragma Brain's automated eval harness; Plutus's backtesting evals). Do not reach for model-training language Santiago cannot back up; if the letter needs a fourth beat, full-stack range (Python/FastAPI plus React/TypeScript) matching Starbridge's own engineering reqs is a safe, true addition.

**Anything else**: a short, honest note that his depth is in applied LLM systems (RAG, agents, evaluation) built on hosted model APIs, not classical ML/model training, if the letter or an answer needs to preempt the ML-lifecycle-tooling language in the req. Keep it brief and confident, framed as where his strength concentrates, not as an apology.

Avoid: do not checklist all of Starbridge's four business areas (product, culture, funding, engineering) in the letter. Do not claim MLflow/dvc/Weights & Biases experience, model training, or LATAM headcount facts that were not verified. Do not invent an EOR or employment-structure claim; if asked, say it needs to be confirmed with the recruiter.

## Sources

researched: 2026-08-11

- https://starbridge.ai/: product description, features, named customers, business model signals
- https://starbridge.ai/about-us: mission statement, leadership names (Justin Wenig, Jenn Jiao), HQ address, culture testimonials
- https://starbridge.ai/blog/starbridge-raises-42m-series-a-to-make-it-easy-for-any-business-to-sell-to-government-education: Series A amount, lead investor, date, mission quote
- https://www.govtech.com/biz/procurement-ai-tech-provider-starbridge-raises-42m: Series A confirmation, customer count, CEO quote on manual research
- https://www.govtech.com/biz/sled-procurement-firm-starbridge-raises-10m-in-seed-funding: seed round, launch timeline, founder background (Coursedog)
- https://www.craftventures.com/articles/why-we-invested-in-starbridge: founder background and rationale, traction metrics, market sizing, Series A investment thesis
- https://starbridge.ai/blog/starbridge-foia: FOIA automation mechanism, data collected, compliance nuance around state residency restrictions
- https://jobs.ashbyhq.com/starbridge (fetched via the public Ashby posting API, https://api.ashbyhq.com/posting-api/job-board/starbridge): live list of all 10 open reqs as of 2026-08-11, including titles, locations, workplace types, compensation bands, and full descriptions used for sections 6, 8, 9, 10
- https://jobs.ashbyhq.com/starbridge/80ee1fbc-2de4-4c9a-b62a-be5ae89b0c37/application (job 18701 in local DB): the target role's full text, requirements, and band
- https://www.linkedin.com/in/justinwenig/: confirms Justin Wenig's Columbia University attendance and current role at Starbridge (used only for these narrow, corroborated facts)
- WebSearch queries for "Starbridge controversy/lawsuit/FOIA 2026" and LATAM-based Starbridge staff on LinkedIn: used to establish absence of negative press and inconclusive LATAM headcount signal (see section 11); no citable page found beyond what is listed above
