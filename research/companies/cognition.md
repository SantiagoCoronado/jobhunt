# Cognition (Devin) : Company Dossier

Draft for Santiago to review before use. All claims are sourced below; anything unverifiable is
labeled as such.

## 1. Snapshot

Cognition AI, Inc. (dba Cognition), San Francisco. Private, growth-stage AI company founded
August 2023 by Scott Wu, Steven Hao, and Walden Yan. Makers of Devin (autonomous AI software
engineer, launched March 2024) and Devin Desktop (formerly Windsurf, the AI-native IDE,
rebranded June 2, 2026). Raised roughly $2.5B total; last round closed May 27, 2026 at $1B on a
$25B pre-money / ~$26B post-money valuation. Revenue run-rate about $492M annualized as of that
raise. [Wikipedia](https://en.wikipedia.org/wiki/Cognition_AI); [TechCrunch, May 27 2026](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/)

## 2. Core narrative

Cognition is racing to build "the first AI software engineer" and, after a chaotic 72-hour deal
to acquire Windsurf in July 2025 (struck right after Google's $2.4B acquihire of Windsurf's CEO
and just after OpenAI's $3B offer expired), fused agent and IDE into one line: Devin plus Devin
Desktop. The company dogfoods hard: Devin now commits about 89% of Cognition's own code, and
leadership frames the company's edge as engineering rigor (microVM isolation, hypervisor-level
state snapshots, hierarchical multi-agent orchestration built over roughly two years) rather than
a thin model wrapper. Culturally, it runs an explicitly "extreme performance culture," publicly
stated by the CEO, which is unusual candor and a real signal about how the company operates.
[Cognition, Windsurf acquisition post](https://cognition.com/blog/windsurf); [TechCrunch, Jul 14 2025](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/); [TechCrunch, May 29 2026](https://techcrunch.com/2026/05/29/cognitions-scott-wu-says-ai-coding-agents-shouldnt-replace-humans/); [Scott Wu on X, Aug 2025](https://x.com/ScottWu46/status/1952776198947520659)

## 3. Mission & product

- **Devin**: autonomous AI software engineer that plans, writes, tests, and ships code inside a
  sandboxed workspace (shell, editor, browser, persistent filesystem). Public launch March 2024;
  Devin 2.0 shipped April 2025 starting at $20/month. At launch, Devin resolved 13.86% of issues
  end-to-end on SWE-bench versus a prior state of the art of 1.96%.
  [Cognition, Introducing Devin](https://cognition.com/blog/introducing-devin); [Wikipedia](https://en.wikipedia.org/wiki/Cognition_AI); [VentureBeat](https://venturebeat.com/ai/cognition-emerges-from-stealth-to-launch-ai-software-engineer-devin)
- **Devin Desktop** (formerly Windsurf, rebranded June 2, 2026): AI-native IDE with an "Agent
  Command Center" that surfaces local and cloud agent sessions together. It now ships on the open
  Agent Client Protocol (Apache 2.0), so Claude Agent, Codex, Gemini CLI, OpenCode, and Junie run
  as first-class agents inside it, not just Devin. Windsurf's original built-in agent, Cascade,
  reached end of life July 1, 2026, replaced by "Devin Local," a Rust rewrite roughly 30% more
  token-efficient. [Devin Docs, Desktop FAQ](https://docs.devin.ai/desktop/devin-desktop-faq); coverage of the rebrand: [ChatForest](https://chatforest.com/builders-log/windsurf-devin-desktop-rebrand-devin-local-acp-builder-guide/)
- **Business model**: enterprise seats and usage-based pricing. Publicly named customers include
  Mercedes-Benz, Goldman Sachs, Infosys, NASA, and Santander.
  [Cognition site](https://cognition.com/); [TechCrunch, May 27 2026](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/)
- **Traction**: Devin's ARR grew from about $1M (Sep 2024) to about $73M (Jun 2025); Windsurf
  brought $82M ARR at acquisition (enterprise ARR doubling quarter over quarter, 350+ enterprise
  customers). Combined run-rate reached about $492M annualized by May 2026, with enterprise usage
  up 50% month over month over the prior six months.
  [Wikipedia](https://en.wikipedia.org/wiki/Cognition_AI); [TechCrunch, Jul 14 2025](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/); [TechCrunch, May 27 2026](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/)

## 4. Culture & voice

- Founding team includes 10 IOI (International Olympiad in Informatics) gold medalists; hires
  come from Cursor, Scale AI, Modal, Google DeepMind, Waymo, and Nuro.
  [Cognition Careers](https://cognition.com/careers)
- CEO Scott Wu has stated publicly that Cognition runs an "extreme performance culture" and is
  "upfront about this in hiring so there are no surprises later," describing routine weekend
  office work and late nights. [Scott Wu on X, Aug 2025](https://x.com/ScottWu46/status/1952776198947520659)
- Three weeks after the Windsurf acquisition (by Aug 5, 2025), Cognition laid off 30 of the
  acquired staff and offered the remaining roughly 200 a buyout (nine months' salary, deadline
  Aug 10) rather than absorbing them into an unchanged culture described as six days a week and
  80+ hour weeks. Wu: "We don't believe in work-life balance, building the future of software
  engineering is a mission we all care so deeply about that we couldn't possibly separate the
  two." [TechCrunch, Aug 5 2025](https://techcrunch.com/2025/08/05/three-weeks-after-acquiring-windsurf-cognition-offers-staff-the-exit-door/)
- Interview philosophy: candidates are explicitly encouraged to use AI freely during interviews.
  Wu argues testing raw, unassisted coding output is now "the wrong question"; interviews instead
  probe product judgment ("what do you think is the right thing to build? How do you make these
  product decisions?"). [OfficeChai](https://officechai.com/ai/cognition-ceo-scott-wu-explains-why-they-let-people-use-as-much-ai-as-they-like-in-job-interviews/)
- Public mission language: "the purpose of technology is to expand human capacity, not by
  replacing meaningful work but by working alongside people as an exponential collaborator,"
  reframing engineers "from bricklayers to architects." [Cognition site](https://cognition.com/); [Windsurf acquisition post](https://cognition.com/blog/windsurf)

## 5. Recent news (last ~12 months)

- **Jul 14, 2025**: Cognition acquires Windsurf (IP, product, trademark, brand; reported deal
  size around $250M), days after Google hired Windsurf's CEO and research leads in a $2.4B
  licensing deal and hours after OpenAI's $3B acquisition offer expired.
  [TechCrunch](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/); [Cognition blog](https://cognition.com/blog/windsurf)
- **Aug 5, 2025**: 30 acquired Windsurf staff laid off; ~200 more offered a nine-month buyout
  (deadline Aug 10) instead of the always-on culture. [TechCrunch](https://techcrunch.com/2025/08/05/three-weeks-after-acquiring-windsurf-cognition-offers-staff-the-exit-door/)
- **Sep 8, 2025**: Cognition closes a $400M round, valuing the company at $10.2B post-money.
  [CNBC](https://www.cnbc.com/2025/09/08/cognition-valued-at-10point2-billion-two-months-after-windsurf-.html)
- **May 27, 2026**: Raises $1B at $25B pre-money (~$26B post-money), led by Lux Capital, General
  Catalyst, and 8VC, with Founders Fund, Ribbit Capital, Atreides, Elad Gil, Soma Capital, and
  Layer Global also participating. Revenue run-rate reported at $492M, up from $37M a year
  earlier. [TechCrunch](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/); [Bloomberg](https://www.bloomberg.com/news/articles/2026-05-27/ai-coding-startup-cognition-raises-1-billion-at-26-billion-value)
- **May 29, 2026**: In a TechCrunch interview, Scott Wu says agents "shouldn't replace humans,"
  describes Devin's current capability as "somewhere between a junior and a mid-level engineer,"
  and states Devin commits about 89% of Cognition's own code internally.
  [TechCrunch](https://techcrunch.com/2026/05/29/cognitions-scott-wu-says-ai-coding-agents-shouldnt-replace-humans/)
- **Jun 2, 2026**: Windsurf product rebranded to Devin Desktop; Cascade agent set to reach end of
  life Jul 1, 2026, replaced by "Devin Local" (Rust rewrite); adds open Agent Client Protocol
  support so Claude Agent, Codex, Gemini CLI, OpenCode, and Junie run first-class inside the IDE.
  [Devin Docs](https://docs.devin.ai/desktop/devin-desktop-faq)

## 6. Engineering & AI direction

- **Sandbox infrastructure**: moved from containers to microVM-level isolation for agent
  workloads (each workload gets its own kernel, no shared attack surface), which took over a year
  of hypervisor engineering. Agents persist across async waits (CI, code review) via full
  hypervisor-level state snapshots (memory, processes, filesystem) instead of staying always-on.
  [Cognition, What We Learned Building Cloud Agents](https://cognition.com/blog/what-we-learned-building-cloud-agents)
- **Orchestration and governance**: running hundreds of concurrent agent sessions requires
  environment provisioning, demand prediction, crash recovery, permission inheritance across
  systems, and tamper-evident audit trails; deep integrations into CI, monitoring, registries, and
  internal docs (they cite Stripe maintaining 400+ internal tools as an example of the integration
  surface enterprises need covered). [Cognition, What We Learned Building Cloud Agents](https://cognition.com/blog/what-we-learned-building-cloud-agents)
- **Multi-agent lessons (published)**: writes should stay single-threaded while other agents
  contribute analysis; isolated-context review agents (no shared context with the coder) catch
  about 2 bugs per PR, 58% severe, because fresh context avoids attention degradation at long
  context lengths; unstructured "swarms" of negotiating agents are "mostly a distraction" versus
  hierarchical manager/child delegation; cross-frontier model routing (pairing Claude and GPT)
  helps on complex tasks when routed by capability, not just difficulty; a weaker model cannot
  reliably self-escalate to a stronger one. [Cognition, Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working)
- **Dogfooding**: Devin writes about 89% of Cognition's own code today (Wu, May 2026).
  [TechCrunch](https://techcrunch.com/2026/05/29/cognitions-scott-wu-says-ai-coding-agents-shouldnt-replace-humans/)
- **Bet**: an agent-agnostic IDE layer (Devin Desktop, open Agent Client Protocol) paired with a
  proprietary autonomous agent (Devin), betting the orchestration/IDE layer matters as much as any
  single model. [Devin Docs](https://docs.devin.ai/desktop/devin-desktop-faq)
- Some third-party coverage references an in-house "SWE-1.5 / SWE-1.7" model family with specific
  benchmark claims (for example Terminal-Bench scores); this is from an aggregator blog, not a
  Cognition primary source, so treat those specific numbers as unverified.

## 7. What an Applied AI Engineer does there

Per the job posting and cached listing content (Ashby page did not fully render for direct fetch;
details below are corroborated via search-indexed content of the same posting and a matching
Glassdoor listing):

- Applied AI Engineers "operationalize AI modernization at the enterprise level": rather than
  demoing Devin, they deploy it by embedding with customer engineering teams, integrating agentic
  workflows into how those teams actually build and ship, and driving measurable productivity
  gains.
- Concretely: lead live workshops and pair-programming sessions with enterprise engineering teams;
  guide customers through installing, configuring, and optimizing Devin and related tooling
  (DeepWiki, MCP integrations); pair-program on live production problems to demonstrate high-value
  usage patterns; quantify impact via productivity metrics and ROI stories; turn individual
  engagements into repeatable playbooks, digital learning content, and partner-enablement models.
- Requirements: STEM degree or equivalent hands-on experience; 3+ years as a software engineer,
  technical consultant, deployment strategist, forward-deployed engineer, solutions engineer, or
  similar; strong coding proficiency in Python and JavaScript/TypeScript.
- Compensation band: $180K to $225K (US).
- Location: San Francisco per the role title; Cognition's broader Customer Engineering function
  (18+ open roles) spans multiple geographies, but this specific listing appears SF-based.

[Job posting](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d); corroborating listing: [Glassdoor](https://www.glassdoor.com/job-listing/applied-ai-engineer-cognition-ai-JV_KO0,19_KE20,32.htm?jl=1009917018619)

## 8. Why-fit angles for Santiago

**Lead hook**: Santiago is a 3x technical founder who has already been the person the Applied AI
Engineer role is meant to create: someone who ships production, full-stack LLM/agent systems
himself and uses Claude Code daily as his primary build tool. He is not applying to learn what an
agentic workflow is, he has been running one solo for years (Pragma AI's RAG "company brain",
Plutus's autonomous discovery agent with an MCP control plane, Kairos's dual integration of the
Claude Agent SDK and an MCP server over one typed tool layer). That is directly the "applied AI
fluency" and hands-on deployment posture the role is hired for.

Supporting angles:

- The role is explicitly forward-deployed: embed with engineering teams, pair-program live,
  convert engagements into playbooks. That is the same motion as his on-site client deployments at
  Eugenia.ai (onboarding HOAs and property administrators, translating conflicting requirements
  into shipped product) and his hands-on delivery work at Online Basics and now Pragma AI.
- His MCP and Claude Agent SDK shipping experience is concretely relevant now that Devin Desktop
  has adopted the open Agent Client Protocol and treats Claude Agent as a first-class citizen
  alongside Devin. He can speak to agent tooling interop from direct build experience, not just as
  a user of Devin.
- Cognition's own team composition (careers page: "high concentration of former founders")
  suggests a real cultural fit for someone who has raised capital, led a 9-person team, and built
  and exited a company (Eugenia.ai) and scaled another to $8M revenue (Online Basics).

**Honest concerns / watch-outs**:

- Cognition is explicit and public about an "extreme performance culture": weekend office time and
  80+ hour weeks described by the CEO as the norm, not an opt-out once hired. This is a real,
  stated risk against a sustainable-hours expectation and worth Santiago being honest with himself
  about before applying.
- The posting is San Francisco based. Santiago's profile (`config/profile.yaml`) lists him as
  Mexico City based, TN-visa eligible for US employment, but not open to relocating for an
  on-site or hybrid role outside Mexico City. This is a direct conflict with his own stated
  dealbreaker and should be resolved (confirm whether meaningful remote or travel-based
  forward-deployed arrangement exists, or treat this as a deliberate, discussed exception) before
  investing in a full application.
- Days after acquiring Windsurf, Cognition laid off or bought out a large share of the acquired
  team rather than retaining them. It signals a company that moves fast and is blunt about
  headcount when priorities shift; not necessarily disqualifying, but worth knowing.
- The posted compensation ($180K to $225K) is a US band; if TN-visa and relocation logistics are
  in play, that is worth clarifying early in process, not assuming.

## 9. Application-question angles

- **Why this company**: lean on the core narrative, not a feature list. He has already lived, for
  seven-plus years, the shift Cognition is trying to productize: from writing every line himself
  to owning outcomes while an agent (Claude Code, in his case) does execution. He is applying
  because he has already been the kind of builder Cognition wants Applied AI Engineers to create
  in enterprise teams, not because he wants to learn what an agentic workflow is.
- **Why you fit**: anchor on the job's actual motion (embed, pair-program live, turn engagements
  into playbooks), which maps directly onto his founder career: on-site client deployments at
  Eugenia.ai, hands-on delivery and team leadership at Online Basics, and now productizing an AI
  consultancy at Pragma AI. Add one concrete technical proof point (Kairos's Claude Agent SDK plus
  MCP integration, or Plutus's MCP control plane) rather than a generic "I love AI" claim, since
  Devin Desktop's own architecture just moved toward the same agent-agnostic, MCP-native world he
  has been building in.
- **Anything else**: be candid, briefly, about the location question (Mexico City based, TN-visa
  eligible, glad to discuss what a forward-deployed or hybrid arrangement could look like) so it is
  not a surprise later, and note genuine interest in the specific bet Cognition is making right now
  (an agent-agnostic IDE plus a proprietary autonomous engineer) rather than AI enthusiasm in
  general.

## Sources

researched: 2026-07-13

- [Cognition homepage](https://cognition.com/) : mission language, product positioning, named
  enterprise customers.
- [Cognition, Introducing Devin](https://cognition.com/blog/introducing-devin) : Devin launch,
  product description, SWE-bench framing.
- [Cognition, Windsurf acquisition post](https://cognition.com/blog/windsurf) : acquisition
  rationale, terms for Windsurf staff, combined product vision.
- [Cognition Careers page](https://cognition.com/careers) : founding team background, hiring
  categories, benefits, employee quote.
- [Cognition, What We Learned Building Cloud Agents](https://cognition.com/blog/what-we-learned-building-cloud-agents) : infrastructure (microVMs, state snapshots), orchestration and governance lessons.
- [Cognition, Multi-Agents: What's Actually Working](https://cognition.com/blog/multi-agents-working) : published multi-agent engineering lessons.
- [Devin Docs, Desktop FAQ](https://docs.devin.ai/desktop/devin-desktop-faq) : Devin Desktop
  rebrand, Agent Client Protocol support, Devin Local / Cascade sunset.
- [Wikipedia, Cognition AI](https://en.wikipedia.org/wiki/Cognition_AI) : founding date and
  founders, funding history, product timeline.
- [TechCrunch, Jul 14 2025](https://techcrunch.com/2025/07/14/cognition-maker-of-the-ai-coding-agent-devin-acquires-windsurf/) : Windsurf acquisition context (Google acquihire, OpenAI offer).
- [TechCrunch, Aug 5 2025](https://techcrunch.com/2025/08/05/three-weeks-after-acquiring-windsurf-cognition-offers-staff-the-exit-door/) : post-acquisition layoffs/buyouts, culture quotes.
- [CNBC, Sep 8 2025](https://www.cnbc.com/2025/09/08/cognition-valued-at-10point2-billion-two-months-after-windsurf-.html) : $10.2B valuation, $400M round.
- [TechCrunch, May 27 2026](https://techcrunch.com/2026/05/27/ai-coding-startup-cognition-raises-1b-at-25b-pre-money-valuation/) : $1B raise, $25B/$26B valuation, ARR, investors.
- [Bloomberg, May 27 2026](https://www.bloomberg.com/news/articles/2026-05-27/ai-coding-startup-cognition-raises-1-billion-at-26-billion-value) : corroborates valuation and raise.
- [TechCrunch, May 29 2026](https://techcrunch.com/2026/05/29/cognitions-scott-wu-says-ai-coding-agents-shouldnt-replace-humans/) : Scott Wu on Devin's capability level, internal code-commit share, human-augmentation framing.
- [Scott Wu on X, Aug 2025](https://x.com/ScottWu46/status/1952776198947520659) : "extreme
  performance culture" statement direct from the CEO.
- [OfficeChai](https://officechai.com/ai/cognition-ceo-scott-wu-explains-why-they-let-people-use-as-much-ai-as-they-like-in-job-interviews/) : hiring/interview philosophy on AI use and product judgment.
- [ChatForest, Windsurf/Devin Desktop rebrand guide](https://chatforest.com/builders-log/windsurf-devin-desktop-rebrand-devin-local-acp-builder-guide/) : third-party corroboration of the June 2026 rebrand details.
- [Job posting, Applied AI Engineer](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d) : role responsibilities and requirements (direct fetch did not render full text; content corroborated via indexed search results).
- [Glassdoor listing, Applied AI Engineer](https://www.glassdoor.com/job-listing/applied-ai-engineer-cognition-ai-JV_KO0,19_KE20,32.htm?jl=1009917018619) : corroborating mirror of the same posting (direct fetch returned 403; used as a cross-check via search index only).
- [VentureBeat, Cognition launch coverage](https://venturebeat.com/ai/cognition-emerges-from-stealth-to-launch-ai-software-engineer-devin) : SWE-bench figures at launch.

Note: the SWE-1.5/SWE-1.7 model benchmark figures found in third-party aggregator coverage
(ChatForest) are flagged above as unverified since they were not confirmed against a Cognition
primary source.
