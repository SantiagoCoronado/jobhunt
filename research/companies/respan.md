# Respan (formerly Keywords AI)

Draft dossier for Santiago's review. Job id 13203, "Senior Software Engineer, Frontend" (remote,
per findwork listing), sourced from https://findwork.dev/MrJmBYM/senior-software-engineer-frontend-at-respan.

## 1. Snapshot
Respan is a YC-backed (W24) B2B SaaS building a "self-driving" observability, evals, and AI
gateway control plane for teams running AI agents in production; legal entity is Keywords AI,
Inc., rebranded to Respan in February 2026. About 15 people, HQ/hacker house in Alameda, CA.
Raised a $5M round (announced March 2026) from Gradient, Y Combinator, Hat-Trick Capital,
XIAOXIAO Fund, Antigravity Capital, and Alpen Capital.
(https://www.ycombinator.com/companies/respan, https://www.globenewswire.com/news-release/2026/03/18/3258291/0/en/Respan-Announces-5M-in-Funding-from-Gradient-Y-Combinator-and-others-Launches-First-Proactive-AI-Observability-Platform.html)

## 2. Core narrative
Respan started as "Keywords AI," a broader LLM development platform, and rebranded in February
2026 because that name "sounded like a prompt engineering tool or an SEO plugin" rather than what
the product had become. The new name is a nod to the "span," the atomic unit of a distributed
trace, and signals a narrower, sharper bet: observability alone (what happened) is not enough for
managing AI agents; you need a closed loop from observability to evals to automated decisions to
shipped fixes. This is the story to lean into: a technically confident, recently-repositioned
company betting that the market's real problem is the eval-to-action gap, not tracing in
isolation. (https://www.respan.ai/blog/introducing-respan)

## 3. Mission & product
The platform provides deep production tracing (messages, tool calls, routing, memory, environment
state, outcomes), automated plus human-in-the-loop evals, and an adaptive AI gateway, closing the
loop between detection, decision, and action so agents improve continuously in production. It is
used by 60+ YC companies and, per the company, 100+ AI startups and enterprise teams overall,
processing 1B+ logs and 2T+ tokens per month across 6.5M+ end users, with reported 8x year-over-
year revenue growth in 2025. Business model is B2B SaaS.
(job description via `.venv/bin/python -m src.query job 13203`;
https://www.ycombinator.com/companies/respan; https://www.respan.ai/about;
https://siliconangle.com/2026/03/18/respan-raises-5m-bring-proactive-observability-ai-agents/)

## 4. Culture & voice
Founders Andy Li (CEO) and Raymond Huang (CTO), engineering-school friends from the University of
Illinois, later joined by Hendrix Liu (Head of Sales) as third co-founder. The careers page is
explicit and unusual: "we work 7 days a week and most of the team live together in hacker houses
in Alameda," and they say they "hire for exceptional people first" and are only looking for people
"genuinely excited about the grind." (https://www.respan.ai/careers,
https://www.respan.ai/about, https://pulse2.com/respan-profile-andy-li-interview/)

Blog voice is direct and systems-minded: posts talk in terms of "atomic units," "control planes,"
and "closed loops," acknowledge competitors (Langfuse, Braintrust, Portkey) as genuinely useful
before arguing they solve a narrower problem, and ship a public launch-week cadence (Agent, CLI,
MCP, new integrations, evals 2.0) rather than quiet releases.
(https://www.respan.ai/blog/introducing-respan, https://www.respan.ai/blog)

## 5. Recent news (last ~12 months)
- Feb 20, 2026: rebrand from Keywords AI to Respan, repositioning around agent observability and
  evals rather than general LLM tooling. (https://www.respan.ai/blog/introducing-respan)
- Mar 18, 2026: $5M funding round from Gradient, YC, Hat-Trick Capital, XIAOXIAO Fund, Antigravity
  Capital, Alpen Capital; launched "first proactive AI observability platform."
  (https://www.globenewswire.com/news-release/2026/03/18/3258291/0/en/Respan-Announces-5M-in-Funding-from-Gradient-Y-Combinator-and-others-Launches-First-Proactive-AI-Observability-Platform.html,
  https://siliconangle.com/2026/03/18/respan-raises-5m-bring-proactive-observability-ai-agents/)
- Apr 21-24, 2026: public launch week shipping Respan Agent, CLI and MCP support, "Evals 2.0," 50+
  new integrations, and usage limits/guardrails features. (https://www.respan.ai/blog)
- Apr 30, 2026: blog post reacting to Portkey's acquisition by Palo Alto Networks, positioning
  Respan as an independent alternative for teams migrating off Portkey. (https://www.respan.ai/blog)
- May 5, 19, 21, 2026: engineering/product posts on agent architecture ("Single Agent vs
  Multi-Agent: Why We Rebuilt Our AI Agent"), prompt versioning, and production eval criteria.
  (https://www.respan.ai/blog)

## 6. Engineering & AI direction
The open-source SDK repo (`respanai/respan`, Apache-2.0, 42 stars) is Python-heavy (58.7%) with a
substantial TypeScript SDK (34.6%) plus JavaScript, focused on OpenTelemetry-format instrumentation,
integrations with OpenAI SDK, LangGraph, and the Vercel AI SDK, and 50+ tool integrations via a
plugin system. That repo covers backend/SDK instrumentation, not the customer-facing app.
(https://github.com/respanai/respan) The job description itself is the best source on the actual
product frontend: React and Next.js, a component library and design system serving trace
visualizers, eval dashboards, and prompt editors, with an explicit ask for performance profiling
and accessible, pixel-perfect UI (`.venv/bin/python -m src.query job 13203`). Product direction
per the blog is toward tighter observability-to-evals-to-action loops, an agentic CLI/MCP surface,
and expanding gateway/integration breadth (50+ integrations, launch-week cadence).
(https://www.respan.ai/blog)

## 7. Why-fit angles for Santiago
Strong hooks:
- Design-system and dashboard ownership: Santiago shipped an in-house design system (Radix UI
  primitives, CVA variants, CSS-variable tokens) and data-dense dashboards (React Flow node-graph
  canvas, charting with lightweight-charts and ECharts) on the Hydrel and Plutus projects, which is
  close to this role's "trace visualizers, eval dashboards, prompt editors, and design system"
  scope (resume/master_resume.yaml, Hydrel and Plutus project entries).
- Real-time and data-heavy UI experience: WebSocket feeds, SSE streaming clients, and multi-pane
  charting in Plutus map directly to "complex data-heavy UIs such as dashboards, editors, or
  visualizers," a "strong plus" in the posting.
- Founder-level ownership fits a 15-person team that wants someone who can "own frontend
  architecture" with "real architectural ownership," matching his track record leading
  0-to-1 product builds (Eugenia.ai, Online Basics, Pragma AI).

The single best hook to lead with: concrete, named design-system and data-visualization work
(Hydrel's design system, Plutus's charting stack) rather than generic React years, since this role
is explicitly about owning a design system plus dashboards/visualizers, not just building features.

Honest concerns / watch-outs:
- Location mismatch risk: Respan's own YC job listings show this exact role (and most engineering
  roles) as "Alameda, CA, US / Remote (IN)", i.e. remote is scoped to India, not general remote or
  LATAM. The findwork aggregator listing that produced this job record only says "Remote" with no
  country scope, which may be a stripped-down or stale copy of the original posting.
  (https://www.ycombinator.com/companies/respan/jobs) This should be verified directly with Respan
  or on the primary YC listing before assuming Mexico-based remote eligibility.
- Culture intensity: the careers page states the team lives together in hacker houses in Alameda
  and works 7 days a week; this reads as an in-person, high-intensity culture that may sit awkwardly
  next to a "Remote (IN)" listing, and is worth asking about directly. (https://www.respan.ai/careers)
- No LATAM-specific signal found anywhere (no LATAM customers, hires, or statements), so any
  "why Mexico" framing would be speculative; better to lean on product/skill fit than on any
  claimed regional fit.

## 8. Application-question angles
- Why this company: lead with the rebrand story, i.e. Respan bet that the market's real gap is
  between "what happened" (observability) and "what to fix next" (closed-loop evals and action),
  and connect that to wanting to build the specific surface where that loop becomes visible to
  users: trace visualizers, eval dashboards, and prompt editors.
- Why you fit: point to the Hydrel design system and Plutus's data-heavy, real-time visualizers as
  direct precedent for "architect the design system, ship pixel-perfect data-dense UI," not a
  generic React-years pitch.
- Anything else: it is fair to ask, plainly, whether the role is open to Mexico City given the
  YC listing shows "Remote (IN)" for this posting; better to surface this early than assume.

## 9. Sources
- researched: 2026-07-21
- https://findwork.dev/MrJmBYM/senior-software-engineer-frontend-at-respan (original job posting, aggregated)
- job id 13203 description via `.venv/bin/python -m src.query job 13203` (role responsibilities, stack, requirements)
- https://www.ycombinator.com/companies/respan (founding year, team size, batch, product one-liner)
- https://www.ycombinator.com/companies/respan/jobs (open roles and location fields, confirms "Remote (IN)" scoping for this role and most engineering roles)
- https://www.respan.ai/about (founders, mission statement, team/culture description)
- https://www.respan.ai/careers (hacker house / 7-day culture statement, hiring philosophy)
- https://www.respan.ai/blog/introducing-respan (rebrand story, date, narrative and voice)
- https://www.respan.ai/blog (blog post titles/dates: launch week, Portkey migration post, eval/prompt posts)
- https://www.globenewswire.com/news-release/2026/03/18/3258291/0/en/Respan-Announces-5M-in-Funding-from-Gradient-Y-Combinator-and-others-Launches-First-Proactive-AI-Observability-Platform.html (funding amount, investors, date)
- https://siliconangle.com/2026/03/18/respan-raises-5m-bring-proactive-observability-ai-agents/ (funding coverage, usage stats corroboration)
- https://pulse2.com/respan-profile-andy-li-interview/ (founder interview, culture corroboration)
- https://github.com/respanai/respan (open-source SDK stack, license, stars)
