# Thomson Reuters

Researched for: Lead Software Engineer AI (Staff Engineer), Ciudad de Mexico (job id 8036).
researched: 2026-07-14

## Snapshot
Thomson Reuters (NYSE/TSX: TRI) is a public, ~27,100-employee content and technology company
(Canada-headquartered) serving legal, tax, accounting, audit, and news professionals. It runs
Westlaw, Practical Law, CoCounsel, Cloud Audit Suite, and Reuters News. Not a startup: it trades
publicly, reported Q1 2026 revenue of $2.09B (up from $1.90B in Q1 2025, +8%), and has committed
up to $10B toward AI investment on top of roughly $2.5B already spent on AI-related acquisitions.
[thomsonreuters.com AI page](https://www.thomsonreuters.com/en/artificial-intelligence),
[Forbes](https://www.forbes.com/sites/ceo/2025/10/13/how-thomson-reuters-became-a-gen-ai-powerhouse/),
[Q1 2026 results](https://ir.thomsonreuters.com/news-releases/news-release-details/thomson-reuters-reports-first-quarter-2026-results).
Has an office in Mexico City (Paseo de la Reforma 26).
[TR Mexico City location page](https://www.thomsonreuters.com/en/locations/location-detail.html/mexico-city).

## Core narrative
Thomson Reuters is mid-transformation from "a database business into an AI business": it is
rebuilding its flagship legal AI product, CoCounsel Legal, from the ground up on Anthropic's
Claude Agent SDK, and this week (July 13-14, 2026) it publicly tied that shift to headcount,
cutting roughly 500 engineering roles while committing to hire 250+ net-new, mostly senior,
"AI-native" engineering roles over the next two years.
[LawNext, June 2026](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html),
[TechFocus24, July 14 2026](https://techfocus24.com/thomson-reuters-to-cut-engineering-roles-as-ai-reshapes-workforce/),
[Investing.com/Reuters wire, July 13 2026](https://www.investing.com/news/stock-market-news/thomson-reuters-to-cut-small-number-of-engineering-jobs-4789191).
This exact "Lead Software Engineer AI (Staff Engineer)" req, whose description explicitly says
the role will "help drive our shift to an engineering-led, AI-native organization," is one of
those new senior AI-native seats, not a legacy backfill.

## Mission & product
- **CoCounsel Legal**: agentic legal AI assistant, originally built from the 2023 Casetext
  acquisition ($650M). Next-generation version (early access opened June 22, 2026, U.S. general
  availability planned August 2026) is rebuilt on Anthropic's Claude Agent SDK as a unified
  agentic system that plans, selects tools, retrieves authoritative content from Westlaw and
  Practical Law, and adapts mid-workflow. Integrates with Microsoft 365, iManage, NetDocuments,
  SharePoint, Icertis, DeepJudge, Supio, Smokeball, and exposes an MCP (Model Context Protocol)
  integration so lawyers can reach CoCounsel from inside Claude itself.
  [LawNext](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html),
  [legal.thomsonreuters.com CoCounsel Legal](https://legal.thomsonreuters.com/en/products/cocounsel-legal).
- **CoCounsel for tax, audit, accounting**: agentic assistant for that vertical (client review,
  memo drafting, compliance checks), launched June 2025, accelerated by the October 2024
  acquisition of Materia (agentic AI specialist for tax, audit, accounting).
  [PRNewswire, TR acquires Materia](https://www.prnewswire.com/news-releases/thomson-reuters-acquires-materia--a-specialist-in-agentic-ai-for-the-tax-audit-and-accounting-profession-302282041.html),
  [insideAI News](https://insideainews.com/2025/06/02/thomson-reuters-launches-agentic-ai-for-tax-audit-and-accounting/).
- **Cloud Audit Suite** (named in this job's own description): Engagement Manager + Guided
  Assurance, audit workflow products this Lead/Staff role's backend and AI orchestration work
  reportedly touches.
- Business model: enterprise/professional subscriptions (legal, tax, audit customers), not
  consumer. Content moat is proprietary (Westlaw, Practical Law, 4,500+ subject-matter experts)
  which TR positions as the differentiator versus generic web-trained AI.
  [thomsonreuters.com AI page](https://www.thomsonreuters.com/en/artificial-intelligence).

## Stage/scale
Large public incumbent (not venture-backed), ~27,100 employees globally, ~9,400 in the
Operations & Technology unit. AI investment is being funded from operating cash flow and balance
sheet, not a funding round: ~$2.5B spent on AI-related M&A to date (Casetext, ThoughtTrace, Safe
Sign Technologies, Materia) with up to $10B more earmarked. 17,000+ employees use TR's internal
"Open Arena" AI experimentation platform. [Forbes](https://www.forbes.com/sites/ceo/2025/10/13/how-thomson-reuters-became-a-gen-ai-powerhouse/).

## Tech stack
- Next-gen CoCounsel Legal: Anthropic Claude Agent SDK, agentic (not fixed-workflow) architecture,
  MCP integration with Claude. [LawNext](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html).
  AI/cloud partners named publicly: Google, Microsoft, OpenAI, AWS, Anthropic.
- Thomson Reuters Labs (research/ML engineering org) publishes on Medium: domain-specific
  language models, multi-agent systems, information retrieval, evaluation, legal reasoning, LLM
  training, document understanding; also engineering-productivity posts (e.g. "Using AI Tools as
  a Principal Engineer"). [TR Labs Medium](https://medium.com/tr-labs-ml-engineering-blog).
- This job's own description: "own core backend and AI orchestration systems that turn frontier
  models into reliable, production-grade workflows at scale," under an explicit "engineering-led,
  AI-native" mandate. (source: job posting, id 8036, Adzuna listing).
- No public confirmation found of the specific backend language/framework for this team; do not
  assert one.

## Recent news (last ~12 months)
- **Oct 2024**: Acquired Materia, agentic AI specialist for tax/audit/accounting.
  [PRNewswire](https://www.prnewswire.com/news-releases/thomson-reuters-acquires-materia--a-specialist-in-agentic-ai-for-the-tax-audit-and-accounting-profession-302282041.html)
- **June 2025**: Launched CoCounsel agentic AI for tax, audit, accounting professionals.
  [insideAI News](https://insideainews.com/2025/06/02/thomson-reuters-launches-agentic-ai-for-tax-audit-and-accounting/)
- **Jan 2026**: Expanded CoCounsel Legal to the UK.
  [TR press release](https://www.thomsonreuters.com/en/press-releases/2026/january/thomson-reuters-expands-cocounsel-legal-to-uk-continuing-its-transformation-of-legal-work-with-agentic-ai-innovation)
- **Q1 2026 (reported)**: Revenue $2.09B, +8% organic growth, CEO cites AI-enabled products as
  driving legal segment growth. [Investing.com transcript](https://ca.investing.com/news/stock-market-news/earnings-call-transcript-thomson-reuters-q1-2026-shows-8-revenue-growth-93CH-4609874)
- **June 22, 2026**: Opened early access to next-gen CoCounsel Legal, rebuilt on Claude Agent SDK;
  full U.S. GA planned August 2026. [LawNext](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html)
- **July 13-14, 2026**: Announced cutting up to ~500 engineering roles (5.2% of the ~9,400-person
  Operations & Technology unit) while committing to hire 250+ net-new engineering roles over two
  years, "the large majority senior and AI-native." Framed explicitly as a shift from "database
  business" to "AI business." [TechFocus24](https://techfocus24.com/thomson-reuters-to-cut-engineering-roles-as-ai-reshapes-workforce/),
  [Investing.com/Reuters](https://www.investing.com/news/stock-market-news/thomson-reuters-to-cut-small-number-of-engineering-jobs-4789191)
- Q2 2026 earnings scheduled for release August 5, 2026 (not yet reported as of this research).
  [StockTitan](https://www.stocktitan.net/news/TRI/thomson-reuters-second-quarter-2026-earnings-announcement-and-e4sk98i2hal5.html)

## Culture & voice
- Public tone is confident and "steward" framed, not disruptor framed: "For 30 years, we have
  been at the forefront of technological advancement," paired with "professional-grade AI,"
  "fiduciary-grade AI" (CTO Joel Hron), and explicit human-oversight and data-privacy commitments
  (contractually blocks partners from training on customer data).
  [thomsonreuters.com AI page](https://www.thomsonreuters.com/en/artificial-intelligence),
  [LawNext](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html).
- Employee sentiment (Glassdoor, Software Engineer track): 3.9/5 overall, 4.3 work-life balance,
  4.0 culture and values, but recurring complaints about frequent reorgs ("every six months"),
  below-market pay, and being evaluated on AI-tool usage. Take as one data point, not verified
  independently. [Glassdoor Software Engineer reviews](https://www.glassdoor.com/Reviews/Thomson-Reuters-Software-Engineer-Reviews-EI_IE100303.0,15_KO16,33.htm)
- Mexico City employee reviews (Glassdoor): 76% would recommend to a friend; 4/5 work-life
  balance, 4.2/5 diversity and inclusion, 4/5 culture and values (self-reported, unverified beyond
  the review aggregator itself). [Glassdoor Mexico City reviews](https://www.glassdoor.com/Reviews/Thomson-Reuters-Mexico-City-Reviews-EI_IE100303.0,15_IL.16,27_IM1176.htm)

## Engineering & AI direction
- Explicit strategic pivot: "AI-native" is the company's own term for the type of engineer it is
  now hiring, used in both the layoff/hiring announcement and in this job's own description
  ("engineering-led, AI-native organization"). [TechFocus24](https://techfocus24.com/thomson-reuters-to-cut-engineering-roles-as-ai-reshapes-workforce/)
- Flagship proof point: CoCounsel Legal was rebuilt "from the ground up" on Anthropic's Claude
  Agent SDK as a true multi-step agent (plans, selects tools, retrieves grounded content, adapts
  mid-workflow) rather than a set of fixed skills/workflows, with MCP as a first-class integration
  surface. [LawNext](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html)
- Thomson Reuters Labs (research arm) publishes applied ML/agent engineering work: domain-specific
  LLMs, multi-agent systems, evaluation methods, legal reasoning, and practitioner posts on using
  AI coding tools day to day. [TR Labs Medium](https://medium.com/tr-labs-ml-engineering-blog)
- Company-wide internal AI experimentation platform ("Open Arena") used by 17,000+ employees,
  suggesting AI-tool fluency is expected broadly, not just on AI teams.
  [Forbes](https://www.forbes.com/sites/ceo/2025/10/13/how-thomson-reuters-became-a-gen-ai-powerhouse/)

## Why-fit angles for Santiago
**Best hook to lead with:** Santiago already builds on the exact stack TR just bet its flagship
product on. His Kairos project integrates Claude on two surfaces from one codebase (an in-app
agent via the Claude Agent SDK and a standalone MCP server exposing the same tools), which is
functionally the same architecture pattern TR just used to rebuild CoCounsel Legal (Claude Agent
SDK plus MCP). That is a rare, concrete, verifiable overlap, not a generic "I use AI" claim.

Other angles:
- TR frames this specific req as one of the new "AI-native," "engineering-led" senior hires it
  just publicly committed to (250+ over two years) as it cuts legacy roles. Santiago's founder
  background (three companies, 0-to-1 product ownership, shipping production LLM workflows
  end-to-end) matches the "own core backend and AI orchestration systems" scope in this job's own
  description, not a narrow feature-team mandate.
- He has direct experience turning "frontier models into reliable, production-grade workflows":
  the Online Basics LLM content pipeline (Anthropic and OpenAI APIs, multi-stage validation,
  100+ listings/month) and Pragma Brain (RAG over a company's internal data) are both examples of
  exactly that pattern, just in a different vertical than legal/tax.
- CDMX office and role location match his stated preference (hybrid Mexico City) without a
  relocation ask.

Honest concerns / watch-outs:
- This role sits inside a division (Cloud Audit Suite: audit/accounting workflow) rather than the
  headline CoCounsel Legal team; the Claude Agent SDK connection is a company-wide direction, not
  confirmed for this specific team's stack. Do not overclaim it as "the same codebase."
  (No public source ties Cloud Audit Suite specifically to Claude Agent SDK.)
- Public company with recent, large-scale, AI-driven engineering layoffs (up to 500 roles cut the
  same week as this research) alongside net new hiring; worth a candid gut-check on stability and
  a good question to ask in interviews rather than a hidden risk.
- Glassdoor engineering reviews flag frequent reorgs and below-market pay as recurring themes;
  unverified beyond the aggregator, but worth probing on comp and team stability in interviews.
- No public evidence found (yet) of the team's day-to-day backend language/framework; do not
  assume Python/Node without confirming in the interview process.

## Application-question angles
- **Why this company**: Lead with the Claude Agent SDK/MCP overlap between Kairos and the
  next-gen CoCounsel Legal rebuild, framed as genuine excitement about joining a company that just
  publicly restructured its engineering org around exactly the AI-native pattern he already builds
  in his own projects, not a generic "I like AI" pitch.
- **Why you fit**: Anchor on "own core backend and AI orchestration systems that turn frontier
  models into reliable, production-grade workflows at scale" (the job's own language) and map it
  to concrete shipped work: the Online Basics LLM pipeline and Pragma Brain RAG system, both
  production systems he owned end to end as a founder, not a component within a larger team.
- **Anything else**: Mention TN-visa eligibility and CDMX base as a practical fit for the office
  location, and (if space allows) that he is applying into a moment where TR itself has called out
  wanting senior, AI-native engineers, a bar he can speak to directly with recent shipped agent
  and RAG work.

## Sources
- researched: 2026-07-14
- [Thomson Reuters AI page](https://www.thomsonreuters.com/en/artificial-intelligence) - AI mission, principles, $200M+/yr investment claim, Open Arena
- [Forbes, "How Thomson Reuters Became A Gen AI Powerhouse" (Oct 2025)](https://www.forbes.com/sites/ceo/2025/10/13/how-thomson-reuters-became-a-gen-ai-powerhouse/) - AI investment scale, acquisitions, leadership, headcount
- [LawNext, next-gen CoCounsel Legal early access (June 2026)](https://www.lawnext.com/2026/06/thomson-reuters-opens-early-access-to-the-next-generation-of-cocounsel-legal-saying-beta-users-fing-loved-the-product.html) - Claude Agent SDK rebuild, architecture, leadership names, dates
- [legal.thomsonreuters.com, CoCounsel Legal product page](https://legal.thomsonreuters.com/en/products/cocounsel-legal) - product description
- [PRNewswire, Thomson Reuters acquires Materia (Oct 2024)](https://www.prnewswire.com/news-releases/thomson-reuters-acquires-materia--a-specialist-in-agentic-ai-for-the-tax-audit-and-accounting-profession-302282041.html) - Materia acquisition
- [insideAI News, CoCounsel for tax/audit/accounting launch (June 2025)](https://insideainews.com/2025/06/02/thomson-reuters-launches-agentic-ai-for-tax-audit-and-accounting/) - product launch
- [Thomson Reuters press release, CoCounsel Legal UK expansion (Jan 2026)](https://www.thomsonreuters.com/en/press-releases/2026/january/thomson-reuters-expands-cocounsel-legal-to-uk-continuing-its-transformation-of-legal-work-with-agentic-ai-innovation)
- [Investing.com, Q1 2026 earnings call transcript](https://ca.investing.com/news/stock-market-news/earnings-call-transcript-thomson-reuters-q1-2026-shows-8-revenue-growth-93CH-4609874) - Q1 revenue, growth
- [Thomson Reuters IR, Q1 2026 results release](https://ir.thomsonreuters.com/news-releases/news-release-details/thomson-reuters-reports-first-quarter-2026-results)
- [StockTitan, Q2 2026 earnings date announcement](https://www.stocktitan.net/news/TRI/thomson-reuters-second-quarter-2026-earnings-announcement-and-e4sk98i2hal5.html)
- [TechFocus24, engineering cuts and AI-native hiring (July 14, 2026)](https://techfocus24.com/thomson-reuters-to-cut-engineering-roles-as-ai-reshapes-workforce/) - layoffs and hiring numbers, quotes
- [Investing.com/Reuters wire, engineering job cuts (July 13, 2026)](https://www.investing.com/news/stock-market-news/thomson-reuters-to-cut-small-number-of-engineering-jobs-4789191) - corroborating numbers and quotes
- [Thomson Reuters Labs Medium blog](https://medium.com/tr-labs-ml-engineering-blog) - engineering/ML blog themes
- [Thomson Reuters location page, Mexico City](https://www.thomsonreuters.com/en/locations/location-detail.html/mexico-city) - CDMX office address
- [Glassdoor, Thomson Reuters Software Engineer reviews](https://www.glassdoor.com/Reviews/Thomson-Reuters-Software-Engineer-Reviews-EI_IE100303.0,15_KO16,33.htm) - engineering culture sentiment (unverified beyond aggregator)
- [Glassdoor, Thomson Reuters Mexico City reviews](https://www.glassdoor.com/Reviews/Thomson-Reuters-Mexico-City-Reviews-EI_IE100303.0,15_IL.16,27_IM1176.htm) - CDMX employee sentiment (unverified beyond aggregator)
- Job posting id 8036 (Adzuna listing, "Lead Software Engineer AI (Staff Engineer)", CDMX) - role description quoted above

---
Draft dossier for Santiago to review. All facts above trace to the cited URLs; anything not
sourced is explicitly flagged as unverified.
