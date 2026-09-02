# airCFO (aircfo.com)

Draft dossier for Santiago Coronado, prepared for the "Founding Engineer" (remote) role, job id 8782.
This is a draft for Santiago to review before use in application materials.

## 1. Snapshot

airCFO is an outsourced back-office partner (accounting, bookkeeping, fractional CFO/finance,
tax, people ops) for VC-backed startups, founded in 2012 by Justin McLoughlin out of an informal
remote-accounting arrangement with his former employer Apartment List, its first client
(aircfo.com/about-us). It has grown to 300+ current/former startup clients and a "fully-distributed"
team of 60+ people (aircfo.com/team). No credible external funding round was found for airCFO
itself; it reads as a founder-led, profitable services business, not a VC-backed startup (see
Sources note on rejected funding figures). It is now hiring its first dedicated software engineer,
remote, timezone band UTC-8 to UTC+2, to build an internal AI platform on top of the services
business (Hacker News job posting, item 48768318).

## 2. Core narrative

airCFO is a 13-year-old accounting/finance services firm mid-pivot into a software company. CEO
Alex Wittenberg has publicly framed 2026 as the year "airCFO becomes aiCFO": the plan is to encode
the firm's own accumulated back-office expertise into AI workflows and custom internal tooling
instead of competing on commodity bookkeeping tasks (Wittenberg LinkedIn post, "2026 will be the
year airCFO becomes aiCFO"). This is not a marketing-only AI story: Wittenberg has personally built
internal tools with Claude Code, with an assist from the firm's part-time CTO Yair Aviner (Wittenberg
LinkedIn post on the board-reporting dashboard launch; Yair Aviner LinkedIn profile). The Founding
Engineer role is the first full-time technical hire to formalize that: a RAG context layer over the
firm's own tools plus internal apps built with Claude and MCP (HN posting, item 48768318).

## 3. Mission & product

- Core service: bookkeeping, AR/AP, revenue recognition, fractional CFO work (financial modeling,
  budgeting, board reporting), tax planning/compliance, and people ops, sold as one integrated team
  replacing a patchwork of a bookkeeper, tax firm, CFO, and HR consultant (aircfo.com/why-aircfo).
- Stage-matched packaging under a "Flightplan Framework": pre-seed, seed, Series A, Series B+
  (aircfo.com/why-aircfo).
- Pitch is hybrid: "technology + personal advisor," claiming up to 80% savings versus an in-house
  finance team (aircfo.com/why-aircfo).
- Shipped a Board Reporting Dashboard (auto-populated actuals/projections, burn, headcount,
  custom-metric scorecards, synced via LiveFlow) as an example of the productized direction
  (Wittenberg LinkedIn post on the dashboard launch).
- Named current/former clients: Apartment List, Replit, Anthropic, Coffee Meets Bagel, Desmos,
  WorkRamp, ScootScience, Crosschq, Edge Impulse, FloatMe, TruSTAR (acquired by Splunk), 1Konto,
  Basis, LiveFlow (aircfo.com homepage; aircfo.com/client-stories). Harmonic is named as a
  current/former client only in the company's own HN job posting (item 48768318); not independently
  corroborated elsewhere, so treat as company-stated, not third-party-verified.
- Tech/finance partner integrations: Mercury, Stripe, Ramp, QuickBooks Online, LiveFlow, Carta,
  Pulley, Vouch, Embroker, Taxbit, Bitwave (for web3 clients) (aircfo.com/partner-hub/tech-partners).

## 4. Stage/scale

- Founded 2012, Bay Area origin, now serving 300+ startups across the US (aircfo.com/about-us).
- Team: "fully-distributed... 60+ team members spread across the globe" per the company's own team
  page (aircfo.com/team). Third-party data aggregators (ZoomInfo, RocketReach) give rougher,
  lower estimates (roughly 50 employees); treat the company's own figure as primary.
- Leadership: Alex Wittenberg, CEO (aircfo.com/team; LinkedIn); Justin McLoughlin, President/founder
  (aircfo.com/team); part-time/fractional CTO is Yair Aviner, referred to by Wittenberg as "our PT
  CTO" (Yair Aviner LinkedIn profile, via Wittenberg's product-launch post).
- Funding: search results surfaced two "funding" figures for airCFO ($200M seed, $731M raised) from
  a low-quality aggregator (SignalBase); these are implausible for a bookkeeping services firm and
  are explicitly excluded here as not credible. No legitimate funding-round data was found. Treat
  airCFO as likely bootstrapped/founder-owned unless told otherwise in an interview.

## 5. Tech stack (from the role itself, primary source)

TypeScript, Node, Python/FastAPI, React, Postgres, Claude, and MCP (Model Context Protocol), used
both for the new RAG/context-layer platform and for the internal apps the team uses daily (HN
posting, item 48768318). The company's public content also shows real internal use of Claude Code
and custom MCP servers connecting client tools (Mercury, Stripe, Ramp, QuickBooks) to Claude for
finance workflows (Wittenberg's CFO update demo, referenced in his LinkedIn activity and in the
company's own "Claude Code quickstart" newsletter content, aircfo.com/resources).

## 6. Recent news (dated where a date could be confirmed)

- July 2026: airCFO posts "Founding Engineer" to the Hacker News "Who is hiring?" (July 2026)
  thread, its first dedicated software engineering hire, to build a RAG context layer and internal
  Claude/MCP apps (HN item 48768318; job first seen in this pipeline's DB 2026-07-08).
- 2026 (exact date not recoverable from public cache): CEO Alex Wittenberg posts "2026 will be the
  year airCFO becomes aiCFO," describing the strategic pivot toward AI-encoded expertise and custom
  client tooling (Wittenberg LinkedIn post).
- 2026 (exact date not recoverable): Wittenberg posts about shipping a Board Reporting Dashboard,
  built with Claude Code and "an assist from our PT CTO" Yair Aviner, syncing with LiveFlow
  (Wittenberg LinkedIn post).
- Beyond these, no additional dated press, funding, or leadership news was found in the last 12
  months. Coverage of this company is thin outside its own site and LinkedIn; say so plainly rather
  than pad this section.

## 7. Engineering & AI direction

- The founding-engineer mandate is explicit: build a retrieval/RAG context layer over all of
  airCFO's internal tools, plus the TypeScript/Node/Python-FastAPI/React/Postgres internal apps the
  team uses daily, using Claude and MCP (HN item 48768318).
- Reporting line is a hands-on, part-time/fractional CTO (Yair Aviner), not a resident engineering
  team; the posting explicitly wants someone senior who "drives coding agents hard but refuses to
  lose the plot," i.e. comfortable with AI-assisted/agentic coding while still owning system
  architecture end to end (HN item 48768318).
- "Production RAG/agents a plus, not a requirement," small team, high autonomy (HN item 48768318).
- Leadership is already a practitioner, not just a sponsor: the CEO personally builds internal
  tooling with Claude Code and has floated (informally, via a webinar/newsletter) a "Claude for
  Startup Finance" plugin connecting Ramp, Mercury, Stripe, and QuickBooks (Wittenberg LinkedIn
  activity referenced via search; aircfo.com/resources Claude Code content). This is circumstantial
  (pieced together from a search summary plus the newsletter itself, not one single primary
  document), so treat the "plugin" detail as directional rather than confirmed product fact.

## 8. Culture & voice

- Tagline-level value statement: "we don't just understand startups, we live them"
  (aircfo.com/why-aircfo).
- Public voice is founder-led and personal: Wittenberg posts under his own name about product
  builds, strategy, and AI tooling rather than posting only through a branded company account
  (Wittenberg LinkedIn, multiple posts cited above).
- Educational, founder-friendly content arm ("The AI CFO" newsletter/resources) that teaches
  startup founders how to use tools like Claude Code and Claude in Excel, not just markets airCFO's
  own services (aircfo.com/resources/claude-code-quickstart-guide-brexs-5b-exit-story-the-ai-cfo).
- Team composition is CPAs/MBAs/advisory leads, not engineers; per its own team page there is no
  listed CTO or engineering headcount today, which is consistent with this being the first
  engineering hire (aircfo.com/team).

## 9. Why-fit angles for Santiago

Best single hook to lead with: Santiago has personally run the exact transition airCFO says it
wants to make, turning a services/ops-heavy business into one that runs on his own AI/software
tooling, more than once, and he already operates the specific stack (TypeScript, Node, Python/
FastAPI, React, Postgres, Claude, MCP) this role calls for in solo/small-team production systems.

Supporting angles:
- Founder pattern match: founder/co-founder across three ventures (Online Basics, Eugenia.ai,
  Pragma AI, per resume/master_resume.yaml), each involving 0-to-1 build and product ownership,
  maps directly to a "founding engineer under a fractional CTO, small team, high autonomy" mandate.
- Stack match is close to exact: FastAPI, React, TypeScript/Node.js, PostgreSQL are all listed
  under Santiago's "Software & Cloud" skills; he ships production RAG (Pragma Brain), a function-
  calling agent (Hermes), and an MCP-based agent (Plutus), each a smaller version of what this role
  scopes (RAG context layer, internal Claude/MCP apps) (resume/master_resume.yaml).
- Daily Claude Code use lines up with a company whose CEO already drives coding agents personally;
  the posting's "drives coding agents hard but refuses to lose the plot" line is a near-literal
  description of how Santiago already works.
- Finance-adjacency exists but is not accounting-specific: Online Basics ran financial/inventory
  analytics pipelines at $8M revenue scale, and Plutus is a self-hosted investment-research platform
  on Postgres/TimescaleDB, both finance-flavored, neither is bookkeeping/GAAP/tax domain experience.
- Timezone fits cleanly: the role's stated band is UTC-8 to UTC+2 (HN item 48768318); Mexico City is
  UTC-6, comfortably inside that range, and Santiago is TN-visa eligible if relevant for a US entity
  (resume/master_resume.yaml, config/profile.yaml).

Honest concerns / watch-outs:
- No salary or equity information is public anywhere (job DB, HN posting); profile.yaml's $65k
  minimum-base dealbreaker cannot be checked before applying, this needs to be raised early.
- The role reports to a part-time/fractional CTO, not a resident engineering team or manager;
  Santiago has led a 7-person team before but here he would likely be the only full-time engineer,
  a much more solo setup than Online Basics or Pragma AI.
- Domain gap: no direct bookkeeping, GAAP, revenue-recognition, or tax-compliance experience on the
  resume; the role explicitly needs someone who can build a RAG layer "over all our tools," which
  implies real exposure to accounting workflows and terminology he would need to ramp on fast.
- Company scale and funding profile are genuinely small and likely bootstrapped (60ish people, no
  credible funding round found); this is a stability/runway question worth asking directly rather
  than assuming VC-style backing.

## 10. Application-question angles (narrative-led, not full answers)

- Why this company: lean on the pivot, not the accounting-firm label. airCFO already has 13 years
  of financial operating expertise across 300+ startups; 2026 is explicitly the year it tries to
  turn that expertise into software instead of headcount. Santiago has done the same move himself
  (Online Basics: LLM workflows replacing manual e-commerce ops; Pragma AI: productizing client
  expertise into a RAG "company brain"), so this isn't an abstract interest in fintech, it's the
  exact shape of company he keeps building.
- Why you fit: lead with stack-plus-founder overlap in one breath rather than listing all four
  research areas. He already ships production RAG, function-calling agents, and MCP tooling on
  FastAPI/React/Postgres/TypeScript, solo, with Claude Code as his daily driver, which is the literal
  job description here, not an adjacent skill set.
- Anything else: worth naming plainly that he is remote from Mexico City (inside the role's UTC-8 to
  UTC+2 band) and that reporting to a hands-on, coding fractional CTO rather than a big engineering
  org is a good fit for someone who has always been the person closest to the code and the product
  decision at once.

## Sources

- https://aircfo.com/ , home page: services, business model, named clients, "proprietary AI" claim.
- https://aircfo.com/team , team page: leadership names/titles, "60+ team members... fully
  distributed" headcount claim.
- https://aircfo.com/why-aircfo , value proposition, hybrid tech+advisor pitch, culture tagline.
- https://aircfo.com/client-stories , named clients and testimonial themes.
- https://aircfo.com/about-us , founding story, 2012 origin, Justin McLoughlin/Apartment List.
- https://aircfo.com/partner-hub/tech-partners , fintech/tech partner integrations list.
- https://aircfo.com/resources/claude-code-quickstart-guide-brexs-5b-exit-story-the-ai-cfo , CEO's
  founder-facing newsletter content on Claude Code and Claude in Excel.
- https://news.ycombinator.com/item?id=48768318 , primary source: full text of the Founding
  Engineer job posting (stack, reporting line, remote timezone band, contact).
- https://findwork.dev/MNNV47M/founding-engineer-at-aircfo , the listing as ingested into this
  pipeline (job id 8782).
- https://www.linkedin.com/in/yairaviner/ , confirms Yair Aviner as airCFO's part-time/fractional
  CTO (via a quoted line from CEO Alex Wittenberg).
- https://www.linkedin.com/in/awittenberg17/ , CEO Alex Wittenberg's background and role.
- https://www.linkedin.com/posts/awittenberg17_2026-will-be-the-year-aircfo-becomes-aicfo-activity-7405291381944000512-HF-W ,
  CEO's "airCFO becomes aiCFO" strategic post (exact publish date not recoverable via public cache).
- https://www.linkedin.com/posts/awittenberg17_aircfos-latest-product-launch-is-the-best-activity-7247293230621364226-RB1T ,
  Board Reporting Dashboard launch post, Claude Code / PT CTO detail (exact publish date not
  recoverable via public cache).
- Note on rejected sources: SignalBase ("airCFO Secures $200M in Seed Round," "airCFO Secures
  $731.0[M]") returned implausible funding figures for a bookkeeping services firm; treated as
  not credible and excluded from all claims above.

researched: 2026-07-14
