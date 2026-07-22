# Mercury (mercury.com)

Draft dossier for Santiago Coronado, prepared for the "Senior Software Engineer, AI Engineering / Mercury Command" role (job id 641). Review before use.

Note on disambiguation: this is Mercury Technologies, Inc. (mercury.com), the fintech banking platform for startups, founded 2017, HQ San Francisco. Not to be confused with Mercury Systems (defense electronics), Mercury Insurance, or Mercury Financial.

## 1. Snapshot

Mercury is a fintech that provides banking, payments, and financial-operations software for startups and growing businesses (banking services provided through partner banks Choice Financial Group and Column N.A., both FDIC members, pending Mercury's own bank charter). Founded 2017 by CEO Immad Akhund, HQ San Francisco with a remote-first culture (also offices in New York and Portland). Over 300,000 business and personal customers, roughly 1,000+ employees. Raised a $200M Series D in May 2026 at a $5.2B valuation (TCV-led), following a $300M Series C in March 2025 at $3.5B (Sequoia-led); ~$650M annualized revenue and four consecutive years of GAAP/EBITDA profitability as of the Series D. In April 2026 Mercury won conditional OCC approval to establish its own national bank, Mercury Bank, N.A.

## 2. Core narrative

Mercury is trying to become the AI-native operating layer for how a company handles money, not just a bank account. It's doing this on strong financial footing (profitable, growing, freshly chartering its own bank) and is making a public, company-wide bet that AI agents (used by both customers and Mercury's own employees) become the primary interface to banking. The AI Engineering / Mercury Command role sits exactly at that bet: building the internal platform (MCP servers, LLM gateway, shared knowledge layer, eval harnesses) that lets Mercury's own engineers and non-engineers safely build and ship agentic features company-wide, the same infrastructure class that powers the customer-facing Mercury Command assistant launched in June 2026.

## 3. Mission & product

- Core product: business banking accounts, corporate credit cards (since 2022), bill pay, invoicing, expense management, treasury/yield products, and (from 2025) a consumer banking product. Customers span tech startups, ecommerce, agencies, VC funds, crypto, accounting firms, and life sciences; notable named customers include Linear, Phantom, and ElevenLabs. (mercury.com/blog/series-c-announcement, TechCrunch Series C article)
- Business model: interchange, banking/deposit economics, and software/subscription revenue from the financial-ops tooling layered on top of the account.
- June 2026: launched Mercury Command, a conversational AI assistant built into Mercury accounts that turns natural language into completed financial work (payments, transfers, card issuance/limits, invoicing, GL coding, department/approval administration, spend insights). It operates strictly inside the customer's existing permissions, stages every action for explicit human approval before executing, and logs everything for a traceable record. Interfaces span the web app, API, MCP, and CLI. (mercury.com/command, mercury.com/blog/introducing-mercury-command, dated 2026-06-16)
- Also in 2026: a read-only Mercury MCP server that lets customers connect their Mercury account to external AI tools like Claude and ChatGPT, and "Mercury Insights," an AI financial-analytics product. (GrowwStacks, PYMNTS coverage)
- April 2026: conditional OCC approval to charter Mercury Bank, N.A., which will let Mercury offer Zelle integration, expanded lending, and direct control of payments infrastructure instead of routing through partner banks. Still needs FDIC/Federal Reserve sign-off. (businesswire.com/news/home/20260427949683, americanbanker.com)

## 4. Culture & voice

- Careers page states six values: think actively with curiosity, be helpful as a team, act with humility, appreciate quality, focus on outcomes, build relentlessly. Reports "96% of employees say Mercury is a great place to work." Remote-first, with optional in-office in SF, NY, and Portland; most engineering roles are listed as fully remote. (mercury.com/careers)
- Engineering identity is distinctive: Mercury's production backend is largely Haskell (with an Elm frontend history), a deliberate bet on strong typing for financial infrastructure; the eng blog runs Haskell-specific technical posts (e.g. "Escalating Esqueleto," on converting SQL to Haskell/Esqueleto syntax). (mercury.com/blog/topics/engineering-blog, dev.to "A Couple Million Lines of Haskell: Production Engineering at Mercury")
- Public-facing voice from leadership is candid about AI upending the startup playbook: CEO Immad Akhund on the Series D: "AI is collapsing the friction between an idea and a company faster than anything I have seen in my career," and cites a 2.5x jump in Mercury account applications in Q1 2026 versus Q1 2025 that he attributes to AI-enabled founders. (fintech.global Series D writeup, PYMNTS "Mercury CEO Says AI Is Breaking the Old Startup Model," 2026-06-09)
- Internally, Mercury has been building its own "second brain": an employee (Product Lead Ryan Wiggins) built a Claude-powered internal knowledge system indexing roughly 5 million words of institutional knowledge (strategy docs, specs, meeting notes) using a local knowledge base, Claude hooks for context injection, and connections to internal tools like Metabase and Linear; the write-up says Mercury's AI data-analyst tooling now handles 80 to 90 percent of routine internal data queries. This is the kind of scattered, high-agency AI usage the AI Engineering role is explicitly tasked with turning into shared infrastructure. (GrowwStacks, "How Mercury Built AI Banking Agents and a Claude-Powered Second Brain," 2026-04-22)
- Retained 92% of customers through the March 2023 SVB collapse, a moment the company still cites as proof of trust with its startup customer base. (mercury.com/about)

## 5. Recent news (last ~12 months)

- 2025-03-26: $300M Series C led by Sequoia Capital (Sequoia's first Mercury investment), valuation doubles to $3.5B; participation from Coatue, CRV, a16z, Spark Capital, Marathon. 2024 revenue reported at $500M, 10 consecutive profitable quarters, 200,000+ customers, 40% YoY customer growth. (techcrunch.com/2025/03/26/..., mercury.com/blog/series-c-announcement)
- 2026-04-22: Public detail on Mercury's internal AI tooling (Claude-powered knowledge system, AI banking agents via MCP) surfaces via Product Lead Ryan Wiggins. (GrowwStacks)
- 2026-04-27: OCC grants conditional approval for Mercury to charter its own national bank, Mercury Bank, N.A. (businesswire.com/news/home/20260427949683, fintechfutures.com, americanbanker.com)
- 2026-05-20/21: $200M Series D led by TCV at a $5.2B valuation (up 49% in 14 months), with a16z, Coatue, CRV, Sapphire Ventures, Sequoia, Spark Capital participating. $650M annualized revenue, four straight years of GAAP/EBITDA profitability, 300,000+ customers (one in three US startups), 73%+ of new customers now from outside AI/tech. (cnbc.com/2026/05/20/..., fintech.global/2026/05/21/...)
- 2026-06-09: CEO Immad Akhund public comments framing AI as collapsing the cost/time of starting a company, citing 2.5x YoY growth in Mercury applications in Q1 2026. (pymnts.com, "Mercury CEO Says AI Is Breaking the Old Startup Model")
- 2026-06-16: Mercury launches Command (customer-facing conversational AI assistant for financial work) company-wide, plus a read-only Mercury MCP server for connecting accounts to external AI tools like Claude/ChatGPT. (mercury.com/blog/introducing-mercury-command, businesswire.com/news/home/20260616596362, pymnts.com "Mercury Deploys Conversational AI Interface Across FinTech Platform")

## 6. Engineering & AI direction

- Core backend: Haskell (functional, strongly typed), historically paired with an Elm frontend; Mercury is known in the engineering community specifically for running a large production Haskell codebase for financial infrastructure and for training engineers into Haskell rather than requiring prior experience. (dev.to "A Couple Million Lines of Haskell," mercury.com/blog/topics/engineering-blog)
- The open Senior SWE, AI Engineering role (job 641) sits on the team already building Mercury's internal AI platform and enablement layer, work is described as extending and hardening: MCP servers connecting internal systems/data for agents and engineers, an LLM gateway (routing, rate limiting, cost attribution, observability), shared prompt libraries and guardrails/policy-as-code, structured "agent-consumable" internal knowledge/context artifacts, and sandbox/eval environments so both engineers and non-engineers (PM, ops, finance) can prototype AI workflows safely. Ideal candidate profile: 5+ years backend in production systems, fluency across languages/platform engineering, hands-on production experience with RAG pipelines/agents/eval frameworks, and literacy in the real tradeoffs (cost, observability, latency, safety) of AI deployments. (job-boards.greenhouse.io/mercury/jobs/5850044004)
- This mirrors what's already shipped externally: Mercury Command (customer-facing agent with staged, human-approved actions and full audit trail) and the read-only customer MCP server, plus the internal Claude-powered "second brain" and MCP-based internal AI banking agents described by Product Lead Ryan Wiggins. (mercury.com/command, GrowwStacks)
- Salary band listed for this role: US $166,600 to $218,700 base (CAD 157,400 to 206,650 for Canadian employees), plus equity and benefits. (job-boards.greenhouse.io/mercury/jobs/5850044004)

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago has already built, on his own initiative, almost the exact shape of infrastructure this team owns, an MCP control plane (Plutus), a function-calling/tool-use agent (Hermes), and a production RAG "company brain" (Pragma Brain) that ingests a company's internal data to answer questions and generate reports. Mercury's own team is doing this same thing right now (internal MCP servers, an LLM gateway, an agent-consumable knowledge layer, a Claude-powered "second brain") and is hiring specifically to harden and scale it. That is a rare, close match between what he has shipped solo and what this team's actual backlog looks like, not a generic "I love AI" pitch.

Supporting angles:
- Founder background maps to Mercury's own customer base and current growth story: he has been the exact kind of ambitious, resource-constrained founder (Online Basics to $8M revenue on LLM-powered workflows, Eugenia.ai built and exited) that Mercury serves and that Akhund describes as the newly AI-accelerated wave of startup formation. He can speak to the founder's-eye view of "banking as the operating layer," not just the engineering brief.
- Eval/guardrail/production-tradeoff literacy: the JD explicitly wants someone who understands cost modeling, observability, latency, and safety, not just "the exciting parts." Santiago's RAG and agent projects (Plutus, Pragma Brain) were built end to end (ingestion, retrieval, backtesting/evaluation harnesses in Plutus), giving him concrete stories about tradeoffs, not just usage.
- Daily Claude Code user, comfortable being a "high-agency, self-directed" builder without tightly defined scope, which is explicitly called out as the ideal-candidate trait; his solo-founder track record (0-to-1, ambiguous scope, ships alone) backs that up directly.

Honest concerns and watch-outs:
- Mercury's core production backend is Haskell, a language not in Santiago's resume (Python, TypeScript/JavaScript, Java, Swift). The AI Engineering role's stack, per the JD, sounds Python/LLM-infra-centric (gateway, MCP, sandbox tooling) rather than core-banking Haskell, but this should be clarified in interviews since "fluent across programming languages" is listed as a requirement and Mercury's engineering culture leans on training people into Haskell.
- Work authorization: the job posting does not state a citizenship-only restriction or confirm visa/TN sponsorship either way (no dealbreaker language found), but Mercury's sponsorship posture for a TN-eligible, non-US-citizen candidate is not confirmed by any source found in this research and should be raised early in the process.
- Location: role is SF/NYC/Portland or remote in US/Canada only, no Mexico-based remote option; Santiago would need to confirm his TN plan and physical work location before applying.

## 8. Application-question angles

- Why this company: lead with the infrastructure match, not "Mercury seems cool." Frame it as: Mercury is publicly building the same category of system (internal MCP servers, an LLM gateway, an agent-consumable knowledge layer) that he has already shipped solo three times over (Plutus, Hermes, Pragma Brain), and Mercury is doing it at a moment (profitable, freshly chartering its own bank, customer base surging on AI-native founders) where that infrastructure has real leverage across a real company, not a hypothetical.
- Why you fit: anchor on "I've already built the job." Don't recite all three projects exhaustively; pick the one or two that map tightest to the JD's actual bullets (MCP servers plus a RAG/agent-consumable knowledge layer is the strongest overlap) and go deep on one concrete tradeoff he had to make (cost, latency, eval, or guardrails) rather than listing features.
- Anything else: use his founder history as the differentiator, not a caveat. He is not just an engineer who has used AI infra, he has been the kind of resource-constrained founder-builder Mercury's own growth numbers say are flooding into the platform right now, which gives him an unusually direct read on why this internal-enablement work matters to the business, not just the codebase.

## 9. Sources

researched: 2026-07-14

- https://job-boards.greenhouse.io/mercury/jobs/5850044004 (target job posting: role scope, ideal-candidate bullets, salary band)
- https://mercury.com/command (Mercury Command product page: features, permission/approval model, MCP/API/CLI interfaces)
- https://mercury.com/blog/introducing-mercury-command (Command launch post, 2026-06-16, architecture/security framing)
- https://mercury.com/about (mission, values, team size, customer verticals, SVB retention stat)
- https://mercury.com/careers (values, remote-first policy, office locations)
- https://mercury.com/blog/topics/engineering-blog (eng blog themes, Haskell focus)
- https://dev.to/onsen/a-couple-million-lines-of-haskell-production-engineering-at-mercury-4jd6 ("A Couple Million Lines of Haskell," Mercury's backend language choice)
- https://techcrunch.com/2025/03/26/fintech-mercury-lands-300m-in-sequoia-led-series-c-doubles-valuation-to-3-5b/ (Series C details, 2024 revenue, founding date, headcount, customer names)
- https://mercury.com/blog/series-c-announcement (Series C announcement, primary source)
- https://www.cnbc.com/2026/05/20/fintech-mercury-valuation-fundraise-bank-charter.html (Series D valuation headline figures)
- https://fintech.global/2026/05/21/mercury-raises-200m-series-d-as-ai-fuels-startup-surge/ (Series D detail: investors, revenue, profitability, customer mix, AI strategy quote)
- https://www.businesswire.com/news/home/20260427949683/en/Mercury-Receives-OCC-Conditional-Approval-to-Establish-Mercury-Bank-N.A. (OCC conditional bank charter approval)
- https://www.pymnts.com/news/artificial-intelligence/2026/mercury-ceo-says-ai-is-breaking-the-old-startup-model/ (CEO Immad Akhund quotes on AI and startup formation, 2026-06-09)
- https://growwstacks.com/blog/how-mercury-built-ai-banking-agents (internal Claude-powered knowledge system, MCP banking agents, 2026-04-22)
- https://www.pymnts.com/news/artificial-intelligence/2026/mercury-deploys-conversational-ai-interface-across-fintech-platform/ (Command launch coverage)
- https://www.americanbanker.com/news/mercury-raises-200-million-after-occ-bank-charter-approval (Series D plus charter context)
