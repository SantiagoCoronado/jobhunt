# Cohere

*Draft dossier for Santiago Coronado. Verify before relying on it in an application; refresh if stale.*

## 1. Snapshot

Toronto-founded enterprise AI company (2019) building foundation models (Command) and an agentic
workplace platform (North), plus retrieval infrastructure (Embed, Rerank), sold to large
regulated enterprises and governments as privately deployable, "sovereign" AI. Reported ~$240M
USD ARR (Feb 2026 investor memo), valued at ~$7B standalone, and in the process of merging with
German AI company Aleph Alpha (announced April 24, 2026) to form a combined entity valued at
roughly $20B with dual Toronto/Berlin HQ. Global but distributed team (offices in Toronto,
Montreal, New York, San Francisco, London, Paris, Seoul); public headcount estimates vary widely
across secondary sources (roughly 450 to 1,100+) and are not officially confirmed here, so treat
as unverified. CEO Aidan Gomez has said an IPO is possible "soon."
[cohere.com/blog/august-2025-funding-round](https://cohere.com/blog/august-2025-funding-round),
[betakit.com valuation](https://betakit.com/coheres-valuation-hits-7-billion-usd-following-100-million-round-extension/),
[techcrunch.com merger](https://techcrunch.com/2026/04/24/cohere-acquires-merges-with-german-based-startup-to-create-a-transatlantic-ai-powerhouse/),
[cnbc.com $240M ARR](https://www.cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html),
[en.wikipedia.org/wiki/Cohere](https://en.wikipedia.org/wiki/Cohere).

## 2. Core narrative

Cohere was founded by two of the eight "Attention Is All You Need" transformer-paper authors
(Aidan Gomez, Nick Frosst) plus Ivan Zhang, all out of Toronto, and has spent seven years betting
that the enterprise AI market wants a "sovereign," privately deployable alternative to
Silicon-Valley-hosted models: run inside a bank's or government's own infrastructure, never
touching Cohere's servers. That thesis is now compounding: real revenue ($240M ARR, 50%+
quarter-over-quarter growth through 2025), a pivot from "just an API" to a full agentic
workplace platform (North), and a bet-the-company move (merging with Germany's Aleph Alpha to
build a transatlantic, government-friendly AI powerhouse) that makes data sovereignty and
regulated-industry deployment the whole strategy, not a feature.
[wikipedia.org/wiki/Cohere](https://en.wikipedia.org/wiki/Cohere),
[cnbc.com](https://www.cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html),
[techcrunch.com merger](https://techcrunch.com/2026/04/24/cohere-acquires-merges-with-german-based-startup-to-create-a-transatlantic-ai-powerhouse/).

## 3. Mission & product

- **Mission**: "Do whatever it takes to scale intelligence and serve humanity" / "enhance human
  wellbeing" by helping businesses "scale innovation, boost productivity, and drive progress."
  [cohere.com/about](https://cohere.com/about).
- **Command family**: generative LLMs (Command A, Command A Reasoning, Command A Translate,
  Command A Vision, and the newest Command A+, released May 20, 2026, a 218B-parameter MoE model
  built for "sovereign agentic capabilities," runnable on as little as one Blackwell GPU or two
  quantized H100s). [cohere.com/blog/command-a-plus](https://cohere.com/blog/command-a-plus).
- **North**: Cohere's flagship enterprise agentic platform, generally available since August
  2025. Three pillars: Discover (grounded enterprise search/Q&A), Create (document/summary/chart
  generation), Automate (AI agents that run workflows). Deployable in the cloud, a private VPC,
  fully on-prem, or air-gapped, targeting security-first industries (banking, legal, healthcare,
  telecom, government). Named customers/pilots include RBC, Dell, LG, Fujitsu, Oracle, Salesforce,
  SAP, Asana, Ensemble Health Partners, and Palantir.
  [cohere.com/blog/north-ga](https://cohere.com/blog/north-ga),
  [cohere.com/north](https://cohere.com/north),
  [techcrunch.com North launch](https://techcrunch.com/2025/08/06/coheres-new-ai-agent-platform-north-promises-to-keep-enterprise-data-secure/).
- **North Mini Code** (June 9, 2026): Cohere's first open-weight model built specifically for
  agentic software engineering (sub-agent orchestration, terminal work, code review); 30B params,
  3B active (MoE), Apache 2.0, runs on a single H100.
  [cohere.com/blog/north-mini-code](https://cohere.com/blog/north-mini-code).
- **Embed / Rerank**: the retrieval layer under RAG and agents. Embed turns text and images into
  embeddings for semantic search and agentic tool use (100+ languages, up to 96% embedding
  compression); Rerank boosts search/retrieval quality. Together they underpin North and Compass
  (Cohere's search product) and are also sold standalone via API.
  [cohere.com/embed](https://cohere.com/embed).
- **Business model**: software licenses and services rather than pure consumption; customers run
  models via Cohere's managed cloud or directly on their own hardware (a "Model Vault" style
  private-inference option), which CNBC's reporting frames as a capital-efficient alternative to
  full-stack, infrastructure-heavy competitors. 70% gross margins reported.
  [cnbc.com](https://www.cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html).

## 4. Culture & voice

- Stated values: **Momentum** (move quickly, trust each other, push with purpose),
  **Openness** (inclusivity, diverse perspectives), **Autonomy** (flexibility and ownership for
  every team member). [cohere.com/careers](https://cohere.com/careers).
- Globally distributed, remote-friendly org with 7+ office hubs (Toronto, Montreal, New York, San
  Francisco, London, Paris, Seoul, and a newly tripled London footprint as of June 15, 2026);
  benefits emphasize flexibility (weekly remote-work meal stipend, co-working allowance for
  non-office staff, six weeks paid vacation, six months parental leave, $2,000/yr professional
  development budget). [cohere.com/careers](https://cohere.com/careers),
  [cohere.com/blog (London office)](https://cohere.com/blog).
- Voice leans research-credible and enterprise-serious rather than hype-driven: blog content mixes
  product launches with technical research posts (e.g. "Hardware-aware dynamic speculative
  decoding," "LLM Serving Fairness: No more noisy neighbors") and cultural/localization work
  (Cohere and Mila partnering on Quebec French; a dedicated Arabic transcription model), consistent
  with a company that sells sovereignty and cultural/linguistic nuance as differentiators, not just
  raw benchmark wins. [cohere.com/blog](https://cohere.com/blog).
- Cohere Labs (open science research arm, launched 2022) claims 4,500+ community members, signaling
  a research-open, academically credible identity alongside the enterprise sales motion.
  [cohere.com/about](https://cohere.com/about).

## 5. Recent news (last ~12 months)

- **Aug 6, 2025**: North launched into general availability, positioned around private,
  behind-the-firewall agent deployment.
  [techcrunch.com](https://techcrunch.com/2025/08/06/coheres-new-ai-agent-platform-north-promises-to-keep-enterprise-data-secure/).
- **Aug 2025**: Raised $500M at a $6.8B valuation, led by Radical Ventures and Inovia Capital.
  [cohere.com/blog/august-2025-funding-round](https://cohere.com/blog/august-2025-funding-round).
- **Sep 24, 2025**: Extended the round with an additional $100M, pushing valuation to ~$7B (new
  investors: Business Development Bank of Canada, Nexxus Capital).
  [betakit.com](https://betakit.com/coheres-valuation-hits-7-billion-usd-following-100-million-round-extension/).
- **Feb 13, 2026**: Investor memo obtained by CNBC shows $240M ARR (beat a $200M target), 50%+
  QoQ growth through 2025, 70% gross margins; CEO Aidan Gomez says IPO "soon" is possible, targets
  profitability by 2029. [cnbc.com](https://www.cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html).
- **Mar 26, 2026**: Launched Cohere Transcribe, an open-source speech recognition model.
  [cohere.com/blog](https://cohere.com/blog).
- **Apr 24, 2026**: Announced a merger with German AI company Aleph Alpha, structured as a
  simultaneous acquisition plus Series E, backed by a ~$600M commitment from Germany's Schwarz
  Group; combined entity valued at roughly $20B, expected dual HQ in Toronto and Berlin, aimed at
  "Sovereign AI for the World" and deeper access to European government/enterprise relationships
  (Aleph Alpha's ties include Deutsche Bank, SAP, Bosch, the German federal government). Deal not
  yet closed as of this research, subject to regulatory approval.
  [techcrunch.com](https://techcrunch.com/2026/04/24/cohere-acquires-merges-with-german-based-startup-to-create-a-transatlantic-ai-powerhouse/),
  [cnbc.com merger](https://www.cnbc.com/2026/04/24/cohere-aleph-alpha-germany-ai-europe-expansion.html).
- **May 20, 2026**: Launched Command A+ (sovereign, agentic, multimodal, 48-language MoE model).
  [cohere.com/blog/command-a-plus](https://cohere.com/blog/command-a-plus).
- **May 27, 2026**: Partnership with Mila to advance Quebec French language/cultural AI.
  [cohere.com/blog](https://cohere.com/blog).
- **Jun 9, 2026**: Launched North Mini Code, Cohere's first open-weight agentic coding model.
  [cohere.com/blog/north-mini-code](https://cohere.com/blog/north-mini-code).
- **Jun 15, 2026**: Tripled UK footprint with a new London office to support R&D growth.
  [cohere.com/blog](https://cohere.com/blog).
- **Jul 7 and Jul 10, 2026**: Shipped Cohere Transcribe Arabic and published research on
  hardware-aware dynamic speculative decoding, ongoing signal that model/infra research is active
  and shipping cadence is fast. [cohere.com/blog](https://cohere.com/blog).

Watch-out on history: in July 2024 Cohere laid off ~5% of staff (~20 people) the day after closing
a $500M round, described internally as "realignment." No layoffs have been reported since; 2025-26
coverage shows continued hiring and funding growth.
[cnbc.com 2024 layoffs](https://www.cnbc.com/2024/07/23/cohere-layoffs-20-employees-cut-following-500-million-funding.html).

## 6. Engineering & AI direction

- Core stack signal from the job description itself and product docs: Python in production,
  RAG and agentic architectures (ReAct, Plan-and-Execute patterns), vector databases, orchestration
  frameworks, and a strong emphasis on building evaluation frameworks for agent accuracy, safety,
  and latency (not just "vibes" testing). [jobs.ashbyhq.com / mirrored posting](https://jobs.ashbyhq.com/cohere/75c0032c-7200-48bf-9d6d-355880dd93d9).
- Model direction: mixture-of-experts architectures optimized to run on modest hardware footprints
  (Command A+ on 1-2 GPUs; North Mini Code on a single H100), explicitly trading some raw scale
  for deployability inside a customer's own infrastructure, which is the technical expression of
  the "sovereign AI" business thesis. [cohere.com/blog/command-a-plus](https://cohere.com/blog/command-a-plus),
  [marktechpost.com North Mini Code](https://www.marktechpost.com/2026/06/11/meet-north-mini-code-coheres-30b-open-weight-mixture-of-experts-model-with-3b-active-parameters-for-agentic-coding/).
- Active applied-research output on serving efficiency and multi-tenant fairness (speculative
  decoding, "no more noisy neighbors" serving fairness), suggesting engineering org invests in
  inference-serving infra, not just model training.
  [cohere.com/blog](https://cohere.com/blog).
- Retrieval as a first-class product line (Embed, Rerank) rather than a commodity, positioned
  explicitly for RAG and agentic tool use, multilingual (100+ languages) and multimodal (text +
  images). [cohere.com/embed](https://cohere.com/embed).
- Deployment model spans managed cloud, private VPC, on-prem, and air-gapped, which pushes
  engineering (and Forward Deployed Engineers specifically) to build for observability, security,
  and auditability as core requirements, not afterthoughts.
  [cohere.com/north](https://cohere.com/north).

## 7. The role: Forward Deployed Engineer, Agentic Platform

From the live Cohere/Ashby posting (mirrored content, since the direct Ashby page is JS-rendered
and did not return text to automated fetch; same role family, US-based variant, San
Francisco/Eastern-time-zone-preferred, 20-40% travel):
[jobs.ashbyhq.com/cohere/75c0032c-7200-48bf-9d6d-355880dd93d9](https://jobs.ashbyhq.com/cohere/75c0032c-7200-48bf-9d6d-355880dd93d9),
[mirrored posting via ziprecruiter/linkedin](https://www.linkedin.com/jobs/view/forward-deployed-engineer-agentic-platform-at-cohere-4319336681).

- Own design, build, and production deployment of agentic workflows (LLM agents that reason, plan,
  and act across tools, APIs, and sensitive enterprise data) for real enterprise customers, from
  prototype to production.
- Work directly with enterprise clients to turn ambiguous business problems into well-scoped
  agentic workflows with clear success criteria and evaluation methodology.
- Build evaluation frameworks that measure agent accuracy, safety, and latency (not ad hoc
  testing).
- Contribute directly to the North platform itself (not just deploy on top of it): feed
  first-of-their-kind customer patterns back into shared frameworks used org-wide.
- Flex across the stack as the problem demands, including frontend work when needed.
- Travel 20 to 40% to work on-site with customers and partners.
- Bonus: experience in regulated industries (finance, healthcare, telecom) and enterprise
  security/compliance/auditability for AI systems, both squarely in North's target market.

## 8. Why-fit angles for Santiago

**Lead hook: forward-deployed, founder-shaped, 0-to-1 delivery.** Santiago has spent three
companies (Online Basics, Eugenia.ai, Pragma AI) doing exactly what this role asks of a Forward
Deployed Engineer: sit with a real (often messy) business or client problem, scope it end to end,
and ship a working system, not a slide deck. At Eugenia.ai he personally "owned the full product
lifecycle and led on-site client deployments," translating conflicting HOA/property-manager
requirements into a shipped product across 20+ buildings; that is a direct, literal precedent for
"convert ambiguous business problems into well-scoped agentic workflows" and for the 20-40% travel
expectation. At Pragma AI he is currently building "Pragma Brain," a RAG "company brain" for SMB
clients, plus conversational agents and internal automations, which maps straight onto North's
Discover/Create/Automate pillars and Cohere's own Embed/Rerank retrieval stack. Santiago should
lead with this founder-as-forward-deployed-engineer framing rather than generic "I love AI"
enthusiasm.
[resume/master_resume.yaml].

**Second hook: the LLM/agent engineering is real, not resume-inflated.** He has shipped an LLM
workflow on the Anthropic and OpenAI APIs with custom prompt engineering and multi-stage
validation (Online Basics), an autonomous tool-use/function-calling agent (personal-finance agent
on the Hermes framework), and an MCP-based agentic research platform (Plutus) with vectorized
signal scans and an LLM research agent, plus a Claude Agent SDK integration (Kairos). That is
concrete RAG + agentic + evaluation-adjacent experience that speaks directly to the JD's ask for
"hands-on production Python," "RAG and agentic applications," and "orchestration frameworks."
He is also a daily Claude Code user, which is a small but genuine, honest resonance point given
Cohere's own recent bet on agentic coding models (North Mini Code) and its emphasis on engineering
tooling and standards.

**Honest concerns / watch-outs:**
- **Location and travel**: the posting is US-based (San Francisco / Eastern-time-zone
  preferred) with 20-40% travel to customer sites. Santiago is based in Mexico City and is TN-visa
  eligible, not a US citizen or current US resident; work authorization and physical relocation or
  heavy cross-border travel logistics are a real, non-trivial gap to address head-on, not gloss
  over, if he pursues this. This should be surfaced early in any application, not left implicit.
- **Enterprise sales-cycle and compliance depth**: North's core customers are banks, health
  systems, telecoms, and governments with real audit, security, and compliance requirements.
  Santiago's client work (Online Basics ecommerce, Eugenia.ai proptech, Pragma AI SMBs) is real
  0-to-1 delivery experience but not large-regulated-enterprise experience; he should not overstate
  this, and can honestly frame it as "built the deployment muscle at SMB/mid-market scale, ready to
  apply it at enterprise scale" rather than claiming direct enterprise-compliance experience he
  does not have.
- **Company-specific tooling depth**: no evidence Santiago has hands-on experience with Cohere's
  specific stack (Command models, Embed/Rerank APIs, North itself). This is a normal, expected gap
  for an external candidate and not worth apologizing for, but it means leaning on transferable
  RAG/agent architecture experience (built on Anthropic/OpenAI APIs) rather than claiming Cohere
  product familiarity.

## 9. Application-question angles

- **Why this company**: Lead with the founder-to-forward-deployed-engineer throughline, not a
  tour of Cohere's four product areas. The honest angle is that Cohere's whole current chapter
  (North GA, the Aleph Alpha merger, the sovereign-AI thesis) is a bet that enterprise AI wins by
  being deployed inside the customer's own walls by people who can sit with a client's actual mess
  and ship something real, which is the exact motion Santiago has run three times as a founder.
  Reference the Aleph Alpha merger or North's GA launch as evidence this is a company in an active,
  high-conviction growth chapter right now, not a static pitch.
- **Why you fit**: Do not checklist skills. Pick one concrete story (Eugenia.ai on-site
  deployments translating conflicting stakeholder needs into a shipped product, or the Pragma
  Brain RAG system built for real client data) and show the line from that story to "own an
  agentic workflow end to end with an enterprise customer, build the eval framework, ship it."
  Mention Claude Code / Claude Agent SDK fluency as a small, honest signal of comfort building
  with and on top of frontier agent tooling day to day.
- **Anything else**: This is the natural place to be upfront about the US-location and TN-visa
  reality, framed as a practical logistics note rather than a disqualifier: he is TN-eligible,
  based in Mexico City, comfortable with the travel cadence the role describes, and wants to raise
  the location question directly rather than have it surface later.

## 10. Sources

researched: 2026-07-13

- [cohere.com/about](https://cohere.com/about) - mission statement, founding story, HQ/offices, Cohere Labs.
- [cohere.com/careers](https://cohere.com/careers) - values (Momentum, Openness, Autonomy), remote/distributed work style, benefits.
- [cohere.com/blog](https://cohere.com/blog) - recent product/research/partnership post titles and dates (2026).
- [cohere.com/blog/north-ga](https://cohere.com/blog/north-ga) - North general-availability details.
- [cohere.com/north](https://cohere.com/north) - North product pillars, deployment options, named customers, RBC quote.
- [cohere.com/blog/command-a-plus](https://cohere.com/blog/command-a-plus) - Command A+ launch, specs, sovereign-agentic positioning.
- [cohere.com/blog/north-mini-code](https://cohere.com/blog/north-mini-code) - North Mini Code launch and specs.
- [cohere.com/embed](https://cohere.com/embed) - Embed/Rerank product details and use cases.
- [cohere.com/blog/august-2025-funding-round](https://cohere.com/blog/august-2025-funding-round) - Aug 2025 $500M raise at $6.8B valuation.
- [en.wikipedia.org/wiki/Cohere](https://en.wikipedia.org/wiki/Cohere) - founders' background (transformer paper authors), funding timeline, HQ, product list.
- [betakit.com/coheres-valuation-hits-7-billion](https://betakit.com/coheres-valuation-hits-7-billion-usd-following-100-million-round-extension/) - Sep 2025 valuation extension to ~$7B.
- [cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html](https://www.cnbc.com/2026/02/13/ai-startup-cohere-revenue-ipo.html) - $240M ARR, growth rate, margins, IPO commentary from CEO Aidan Gomez.
- [techcrunch.com/2026/04/24/...transatlantic-ai-powerhouse](https://techcrunch.com/2026/04/24/cohere-acquires-merges-with-german-based-startup-to-create-a-transatlantic-ai-powerhouse/) - Aleph Alpha merger details, ~$20B valuation, dual HQ.
- [cnbc.com/2026/04/24/cohere-aleph-alpha-germany-ai-europe-expansion.html](https://www.cnbc.com/2026/04/24/cohere-aleph-alpha-germany-ai-europe-expansion.html) - merger, European government/enterprise rationale.
- [techcrunch.com/2025/08/06/...north-promises-to-keep-enterprise-data-secure](https://techcrunch.com/2025/08/06/coheres-new-ai-agent-platform-north-promises-to-keep-enterprise-data-secure/) - North launch coverage, pilot customers (RBC, Dell, LG, Ensemble Health, Palantir).
- [cnbc.com/2024/07/23/cohere-layoffs-20-employees-cut-following-500-million-funding.html](https://www.cnbc.com/2024/07/23/cohere-layoffs-20-employees-cut-following-500-million-funding.html) - July 2024 layoffs (5% of staff), historical watch-out.
- [marktechpost.com/.../north-mini-code](https://www.marktechpost.com/2026/06/11/meet-north-mini-code-coheres-30b-open-weight-mixture-of-experts-model-with-3b-active-parameters-for-agentic-coding/) - North Mini Code technical detail.
- [jobs.ashbyhq.com/cohere/75c0032c-7200-48bf-9d6d-355880dd93d9](https://jobs.ashbyhq.com/cohere/75c0032c-7200-48bf-9d6d-355880dd93d9) - Forward Deployed Engineer, Agentic Platform job listing (role family match; direct Ashby fetch of the specific URL provided, https://jobs.ashbyhq.com/cohere/b0bcef37-1d20-414f, returned only JS shell content, no extractable text).
- [linkedin.com/jobs/view/forward-deployed-engineer-agentic-platform-at-cohere-4319336681](https://www.linkedin.com/jobs/view/forward-deployed-engineer-agentic-platform-at-cohere-4319336681) - mirrored full job description text (location, travel %, responsibilities, requirements).
- `config/profile.yaml`, `resume/master_resume.yaml` - Santiago's background used for fit angles (internal files, not public sources).

Note: the exact job URL given (https://jobs.ashbyhq.com/cohere/b0bcef37-1d20-414f) could not be
fetched directly (Ashby serves the description via client-side JavaScript that the fetch tool did
not render); the role details above come from a same-title, same-team posting on Cohere's Ashby
board and its LinkedIn mirror. If the specific posting differs in scope, location, or requirements,
re-verify against the live link before finalizing an application.
