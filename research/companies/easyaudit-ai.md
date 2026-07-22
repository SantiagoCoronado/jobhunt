# EasyAudit AI, Inc.

*Draft dossier for Santiago's review. All claims are sourced below; items without a solid public
source are explicitly marked "unverified." This is a very small, early-stage startup, so public
information is thin and sometimes conflicting (see notes on HQ and funding).*

## 1. Snapshot

EasyAudit is an early-stage, AI-native compliance automation platform (agentic SaaS) that helps
lean startups and SMBs achieve and maintain SOC 2, ISO 27001, ISO 42001, HIPAA, GDPR, and other
security/AI-governance certifications, replacing manual consultants and legacy GRC dashboards with
AI agents that write policies, map controls, and collect evidence. Founded in 2023 to 2024 by
Christian Khoury (CEO, ex-Deloitte risk and compliance) and Aidan Slack-Watkins. Very small team,
roughly 4 to 7 people across public sources from 2026. HQ is reported inconsistently as Toronto,
Canada or Miami, FL, US (unverified which is current). Fully remote hiring, worldwide. Funding is
small and not clearly disclosed: aggregator data shows one funding round involving RevTech Labs
(a Charlotte, NC accelerator/fund), with amounts conflicting across sources (as low as ~$20K per
PitchBook-derived data, versus a ~$200K pre-seed reported for around October 2025 in company
LinkedIn content); treat the exact figure as unverified. [Sources: 1, 2, 3, 4, 5]

## 2. Core narrative

EasyAudit's pitch is "compliance without the compliance tax": a team of specialized AI agents
(not a checklist UI) that does the actual work of writing policies, mapping controls, and
collecting evidence, so a 3-person SaaS startup can pass a clean SOC 2 audit in about three weeks
with under five hours of internal effort, instead of hiring a compliance officer or consultant.
The founder-market fit story is direct: an ex-Deloitte compliance analyst who saw founders
"duct-taping Google Docs, overpriced platforms, and part-time consultants" to fake being
audit-ready, and built the AI-agent alternative. They frame the market as moving from "Era 2"
dashboard-and-checklist compliance tools (Vanta, Drata, Secureframe) to "Era 3," where compliance
becomes an invisible, continuously-running background function. [Sources: 1, 3, 6, 7, 8]

## 3. Mission & product

- **What they build**: an agentic compliance platform. AI agents generate tailored security
  policies and a risk register from a company's actual tech stack, map existing docs/evidence to
  required controls, connect to systems (AWS, GCP, Azure, GitHub, Notion, Okta, Slack, Microsoft
  365) to auto-collect evidence, and prepare audit-ready documentation; a partnered CPA firm signs
  off on the resulting SOC 2 report. Frameworks covered: SOC 2, ISO 27001, ISO 42001 (AI
  management systems), HIPAA, GDPR, CCPA, NIST CSF, CMMC. [Sources: 1, 6, 9]
- **Business model**: B2B SaaS, flat/transparent pricing positioned explicitly against Vanta,
  Drata, Sprinto, and Secureframe ("no hidden fees or upsells"). [Source: 1]
- **Customers**: lean, early-stage SaaS companies and founders (often pre-compliance-hire) who
  need a certification to unblock enterprise sales cycles. Documented customers: Alignd (3-person
  SaaS startup, Burlington VT, hit SOC 2 Type I in 3 weeks with zero exceptions) and TheStage AI
  (SOC 2 achieved, per company LinkedIn posts). [Sources: 6, 10]
- **Differentiation claim**: EasyAudit publishes an analysis claiming its customers' SOC 2 reports
  average ~40% textual similarity to each other (implying real customization), versus ~99.8% for
  unnamed competitors, whom they characterize as producing "templates" rather than genuine
  programs. Treat this as a company-authored marketing claim, not independently verified. [Source: 10]

## 4. Culture & voice

- Public-facing voice is direct, founder-to-founder, and slightly combative toward incumbent GRC
  vendors ("compliance shouldn't kill your startup," "no compliance tax"). Marketing leans on
  concrete before/after metrics (3 weeks, under 5 hours, zero exceptions) rather than enterprise
  GRC jargon. [Sources: 6, 7]
- Stated values (company About page): Innovation, User-Centricity, Integrity, Excellence.
  [Source: 3]
- Origin story emphasizes listening hard to early customers (one anecdote: the team pushed
  intensively to ship a feature a client needed to close a deal). [Source: 8]
- Job posting culture signals: informal dress code, pet-friendly, stock options for early hires,
  "individual voice" and growth as the company scales, described as "mission-driven." [Source: 2]
- Team is tiny (single digits), so culture is closer to "early founding team" than "company with
  an HR-documented culture." No public engineering blog, no visible Glassdoor/employee-review
  presence was found; culture claims above come from marketing copy and the job post, not
  independent employee sources. Mark as thin/unverified beyond what's cited.

## 5. Recent news (last ~12 months, dated where possible)

- **2026 (ongoing)**: Actively hiring across roles, including this Full-Stack Developer opening
  and a Senior Backend Developer role focused on agentic AI engineering (Go, Python, cloud
  infra across AWS/Azure/GCP), fully remote in US/Canada per that posting; also recent
  non-engineering hires (a Compliance & Risk / Customer Success Manager, and a founding Account
  Executive). [Sources: 2, 5, 11]
- **March 2026**: Company LinkedIn-derived employee count reported at 7 (up from smaller counts
  earlier); Tracxn separately lists 6 employees as of end of May 2026. Treat exact headcount as a
  moving, roughly single-digit number rather than a precise figure. [Sources: 4, 5]
- **January 2026 (case study published)**: Alignd achieves SOC 2 Type I via EasyAudit in 3 weeks,
  under 5 hours of internal effort, zero exceptions; used as the company's flagship proof point.
  [Source: 6]
- **Reported ~October 2025**: Pre-seed funding (reported around $200K in company/LinkedIn-derived
  content) referenced alongside RevTech Labs accelerator involvement; PitchBook/aggregator data
  shows a much smaller figure (~$20K) for what may be the same or a different tranche. This is the
  one clearest gap in public data; do not repeat a specific number as fact without further
  verification. [Sources: 4, 5, 12]
- **ISO/IEC 42001 (AI management system) support** added to the platform's framework lineup at
  some point before mid-2026 (no specific launch date found), positioning EasyAudit for the
  emerging "AI governance" compliance wave alongside SOC 2/ISO 27001. [Source: 9]
- Press/mention roundup (undated or lightly dated, secondary coverage, not verified beyond
  headline-level): ComputerWorld, CSO Online, GRC Viewpoint, KBI Media, SecuritySenses,
  TechBullion logos appear on the homepage as "as seen in," with a Cyber Defense Magazine byline
  from founder Christian Khoury. [Sources: 1, 13]

## 6. Engineering & AI direction

- **Product stack signals (from this job posting)**: Frontend in JavaScript/TypeScript,
  React.js, Next.js, MUI; backend in Node.js and Python; testing with Playwright and Storybook;
  Postgres and S3 for data/storage; deployed across Azure, AWS, GCP, Vercel, Render, and Supabase.
  AI layer built on the OpenAI Agents SDK and Google's A2A (agent-to-agent) protocol, with the team
  itself using ChatGPT, Claude Code, and Cursor as AI-assisted dev tools. [Source: 2]
- **Separately posted Senior Backend Developer role** skews toward Go and Python for "agentic AI
  engineering" across AWS/Azure/GCP, suggesting the backend may be diversifying beyond Node,
  or that different services use different languages. Treat as a signal of stack evolution, not
  a confirmed unified architecture. [Source: 11]
- **AI approach**: multi-agent architecture ("a team of AI agents," not a single chatbot) that
  performs discrete jobs (policy generation, control mapping, evidence collection, gap analysis,
  audit-doc prep) rather than one monolithic assistant. No public technical writeup on model
  choice, RAG design, or evaluation approach was found; the "AI-native" and "world's first
  AI-native platform" claims are company marketing, not independently verified. [Sources: 1, 9]
- No dedicated public engineering blog was found as of this research date; engineering practice
  (testing rigor, deploy cadence, on-call, etc.) is not independently documented beyond what the
  job posting states (own features from local to staging with e2e/unit tests, work independently
  in a fast-shifting startup). [Source: 2]

## 7. Why-fit angles for Santiago

**Best hook to lead with**: Santiago has personally built the exact category of product EasyAudit
sells (an AI agent that ingests a company's real data and does the work a human specialist used
to do) and he's done it as a founder shipping to real B2B clients under deadline pressure, not
just as an engineer following a spec. Pragma AI's "company brain" (RAG over internal company data
to answer questions and auto-generate business reports) is structurally the same problem EasyAudit
solves for compliance evidence and policy generation: turn a company's messy real data into a
trustworthy AI-generated document a human will sign off on.

- **Agent-native stack overlap**: the job asks for OpenAI Agents SDK, tool-use/function-calling
  AI agents, React/Next.js, Node/Python, Postgres, AWS. Santiago's master resume shows direct,
  recent hands-on work with exactly this shape of stack (Claude Agent SDK, MCP tool layers, agent
  frameworks with function calling, FastAPI/Python, React/TypeScript/Vite, PostgreSQL, AWS,
  Supabase) across Plutus, Kairos, and the Pragma AI personal-finance agent.
- **Founder who ships 0-to-1 alone or in tiny teams**: EasyAudit is a single-digit-headcount team
  that explicitly wants someone who "gets features from local to staging without constant
  oversight" in a "fast-paced" startup where "priorities shift rapidly." Santiago founded and ran
  two companies (Eugenia.ai to acquisition, Online Basics to $8M revenue on a 9-person team) and
  is currently building solo AI products end to end (Plutus, Kairos), which is a strong, honest
  match for "self-starter, startup and side-project track record."
- **Trust/verification framing**: EasyAudit's core value prop is AI output a CPA and an enterprise
  buyer will actually trust. Santiago's LLM work (Online Basics: custom prompt engineering plus a
  "multi-stage validation pipeline" for AI-generated content) is directly relevant experience
  building guardrails around AI output that a human reviews before it goes out the door.

**Honest concerns / watch-outs**:
- **Compliance domain is new to him.** Nothing in his resume shows SOC 2/ISO 27001/GRC/audit
  experience. The posting lists compliance background as "desirable," not required, so this is a
  gap to name plainly rather than paper over, and to pair with fast-learner evidence (e.g., he
  built financial/compliance-adjacent tooling like Plutus's data-provider ingestion, and ran
  operational/data-validation systems at Online Basics that cut data-entry errors 90%).
- **Very small, thinly documented company.** Headcount is roughly 4 to 7 people, funding is small
  and unclearly disclosed, HQ location is inconsistent across sources (Toronto vs Miami), and
  there is no public engineering blog. This is real seed/pre-seed risk (a title Santiago should
  weigh honestly): limited runway visibility, no evidence yet of what engineering process/on-call
  looks like day to day.
- **Pay band is modest for his level.** Listed $5,000 to $7,000 USD/month ($60k to $84k/year),
  which is at or below his $65k floor at the low end and clearly below what a 7+ year
  founder-engineer with two exits/scale stories would command elsewhere. Fine if the equity and
  mission compensate, worth a candid gut-check.
- **Backend language drift.** A separate Senior Backend role skews Go/Python, while this
  Full-Stack posting is Node/Python; worth clarifying in an interview which stack he'd actually
  touch day to day.

## 8. Application-question angles

- **Why this company**: Lead with the founder-to-founder resonance, not the compliance
  vertical itself. He has personally lived the problem EasyAudit is solving (a small team needing
  an AI system that turns real, messy company data into a document a human authority will trust)
  because he built that exact pattern (Pragma's RAG "company brain," the LLM content-validation
  pipeline at Online Basics). Frame it as "I've shipped the class of product you're selling," not
  "I want to work in compliance."
- **Why you fit**: Lead with agent-native stack fluency plus solo-shipping track record. Name
  the specific overlap (OpenAI Agents SDK-equivalent work via Claude Agent SDK and MCP, tool-use
  function calling, React/Node/Python/Postgres/AWS) and pair it with concrete proof he can own a
  feature end to end without oversight (two companies built and scaled/exited, current solo
  full-stack AI products). Keep it to one or two of these, not a checklist of every skill match.
- **Anything else**: A short, honest note that compliance/GRC is a new domain for him, framed as
  an asset (a founder's outsider eye plus a demonstrated habit of building validation/QA rigor
  around AI output) rather than a hedge. Optionally note remote-from-Mexico-City availability and
  TN-visa eligibility if the team's US/Canada location matters to them; do not overstate this since
  the role appears fully remote worldwide.

## 9. Sources

1. https://www.easyaudit.ai/ (homepage: product description, framework list, "as seen in" press
   logos, positioning vs. Vanta/Drata/Sprinto/Secureframe, "world's first AI-native platform"
   claim)
2. https://www.getonbrd.com/jobs/full-stack-developer-easyaudit-ai-inc-remote (this job posting:
   full stack, responsibilities, requirements, salary $5,000 to $7,000/month, remote worldwide,
   informal/pet-friendly culture notes, stock options)
3. https://www.easyaudit.ai/about-us (mission statement, founding story summary, four core values:
   Innovation, User-Centricity, Integrity, Excellence)
4. https://tracxn.com/d/companies/easyaudit/__iAtEPzPkT7bmmX6wZuWNld7Uash3U3wJChsH1ihxXj0 (founding
   year 2024, US HQ, 6 employees as of May 2026, RevTech Labs investor, 1 funding round amount
   undisclosed)
5. https://ca.linkedin.com/company/easyauditai (company LinkedIn: 7 employees, Miami FL HQ,
   pre-seed ~$200K reported around October 2025, "Era 2 to Era 3" positioning, recent hires,
   TheStage AI customer mention, Senior Backend Developer opening details); note this was read via
   an automated fetch/summary of the page, treat headcount/funding specifics as lower-confidence
   than the company's own site
6. https://www.easyaudit.ai/case-studies/alignd (Alignd customer case study: 3 weeks to SOC 2 Type
   I, under 5 hours internal effort, zero exceptions, customer quote)
7. https://killerstartups.com/easyaudit/ (founder Christian Khoury, one-line mission, 4-year
   vision, secondary press profile)
8. https://kbi.media/spotlight/easyaudit/ (founding story framing: "built by founders, for
   founders," "compliance without the compliance tax," Toronto HQ per this source, client-pressure
   anecdote)
9. https://www.easyaudit.ai/frameworks/iso-42001 and https://www.easyaudit.ai/features (ISO 42001
   AI-governance framework support; AI Compliance Officer / multi-agent feature descriptions)
10. LinkedIn company post content on customer similarity analysis and TheStage AI, surfaced via
    web search of easyaudit.ai/LinkedIn content (SOC 2 report similarity claim: ~40% for EasyAudit
    customers vs ~99.8% for unnamed competitors); treat as company marketing claim, unverified
    independently
11. Web search results referencing an EasyAudit "Senior Backend Developer" LinkedIn posting dated
    around March 21, 2026 (Go/Python, agentic AI engineering, remote US/Canada)
12. PitchBook company profile summary (funding amount conflict: ~$20K figure), via search result
    snippet of https://pitchbook.com/profiles/company/682015-51 (full page not directly
    accessible)
13. https://www.cyberdefensemagazine.com/the-3-hidden-dangers-of-avoiding-soc-2-compliance/
    (bylined guest article context confirming Christian Khoury as founder/CEO, ex-Deloitte
    background)

researched: 2026-07-07

**Note on confidence**: This is a very early-stage, low-headcount startup with thin, sometimes
contradictory public documentation (HQ city, exact funding amount, and precise headcount all vary
by source). Facts above are attributed source by source; where sources conflict, both figures are
shown and flagged rather than picking one. Treat this dossier as a solid starting point, not a
verified data room, and confirm funding/HQ/team size directly in the interview process if it
matters to Santiago's decision.
