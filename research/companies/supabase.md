# Supabase

Draft dossier for Santiago's review. Researched 2026-08-11.

## 1. Snapshot

Open-source Postgres development platform (database, auth, storage, edge functions, realtime,
vector search), positioned as the open-source Firebase alternative. Born-remote, no physical
offices, roughly 350 to 400 team members across 60+ countries. Just closed a $500M Series F in
June 2026 at a $10.5B post-money valuation (total raised over $1B), seven months after a $100M
Series E at $5B. Legal entities in Singapore and the US; founded 2020 by Paul Copplestone and
Ant Wilson.

## 2. Core narrative

Supabase's growth curve just bent hard toward AI-authored code: the company says database
launches grew over 600% year over year and more than 60% of new databases are now created by an
AI tool (Claude Code, Codex, Cursor, Lovable, Bolt, Replit), and CEO Paul Copplestone credits
that shift directly for the valuation doubling in eight months. That reality is now reshaping how
the company builds its own product: the Frontend Engineer req is explicitly about building the CI
and quality pipeline that lets humans and AI agents ship safely at that speed, not about hand
writing more UI. Layered on top is a deliberately literal remote model: no offices, no
geo-adjusted pay, and a stated preference for stocking the team with former founders.

## 3. Mission & product

Supabase bundles Postgres database, auth, storage, edge functions (Deno/TypeScript), realtime
(WebSocket sync), and pgvector-based vector search into one integrated, open-source backend
platform, pitched as "build in a weekend, scale to millions." [supabase.com] Customers range from
early-stage startups (over 50% of a recent YC batch, per the Series E announcement) to enterprise
accounts like PwC, McDonald's, and GitHub Next. [supabase.com/blog/supabase-series-e] The Series F
post frames the next phase explicitly around AI-native and agentic applications, citing nearly 10
million developers on the platform (more than doubling in eight months) and heavy integration
with AI coding tools. [supabase.com/blog/supabase-series-f]

## 4. Culture & voice

- **Fully remote, no offices, deliberately:** the company's own 2023 post on staying remote
  argues against geo-adjusted pay ("we don't do geo-adjusted pay"), against forcing relocation
  near an office, and for hiring outside major tech hubs; it says compensation targets the
  60th-80th percentile in major US cities and the 95th-99th percentile in most other markets.
  [supabase.com/blog/why-supabase-remote, dated 2023-08-05, still linked from careers messaging
  in 2026]
- **Stated values (careers page, 2026):** Egoless, Kaizen mindset, Truth seeking (intellectual
  honesty), Batteries included (high ownership), Undeniable (earn trust by delivering).
  [supabase.com/careers]
- **Deliberately hires former founders:** as of the Series E announcement (Oct 2025) the company
  said it employed over 30 former founders across 37 countries. [supabase.com/blog/supabase-series-e]
- **Build-in-public, ship-fast identity:** "launch week" release cadence is a recurring theme in
  third-party culture writeups; one secondary source (a small, 5-review Glassdoor-based summary)
  reports high overall satisfaction but flags work-life balance as the weakest dimension amid the
  launch-week pace. This is a thin, unverified sample and should be treated as a soft signal, not
  a fact. [jobsbyculture.com/blog/working-at-supabase-2026]
- Coordination is async-first (Notion, Slack, Discord, GitHub per third-party summaries); annual
  company-wide off-site is a stated benefit on both job postings researched here.

## 5. Recent news (last ~12 months)

- **2025-10-03:** Series E, $100M at a $5B valuation, led by Accel and Peak XV with Figma
  participating; over 30 former founders across 37 countries on the team at the time.
  [supabase.com/blog/supabase-series-e]
- **2025-10-03:** Announced the Remote MCP Server (HTTP-based, OAuth2), letting AI agents
  (ChatGPT, Claude, Builder.io) connect to a Supabase project without a local Node install; added
  doc search and security/performance advisor tools. [supabase.com/blog/remote-mcp-server]
- **2026-06-04:** Series F, $500M at a $10.5B valuation (total raised over $1B), led by GIC with
  Stripe's second investment plus new investors Georgian and Salesforce Ventures; announced
  Multigres v0.1 alpha (a scaling layer for Postgres) alongside the round.
  [supabase.com/blog/supabase-series-f, cnbc.com 2026-06-04, techcrunch.com 2026-06-05]
- **2026 (ongoing):** CEO Paul Copplestone publicly credited Claude Code and Codex adoption for
  accelerated growth, and said on the Equity podcast that he has turned down enterprise deals that
  would have required compromising the product's developer-first design.
  [techcrunch.com/2026/06/05/supabase-doubles-valuation-to-10b-in-8-months]

## 6. Engineering & AI direction

- **Polyglot stack by problem area:** TypeScript for dashboard/API-layer work, Elixir for
  realtime (Supavisor, the Postgres connection pooler built for millions of connections), Go for
  storage, Rust for performance-critical and replication work (Supabase ETL).
  [supabase.com/blog/supavisor-1-million; corroborated by third-party technical writeups]
- **AI-agent-first product direction:** official MCP server (local, since April 2025, per
  third-party sources) and remote MCP server (Oct 2025) exposing SQL execution, schema/migration
  management, Edge Function deploys, log reads, and doc search to AI agents; vector search
  (pgvector) marketed explicitly as "AI toolkit." [supabase.com/docs/guides/ai-tools/mcp,
  supabase.com/blog/remote-mcp-server, supabase.com]
- **The Frontend Engineer req (17000) is itself an engineering-culture data point:** it describes
  a world where "an agent writes a large share of the code" and frames the job as building the
  layered checks (types, lint, unit/component tests, contract tests, accessibility, visual
  regression, bundle-size budgets) that keep that safe, plus working with tools like Vitest,
  Playwright, and MSW. [job posting 17000, jobs.ashbyhq.com/supabase]

## 7. Why-fit angles for Santiago

**Best hook to lead with:** the Frontend req is explicitly about supervising and building
guardrails around AI coding agents while shipping real product, and Santiago has done exactly that
twice over: Kairos wires Claude into two surfaces (an in-app agent via the Claude Agent SDK and a
standalone MCP server exposing 46 tools) with 228 Vitest tests over the core logic, and Pragma AI
runs client work as tools inside Claude Code with a hosted MCP brain service. That is a direct,
concrete answer to "comfort working with AI coding agents: reviewing what they produce, tightening
the architecture where they overreach."

**Supporting fit, Frontend (17000):** 0-to-1 shipping and iterating on real user feedback
(Eugenia.ai to acquisition, Online Basics's internal ops platform used daily by operators); React
18/TypeScript/Vite frontend depth (Plutus: 11 routes, 45+ components, WebSocket and SSE
real-time layers); a real test-and-tooling habit, not just claimed (Hydrel: 114 Vitest unit tests
plus 10 Playwright E2E flows, zero-console-error assertions).

**Supporting fit, Customer Solution Architect AMER (4488):** founder background doing the exact
CSA loop solo (discovery, build, prove value, retain trust) at Eugenia.ai and Pragma AI; direct
client-facing technical translation work (the Hydrel energy-operations portal was built for and
with a client, CFO-grade economics, scenario compare); Postgres and SQL in active use (Plutus runs
on PostgreSQL 16 with TimescaleDB). Honest gap: the req's "preferred experience" line wants 6+
years specifically in Solutions Architecture/Database Engineering and Postgres performance tuning
at scale; Santiago's Postgres experience is from building his own products, not from tuning
production databases for external customers at scale, so this would need direct acknowledgment,
not overclaiming, in an interview.

**Honest concerns / watch-outs:**
- **Compensation is unconfirmed for these two roles.** Neither posting lists a salary. Supabase's
  own 2023 policy post says it does not geo-adjust pay and targets high percentiles outside major
  US cities, which argues against a below-floor offer, but that is a stated policy from 2023, not
  a number tied to either req, and it should be verified directly in process rather than assumed.
  His floor is 70,000 USD annual for LATAM-scoped roles.
- **No confirmed Mexico-based hire found.** Research surfaced "we hire globally," 60+ countries,
  and an explicit no-geo-adjustment pay policy, but no source names Mexico or a current
  Mexico-based team member specifically. Nothing in any source excludes Mexico either; this reads
  as genuinely open rather than confirmed.
- The CSA posting (4488) carries a stale team-size line (280+ members, 55+ countries) versus the
  Frontend posting's fresher figure (~400, 60+ countries) and the careers page (350+, 60+
  countries): the posting itself looks old (first seen 2024-11-14) even though it is still live,
  so treat headcount claims from that specific posting as dated, not the current state of the
  company.
- The one culture data point on work-life balance (3.0/5) comes from a thin, secondary aggregator
  source (5 reviews) and should not be repeated as fact.

## 8. Application-question angles

**Why this company:** lead with the AI-agent-authored-code angle, not the generic "I love
Postgres" framing. Supabase's own numbers (600%+ database-launch growth, 60%+ of new databases
created by AI tools) mean the Frontend team's actual mandate right now is building the checks that
keep agent-written code safe in production. That is the specific problem Santiago has already
built for himself in two different codebases (Kairos, Pragma AI), which makes this a "I already
do this" pitch rather than an aspirational one.

**Why you fit:** for the Frontend req, anchor on the CI/quality-pipeline framing in the JD itself
(types, tests, contract tests against APIs, catching a regression once and encoding the check that
prevents it forever) and point to concrete, countable evidence (228 Vitest tests in Kairos, 114
Vitest plus 10 Playwright E2E in Hydrel), not adjectives. For the CSA req, anchor on having run the
entire discovery-to-trust customer loop alone as a founder (Eugenia.ai, Pragma AI client
diagnostics) rather than claiming enterprise-scale Postgres tuning he has not done.

**Anything else:** the remote model is worth a direct, honest line, since Supabase is unusually
literal about it (no offices, no geo-adjusted pay by stated policy). Worth naming plainly that
he is Mexico City based, not relocating, and confirming the role is scoped to hire him from there,
rather than assuming it from the "AMER" or "fully remote" label alone.

## 9. Sources

researched: 2026-08-11

- https://supabase.com/careers - team size (350+, 60+ countries), stated values, benefits, hiring-globally language
- https://supabase.com/blog/why-supabase-remote - primary source for no-geo-adjusted-pay policy, remote hiring philosophy, dated 2023-08-05
- https://supabase.com/blog/supabase-series-f - Series F amount/valuation/investors, Multigres launch, developer growth numbers
- https://supabase.com/blog/supabase-series-e - Series E amount/valuation/investors, "30+ former founders across 37 countries," YC customer stat
- https://supabase.com/blog/remote-mcp-server - Remote MCP Server announcement (2025-10-03), AI-agent product direction
- https://supabase.com/blog/supavisor-1-million - Elixir-based Supavisor connection pooler, engineering stack evidence
- https://supabase.com/docs/guides/ai-tools/mcp - MCP server docs, AI-agent tooling surface
- https://supabase.com/ - product overview (database, auth, storage, edge functions, realtime, vector search)
- https://techcrunch.com/2026/06/05/supabase-doubles-valuation-to-10b-in-8-months/ - growth metrics, founder quotes on AI-driven growth and enterprise-deal refusal
- https://www.cnbc.com/2026/06/04/database-startup-supabase-raises-500-million-10point5-billion-valuation.html - Series F date/amount corroboration
- https://jobsbyculture.com/blog/working-at-supabase-2026 - secondary source on same-pay-worldwide framing and work-life-balance sentiment (thin sample, flagged as such)
- https://www.levels.fyi/companies/supabase/salaries - secondary compensation data points (limited, mostly non-role-specific)
- https://www.sgpbusiness.com/company/Supabase-Pte-Ltd and https://opengovsg.com/corporate/T20UF4683B - Singapore incorporation record, founded 2020
- Job posting 17000 (Frontend Engineer): https://jobs.ashbyhq.com/supabase/f048dd68-63f8-4f98-9860-3d5a43c09a01/application - role scope, "What We Offer" benefits, team headcount as of 2026-07-29 posting
- Job posting 4488 (Customer Solution Architect, AMER): https://jobs.ashbyhq.com/supabase/d5573afa-636c-4219-832f-386f498243bf/application - role scope, preferred experience, team headcount as of original 2024-11-14 posting (stale figure, noted above)
