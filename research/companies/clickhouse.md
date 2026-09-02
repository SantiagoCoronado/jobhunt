# ClickHouse (dossier draft for Santiago, review before use)

## 1. Snapshot
Open-source columnar database company (real-time analytics, data warehousing, observability,
and AI workloads) that also sells a managed cloud product, ClickHouse Cloud. Late-stage,
fast-growing private company: raised a $400M Series D in January 2026 at a $15B valuation
(more than double its ~$6.35B Series C valuation from May 2025), and reported over $250M ARR
and 4,000+ customers by May 2026. HQ in the San Francisco Bay Area with a European entity
(ClickHouse B.V.) in Amsterdam; globally distributed team operating in 20+ countries, remote-friendly.
Current role in context: **AI Operations Engineer** (Greenhouse 6143997004, job id 18857 in this
pipeline), listed location "AMER," a newly formed internal AI Ops function inside IT Operations
(Technical Lead plus one or two AI Ops Engineers, reporting to the IT Business Systems Manager);
posted salary $170,000 to $220,000 US base / $200,000 to $250,000 in US premium markets.
[clickhouse.com/blog Series D](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres),
[Open House 2026 milestones](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers),
[Wikipedia](https://en.wikipedia.org/wiki/ClickHouse),
[Job posting: AI Operations Engineer (Greenhouse 6143997004)](https://job-boards.greenhouse.io/clickhouse/jobs/6143997004)

## 2. Core narrative
ClickHouse spent a decade proving it has the fastest, most efficient engine for real-time
analytics at petabyte scale (born at Yandex in 2009-2012, open-sourced in 2016). It is now
converting that speed advantage into an "agentic data stack" bet: rather than just selling a
database, it is building the full loop that lets AI agents query, investigate, and act on live
telemetry and business data themselves, evidenced by the January 2026 acquisition of the LLM
observability tool Langfuse, the public beta of Claude-powered "ClickHouse Agents," a
purpose-built MCP server for its ClickStack observability product, and the August 2026 launch of
ClickHouse Labs (a new database-research division led by Carnegie Mellon's Andy Pavlo). The
company practices what it sells internally, too: its own data warehouse team built "DWAINE," an
internal Claude- and MCP-based natural-language analyst that now fields roughly 200+ daily
messages from 250+ employees and cut ad hoc analyst requests by 50 to 70 percent, the same
pattern of internal AI-agent enablement the AI Operations Engineer role is now being asked to
formalize company-wide. The company is explicit that in 2026 "a complete data platform is more
than a database, it is a database plus the tools that make it accessible to AI agents and the
instrumentation to understand how those agents behave."
[The Agentic Data Stack](https://clickhouse.com/blog/the-agentic-data-stack),
[Managed ClickStack MCP Server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server),
[AI is redrawing the database market](https://clickhouse.com/blog/ai-redrawing-database-market),
[How we made our internal data warehouse AI-first](https://clickhouse.com/blog/ai-first-data-warehouse),
[ClickHouse Labs launch](https://clickhouse.com/blog/andy-pavlo-founding-clickhouse-labs)

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
  service in ClickHouse Cloud, with continued feature work (richer trace navigation, broader
  metrics support, smarter dashboards/alerts/APIs) through June and July 2026.
  [ClickStack blog](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse),
  [What's new in ClickStack, June + July 2026](https://clickhouse.com/blog/whats-new-in-clickstack-june-2026)
- 2026 releases: ClickHouse Postgres (public beta, built with Ubicloud, over 5x TPS vs AWS RDS,
  native CDC); Langfuse V4 (LLM observability, 200x query performance improvement
  post-acquisition); ClickHouse Agents (Claude-powered agentic analytics, public beta, no-code
  agent builder); and, in the July 26.6 core release, AI embedding functions and "hypothetical
  skip indexes" (preview an index's performance gain before building it).
  [Series D blog](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres),
  [Open House Day 1](https://clickhouse.com/blog/open-house-2026-day-1),
  [July 2026 newsletter](https://clickhouse.com/blog/202607-newsletter)
- Customers span AI-native companies and global enterprises: Anthropic, Meta, Cursor, Sony,
  Tesla, Capital One, Lovable, Decagon, Polymarket, Airwallex, Lyft, Instacart, and CERN's LHCb
  experiment. [Job posting (Greenhouse 6143997004)](https://job-boards.greenhouse.io/clickhouse/jobs/6143997004),
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
  [job posting](https://job-boards.greenhouse.io/clickhouse/jobs/6143997004),
  [clickhouse.com/company/careers](https://clickhouse.com/company/careers)
- Engineering culture is pragmatic and experimentation-heavy rather than top-down: no company
  mandate to use AI coding agents, but voluntary, wide adoption (Claude Code/Opus as the
  preferred agent, Cursor, Windsurf, custom internal agents), with an explicit ethos that
  "always find a way to validate every change" and that AI adoption widens the gap between good
  and mediocre engineers rather than levelling it. [Agentic coding at ClickHouse](https://clickhouse.com/blog/agentic-coding)
- 10-year open-source milestone (celebrated at Open House 2026) suggests real pride in
  open-source roots and community, not just enterprise sales motion.
  [Open House 2026 Day 2](https://clickhouse.com/blog/open-house-2026-day-2)
- New in mid-2026: expanding beyond pure tech marketing into sports sponsorship, named Principal
  Partner and Front of Shirt Sponsor of Fulham Football Club (Men's First Team) on July 21, 2026,
  a signal of brand-building ambitions beyond the developer community.
  [Fulham sponsorship (Yahoo Finance/press coverage)](https://finance.yahoo.com/technology/articles/clickhouse-announced-principal-partner-front-080000850.html)

## 5. Recent news (last ~12 months, dated)
- **May 2025**: Series C, $350M at ~$6.35B valuation, led by Khosla Ventures. Included here as
  funding-history context (outside the strict 12-month window from this refresh date).
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
- **June 8, 2026**: Appointed Ed Lenta as Vice President for Asia Pacific and Japan, expanding
  global go-to-market leadership, signaling continued international scale-up.
  [BusinessWire](https://www.businesswire.com/news/home/20260608754768/en/ClickHouse-Appoints-New-Leader-for-Asia-Pacific-and-Expands-Global-Go-To-Market-Leadership-Team)
- **June 24, 2026**: Announced the Managed ClickStack MCP server in ClickHouse Cloud, exposing
  purpose-built observability investigation tools (event-pattern clustering via Drain3, trend
  correlation, trace inspection, dashboard persistence) to AI agents; internal benchmarks
  showed 25% fewer tool calls, 2.5x consistency, and ~20% higher eval scores versus a generic
  ClickHouse MCP server. [Managed ClickStack MCP Server](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server)
- **July 17-23, 2026**: Ran its first virtual summer hackathon (with Trigger.dev, EUR 10,000 in
  prizes) focused on building AI agent chat experiences on ClickHouse.
  [July 2026 newsletter](https://clickhouse.com/blog/202607-newsletter)
- **July 21, 2026**: Named Principal Partner and Front of Shirt Sponsor of Fulham Football Club.
  [Press coverage](https://finance.yahoo.com/technology/articles/clickhouse-announced-principal-partner-front-080000850.html)
- **August 3, 2026**: Launched ClickHouse Labs, a new research group focused on foundational
  database and data-architecture research (query processing, systems performance,
  infrastructure) for both ClickHouse and PostgreSQL, led by Andy Pavlo (Carnegie Mellon
  database researcher) as VP of Database Research.
  [ClickHouse Labs launch](https://clickhouse.com/blog/andy-pavlo-founding-clickhouse-labs),
  [BusinessWire](https://www.businesswire.com/news/home/20260803890510/en/ClickHouse-Launches-ClickHouse-Labs-With-Andy-Pavlo-as-VP-of-Database-Research)
- **Mid-August 2026** (posted August 14, 2026): Opened the AI Operations Engineer requisition,
  standing up a net-new AI Ops function inside IT Operations to centralize agent/LLM tooling,
  model evaluation, cost visibility, and AI training across People, Finance, Legal, and
  Engineering, a concrete internal-hiring signal that the company is scaling its own
  AI-enablement practice (the DWAINE precedent below) into a dedicated team.
  [Job posting (Greenhouse 6143997004)](https://job-boards.greenhouse.io/clickhouse/jobs/6143997004)

## 6. Engineering & AI direction
- Core engine is written for raw speed at petabyte scale (the open-source ClickHouse project,
  10 years old as of 2026, originally built at Yandex to power Yandex.Metrica).
  [Wikipedia](https://en.wikipedia.org/wiki/ClickHouse), [Open House Day 2](https://clickhouse.com/blog/open-house-2026-day-2)
- AI product surface as of mid-2026: ClickHouse Agents (Claude-powered, no-code agent builder,
  public beta), a Remote/Ask AI MCP server for general analytics, and the ClickStack-specific
  MCP server for observability investigation; Langfuse for LLM tracing, evaluation, and cost
  monitoring (integrated post-acquisition, V4 shipped with 200x query performance gains).
  [clickhouse.com/ai](https://clickhouse.com/ai), [ClickHouse Agents beta](https://clickhouse.com/blog/clickhouse-agents-beta)
- Internal precedent for exactly the kind of function the AI Operations Engineer role is hiring
  for: ClickHouse's own data warehouse team built "DWAINE" (Data Warehouse AI Natural Expert),
  an internal natural-language analyst on Claude 4 (via AWS Bedrock), LibreChat as the chat UI,
  and MCP servers over ClickHouse Cloud, backed by a business glossary and data-quality rules;
  by the time of the write-up it served 250+ internal users, 200+ daily messages, and cut analyst
  request volume by 50 to 70 percent, while a hard 70/30 split kept certified financial metrics
  on traditional BI. [How we made our internal data warehouse AI-first](https://clickhouse.com/blog/ai-first-data-warehouse)
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
  of Langfuse, the open "Agentic Data Stack" reference architecture (LibreChat + ClickHouse/MCP
  + Langfuse), and the new ClickHouse Labs research division (foundational work on query
  processing and infrastructure "powering the next generation of ... AI applications") are the
  concrete bets behind that thesis. [The Agentic Data Stack](https://clickhouse.com/blog/the-agentic-data-stack),
  [ClickHouse Labs launch](https://clickhouse.com/blog/andy-pavlo-founding-clickhouse-labs)
- July 2026 core release (26.6) shipped AI embedding functions directly in the database and
  "hypothetical skip indexes" for previewing index performance gains, plus experimental
  continuous queries. [July 2026 newsletter](https://clickhouse.com/blog/202607-newsletter)

## 7. Why-fit angles for Santiago (AI Operations Engineer, Greenhouse 6143997004)
**Best hook to lead with:** Santiago has already built, solo and at a smaller scale, the exact
thing this new internal function exists to formalize: an internal, agent-driven operations layer
that lets non-engineers run real workflows through Claude and MCP. At Pragma AI he co-built the
firm's internal operating platform, a hosted, authenticated MCP "brain" service (per-operator
tokens, rate limits) exposing 15 agent definitions and 10 reusable routines so operators run
quoting, diagnostics, discovery research, and delivery work as tools inside Claude Code. That is
a small, self-built version of the same job ClickHouse's new IT Ops AI function is standing up:
agent infrastructure, access control for non-human actors, and AI adoption across business teams,
which is also exactly what ClickHouse's own DWAINE case study describes doing at company scale.

- **Agent infrastructure and identity/access control for non-human actors**: Pragma AI's MCP
  brain service issues per-operator tokens and rate limits; Kairos exposes 52 tools through one
  typed tool layer to both an in-app Claude Agent SDK agent and a standalone MCP server. The JD
  explicitly asks for "provision, credential, and de-provision AI agent access" and "identity and
  access controls for automated/non-human actors." [resume/master_resume.yaml]
- **Internal AI adoption and enablement across business functions**: Pragma AI ships
  conversational agents and internal automations for quoting, reporting, onboarding, and
  collections for non-technical operators, and ran an adoption-blocker analysis that reshaped
  onboarding after dogfooding the RAG brain internally. The JD's core mandate is building AI
  workflows across People, Finance, Legal, and Engineering and driving "AI fluency and literacy
  org-wide." [resume/master_resume.yaml]
- **Internal dashboards and cost/operations visibility**: at Online Basics, Santiago built the
  company's internal operations platform (pricing dashboard, inventory admin panel, alerting)
  used daily by 4 operators, and orchestrated 10+ third-party APIs into hourly-synced pipelines
  processing 100K+ daily data points. The JD wants someone who can "build dashboards and
  reporting for AI/LLM spend" and "implement tagging, monitoring, and alerting for cost
  anomalies," a structurally similar build even though the previous domain was e-commerce spend,
  not LLM spend. [resume/master_resume.yaml]
- **Model evaluation instinct**: Pragma AI's RAG "company brain" shipped with an automated eval
  harness and deterministic no-answer/citation gating; Santiago has hands-on production use of
  both Anthropic and OpenAI APIs plus ElevenLabs, giving him real, if informal, cross-provider
  comparison experience to build on for the JD's "compare and evaluate AI models across
  providers" ask.

**Honest concerns / watch-outs:**
- **No formal training/enablement delivery track record**: the JD wants someone who designs and
  delivers "company-wide AI training programs" and runs "onboarding sessions, office hours, and
  workshops" for mixed technical/non-technical audiences. Santiago has run client AI diagnostics
  and onboarding at Pragma AI, but there is no evidence of formal, recurring internal-training
  program delivery at his scale; worth naming as an area he would be building out rather than
  repeating.
- **This is an internal IT Operations role, not a product/customer-facing engineering seat**: the
  team reports to the IT Business Systems Manager, not an engineering leader, and the scope is
  explicitly internal tooling (HRIS, ATS, ERP, procurement, ticketing, CLM) rather than
  ClickHouse's product surface. That is a genuine fit for Santiago's "internal tooling" strength
  (Family D), but he should walk into interviews clear that this is an IT/business-systems
  function, not a core product engineering track, and be ready to say why that scope appeals to
  him specifically.
- **No named production experience with enterprise SaaS integrations** the JD calls out (HRIS,
  ATS, ERP, CLM/Matter Management, procurement orchestration); his integration experience is
  real (Amazon, Mercado Libre, Inflow APIs at Online Basics; internal CRM at Kairos and Pragma)
  but not with these specific enterprise system categories, a legitimate gap to name rather than
  imply away.
- **Formal GRC/security process experience is thin**: the JD wants support for "model risk
  assessments and due diligence alongside Security and GRC" and "data privacy, security, and
  compliance considerations." Santiago's access-control work (per-operator tokens, rate limits,
  sensitivity labeling at ingest in Pragma's RAG brain) is a reasonable proof point, but he has
  not worked inside a formal GRC process before.

## 8. Application-question angles
- **Why this company**: Lead with the internal-mirror version of the Core narrative: ClickHouse
  does not just sell agent-facing infrastructure to customers (ClickStack MCP server, Langfuse,
  Claude-powered ClickHouse Agents), it already proved the model works on itself with DWAINE, an
  internal Claude and MCP agent that took real load off its own analyst team. Frame Santiago's
  interest as wanting to help ClickHouse turn that proven, ad hoc internal pattern into a
  disciplined, company-wide practice, rather than a generic "I like fast databases" answer.
- **Why you fit**: Anchor on the Pragma AI internal-platform parallel: Santiago already built a
  hosted, access-controlled MCP agent layer that lets non-engineers run real business workflows
  (quoting, diagnostics, onboarding, collections) as Claude Code tools, plus the dashboards and
  API-orchestration muscle from Online Basics to give that platform cost and operations
  visibility. Name this directly as "I have already built a small version of what this team is
  standing up," then be candid that the enterprise-system integrations and formal training
  delivery are the parts he would be growing into.
- **Anything else**: Use this slot for the honest gaps rather than more selling: no direct
  experience integrating with the specific enterprise systems named in the JD (HRIS, ATS, ERP,
  CLM) and no formal GRC process background, while pointing to a track record of picking up
  unfamiliar systems fast (Swift and Java at Nextia.mx, cloud microservices at Online Basics,
  the MCP brain service and access-control work at Pragma AI) as evidence he closes this kind of
  gap quickly on the job.

## 9. Sources
- [ClickHouse Series D announcement (funding, Langfuse acquisition, Postgres launch)](https://clickhouse.com/blog/clickhouse-raises-400-million-series-d-acquires-langfuse-launches-postgres)
- [Bloomberg: ClickHouse Lands $15 Billion Valuation](https://www.bloomberg.com/news/articles/2026-01-16/clickhouse-lands-15-billion-valuation-in-ai-database-race)
- [ClickHouse product/homepage](https://clickhouse.com/clickhouse)
- [ClickHouse Docs: What is ClickHouse](https://clickhouse.com/docs/intro)
- [ClickStack overview blog](https://clickhouse.com/blog/clickstack-a-high-performance-oss-observability-stack-on-clickhouse)
- [What's new in ClickStack, June + July 2026](https://clickhouse.com/blog/whats-new-in-clickstack-june-2026)
- [Managed ClickStack MCP Server announcement](https://clickhouse.com/blog/announcing-managed-clickstack-mcp-server)
- [The Agentic Data Stack blog](https://clickhouse.com/blog/the-agentic-data-stack)
- [AI is redrawing the database market blog](https://clickhouse.com/blog/ai-redrawing-database-market)
- [Agentic coding at ClickHouse (internal AI-agent adoption)](https://clickhouse.com/blog/agentic-coding)
- [How we made our internal data warehouse AI-first (DWAINE)](https://clickhouse.com/blog/ai-first-data-warehouse)
- [ClickHouse Agents public beta announcement](https://clickhouse.com/blog/clickhouse-agents-beta)
- [clickhouse.com/ai (AI platform positioning)](https://clickhouse.com/ai)
- [Open House 2026 milestones ($250M ARR, 4,000 customers)](https://clickhouse.com/blog/clickhouse-tops-250m-arr-and-4000-customers)
- [Open House 2026 Day 1 recap](https://clickhouse.com/blog/open-house-2026-day-1)
- [Open House 2026 Day 2 recap (10 years open source)](https://clickhouse.com/blog/open-house-2026-day-2)
- [BusinessWire: Open House 2026 milestones](https://www.businesswire.com/news/home/20260527813115/en/ClickHouse-Tops-$250M-ARR-and-4000-Customers-Launches-Claude-Powered-Agents-at-Open-House-2026)
- [BusinessWire: APAC leader appointment / GTM expansion](https://www.businesswire.com/news/home/20260608754768/en/ClickHouse-Appoints-New-Leader-for-Asia-Pacific-and-Expands-Global-Go-To-Market-Leadership-Team)
- [July 2026 newsletter (26.6 release, hackathon, AI embedding functions)](https://clickhouse.com/blog/202607-newsletter)
- [Fulham FC sponsorship coverage](https://finance.yahoo.com/technology/articles/clickhouse-announced-principal-partner-front-080000850.html)
- [ClickHouse Labs launch (Andy Pavlo, VP of Database Research)](https://clickhouse.com/blog/andy-pavlo-founding-clickhouse-labs)
- [BusinessWire: ClickHouse Labs launch](https://www.businesswire.com/news/home/20260803890510/en/ClickHouse-Launches-ClickHouse-Labs-With-Andy-Pavlo-as-VP-of-Database-Research)
- [ClickHouse company careers page (values, culture)](https://clickhouse.com/company/careers)
- [Wikipedia: ClickHouse (founding history, funding history, HQ)](https://en.wikipedia.org/wiki/ClickHouse)
- [Job posting: AI Operations Engineer (Greenhouse 6143997004)](https://job-boards.greenhouse.io/clickhouse/jobs/6143997004)
- [config/profile.yaml, resume/master_resume.yaml (internal, for fit angles)]

researched: 2026-08-17
