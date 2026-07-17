# RouteGenie

Draft dossier for Santiago's review. Prepared for the "AI Application Engineer" role (job id 8041,
Mexico, via Adzuna).

## Core narrative

RouteGenie is a ~40-person, Buffalo NY based non-emergency medical transportation (NEMT) SaaS,
founded in 2017 by operators who built the software to run their own transportation business first
(routegenie.com/about). In September 2025 it was acquired by a self-funded search fund, Ascend
Equity Partners, led by new CEO Cameron Craig, backed by Next Coast Legacy and Northspring Partners
(searchfundsnews.com; northspringpartners.com). Since the acquisition the company is visibly staffing
up its AI and engineering leadership (parallel open roles for Head of Engineering and Head of
Technology, plus this AI Application Engineer role), suggesting a founder-owner is actively building
a real production AI practice inside an established, profitable vertical SaaS rather than doing AI
theater. The company already writes cautious, HIPAA-aware guidance on where AI helps and where it
should not touch PHI (routegenie.com/blog), so the mandate looks like "ship real LLM features into a
regulated, compliance-heavy workflow," not a green-field AI lab.

## Product

- All-in-one NEMT platform: scheduling, routing/dispatch, billing, fleet management, driver and
  passenger apps, marketed as a family of "Genie" modules (DispatchGenie, BillingGenie,
  Pre-RouteGenie, DriverGenie, CustomerGenie, FleetGenie, HRGenie) (routegenie.com).
- Business model: subscription SaaS for NEMT/paratransit providers and brokers, "starting at
  $50/month" (routegenie.com/nemt-broker-software; WebSearch summary of routegenie.com).
- Scale claimed on site: 600-700+ fleets, 20,000+ vehicles, 46 states and two countries, over
  1 million coordinated rides per month (routegenie.com/about; press release, submitmypressrelease
  July 2026).
- Billing output is HIPAA-compliant electronic claims (837P, CMS 1500) for Medicaid and other payers
  (routegenie.com).
- Customer proof point: a July 2026 case study describes a client, 360 Transport, tripling its
  fleet while holding 98% on-time performance and lifting driver safety scores from 66% to 97% on
  RouteGenie (submitmypressrelease.com, 2026-07-03).

## Stage/scale

- Founded 2017; acquired by search fund Ascend Equity Partners (CEO Cameron Craig) in September
  2025, backed by Next Coast Legacy and Northspring Partners (searchfundsnews.com,
  northspringpartners.com/portfolio-companies/route-genie).
- Roughly 40-41 employees as of early 2026, over 40 of whom are described as developers
  (routegenie.com/about; Tracxn company profile).
- Recognized on the Inc. 5000 (2023 and 2024) and as a repeat SourceForge "Top Performer"
  (WebSearch summary citing Inc./SourceForge; unverified beyond aggregator search snippet, worth a
  quick independent check before quoting in a cover letter).
- HQ: Buffalo, New York (routegenie.com/about, northspringpartners.com). This specific role is
  listed as location "Mexico" with no city and no explicit remote/hybrid label on the ad itself
  (Adzuna listing, job id 8041); the tech-stack brief for the role asks for "strong async
  communication for distributed teams," which points to a distributed/remote engineering setup, but
  this is an inference, not a stated policy, so confirm remote status directly in the interview.

## Tech stack

From the role's own "Technology Stack" section (Adzuna posting, job id 8041, retrieved via
webfetch) and confirmed against the core product stack:
- Core product: Python, Django, PostgreSQL, Angular, TypeScript.
- LLM providers: Anthropic Claude (primary), OpenAI, AWS Bedrock.
- Local/self-hosted LLMs: Ollama, LM Studio, llama.cpp, vLLM; open-weight families (Llama, Qwen,
  Mistral).
- Agent frameworks: LangChain/LangGraph, LlamaIndex, OpenAI Agents SDK or equivalent.
- Retrieval: vector databases (Pinecone, Weaviate, pgvector), RAG, GraphRAG, cache-augmented
  generation.
- Voice AI: ElevenLabs, VAPI, LiveKit, Deepgram (for dispatch/customer-service voice use cases).
- Observability: LangSmith, Braintrust, Phoenix, Helicone.
- Explicitly names "Claude Code" as part of the development workflow.
- Required: 3+ years software engineering, 1+ year hands-on shipping production LLM/AI features to
  real users, strong Python and TypeScript, ability to describe metrics and test datasets used to
  validate production AI quality.
- Strongly preferred: voice AI for dispatch/customer service, healthcare or regulated data handling
  (HIPAA, PII/PHI), self-hosted LLM deployment, Claude API/SDK depth.

## Recent news (last ~12 months)

- 2026-07-03: Case study, "RouteGenie Helps 360 Transport Triple Its Fleet While Holding 98%
  On-Time" (submitmypressrelease.com / RouteGenie newsroom).
- 2026-02-18: Blog post, "How to Use AI in Medical Transportation: 5 Practical NEMT Use Cases,"
  laying out RouteGenie's own cautious AI philosophy and PHI safeguards (routegenie.com/blog).
- 2025-09-11: Acquisition announced. Ascend Equity Partners (search fund led by Cameron Craig)
  acquires RouteGenie, backed by Next Coast Legacy and Northspring Partners (searchfundsnews.com).
- 2025 (mid-year): New Customer Relationship + Review Generation module launched to help NEMT
  providers build rider loyalty and reviews (WebSearch summary of RouteGenie news; original source
  not independently fetched, treat as secondhand).
- Ongoing: currently hiring for multiple senior technical roles alongside this one (Head of
  Engineering, Head of Technology), both in Buffalo, NY per LinkedIn job listings, indicating an
  active post-acquisition engineering build-out (linkedin.com/jobs/view/head-of-engineering-at-routegenie-4303676338;
  linkedin.com/jobs/view/head-of-technology-at-routegenie-4295049747).

## Culture

- Voice: professional, domain-expert, regulation-fluent. LinkedIn posts (862 followers) mix
  policy/Medicaid analysis with operational how-tos for fleet operators, citing specific statistics
  and framing regulatory shifts as "prepare, don't panic" (linkedin.com/showcase/routegenie_by_isi/).
- Public AI stance is notably conservative and safety-first for a company shipping LLM features: the
  blog explicitly warns that public AI tools should never touch PHI, Medicaid IDs, or sensitive
  personal data, and frames AI as an assistant requiring human review, not an autonomous
  decision-maker (routegenie.com/blog/how-to-use-ai-in-medical-transportation-top-5-use-cases-wprompts/).
- Founder-operator DNA: the company was built by people who ran their own NEMT/logistics business
  and needed the tool themselves, and the new CEO is a search-fund operator, not a VC-installed
  executive (routegenie.com/about; northspringpartners.com/entrepreneurs/cameron-craig).
- No independent employee-review data (Glassdoor blocked the page to unauthenticated fetches; not
  used per public-source rule). Treat internal day-to-day culture as unverified.

## Why-it-fits hooks (for Santiago)

- **Best hook: production LLM builder, not a lab experimenter.** Santiago has personally shipped
  production LLM features (Pragma Brain, a RAG "company brain" for SMB clients; Hermes, a
  function-calling/tool-use agent; Plutus, an MCP-exposed research agent with an autonomous
  discovery engine). That maps almost one-to-one onto this role's specific bar: "1+ year hands-on
  experience with production LLM/AI features shipped to real users," Claude as primary provider,
  RAG/vector databases, agent frameworks, and an explicit "Claude Code" workflow, which is his daily
  tool. This is a rare case where the stack match is not generic ("knows Python") but specific
  (Claude-first, RAG, agents, MCP).
- **Secondary hook: regulated-data discipline.** Santiago's Eugenia.ai work involved resident PII
  in a compliance-sensitive property-management context, and his consultancy work runs on real
  client business data. That is a smaller-scale echo of RouteGenie's HIPAA/PHI carefulness and gives
  him something honest to say about handling sensitive data responsibly, though he should not
  overstate this as formal healthcare/HIPAA experience (he has none verified).
- **Fit for the moment, not just the stack.** RouteGenie is a small, newly-acquired, founder-run
  company actively building its first real AI capability (parallel Head of Engineering/Head of
  Technology hires). Santiago's 3x founder background (built and exited Eugenia.ai, scaled Online
  Basics to $8M) is a good match for a company at this "we just changed hands and are building the
  next chapter" stage, where ownership and 0-to-1 instincts matter more than tenure at a big-name
  AI lab.
- **Honest concerns / watch-outs:**
  - No healthcare/HIPAA/regulated-industry experience on his resume; he should not claim domain
    expertise he does not have, only transferable data-handling discipline.
  - Voice AI (ElevenLabs, VAPI, LiveKit, Deepgram) is called out as "strongly preferred" and is not
    in his resume; he should be upfront that this would be new but learnable given his agent/API
    background.
  - Remote/location status for this Mexico posting is not explicitly stated on the ad (no city, no
    "remote" label); confirm this directly rather than assuming it matches his remote/CDMX
    preference.
  - Small company (about 40 people) recently changed ownership, so stability, roadmap, and
    engineering-team maturity should be probed in the interview; there is no independent
    (non-company) signal on engineering culture or attrition.
  - The Django/PostgreSQL/Angular core stack is not in his resume (his web stack is React/Node,
    not Angular); worth naming as a fast-learn gap rather than a blocker, especially since the role
    is scoped around the AI layer, not the Angular front end.

## Application-question angles

- **Why this company:** Lead with the specific-stack match, not generic interest in AI or NEMT.
  Something like: RouteGenie is one of the few postings where the tech stack (Claude-primary,
  RAG, agent frameworks, Claude Code as the dev workflow) reads like a description of what he
  already ships day to day (Pragma Brain, Hermes, Plutus), and the company is at a stage (freshly
  acquired, actively building its first AI capability) where that hands-on production experience
  compounds rather than getting lost in an existing AI org.
- **Why you fit:** Anchor on "I have already shipped the exact category of feature you're hiring
  for": a RAG system on real client data, a function-calling agent, an MCP-exposed research agent,
  built and operated end to end by a founder-engineer, not just prototyped. Pair that with the
  data-handling discipline from working with real client/resident data at Eugenia.ai and his
  consultancy, to speak to the HIPAA-adjacent seriousness the job implies, while being explicit that
  formal healthcare-regulatory experience is new to him.
- **Anything else:** Use this to be candid about the two real gaps (voice AI stack, Angular/Django
  core) framed as fast-learn areas given his track record of picking up unfamiliar stacks
  (Swift/Java mobile at Nextia, Python/Heroku microservices at Online Basics, TimescaleDB/Celery at
  Plutus), plus a one-line confirmation that he is TN-eligible and open to remote or Mexico City
  hybrid, since the posting does not spell out the work arrangement.

## Sources

- https://routegenie.com/ - product overview, module names, positioning
- https://routegenie.com/about/ - mission statement, founding story (2017), team size (40+ devs), Buffalo HQ, scale (600+ fleets, 20,000+ vehicles)
- https://routegenie.com/blog/how-to-use-ai-in-medical-transportation-top-5-use-cases-wprompts/ - RouteGenie's own AI philosophy and PHI/HIPAA safeguards, dated 2026-02-18
- https://newsroom.submitmypressrelease.com/2026/07/03/routegenie-helps-360-transport-triple-its-fleet-while-holding-98-on-time_2486734.html - customer case study, dated 2026-07-03
- https://searchfundsnews.com/ascend-equity-partners-buys-routegenie/ - acquisition details, Ascend Equity Partners, Cameron Craig, Sept 2025
- https://www.northspringpartners.com/portfolio-companies/route-genie - investor confirmation of 2025 investment, business model description
- https://www.northspringpartners.com/entrepreneurs/cameron-craig - CEO/search-fund background
- https://www.adzuna.com.mx/details/5760345064?utm_medium=api&utm_source=44e3003a - the actual job ad (job id 8041): full tech stack, required/preferred qualifications, location "Mexico"
- https://www.linkedin.com/jobs/view/head-of-engineering-at-routegenie-4303676338 - parallel open leadership role, signals active post-acquisition engineering build-out
- https://www.linkedin.com/jobs/view/head-of-technology-at-routegenie-4295049747 - parallel open leadership role, same signal
- https://www.linkedin.com/showcase/routegenie_by_isi/ - public LinkedIn presence, tone, follower count (862), recent post topics
- https://routegenie.applytojob.com/ - careers portal status (checked, currently shows "account no longer active" for the general listing page; role itself sourced via Adzuna)
- Tracxn RouteGenie profile (via WebSearch snippet) - employee count corroboration (~41 as of Jan 2026); not independently fetched, treat as secondary confirmation only

researched: 2026-07-14

Note: this is a first-draft dossier for Santiago to review and correct before it feeds a cover
letter. Glassdoor and Crunchbase pages returned 403 (login-walled) and were not used per the
public-source rule, so employee-review sentiment and detailed funding totals are not covered here.
