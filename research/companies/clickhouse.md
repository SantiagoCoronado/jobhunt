# ClickHouse (dossier draft for Santiago, review before use)

## 1. Snapshot
Open-source columnar database company (real-time analytics, data warehousing, observability,
and AI workloads) that also sells a managed cloud product, ClickHouse Cloud. Late-stage,
fast-growing private company: raised a $400M Series D in January 2026 at a $15B valuation
(more than double its ~$6.35B Series C valuation from May 2025), and reported over $250M ARR
and 4,000+ customers by May 2026. HQ in the San Francisco Bay Area with a European entity
(ClickHouse B.V.) in Amsterdam; globally distributed team operating in 20+ countries, remote-friendly.
The role in question ("AI Product Engineer - ClickStack," Greenhouse posting) is fully remote, US.
[clickhouse.com/blog Series D](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres),
[Open House 2026 milestones](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers),
[Wikipedia](https://en.wikipedia.org/wiki/ClickHouse)

## 2. Core narrative
ClickHouse spent a decade proving it has the fastest, most efficient engine for real-time
analytics at petabyte scale (born at Yandex in 2009-2012, open-sourced in 2016). It is now
converting that speed advantage into an "agentic data stack" bet: rather than just selling a
database, it is building the full loop that lets AI agents query, investigate, and act on live
telemetry and business data themselves, evidenced by the January 2026 acquisition of the LLM
observability tool Langfuse, the public beta of Claude-powered "ClickHouse Agents," and a
purpose-built MCP server for its ClickStack observability product. The company is explicit that
in 2026 "a complete data platform is more than a database, it is a database plus the tools that
make it accessible to AI agents and the instrumentation to understand how those agents behave."
[The Agentic Data Stack](https://clickhouse.com/blog/the-agentic-data-stack),
[Managed ClickStack MCP Server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server),
[AI is redrawing the database market](https://clickhouse.com/blog/ai-redrawing-database-market)

## 3. Mission & product
- Core product: ClickHouse, an open-source, column-oriented SQL database built for speed at
  scale, from a laptop to hundreds of servers at true petabyte scale; unifies application
  analytics, data warehousing, observability, and GenAI workloads in one engine.
  [clickhouse.com/clickhouse](https://clickhouse.com/clickhouse)
- Commercial product: ClickHouse Cloud, a fully managed service; crossed $250M ARR and 4,000+
  customers by May 2026, tripling ARR year over year.
  [Open House 2026 milestones](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers)
- ClickStack: the open-source observability stack (logs, metrics, traces, session replay) built
  on ClickHouse and OpenTelemetry, with HyperDX as the UI layer; also offered as a managed
  service in ClickHouse Cloud. [ClickStack blog](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse),
  [ClickStack use case page](https://clickhouse.com/use-cases/observability)
- New in 2026: ClickHouse Postgres (public beta, built with Ubicloud, over 5x TPS vs AWS RDS,
  native CDC) for unified transactional + analytical workloads; Langfuse V4 (LLM observability,
  200x query performance improvement post-acquisition); ClickHouse Agents (Claude-powered
  agentic analytics, public beta, no-code agent builder). [Series D blog](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres),
  [Open House Day 1](https://clickhouse.com/blog/open-house-2026-day-1)
- Customers span AI-native companies and global enterprises: Anthropic, Meta, Cursor, Sony,
  Tesla, Capital One, Lovable, Decagon, Polymarket, Airwallex, Lyft, Instacart, and CERN's LHCb
  experiment. [Job posting (Greenhouse 6014112004)](https://job-boards.greenhouse.io/clickhouse/jobs/6014112004),
  [customer search results](https://clickhouse.com/user-stories)

## 4. Culture & voice
- Stated values: customer first, distributed (10+ countries), empathy at work, diversity (40%
  female leadership cited), and trust across timezones and cultures.
  [clickhouse.com/company/careers](https://clickhouse.com/company/careers)
- Looks for people who are "a contributor by nature, a thinker as well as a doer," who want
  direct ownership of their work and are drawn to hard technical problems.
  [clickhouse.com/company/careers](https://clickhouse.com/company/careers)
- Fully remote-friendly, globally distributed team (20+ countries per the job posting); the
  careers page tone is approachable and informal ("we'll definitely click!").
  [job posting](https://job-boards.greenhouse.io/clickhouse/jobs/6014112004),
  [clickhouse.com/company/careers](https://clickhouse.com/company/careers)
- Engineering culture is pragmatic and experimentation-heavy rather than top-down: no company
  mandate to use AI coding agents, but voluntary, wide adoption (Claude Code/Opus as the
  preferred agent, Cursor, Windsurf, custom internal agents), with an explicit ethos that
  "always find a way to validate every change" and that AI adoption widens the gap between good
  and mediocre engineers rather than levelling it. [Agentic coding at ClickHouse](https://clickhouse.com/blog/agentic-coding)
- 10-year open-source milestone (celebrated at Open House 2026) suggests real pride in
  open-source roots and community, not just enterprise sales motion.
  [Open House 2026 Day 2](https://clickhouse.com/blog/open-house-2026-day-2)

## 5. Recent news (last ~12 months, dated)
- **May 2025**: Series C, $350M at ~$6.35B valuation, led by Khosla Ventures.
  [Wikipedia](https://en.wikipedia.org/wiki/ClickHouse)
- **January 16, 2026**: Series D, $400M at $15B valuation, led by Dragoneer Investment Group
  (Bessemer, GIC, Index, Khosla, Lightspeed, T. Rowe Price accounts, WCM participating);
  simultaneously announced acquisition of Langfuse (LLM observability, 20,000+ GitHub stars,
  26M+ monthly SDK installs at acquisition) and launch of a native Postgres service built with
  Ubicloud. [Series D blog](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres),
  [Bloomberg coverage](https://www.bloomberg.com/news/articles/2026-01-16/clickhouse-lands-15-billion-valuation-in-ai-database-race)
- **March 3, 2026**: Published "The Agentic Data Stack," an open-source composable
  architecture (LibreChat + ClickHouse/MCP + Langfuse) letting agents query data directly;
  cited internal adoption variants at Shopify, Canva, and Khan Academy.
  [The Agentic Data Stack](https://clickhouse.com/blog/the-agentic-data-stack)
- **April 1, 2026**: Published a detailed account of a year of internal AI-coding-agent
  adoption (700 PRs from agents fixing CI/tests in Jan-Feb 2026 alone, 28% build-speed gain,
  a 6-month-old bug resolved via Claude Opus for under $30 in inference cost).
  [Agentic coding at ClickHouse](https://clickhouse.com/blog/agentic-coding)
- **May 27, 2026**: Open House 2026 (SF): announced crossing $250M ARR and 4,000 customers
  (net +1,000 since January 2026); launched ClickHouse Agents (Claude-powered agentic
  analytics, public beta); published CostBench, an open cost-performance benchmark for cloud
  data warehouses; launched "House Mates," first formal partner program (25+ tech partners,
  35+ services/consulting partners). Also announced Postgres public beta, distributed query
  execution improvements, Langfuse V4, and lakehouse write support for OneLake/Unity Catalog.
  [Open House milestones](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers),
  [Open House Day 1](https://clickhouse.com/blog/open-house-2026-day-1),
  [BusinessWire](https://www.businesswire.com/news/home/20260527813115/en/ClickHouse-Tops-$250M-ARR-and-4000-Customers-Launches-Claude-Powered-Agents-at-Open-House-2026)
- **June 8, 2026**: Appointed a new APAC leader and expanded global go-to-market leadership,
  signaling continued international scale-up.
  [BusinessWire](https://www.businesswire.com/news/home/20260608754768/en/ClickHouse-Appoints-New-Leader-for-Asia-Pacific-and-Expands-Global-Go-To-Market-Leadership-Team)
- **June 24, 2026**: Announced the Managed ClickStack MCP server in ClickHouse Cloud, exposing
  purpose-built observability investigation tools (event-pattern clustering via Drain3, trend
  correlation, trace inspection, dashboard persistence) to AI agents; internal benchmarks
  showed 25% fewer tool calls, 2.5x consistency, and ~20% higher eval scores versus a generic
  ClickHouse MCP server. [Managed ClickStack MCP Server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server)

## 6. Engineering & AI direction
- Core engine is written for raw speed at petabyte scale (the open-source ClickHouse project,
  10 years old as of 2026, originally built at Yandex to power Yandex.Metrica).
  [Wikipedia](https://en.wikipedia.org/wiki/ClickHouse), [Open House Day 2](https://clickhouse.com/blog/open-house-2026-day-2)
- AI product surface as of mid-2026: ClickHouse Agents (Claude-powered, no-code agent builder,
  public beta), a Remote/Ask AI MCP server for general analytics, and the ClickStack-specific
  MCP server for observability investigation; Langfuse for LLM tracing, evaluation, and cost
  monitoring (integrated post-acquisition, V4 shipped with 200x query performance gains).
  [clickhouse.com/ai](https://clickhouse.com/ai), [ClickHouse Agents beta](https://clickhouse.com/blog/clickhouse-agents-beta)
- Explicit product philosophy for the ClickStack MCP server: agents perform much better with
  purpose-built, semantic investigation primitives (event-pattern clustering, trend/anomaly
  correlation, trace root-cause tools) than with raw SQL generation, with a SQL "escape hatch"
  kept for edge cases. [Managed ClickStack MCP Server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server)
- Internal engineering culture treats AI coding agents (Claude Code/Opus primary, Cursor,
  Windsurf, custom agents like "Groene.AI") as standard tooling, used for everything from CI/test
  fixes (700 PRs in two months) to multi-hour bug investigations, under a validate-every-change
  discipline rather than blind trust. [Agentic coding at ClickHouse](https://clickhouse.com/blog/agentic-coding)
- Strategic thesis (stated by the company): databases are shifting from "passive data stores"
  to "agent-facing resources" that AI systems discover and query autonomously; the acquisition
  of Langfuse and the open "Agentic Data Stack" reference architecture (LibreChat + ClickHouse/MCP
  + Langfuse) are the concrete bets behind that thesis. [The Agentic Data Stack](https://clickhouse.com/blog/the-agentic-data-stack)

## 7. Why-fit angles for Santiago
**Best hook to lead with:** Santiago has already built, end to end, the exact category of
system this role is hiring for: an LLM research agent exposed through an MCP control plane
(Plutus), plus a from-scratch MCP server exposing a typed tool layer to both an in-app agent
and Claude Code (Kairos). That is not adjacent experience, it is the same architecture
(agent + tool design + MCP + evals-in-practice) the ClickStack AI Product Engineer role asks
for, just built solo instead of at petabyte scale.

- **MCP and agent-stack ownership**: Kairos exposes 18 tools through a single typed
  tool-definition layer consumed by both an in-app Claude Agent SDK agent and a standalone MCP
  server, mirroring the job's ask for someone who has "hit the limits of generic copilots" and
  can "own the agent stack end-to-end" (context engineering, tool design, evals, tracing, cost).
  [resume/master_resume.yaml]
- **Building agents against a live data substrate**: Plutus pairs an autonomous discovery
  engine (vectorized signal scans, evidence-backed candidate inbox) with an LLM research agent
  that drafts memos and converts natural language into backtestable rules, on a
  Postgres/TimescaleDB + Celery/Redis backend. That is a close structural match to "build agents
  that investigate incidents... using ClickStack as their substrate."
  [resume/master_resume.yaml]
- **SQL and data-pipeline fluency**: 7+ years building on relational/time-series databases
  (SQLAlchemy, TimescaleDB, PostgreSQL) and, earlier, orchestrating 10+ third-party APIs into
  hourly-synced pipelines processing 100K+ daily data points at Online Basics; the JD explicitly
  wants someone who "can write ClickHouse queries directly."
- **Production-minded, ship-fast bias**: founder background (Eugenia.ai exit, Online Basics to
  $8M revenue) shows comfort owning ambiguous 0-to-1 problems and shipping under real
  constraints, which lines up with ClickHouse's own "no top-down AI mandates, validate every
  change, keep shipping" engineering ethos.

**Honest concerns / watch-outs:**
- **Seniority and track record gap**: the JD wants "5+ years of software engineering including
  1-2 years on LLM-powered systems or agents in production," ideally with a track record of
  opinions formed from having shipped agents and dealt with their failure modes at scale.
  Santiago's agent work (Plutus, Kairos, the Pragma AI personal-finance agent) is real and
  recent but is founder/solo-project scale, not production systems serving external customers
  at ClickHouse's petabyte scale; this is a legitimate gap to be upfront about, not a
  fabrication he should paper over.
- **TypeScript/Node.js depth**: the role wants strong backend skills in TypeScript/Node.js
  and/or Python "comfortable in both." Santiago's resume shows strong Python and JavaScript/
  React/Node.js from Eugenia.ai, but his most recent, deepest agent work (Plutus) is
  Python-first (FastAPI); worth being honest that Node.js is less recently exercised.
- **Kubernetes**: the JD lists "comfort with Docker and Kubernetes." Santiago's resume shows
  Docker (Plutus, Kairos) but no explicit Kubernetes experience; this should be named as a gap
  rather than implied.
- **No explicit columnar-database or OpenTelemetry experience**: listed only as a "bonus" in
  the JD, so not a blocker, but worth knowing before an interview.

## 8. Application-question angles
- **Why this company**: Lead with the Core narrative, ClickHouse is not just betting that its
  database is fast, it is betting that databases become "agent-facing resources," and it just
  put real capital behind that bet (Langfuse acquisition, Claude-powered ClickHouse Agents, a
  purpose-built ClickStack MCP server). Frame Santiago's interest as wanting to build inside
  that specific thesis (agents that operate on live telemetry, not toy datasets) rather than a
  generic "I like fast databases" answer.
- **Why you fit**: Anchor on the MCP/agent architecture parallel: Santiago already designed and
  shipped a typed tool-definition layer serving both an in-app agent and an MCP server (Kairos),
  and an agent that turns raw signal into an investigated, evidence-backed output (Plutus's
  discovery engine and research agent). Name this as "I've built the small version of what
  ClickStack is hiring to build at petabyte scale," then be candid that the production-scale,
  team-based agent experience is the part he is actively growing into.
- **Anything else**: Use this slot for the honest gap rather than more selling: flag directly
  that his agent and MCP experience comes from founder-scale/solo projects rather than
  production systems serving thousands of customers, and that Kubernetes is not yet in his
  toolkit, while pointing to his track record of picking up unfamiliar infrastructure fast
  (Swift and Java for Nextia.mx, cloud microservices for Online Basics) as evidence he closes
  gaps quickly on the job.

## 9. Sources
- [ClickHouse Series D announcement (funding, Langfuse acquisition, Postgres launch)](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres)
- [Bloomberg: ClickHouse Lands $15 Billion Valuation](https://www.bloomberg.com/news/articles/2026-01-16/clickhouse-lands-15-billion-valuation-in-ai-database-race)
- [ClickHouse product/homepage](https://clickhouse.com/clickhouse)
- [ClickHouse Docs: What is ClickHouse](https://clickhouse.com/docs/intro)
- [ClickStack overview blog](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse)
- [ClickStack use case page](https://clickhouse.com/use-cases/observability)
- [Managed ClickStack MCP Server announcement](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server)
- [The Agentic Data Stack blog](https://clickhouse.com/blog/the-agentic-data-stack)
- [AI is redrawing the database market blog](https://clickhouse.com/blog/ai-redrawing-database-market)
- [Agentic coding at ClickHouse (internal AI-agent adoption)](https://clickhouse.com/blog/agentic-coding)
- [ClickHouse Agents public beta announcement](https://clickhouse.com/blog/clickhouse-agents-beta)
- [clickhouse.com/ai (AI platform positioning)](https://clickhouse.com/ai)
- [Open House 2026 milestones ($250M ARR, 4,000 customers)](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers)
- [Open House 2026 Day 1 recap](https://clickhouse.com/blog/open-house-2026-day-1)
- [Open House 2026 Day 2 recap (10 years open source)](https://clickhouse.com/blog/open-house-2026-day-2)
- [BusinessWire: Open House 2026 milestones](https://www.businesswire.com/news/home/20260527813115/en/ClickHouse-Tops-$250M-ARR-and-4000-Customers-Launches-Claude-Powered-Agents-at-Open-House-2026)
- [BusinessWire: APAC leader appointment / GTM expansion](https://www.businesswire.com/news/home/20260608754768/en/ClickHouse-Appoints-New-Leader-for-Asia-Pacific-and-Expands-Global-Go-To-Market-Leadership-Team)
- [ClickHouse company careers page (values, culture)](https://clickhouse.com/company/careers)
- [Wikipedia: ClickHouse (founding history, funding history, HQ)](https://en.wikipedia.org/wiki/ClickHouse)
- [Job posting: AI Product Engineer - ClickStack (Greenhouse 6014112004)](https://job-boards.greenhouse.io/clickhouse/jobs/6014112004)
- [config/profile.yaml, resume/master_resume.yaml (internal, for fit angles)]

researched: 2026-07-07
