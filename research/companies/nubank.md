# Nubank (Nu Holdings Ltd., NYSE: NU)

*Draft dossier for Santiago. Researched for the "Lead AI Engineer, Productivity Systems" role
(Greenhouse job 7890393). Review before use; re-check anything time-sensitive.*

## 1. Snapshot

Nubank is the largest digital financial platform in Latin America: a Brazil-founded, publicly
traded (NYSE: NU) neobank serving 135+ million customers across Brazil, Mexico, and Colombia as
of Q1 2026, with $5B+ quarterly revenue and $871M net income (up 41% YoY) [Q1 2026 results,
stocktitan]. In Mexico it just crossed 15 million customers and became the country's largest
digital bank, and on July 10, 2026 its Mexican unit (Nu Mexico) received CNBV authorization to
operate as a full commercial bank, backed by a formalized $4.2B investment commitment through
2030 [PYMNTS, Jul 10 2026; mexicobusiness.news, Jul 7 2026]. HQ is Sao Paulo, Brazil; this
specific role is US-based and hybrid (see section 7).

## 2. Core narrative

Nubank was founded in 2013 on the mission of "fighting complexity to empower people" in a region
where banking meant high fees, paperwork, and exclusion; it scaled that mission to become
Brazil's largest private financial institution and Mexico's third-largest financial institution
by customer count, all built on a self-owned tech stack (Clojure, Datomic, Kafka) rather than
legacy banking software [founders letter, building.nubank.com; engineering-behind-the-scenes,
building.nubank.com]. In 2025-2026 that mission entered a second act: CEO David Velez has said
"we are not adding AI to banking, we are rebuilding banking around AI," and the company is now
pushing a proprietary foundation model (NuFormer) and an "AI Private Banker" (15M+ monthly
active users) to extend the same financial-inclusion thesis into personalized, AI-driven advice
for people who never had access to a private banker before [Q1 2026 results announcement, May 14
2026, international.nubank.com.br].

## 3. Mission & product

- Mission: "fighting complexity to empower people every day, reinventing financial services,"
  founded 2013 in Brazil [founders-letter, building.nubank.com].
- Core products: no-fee credit card, digital checking/savings (NuConta), personal loans, secured
  cards, insurance brokerage, an e-commerce marketplace, and an MVNO; expanding in Mexico to
  include payroll accounts and higher deposit limits now that it holds a full banking license
  [PYMNTS, Jul 10 2026].
- Scale: 135M+ customers total; Brazil 115M+ (largest private financial institution in the
  country); Mexico 15M+ (largest digital bank, ~third-largest financial institution overall,
  reached break-even profitability in Q1 2026); Colombia approaching 5M [stocktitan Q1 2026
  results; PYMNTS, Jul 10 2026].
- Business model: interchange, interest income on credit/lending, deposits; efficiency ratio hit
  a record low 17.6% in Q1 2026 [stocktitan, Q1 2026 results, reported May 14 2026].
- Mexico is the clear next growth leg: $4.2B committed through 2030, $2.5B of that as near-term
  capex, following a meeting between CEO David Velez and President Claudia Sheinbaum; local GM
  Armando Herrera framed it as funding "technology, talent, operational capacity and employee
  development," citing that ~60% of Mexicans still lack formal digital financial access
  [mexicobusiness.news, Jul 7 2026].

## 4. Culture & voice

- Founding value: "think and act like owners, not renters"; ~80% of employees historically held
  equity, a deliberate break from local norms [founders-letter, building.nubank.com].
- Hiring philosophy stated in the founders' letter: recruit for curiosity and problem-solving
  "regardless of CV or pedigree," with philosophers and filmmakers alongside engineers
  [founders-letter, building.nubank.com].
- Product/marketing voice leans pragmatic, not hype-driven: Nubank Brazil CEO Livia Chanes on AI
  messaging, October 2025: "Customers don't care if it's AI-enabled or not... AI is an additional
  tool, not a customer value proposition. People just want to get their problem solved" [Fortune,
  Oct 21 2025]. Useful signal for how this company wants AI framed internally too: as leverage,
  not a marketing feature.
- Engineering culture is intentionally non-Java-shop: functional programming (Clojure), the
  Datomic immutable database (2.5B transactions/day), and Kafka were chosen specifically to
  "drastically reduce system complexity," paired with canary deployments and feature flags for
  safe, frequent releases [engineering-behind-the-scenes, building.nubank.com; Clojure's journey
  at Nubank, building.nubank.com]. Public FAQ explicitly says you do not need to already know
  Clojure to join; they hire for fundamentals and teach the stack [Clojure's journey at Nubank,
  building.nubank.com].

## 5. Recent news (last ~12 months)

- Jul 10, 2026: Nu Mexico received final CNBV authorization to operate as a full commercial bank
  (must formally begin operating within 30 days); prior SOFIPO-to-bank approval came in April
  2025 [PYMNTS, Jul 10 2026].
- Jul 7, 2026: Nubank formalized a $4.2B investment plan for Mexico through 2030 ($2.5B in near-
  term capex), following a meeting with President Sheinbaum [mexicobusiness.news, Jul 7 2026].
- May 14, 2026: Q1 2026 results: 135M+ total customers (+4M in the quarter), revenue past $5B for
  the first time, net income $871M (+41% YoY), Mexico reached break-even profitability, efficiency
  ratio at a record-low 17.6%. Same release: NuFormer (proprietary foundation model) live in
  production for Brazil/Mexico credit card and Brazil unsecured lending; AI Private Banker
  functionality serving 15M+ monthly active users; CEO quote: "We are not adding AI to banking, we
  are rebuilding banking around AI" [stocktitan, Q1 2026 results; international.nubank.com.br
  release, May 14 2026].
- Aug 18, 2025: Eric Young started as Chief Technology Officer [search result summary, unverified
  primary source not directly fetched; treat as directional].
- Oct 21, 2025: Nubank Brazil CEO Livia Chanes publicly pushed back on AI-as-marketing, arguing
  for AI as invisible infrastructure rather than a sales pitch [Fortune, Oct 21 2025].
- Feb 5, 2026: Bloomberg profiled CEO David Velez's plans to pursue expansion of Nu's model beyond
  Latin America [Bloomberg, Feb 5 2026].
- May 2026: Carl Rivera (ex-Shopify, 7+ years senior design/product leadership) joined as Chief
  Product Officer [search result summary; corroborate before quoting in an application].

Note: the CTO and CPO hire dates come from aggregated search summaries rather than a page I
directly fetched; treat them as directionally correct but verify before citing them as a firm
fact in an application.

## 6. Engineering & AI direction

- Stack: Clojure (functional, immutable-by-design) plus the Datomic database and Kafka for async
  messaging, chosen explicitly to reduce system complexity at scale; cloud-first infrastructure
  (no on-prem); Data Mesh model for ~7TB/day of data processed, segmented by domain for team
  autonomy [engineering-behind-the-scenes, building.nubank.com].
- AI platform history: acquired Hyperplane (July 2024) to build out foundation-model capability;
  built internal tooling (Model Catalog, Model View, a drag-and-drop Reporting tool) so "dozens of
  researchers and engineers" can coordinate on shared foundation-model work [Building Nubank,
  foundation-models-ai-nubank-transformation, Jun 11 2025].
- NuFormer: Nu's self-supervised proprietary foundation model, live in Nu's largest Brazil credit
  segment and expanding to personal loans, Mexico, and Colombia; delivers roughly 3x the
  performance of prior ML for optimizing credit limits, letting Nu extend credit to more customers
  without raising overall risk; the research team compressed its experimentation cycle "from
  months to a single day" by automating literature-to-production testing against internal data
  [international.nubank.com.br AI transformation strategy article; Q1 2026 results].
- Customer-facing AI in production with OpenAI (GPT-4o): a Call Center Copilot used by 45%+ of
  agents for next-reply suggestions, chat summarization, and step-by-step guidance; an AI
  assistant that resolves 50-55% of tier-1 chats/emails across 2M+ monthly conversations,
  resolving queries 2.3x faster; GPT-4o vision piloted for fraud-document review
  [openai.com/index/nubank, search-verified].
- Internal productivity/AI-adoption signal directly relevant to this role: Nubank reports 5,000+
  employees actively using internal AI prototyping tools monthly, and describes AI-assisted
  development shaving roughly a year off at least one backend architecture project, with some
  product features that used to take 3 to 4 months now shipping in a week or less [search-derived
  summary of Building Nubank/company material; corroborate specific figures before quoting
  verbatim in a cover letter].
- The open role itself (Lead AI Engineer / Lead IT Engineer, Productivity Systems) is explicitly
  about building this internal layer: agentic workflows with tool-calling, structured outputs,
  RAG and multi-agent orchestration; evaluation/guardrail frameworks for non-deterministic
  outputs; automation via n8n connecting Slack, Google Workspace, Jira and internal APIs; and
  governance for AI coding assistants (Claude Code, Cursor, Copilot are named as reference tools)
  [job-boards.greenhouse.io/nubank/jobs/7890393].

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago has already built, twice, exactly the kind of internal AI
system this role exists to build at Nubank scale. At Pragma AI he built "Pragma Brain," a RAG
"company brain" that answers questions and auto-generates reports from a company's own data, plus
production agents for quoting, reporting, onboarding, and collections. At Online Basics he
designed an LLM workflow with a multi-stage validation pipeline that cut content-creation time by
70% for a real, revenue-generating business. That is not a résumé line about AI, it is the same
job the JD describes: "turning manual, high-friction workflows into AI-assisted ones," with
evaluation and guardrails built in.

Supporting angles:
- Tool-calling and agent orchestration depth: the Plutus project (MCP control plane, LLM research
  agent) and the Kairos project (Claude Agent SDK plus a standalone MCP server exposing 18 tools
  to both an app and Claude Code) map directly onto the JD's asks for tool-calling, structured
  outputs, RAG, and multi-agent orchestration, and onto its explicit mention of Claude Code as a
  reference AI dev tool. Santiago uses Claude Code daily, which is a credible, honest overlap with
  a company that names Claude Code in its own job posting.
- Founder-operator credibility: 3x founder who has owned 0-to-1 product, client delivery, and team
  leadership (7-person team, $8M revenue) is a real match for a "Lead" title that blends hands-on
  engineering with governance and stakeholder work across business units, not just IC coding.
- LATAM fluency is a genuine, if secondary, asset: Nubank's entire growth story and next capital
  commitment ($4.2B through 2030) is concentrated in Mexico, and Santiago is Mexico City based
  and fluent in Spanish, which is useful context even though this specific req is US-based.

Honest concerns / watch-outs:
- Location mismatch is real and material. This role's offices are Durham, Miami, Palo Alto, or
  Washington DC (USA), hybrid 2-3 days per week in office [greenhouse job posting]. Santiago's own
  profile states he is not open to relocating for an on-site/hybrid role outside Mexico City. If
  he pursues this role, he needs to either be open to relocating to one of those four US cities
  (he is TN-visa eligible, which makes this legally feasible) or flag remote-from-Mexico as a real
  ask in the process; do not assume the role is remote-friendly.
- The listed Palo Alto base range in the posting ($11,712 to $17,568 annually) reads as clearly
  malformed for a "Lead" engineering role (likely a monthly figure or a posting error); verify
  actual comp before treating salary as a known quantity.
- No direct evidence Santiago has shipped in Clojure; the JD lists Clojure, Java, or Python as
  preferred languages and Nubank's core stack is Clojure-heavy, though the company's own
  engineering blog states Clojure is not a prerequisite to join. Worth a plain, confident line in
  an application: strong in Python/TypeScript, comfortable ramping into a new primary language,
  not a Clojure claim that cannot be defended in an interview.
- This is a large, publicly traded fintech (135M+ customers, heavy compliance surface for a
  regulated bank in three countries) rather than an early-stage startup; day-to-day pace,
  governance overhead, and internal review cycles are likely a different environment than the
  founder-led shops on Santiago's resume. Worth probing in interviews, not assuming.

## 8. Application-question angles

- Why this company: lead with the mission-to-AI throughline, not a generic "I admire Nubank"
  statement. Nubank spent over a decade fighting complexity to bring formal financial services to
  people who were excluded from them; the AI Private Banker and NuFormer work is the same mission
  applied to personalized financial advice, and the Productivity Systems role is the internal
  version of that same idea (removing friction for Nubank's own people). Santiago can honestly say
  he has built that pattern before, twice, at much smaller scale, and wants to build it at Nubank
  scale.
- Why you fit: do not checklist the stack. Anchor on one concrete proof point (Pragma Brain RAG
  system, or the Kairos MCP/Claude Agent SDK build) and walk through the same shape of problem the
  JD describes: turning a manual workflow into an AI-assisted one, with evaluation built in so it
  earns trust. Mention Claude Code fluency briefly and specifically (daily driver, not a buzzword)
  since the company itself names it as a tool of interest.
- Anything else: be direct about the location question rather than letting it surface as a
  surprise later. A short, honest line (TN-visa eligible, open to relocating to one of the listed
  US offices for the right role) is stronger than staying silent on it, given Santiago's stated
  Mexico City preference.

## 9. Sources

researched: 2026-07-13

- https://job-boards.greenhouse.io/nubank/jobs/7890393 (also mirrored at
  https://careers.base10.vc/companies/nubank/jobs/77255508-lead-it-engineer-productivity-systems)
  - full job description: responsibilities, required/preferred qualifications, US office
    locations, hybrid arrangement, listed Palo Alto base range. Note: the URL given in the task
    (jobs/78903) returned an error page when checked directly; jobs/7890393 is the live,
    matching posting found via search and is used as the source of record here.
- https://www.stocktitan.net/news/NU/nu-holdings-ltd-reports-first-quarter-2026-financial-xgqrbcto6oby.html
  - Q1 2026 results (reported May 14, 2026): 135M+ customers, $5B+ revenue, $871M net income,
    17.6% efficiency ratio, Mexico break-even.
- https://international.nubank.com.br/company/nu-holdings-ltd-reports-first-quarter-2026-financial-results/
  - Q1 2026 release: NuFormer in production, AI Private Banker 15M+ MAU, CEO quote on
    "rebuilding banking around AI."
- https://international.nubank.com.br/company/nubank-details-ai-transformation-strategy-built-on-data-foundation-models-and-democratized-financial-advice/
  - NuFormer detail: 3x performance uplift on credit limits, experimentation cycle compressed
    from months to a day, AI Private Banker framing and target population.
- https://www.pymnts.com/news/banking/2026/nubank-unit-secures-authorization-to-become-mexican-bank/
  - Jul 10, 2026: CNBV authorization for Nu Mexico to become a full bank, 15M+ Mexico customers,
    largest digital bank in Mexico, David Velez quote.
- https://mexicobusiness.news/finance/news/nubank-invest-us42-billion-mexico-through-2030
  - Jul 7, 2026: $4.2B Mexico investment through 2030, $2.5B capex over 4 years, meeting with
    President Sheinbaum, GM Armando Herrera quote.
- https://building.nubank.com/founders-letter/
  - Mission statement, "think and act like owners, not renters," hiring philosophy, equity
    culture.
- https://building.nubank.com/engineering-behind-the-scenes-innovation-nubank/
  - Engineering stack and practices: Clojure, Datomic, Kafka, canary deployments, Data Mesh,
    ~7TB/day.
- https://building.nubank.com/clojures-journey-at-nubank-a-look-into-the-future/
  - Clojure culture, "you do not need to already know Clojure to join" framing.
- https://building.nubank.com/foundation-models-ai-nubank-transformation/
  - Jun 11, 2025: Hyperplane acquisition (Jul 2024), internal foundation-model tooling (Model
    Catalog, Model View, Reporting tool).
- https://openai.com/index/nubank/
  - OpenAI/Nubank case study: Call Center Copilot (GPT-4o), AI assistant tier-1 resolution rates,
    GPT-4o vision fraud pilot.
- https://fortune.com/2025/10/21/nubank-ceo-livia-chanes-ai-selling/
  - Oct 21, 2025: Nubank Brazil CEO Livia Chanes on AI-as-infrastructure-not-marketing voice.

Lower-confidence items (surfaced only via aggregated search summaries, not a directly fetched
primary page; flagged in-text above and should be re-verified before being stated as fact in an
application): Eric Young's CTO start date (Aug 18, 2025) and Carl Rivera's CPO start (May 2026);
the "5,000+ employees using internal AI tools monthly" and "backend project accelerated by nearly
a year" figures.
