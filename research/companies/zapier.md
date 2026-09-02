# Zapier: Company Dossier

Draft for Santiago's review. Built for the "Engineer, Applied AI" role (AI Platform team, job id 4738,
remote NAMER). Refresh before reuse if it gets stale.

## 1. Snapshot

Zapier is a 15-year-old, profitable, largely bootstrapped no-code automation platform (Zaps
connecting thousands of apps) that has spent 2024 to 2026 rebuilding itself into an "AI
orchestration" layer: AI Agents, Canvas, Copilot, and an official MCP server that exposes its app
integrations as tool-calling surface for any LLM. Fully remote and distributed since founding, no
offices anywhere, roughly 730 to 800 employees across 40+ countries, HQ nominally San Francisco.
Valued at $5B as of a January 2021 secondary sale (Sequoia Capital, Steadfast Financial); revenue
was about $310M in 2024 and reportedly trending toward $400M+ in 2025 (third-party trackers; not a
company-confirmed figure). ([Wikipedia](https://en.wikipedia.org/wiki/Zapier), [Sacra](https://sacra.com/c/zapier/))

## 2. Core narrative

Zapier is the rare AI-era company that isn't a startup racing to prove AI works: it is a profitable,
almost-15-year-old, VC-light business that forced itself through an internal AI turnaround first,
then rebuilt its product around it. When GPT-4 shipped in March 2023, CEO Wade Foster called an
internal "code red" (a phrase never used before at Zapier), froze normal work for a week-long
company-wide hackathon, and took weekly AI usage from under 10% of staff to over 50% in that single
week; the company now runs a hackathon like this every 4 to 6 months, and since May 2025 every new
hire has had to demonstrate AI fluency as a hiring bar. ([zapier.com/blog/transform-ai-company-culture](https://zapier.com/blog/transform-ai-company-culture/),
[Madrona](https://www.madrona.com/zapier-has-more-ai-agents-than-employees-heres-how-that-happened/))
Internally, Zapier now says it has more AI agents than human employees, coordinating "pods" of
lightweight agents over Slack for standups, onboarding, and admin work. ([Madrona](https://www.madrona.com/zapier-has-more-ai-agents-than-employees-heres-how-that-happened/),
[GetDX](https://getdx.com/blog/using-ai-to-accelerate-hiring-and-productivity-at-zapier/))
Externally, the product followed the same arc: Zapier Central (chat AI workspace, March 2024) became
Zapier Agents (January 2025), then Copilot and an official Model Context Protocol server (launched
around September 2025) turned the company's 7,000+ to 9,000+ app integrations into a tool-calling
layer any AI agent or model can call. ([community.zapier.com](https://community.zapier.com/p/zapier-central),
[Zapier MCP](https://zapier.com/mcp)) The Applied AI Engineer role on the AI Platform team sits
exactly at the seam between these two stories: it builds the internal "paved road" (LLM proxy,
observability, ML Ops) that both product teams and Zapier's own AI-first internal culture run on.

## 3. Mission & product

- Stated mission/voice: "We're humans who think computers should do more work" / "Make automation
  work for everyone." ([zapier.com/about](https://zapier.com/about))
- Core product: Zaps, no-code trigger-and-action workflow automation across thousands of apps, plus
  Tables (data), Interfaces (forms/mini-apps), and Chatbots. ([zapier.com](https://zapier.com))
- AI layer (2024 to 2026 build-out): Canvas (visual system design that generates Zaps from a diagram,
  now also auto-documents existing workflows), AI Agents ("AI teammates" that reason and act
  autonomously across apps), Copilot (natural-language Zap builder), and Zapier MCP (exposes app
  actions as MCP tools for any AI assistant). Homepage tagline as of this research: "Your tools. Your
  rules. Any AI," positioning Zapier as model-agnostic. ([zapier.com](https://zapier.com), [Zapier MCP](https://zapier.com/mcp))
- Integration count is stated inconsistently across sources: the current homepage says "9,000+"
  apps; third-party review sites cite 6,000 to 8,000. Treat the primary-source figure (9,000+) as
  current and the lower numbers as stale snapshots. ([zapier.com](https://zapier.com))
- Business model: subscription tiers (Free, Starter, Professional, Team, Enterprise) metered on
  tasks; in 2024 Zapier simplified pricing toward task-based, pay-as-you-go billing because, per
  Foster, seat-based pricing "becomes structurally broken when agents replace human users."
  ([Madrona](https://www.madrona.com/zapier-has-more-ai-agents-than-employees-heres-how-that-happened/))
- Customers: SMB through enterprise; recent enterprise pushes include Workday and Workfront
  integrations, SOC 2 readiness (final steps as of December 2025), and an Admin Center with
  approval, connection, and member-management controls, alongside AWS Marketplace availability.
  ([Dec 2025 updates](https://zapier.com/blog/december-2025-product-updates/), [Feb 2026 updates](https://zapier.com/blog/february-2026-product-updates/))

## 4. Culture & voice

Five published values (first set in 2018, refreshed 2022):
1. **Default to Action**: "Most decisions are changeable. It's better to deliver something real
   today over something maybe better later."
2. **Default to Transparency**: "Sharing context, goals, objectives, and in-progress work in public
   helps us all achieve a common goal."
3. **Grow Through Feedback**: "We all have personal goals and ambitions. Let's work together to help
   us all achieve our goals."
4. **Empathy, No Ego**: "All of our teammates are smart and talented. When we work together we will
   be successful."
5. **Don't Be a Robot, Build the Robot**: "Invest in tools and processes that lead to outsized
   impact so Zapier can be more productive than a similar sized company."
([Zapier's own culture and values page, mirrored copy](https://powertofly.com/up/culture-and-values-at-zapier))

Remote/async operating detail: fully distributed since founding (never had an office), async-first
by default, Slack as the "virtual HQ" with most channels public, plus written weekly "Friday
updates" so work stays visible without meetings. ([zapier.com/blog/how-to-work-asynchronously](https://zapier.com/blog/how-to-work-asynchronously/))
Since May 2025, AI fluency is an explicit hiring bar for every new hire, assessed on a four-level
scale (unacceptable, acceptable, adoptive, transformative), reviewed every six months as models
change. The head of HR was retitled Chief People and AI Transformation Officer. ([zapier.com/blog/transform-ai-company-culture](https://zapier.com/blog/transform-ai-company-culture/))
The JD itself explicitly invites candidates to use AI tools "responsibly and transparently" during
the hiring process, consistent with this stance. ([Job posting](https://jobs.ashbyhq.com/zapier/38434b88-086c-424b-8d18-8d006e0b71b8/application))

## 5. Recent news (last ~12 months, dated)

- **May 2025**: Zapier Agents reaches general availability; AI-fluency hiring bar begins for new
  hires. ([Madrona](https://www.madrona.com/zapier-has-more-ai-agents-than-employees-heres-how-that-happened/))
- **~Sept 2025**: Official Zapier MCP server launches, exposing 30,000+ actions across Zapier's app
  catalog to any MCP-compatible AI tool (OpenAI's Responses API integrated with it around the same
  window). ([zapier.com/blog/zapier-mcp-guide](https://zapier.com/blog/zapier-mcp-guide/), [LinkedIn, Wade Foster](https://www.linkedin.com/posts/wadefoster_big-mcp-news-from-openai-today-with-zapier-activity-7330994565933322241-EJvZ))
- **Sept 2025**: Zapier Copilot (natural-language Zap builder) rolls out more broadly.
  ([nocodefinder.com summary](https://www.nocodefinder.com/blog-posts/zapier-agents-guide))
- **Oct 2025**: Acquires Utopian Labs (an AI sales-email chatbot company, formerly Luna.ai).
  ([Wikipedia](https://en.wikipedia.org/wiki/Zapier))
- **Dec 2025**: Product updates include Agents draft/published versions (beta), SOC 2 readiness
  final steps, a redesigned Admin Center, Human-in-the-Loop guest reviewer approvals, and Canvas
  image support. ([zapier.com/blog/december-2025-product-updates](https://zapier.com/blog/december-2025-product-updates/))
- **Feb 2026**: AI Guardrails ships (detects 30+ PII types, blocks Zaps on sensitive data,
  prompt-injection/jailbreak detection, toxicity screening); Agents move into the unified Templates
  hub; Canvas gains auto-generated workflow documentation; org-wide Chatbot admin controls added.
  ([zapier.com/blog/february-2026-product-updates](https://zapier.com/blog/february-2026-product-updates/))
- **2025 (ongoing)**: Zapier positions itself as "AI orchestration," coordinating LLMs, agents, and
  app actions into multi-step systems, and lists on AWS Marketplace. ([zapier.com/blog/zapier-ai-orchestration-platform](https://zapier.com/blog/zapier-ai-orchestration-platform/))

Note: 2023 had a 10% workforce layoff; no comparable 2025 to 2026 layoff was found in this research
(most recent employee chatter describes slowed hiring, not new cuts). Flag as unconfirmed if it
comes up in an interview. ([IBTimes, 2023](https://www.ibtimes.com/tech-layoffs-plex-sacks-20-zapier-slashes-10-staff-after-new-relic-cuts-3702589))

## 6. Engineering & AI direction

- **Role-specific stack** (from the JD): the AI Platform team builds mostly in **TypeScript and
  Python**; the team owns the **LLM proxy server**, **platform APIs**, **observability/monitoring
  tooling**, and **ML Ops platform capabilities** that other product and engineering teams build on
  top of. Explicitly framed as "highly leveraged": not a single feature, but the shared foundation
  many teams depend on. ([Job posting](https://jobs.ashbyhq.com/zapier/38434b88-086c-424b-8d18-8d006e0b71b8/application))
- **Broader engineering stack** (from the eng blog): Kubernetes with KEDA for event-driven worker
  autoscaling, Kafka (recently reduced connection overhead 10x with a sidecar pattern), the outbox
  pattern for reliable event-driven services, and a recent migration off Ingress Nginx. Historically
  Python/Django on the backend with a React/Redux frontend, running on AWS. ([zapier.com/engineering](https://zapier.com/engineering/),
  [zapier.com/blog/zapier-tech-stack](https://zapier.com/blog/zapier-tech-stack/))
- A recent eng-blog post describes "Hobi," an internal context engine built to protect customer
  data, suggesting active investment in data governance tooling alongside the AI Guardrails product
  feature. ([zapier.com/engineering](https://zapier.com/engineering/))
- **Internal AI-agent operations** (proof this team's mandate matters company-wide): "hundreds of
  internal AI agents" now handle async standups (cut from 5 sessions/week to 2), onboarding (cut to
  about 2 weeks versus a 30 to 90 day industry norm), and Slack-coordinated "pods" of task-specific
  agents; AI is estimated to remove 10 to 15% of admin/coordination work per engineer per week.
  ([GetDX, Dec 2025](https://getdx.com/blog/using-ai-to-accelerate-hiring-and-productivity-at-zapier/))
- Product framing ("Your tools. Your rules. Any AI") signals a deliberately model-agnostic
  architecture, consistent with the JD's emphasis on an LLM proxy that standardizes access across
  providers rather than betting on one model vendor. ([zapier.com](https://zapier.com))

## 7. Why-fit angles for Santiago

**Best hook to lead with**: Santiago has already built, solo, the exact shape of thing this team
builds for a whole company. In Kairos he exposed one typed tool-definition layer (18 tools) through
two different consumers, an in-app Claude Agent SDK agent and a standalone MCP server, so both a
product surface and Claude Code itself can operate on the same live data through one governed
interface. In Plutus he built an LLM research agent behind an MCP control plane on top of a real
production data/backtesting stack. That is a shared tool/model-access layer serving multiple
consumers: functionally a miniature version of what Zapier's AI Platform team does with its LLM
proxy and MCP server, just at founder scale instead of company scale.

Supporting angles:
- **Multi-API orchestration at production scale**: at Online Basics he built a cloud microservices
  architecture (Python on Heroku, AWS databases) orchestrating 10+ third-party APIs (Amazon, Mercado
  Libre, Inflow) processing 100K+ daily data points on hourly sync. Zapier's core business is
  orchestrating thousands of third-party APIs reliably; he has done this, just at smaller scale, and
  can speak concretely to the operational pain (auth, rate limits, schema drift, monitoring) that
  makes an "LLM proxy" and shared platform tooling valuable.
- **Production LLM workflow ownership, not just prototyping**: the Online Basics content-generation
  pipeline (Anthropic and OpenAI APIs, custom prompt engineering, multi-stage validation) ran monthly
  in production and cut content-creation time 70%, i.e. he owned an LLM system through its full
  lifecycle (build, validate, operate, iterate), which maps to the JD's ask for "full lifecycle of
  building, testing, deploying, and scaling ML/LLM architectures."
- **Remote-async fluency**: seven-plus years running lean, distributed teams (7-person team at
  Online Basics, git-based workflows, code review, agile delivery) is a real, defensible match for
  Zapier's async-first, no-office culture, not just a stated preference.

**Honest gaps and watch-outs**:
- Scale mismatch: his AI/LLM production work has been at founder/small-team scale (his own products,
  or a 7-person team), not operating a shared platform consumed by many other engineering teams
  inside a ~800-person company. He should be ready to explicitly reframe his tool-layer and
  API-orchestration work as "platform for other consumers," since that is the leverage this specific
  role is testing for, not just "I shipped an AI feature."
- LLM Ops / observability depth: the JD asks for 1+ year specifically in LLM Ops, ML Ops, or
  adjacent platform/infra work (evaluation workflows, monitoring, governance at scale). Santiago's
  strongest evidence here is Kairos/Plutus's typed tool layer and Pragma's RAG pipeline; he has not
  named a formal eval framework, model-monitoring stack, or cost/latency governance system in his
  resume, so he should have a concrete, honest story ready (what he does today to catch prompt
  regressions or bad outputs, even if informal) rather than overclaiming an "Ops" title he hasn't
  held.
- Founder-to-platform-engineer framing: he has always been the founder/owner; this role is
  explicitly "highly leveraged" and in service of other engineers rather than an end product he owns
  end to end. Worth having a genuine, non-generic answer for why that tradeoff (less ownership,
  more leverage) is something he wants now, not just career-stage-appropriate boilerplate.
- Work authorization/location: the JD (NAMER, remote) lists a resource for "countries where we
  currently cannot have Zapiens permanently working"; that specific list was not found in this
  research. Santiago's profile already scored this role as fitting Mexico, but he should confirm
  Mexico's eligibility directly in the process rather than assume it. ([Job posting](https://jobs.ashbyhq.com/zapier/38434b88-086c-424b-8d18-8d006e0b71b8/application))

## 8. Application-question angles

- **Why this company**: do not recite the product feature list. Lead with the internal
  transformation story (code red, hackathon culture, AI-fluency hiring bar, more agents than
  employees) paired with the product's shift into an AI orchestration/MCP layer: Zapier is a
  profitable, 15-year, remote-native company that chose to rebuild itself around AI rather than
  bolt AI on, and that is a rare, credible version of "AI-first" worth building the shared
  infrastructure for.
- **Why you fit**: lead with the Kairos/Plutus MCP tool-layer work as direct, structural proof he
  has already built a shared tool/model-access layer for multiple consumers, then back it with the
  Online Basics multi-API orchestration and production LLM pipeline as evidence he can operate,
  not just prototype, systems like this. Avoid listing all of his experience; these two are the
  resonant pair.
- **Anything else**: name the founder-to-platform-engineer tradeoff honestly (trading full
  end-to-end ownership for leverage across other engineers) and connect it to years of running a
  distributed, async team solo, so the pitch is "I already work the way Zapier works, and I want to
  build the tooling other builders lean on" rather than a generic enthusiasm statement.

## 9. Sources

- [zapier.com/about](https://zapier.com/about): mission statement.
- [zapier.com](https://zapier.com): homepage messaging, AI Agents/Canvas copy, "9,000+" app count,
  "Your tools. Your rules. Any AI" tagline.
- [zapier.com/jobs](https://zapier.com/jobs): careers landing page.
- [Zapier's culture and values page, mirrored on PowerToFly](https://powertofly.com/up/culture-and-values-at-zapier):
  full text of the five core values and descriptions.
- [zapier.com/blog/how-to-work-asynchronously](https://zapier.com/blog/how-to-work-asynchronously/):
  async-first operating model, Slack/Friday-updates practice.
- [zapier.com/blog/transform-ai-company-culture](https://zapier.com/blog/transform-ai-company-culture/):
  the GPT-4 "code red" hackathon story, adoption stats, May 2025 AI-fluency hiring bar.
- [Madrona: Zapier has more AI agents than employees](https://www.madrona.com/zapier-has-more-ai-agents-than-employees-heres-how-that-happened/):
  headcount (~800), revenue scale, code red story, pricing-model shift, internal agent culture.
- [GetDX: Using AI to accelerate hiring and productivity at Zapier](https://getdx.com/blog/using-ai-to-accelerate-hiring-and-productivity-at-zapier/):
  internal agent usage metrics (standups, onboarding time, admin-work reduction), Dec 2025.
- [zapier.com/blog/december-2025-product-updates](https://zapier.com/blog/december-2025-product-updates/):
  Agents draft/published versions, SOC 2 readiness, Admin Center, Human-in-the-Loop, Canvas images.
- [zapier.com/blog/february-2026-product-updates](https://zapier.com/blog/february-2026-product-updates/):
  AI Guardrails, PII detection, Agents templates hub, Canvas auto-documentation, chatbot admin controls.
- [zapier.com/mcp](https://zapier.com/mcp) and [zapier.com/blog/zapier-mcp-guide](https://zapier.com/blog/zapier-mcp-guide/):
  Zapier MCP server, 30,000+ actions, app-catalog exposure.
- [LinkedIn, Wade Foster post on OpenAI/MCP](https://www.linkedin.com/posts/wadefoster_big-mcp-news-from-openai-today-with-zapier-activity-7330994565933322241-EJvZ):
  MCP and OpenAI Responses API integration timing.
- [community.zapier.com/p/zapier-central](https://community.zapier.com/p/zapier-central): Central to
  Agents rebrand, January 2025.
- [zapier.com/blog/zapier-ai-orchestration-platform](https://zapier.com/blog/zapier-ai-orchestration-platform/):
  "AI orchestration" positioning.
- [zapier.com/engineering](https://zapier.com/engineering/): current eng blog post list (KEDA, Kafka
  sidecar pattern, outbox pattern, Ingress Nginx migration, Hobi context engine).
- [zapier.com/blog/zapier-tech-stack](https://zapier.com/blog/zapier-tech-stack/): historical
  Python/Django/React stack background.
- [Wikipedia: Zapier](https://en.wikipedia.org/wiki/Zapier): founding (2011, Wade Foster, Bryan
  Helmig, Mike Knoop), YC 2012, funding history, January 2021 $5B secondary (Sequoia, Steadfast
  Financial), headcount over time (200 in 2018, ~700 in 2022, ~730 in 2025), HQ, acquisitions
  (Makerpad 2021, Vowel 2024, NoCodeOps 2024, Utopian Labs Oct 2025), profitability since 2014.
- [Sacra: Zapier revenue, valuation & funding](https://sacra.com/c/zapier/): $310M 2023 to 2024 ARR,
  35% YoY growth, capital efficiency ($1.4M raised vs $100M+ ARR).
- [IBTimes, 2023 layoffs](https://www.ibtimes.com/tech-layoffs-plex-sacks-20-zapier-slashes-10-staff-after-new-relic-cuts-3702589):
  2023 10% workforce reduction (background context, outside the 12-month window).
- [Job posting (Ashby)](https://jobs.ashbyhq.com/zapier/38434b88-086c-424b-8d18-8d006e0b71b8/application):
  role scope, TypeScript/Python, LLM proxy/observability/ML Ops ownership, requirements, restricted
  countries note. Also pulled via `python -m src.query job 4738`.

researched: 2026-07-14
