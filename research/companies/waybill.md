# Waybill (dossier draft for Santiago, review before use)

**Verification note:** Waybill is a very early-stage (5-person) Y Combinator startup with no
independent press coverage found. Everything below is sourced only to Waybill's own YC company
profile, its own website, its own YC job listing, and the job posting text pulled into this
pipeline's database. There is no third-party confirmation (press, funding database, LinkedIn
verification) of headcount, funding amount beyond the standard YC deal, or founder claims. Treat
company-provided facts as company-provided, not independently audited.

## 1. Snapshot
Y Combinator Summer 2026 (S26) startup building "managed procurement and inventory" software and
AI agents for hardware and deep-tech teams (sourcing, negotiation, freight, customs, delivery,
inventory, one to two months old as a public company). 5 employees, HQ in Gurugram, Haryana,
India per its YC profile; the open Founding Engineer role is based in Bengaluru, Karnataka, India,
in person, six days a week (not remote in the global sense despite how this job aggregator tagged
it). Funding beyond the standard YC batch investment is not disclosed anywhere found.
[YC company profile](https://www.ycombinator.com/companies/waybill),
[waybill.to](https://www.waybill.to/),
[YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)

## 2. Core narrative
Most procurement software stops at an approved purchase order; Waybill's pitch is that it owns
the entire loop through to a physical part landing on a shelf, ready to build with: sourcing
quotes from licensed global suppliers, negotiating price, handling a single consolidated payment
(parts, freight, duties, clearance, delivery), filing customs paperwork, and reconciling
inventory and invoices automatically, with a backup supplier that activates automatically if the
primary source fails. The founders are pitching domain-plus-agents credibility: Rishi Laddha ran
procurement, supply chain, and government relations at LAT Aerospace (founded by Zomato's
Deepinder Goyal), sourcing everything from precision manufacturing equipment to jet engines, and
built AI trade assistants at INDmoney; Tushar Goyal led AI at WareIQ (YC S20), building the
autonomous inventory and demand-forecasting system for 400+ Indian D2C brands. The job posting
itself is candid that the work is unglamorous and specific (one distributor's quote format, why a
shipment cleared customs in Chennai but not Mumbai) and explicit that the team works in person in
Bengaluru six days a week because "early-stage companies get built by people in a room together."
[YC company profile](https://www.ycombinator.com/companies/waybill),
[waybill.to](https://www.waybill.to/),
[YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)

## 3. Mission & product
- Stated mission: "Procurement on autopilot" for teams building hardware.
  [waybill.to](https://www.waybill.to/)
- Product loop: a customer submits a part request (quantity, deadline); Waybill's agents map all
  licensed global suppliers, send simultaneous RFQs, negotiate, present one payment that covers
  parts, freight, duties, clearance, and delivery, then handle customs filing, real-time
  shipment tracking (carrier and flight data feeds), a pre-delivery AI voice agent that calls
  drivers in their local language to confirm dock details, and automatic inventory update with
  duplicate-purchase prevention. [waybill.to](https://www.waybill.to/)
- Reliability feature: an automatic fallback supplier activates if the primary source fails, to
  protect delivery dates. [waybill.to](https://www.waybill.to/)
- Integration surface: reachable via Slack, Gmail, WhatsApp, Outlook, and directly from CAD tools
  (SolidWorks, NX, Altium, KiCad, Eagle), i.e. it wants engineers to request parts from the tools
  they already use rather than a separate procurement portal. [waybill.to](https://www.waybill.to/)
- Target customer: hardware manufacturers and engineering teams building physical products who
  need reliable component sourcing; the job posting's day-to-day examples (BOM decomposition
  agents, negotiation-agent evaluation, inventory design for "what a hardware team actually needs
  to see") confirm hardware/deep-tech engineering teams as the buyer.
  [waybill.to](https://www.waybill.to/), [job posting text, pulled 2026-08-31 via
  `python -m src.query job 34195`, original at
  findwork.dev](https://findwork.dev/XEVJwvn/founding-engineer-at-waybill)

## 4. Culture & voice
- Small team, YC-backed, early: 5 employees per the YC profile as of this research date.
  [YC company profile](https://www.ycombinator.com/companies/waybill)
- Explicit in-person culture: "We work in person in Bengaluru, six days a week. Early-stage
  companies get built by people in a room together, and we're not going to pretend otherwise."
  This is stated as a deliberate belief, not an incidental detail.
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- Ownership-heavy hiring pitch: founding engineers "own a vertical end to end" (sourcing,
  negotiation, logistics and customs, inventory, or the buyer-facing product), talk directly to
  customers, decide what gets built, and carry it through breaking at 2am. Explicitly not looking
  for someone who wants "a clearly defined scope and a well-groomed backlog."
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- Real equity for early engineers is called out as a stated value ("the people who build this
  should own a piece of it"), paired with a real but modest cash band for the market
  (INR 1.8M to 3.5M annually, roughly USD 21K to 42K at recent exchange rates) plus 0.50% to
  1.00% equity. [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- Voice throughout the job post and website is plain, specific, and unhyped: it leads with
  concrete scenarios (a BOM decomposition agent, a negotiation-agent eval harness, a customs
  discrepancy between Chennai and Mumbai) rather than mission-statement abstractions.
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)

## 5. Recent news (last ~12 months, dated)
- **2026 (exact founding date not disclosed)**: Waybill founded by Rishi Laddha and Tushar Goyal.
  [YC company profile](https://www.ycombinator.com/companies/waybill)
- **Summer 2026 (S26 batch)**: Admitted to Y Combinator; primary YC partner listed as Jared
  Friedman. This is the only funding/backing event found; no separate seed or press-covered
  funding round was located. [YC company profile](https://www.ycombinator.com/companies/waybill)
- **Mid-to-late August 2026**: Founding Engineer role posted (found live on the YC jobs board and
  syndicated to at least findwork.dev; posted_at 2026-08-18 per this pipeline's ingestion).
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer),
  [findwork.dev listing](https://findwork.dev/XEVJwvn/founding-engineer-at-waybill)
- No other dated news (launch posts, press, additional funding, leadership changes) was found
  beyond the above; this is consistent with a five-person, pre-launch-stage company.

## 6. Engineering & AI direction
- Stack, stated directly in the job posting: TypeScript end to end. Agents and backend on
  LangGraph, Node.js, Express, PostgreSQL, and Langfuse for LLM observability/evals ("yes we take
  our evals seriously"). Product on Next.js, React, Tailwind, shadcn/ui, and TanStack Query. Data
  and infra on PostgreSQL, Drizzle ORM, and Vercel.
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- AI bet is agentic, not chat-wrapper: the posting explicitly wants engineers who have gone
  "beyond wrapping a chat API" into tool calling, structured outputs, evals, and long-running
  agents that can fail halfway through, and names a negotiation agent (talks to suppliers with
  customers' money, needs guardrails and an eval harness to know if a change is actually better)
  and a procurement-pipeline agent that reads a BOM and decomposes it into sourceable line items
  or handles customs documentation, plus a pre-delivery AI voice agent that calls drivers in
  their local language. [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer),
  [waybill.to](https://www.waybill.to/)
- Domain-encoded engineering: the posting is explicit that supply-chain domain knowledge (what an
  MPN is, why RoHS compliance matters, what a customs broker does, why lead times slip) "is the
  engineering," not separate from it, meaning the eng team is expected to build deep
  domain-specific agent logic rather than a generic ops tool.
  [YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- No public engineering blog, GitHub org, or technical writing was found; all technical detail
  above comes from the job posting and product page.

## 7. Why-fit angles for Santiago (Founding Engineer)

**Critical fit blocker, read first:** the role requires working in person in Bengaluru, India,
six days a week ("early-stage companies get built by people in a room together"), and the YC job
listing scopes it as India-based (location "Bengaluru, Karnataka, India / Remote (India)",
compensation quoted in INR at local market levels, no US-visa language because none is needed for
an India-based hire). This is a direct hit against Santiago's own location_rule: he lives in
Mexico City, will not relocate, and any role that REQUIRES a work location outside Mexico (on-site
or hybrid, anywhere) is a dealbreaker. The job aggregator that surfaced this role tagged it
"Remote," which is misleading; the underlying posting is not remote in the sense his profile
means. Recommend this role be treated as out of scope unless Santiago is deliberately open to
relocating to India, which is not indicated anywhere in his profile.
[YC job posting](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)

Setting the location blocker aside, if Santiago (or a similar-profile candidate willing to relocate)
were to pursue this, the substantive fit is genuinely strong:

- **Exact tech-stack match with founder-level ownership**: TypeScript end to end, LangGraph
  agents, Next.js/React/Tailwind, matches his Plutus (FastAPI/React/TypeScript, LLM research
  agent exposed via MCP), Kairos (Claude Agent SDK plus MCP server, 52 tools, Zod schemas), and
  Pragma AI agent work almost tool for tool. [resume/master_resume.yaml]
- **"Owns a vertical end to end" maps to his founder history**: Waybill wants someone who talks to
  customers, decides what gets built, ships it, and owns the outcome, which is exactly how
  Santiago ran Online Basics (built the company's internal pricing/inventory platform himself,
  end to end, for a $8M revenue business) and Eugenia.ai (owned the full product lifecycle,
  led on-site client deployments). [resume/master_resume.yaml]
- **Agent evals and guardrails experience**: Waybill's negotiation agent needs an eval harness
  before it can be trusted with customers' money; Santiago's Pragma AI "company brain" shipped
  with an automated eval harness and deterministic no-answer/citation gating, a directly
  analogous build. [resume/master_resume.yaml]
- **Comfort with domain-heavy, unglamorous engineering**: Waybill explicitly wants engineers who
  will learn supply-chain specifics (MPNs, RoHS, customs) as part of the job; Santiago's five
  years running a multi-marketplace ecommerce operation (Amazon, Mercado Libre, Inflow
  integrations, inventory and pricing systems) is a directly comparable "the domain grit is the
  job" background, even though the domain (ecommerce retail vs. hardware procurement) differs.
  [resume/master_resume.yaml]

**Honest concerns / watch-outs:**
- The location requirement above is disqualifying as posted; this is the dominant concern, not a
  minor one.
- No hardware, electronics, or physical supply-chain domain experience (MPNs, RoHS, customs
  brokerage) anywhere in his background; his supply-chain-adjacent experience is ecommerce
  retail/inventory, not physical component sourcing or customs, a real domain gap the posting
  itself flags as central to the job.
- Compensation as posted (INR 1.8M to 3.5M, roughly USD 21K to 42K) is well below his stated
  comp floor (`comp.min_usd` 70,000 USD gross annual), separate from and in addition to the
  location issue.

## 8. Application-question angles
Given the location blocker in section 7, these angles are provided for completeness/reference
only; Santiago should not apply to this specific posting as listed.

- **Why this company**: if ever relevant (e.g. a future remote-eligible Waybill opening), the
  honest hook is the "PO is not the finish line" thesis: most procurement tools stop at an
  approved order, Waybill's agents own the loop through to a part physically landing on the
  shelf, which is a genuinely distinctive, harder, more complete version of the agent-ops
  problem than a typical AI wrapper.
- **Why you fit**: lead with founder-level, end-to-end ownership (Online Basics's internal
  platform, Eugenia.ai's full product lifecycle) paired with hands-on agent-eval experience
  (Pragma AI's automated eval harness), the two things the posting cares about most, rather than
  a stack checklist.
- **Anything else**: this is the honest place to name that the role as posted requires relocation
  to Bengaluru, India, six days a week in person, which does not fit his fixed Mexico City base,
  and to ask directly whether any remote or India-optional arrangement exists before going
  further.

## 9. Sources
- [YC company profile: Waybill (team size, HQ, founders, YC batch, partner)](https://www.ycombinator.com/companies/waybill)
- [waybill.to (product, business model, mission, integrations, contact)](https://www.waybill.to/)
- [YC job posting: Founding Engineer (location, compensation, equity, stack, requirements)](https://www.ycombinator.com/companies/waybill/jobs/l28KKVa-founding-engineer)
- [YC jobs listing for Waybill (confirms single open role and its location)](https://www.ycombinator.com/companies/waybill/jobs)
- [findwork.dev job listing (original posting as syndicated to this pipeline)](https://findwork.dev/XEVJwvn/founding-engineer-at-waybill)
- [config/profile.yaml, resume/master_resume.yaml (internal, for fit angles and location_rule)]

researched: 2026-08-31
