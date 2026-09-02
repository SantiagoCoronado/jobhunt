# FortIA: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-22
Target posting: "Ingeniero/a Senior de IA Agentica" (job id 6854), Get on Board,
https://www.getonbrd.com/jobs/ingeniero-a-senior-de-ia-agentica-fortia-remote

## Disambiguation (important)

There are several unrelated companies named "Fortia" or "FortiAI". This dossier is about the
Mexico City agentic AI consultancy at wearefortia.com, confirmed as the poster of the getonbrd
job (same positioning: "consultora de transformacion con IA agentica", Mexican clients, agents,
90-day results language matches the job ad's tone) [wearefortia.com]. It is NOT:
- Fortia Technology (fortia.com.mx), a 28+ year old Mexican HR/payroll software company, CEO
  Ponciano Betancourt [fortia.com.mx, wela.mx].
- Fortia Financial Solutions, a French fintech/AI compliance company founded 2012
  [linkedin.com/company/fortia-financial-solutions].
- The Fortia Group, an Ireland-based M&A advisory boutique [cbinsights.com].
- Fortia Energia, an oil and gas company [linkedin.com/company/fortia-energ-a].
- Fortinet's "FortiAI" security product line [fortinet.com].

## 1. Snapshot

FortIA is a small, newly founded (2026) Mexico City based consultancy that designs and deploys
agentic AI systems inside client operations, for mid-market and larger companies in Mexico, Latin
America, Spain, and the US [wearefortia.com/que-es-fortia, WebSearch summary of wearefortia.com].
Founded and run by Jose Soto [josesoto.ai]. No public funding, headcount, or revenue figures were
found; the job posting itself states the hire would be FortIA's first engineer, which is the
clearest public signal of stage: pre-team, founder plus early hires
[getonbrd.com job posting].

## 2. Core narrative

FortIA's pitch is explicitly anti-platform: "no somos una plataforma de software, somos una
consultora" (we are not a software platform, we are a consultancy). The stated method is
diagnose a specific operational bottleneck, deploy one agent against it with real data, and only
scale what proves ROI within 90 days, rather than selling a generic AI tool
[wearefortia.com/que-es-fortia]. The founder's manifesto frames this as a bet that the next
business advantage comes from redesigning how work flows through an organization, not from
buying more software, and that most companies will waste the agentic AI moment on disconnected
point tools [wearefortia.com/manifiesto]. The technical posting mirrors this philosophy closely:
bare-metal deploys on a Mac Studio and a Hetzner box, driven explicitly by client privacy
requirements (the systems will touch executive emails, contracts, and financial data)
[getonbrd.com job posting].

## 3. Mission & product

- Core offer: agentic AI transformation consulting, executive workshops, and a "fractional Chief
  AI Officer" retainer [wearefortia.com/servicios].
- Also runs a menu of executive programs (C-suite briefings, CHRO track, AI foundations
  workshop, AI automation/transformation programs, agentic transformation, family-business AI,
  board AI advisory, nearshored-operations AI, government AI)
  [wearefortia.com sitemap, wearefortia.com/executive-programs/*].
- Named use cases: reporting, document review, compliance, customer service, reconciliations,
  procurement, forecasting, and pipeline ops [wearefortia.com/casos-de-uso]. No named clients or
  public case studies were found on the site or in search; treat client traction as unverified.
- Notable detail: FortIA says it runs its own business on the same agent architecture it sells to
  clients, with agents handling its own finance tracking, sales tracking, and deliverables
  production [wearefortia.com/nosotros]. This is a self-reported claim, not independently
  verified, but it is consistent with the technical scope in the job posting.

## 4. Culture & voice

- Founder-led, single visible personality: Jose Soto, born Madrid 1985, moved to Mexico City in
  2013, roughly 20 years on the business/operations and marketing side (most recently CEO of TGG,
  a 35-person communications and marketing agency), now pivoting to focus on agentic AI
  [josesoto.ai].
- Soto has built a small ecosystem around this pivot: "La Escuela de IA" (an AI training program),
  "Prompt Nights" (monthly Mexico City events), and "The Agents Summit" for the LATAM region, plus
  a personal "IAX" (IA para Expansion) methodology: "Sin apropiacion no hay activacion. Sin
  activacion no hay expansion." [josesoto.ai].
- Voice is direct and business-fluent rather than deeply technical: manifesto language leans on
  metaphor ("como cuando se reintroduce una especie en un ecosistema") and speed/evidence framing
  over engineering detail [wearefortia.com/manifiesto]. The job posting itself, by contrast, is
  unusually technically specific (quantization, hybrid search, async Python), suggesting the
  posting was written or reviewed with real engineering input.

## 5. Recent news

Very little public news exists; this appears to be too new and too small for press coverage.
- Company founded 2026 by Jose Soto, per his own site [josesoto.ai]. No exact month found.
- No funding announcements, launches, or leadership changes found in web search as of this
  research date. Absence of coverage is itself a data point for a very early-stage shop; do not
  read anything further into it.

## 6. Engineering & AI direction

This is the most concrete, best-sourced part of FortIA's public footprint, taken directly from
the job posting for the role Santiago is applying to [getonbrd.com job posting]:
- Languages: Python (primary), TypeScript/Node for MCP servers and connectors.
- Local LLMs: Ollama, possibly vLLM; models Gemma 3, Llama 3.3.
- Cloud LLMs: Claude API (Anthropic), GPT (OpenAI), Gemini (Google), chosen per client.
- Vector stores: Qdrant primary, ChromaDB as alternative.
- Infra: macOS server (Mac Studio), dedicated Linux (Hetzner), Docker, systemd; deploys are
  "mostly bare-metal for privacy reasons," not cloud-first.
- Integrations: Gmail/Google Workspace APIs, Telegram Bot API, MCP server protocol, Whisper for
  transcription.
- Responsibilities: build custom agents from scratch on local models, deploy and maintain
  production systems, work directly with the founder on client discovery and architecture
  decisions, build MCP connectors to client SaaS platforms, build bidirectional data
  anonymization layers, implement vector stores and contextual/persistent memory, build
  deterministic rule layers on top of LLMs (not pure prompt-and-hope), build custom workflows
  (e.g. automated briefings, voice-to-email), and provide ongoing client maintenance/monitoring.
- Explicit philosophy: privacy and security discipline is a hard requirement because the systems
  touch executive emails, contracts, and financial data, and "no hay margen para sloppiness aqui."
This lines up with the site-level claim that FortIA prioritizes security, compatibility with a
client's existing tools, and client-controlled infrastructure over third-party cloud dependence
[wearefortia.com/tecnologia].

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago is not adjacent to this work, he is doing a near-identical
version of it right now as co-founder of Pragma AI, a B2B AI consultancy for Mexican SMBs that
builds RAG "company brain" systems and ships agentic tooling over MCP for real client operations
[resume/master_resume.yaml]. The overlap is unusually tight for a job search: same customer
profile (Mexican companies), same consulting motion (diagnose an operational bottleneck, deploy a
scoped agent, prove it, then expand), and the same core stack shape (RAG, MCP, vector search,
LLM-at-ingest data handling, internal automations for quoting/reporting/onboarding).

Concrete transferable evidence:
- Built and operates a hosted, authenticated MCP server (per-operator tokens, rate limits) over a
  company knowledge vault, plus 15 agent definitions and 10 reusable routines, for Pragma's own
  internal operations, which is the same "eat your own agent architecture" model FortIA claims for
  itself [resume/master_resume.yaml; wearefortia.com/nosotros].
- Kairos (personal project) pairs an in-app Claude Agent SDK integration with a standalone MCP
  server exposing 46 tools from one typed tool layer, running local-first on SQLite, which
  demonstrates comfort with the local-first, privacy-first architecture FortIA's stack embodies
  (Mac Studio/Hetzner bare-metal, MCP connectors, contextual memory) [resume/master_resume.yaml].
- Plutus exposes an LLM research agent and screening logic through an MCP control plane on top of
  a Python/Postgres backend, direct experience with the same protocol the role is built around
  [resume/master_resume.yaml].
- "Pragma Brain" (RAG company brain) shipped scoped retrieval with deterministic no-answer and
  citation gating and LLM-at-ingest sensitivity labeling, which maps onto the posting's
  requirement for "deterministic rule layers over LLMs" and data anonymization discipline
  [resume/master_resume.yaml].

Honest concerns and watch-outs:
- Pay: the posting lists 3,500 to 5,500 USD/month (42,000 to 66,000 USD/year). The top of that
  range just clears Santiago's stated 65,000 USD minimum; the bottom is well under it. Worth
  clarifying where in the band an offer would land before investing heavily in the process.
- Stage risk: no public funding, revenue, or named-client evidence was found. The role is
  explicitly "first engineer" with "no tech lead above you," which is upside for autonomy but
  means the business risk (single founder, unproven public traction) sits closer to a very early
  startup than a funded scale-up.
- Founder's background is business/marketing/operations (TGG agency, 20 years on the business
  side), not a technical AI background himself, per his own site [josesoto.ai]. Santiago would
  likely be the primary technical decision-maker with real architecture ownership rather than
  someone to learn engineering practice from.
- Local-model production ops (Ollama/vLLM quantization choices, VRAM sizing, throughput tradeoffs)
  is explicitly required and is a narrower, more infrastructure-specific skill than Santiago's
  resume evidence emphasizes; his RAG/MCP/agent work is strong, but this specific local-inference
  operations depth should be prepped for directly in interviews rather than assumed as covered.

## 8. Application-question angles

- Why this company: lead with the near-1:1 overlap between what Pragma AI already does (a
  Mexican AI consultancy building RAG and MCP systems for real client operations, diagnosing a
  bottleneck and proving an agent before scaling it) and what FortIA is building. Frame it as
  "I have been running this exact playbook for Mexican clients already, I want to do it at
  FortIA's stage and pace." Avoid restating the tech stack list; anchor on the operating model
  match (diagnose, deploy narrow, prove, scale) since that is FortIA's actual differentiator, not
  a specific model or vector database choice.
- Why you fit: lean on being the builder of a hosted MCP brain service and agent tooling that
  Pragma's own team uses daily, plus the privacy-conscious, local-first architecture instinct
  shown in Kairos. This role wants someone who can own architecture decisions without a tech lead;
  point to founder-level ownership (Online Basics, Eugenia.ai) as evidence of operating with that
  kind of autonomy already, not just as an engineer executing a spec.
- Anything else: if it comes up naturally, be straightforward that the local-inference ops side
  (quantization, VRAM sizing for Ollama/vLLM) is the one area to ramp fastest on, since the rest
  of the stack (MCP, RAG, vector stores, agent memory, deterministic guardrails) is already daily
  work. Do not raise compensation unprompted; if asked, the posted range is workable at the top
  end and worth a direct conversation about where an offer would land.

## Sources

- https://www.getonbrd.com/jobs/ingeniero-a-senior-de-ia-agentica-fortia-remote (target job
  posting: full tech stack, responsibilities, requirements, salary, remote/hybrid, application
  process; also pulled verbatim via local job id 6854 in `data/jobs.db`)
- https://wearefortia.com/ (company homepage, positioning statement)
- https://wearefortia.com/que-es-fortia (core methodology: diagnose, deploy, scale; "not a
  software platform" framing)
- https://wearefortia.com/nosotros (team model, mission statement, "eats its own dog food" claim)
- https://wearefortia.com/manifiesto (founder's stated beliefs about AI as infrastructure vs.
  point tools, speed and evidence framing)
- https://wearefortia.com/servicios (service lines: consulting, executive workshops, fractional
  Chief AI Officer)
- https://wearefortia.com/tecnologia (technology philosophy: security, integration with existing
  tools, client-controlled infrastructure)
- https://wearefortia.com/casos-de-uso (named use-case categories: reporting, document review,
  compliance, customer service, reconciliations, procurement, forecasting, pipeline ops)
- https://wearefortia.com sitemap (executive-programs subpages, confirms breadth of offer;
  fetched via https://wearefortia.com/sitemap.xml)
- https://josesoto.ai/ (founder Jose Soto bio: background, TGG role, creation of FortIA, La
  Escuela de IA, Prompt Nights, The Agents Summit, IAX methodology)
- https://fortia.com.mx/ and https://wela.mx/2025/11/28/taller-con-ponciano-betancourt-ceo-y-fundador-de-fortia-technology-estrategias-reales-para-escalar-y-gestionar-equipos/
  (used only to confirm Fortia Technology is a distinct, unrelated HR software company, CEO
  Ponciano Betancourt, for disambiguation)
- https://www.linkedin.com/company/fortia-financial-solutions, https://cbinsights.com (used only
  for disambiguation of other unrelated "Fortia" entities)
- https://www.fortinet.com/products/fortiai-assist (used only to confirm "FortiAI" is Fortinet's
  unrelated security product line, for disambiguation)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience:
  Pragma AI, Kairos, Plutus, prior founder roles, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile and salary
  floor, used to flag the compensation watch-out)

Note for Santiago: this is a draft dossier. FortIA has almost no public footprint beyond its own
site and the founder's personal site (expected for a company this new and this small); no client
names, no funding data, and no independent press were found anywhere. Treat every claim above
about FortIA's traction, team size, or "runs its own business on this architecture" as
self-reported by the company, not independently verified. Please review before it feeds into a
cover letter or application answers.
