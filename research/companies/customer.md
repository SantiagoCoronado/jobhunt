---
company: Customer.io
researched: 2026-08-25
draft: true
job_context: "Senior Full-Stack SDK Engineer (job id 20071), https://job-boards.greenhouse.io/customerio/jobs/8076081, Americas remote, posted 2026-07-21/2026-08-16, band $150k-$200k USD"
---

# Customer.io

## 1. Snapshot
Customer.io is a Portland, Oregon-founded (2012) customer engagement platform (email, push, in-app, SMS, webhooks) used by 8,000+ paying companies to send data-powered messaging; it crossed $100M ARR in September 2025 (up 37% year over year from $78M), is capital-efficient (only ~$38.8M raised total, most recently a $29.9M Series A from Spectrum Equity in March 2022, after reaching $30M ARR on under $4M raised), and runs as a globally distributed, remote-first team of roughly 250 people across 36+ countries [1][2][3][4].

## 2. Core narrative
Customer.io grew slowly and profitably for a decade on almost no outside capital before taking a single Series A once it had already proven the model at $30M ARR, and its founder frames the recent $100M ARR mark as "not the finish line, it's the start" for building the AI-native platform they've wanted to build all along [2][5]. That founder-led, fundstrapped-to-scale story, paired with a 2026 pivot toward agentic AI (an in-product AI Agent that builds campaigns from a prompt, plus MCP-based tooling for both internal and external agents) sits right at the intersection of what this SDK role is asking for: a company that still moves like a lean product-engineering shop but now bets its next chapter on AI agents doing real work inside the product and the SDKs [5][6].

## 3. Mission & product
Customer.io's stated mission is "a world where you have one unified view of your audience and a single place where unlimited, real-time data powers more effective engagement" [7]. The product is a customer engagement/messaging automation platform: email, mobile push, in-app messages, SMS, WhatsApp, LINE and webhooks, built on first-party customer data, with data pipelines (the former Segment-compatible `cdp-analytics-js` client) feeding the messaging layer [7][8]. Customers cited on the company's own materials include Notion, Segment, Clearbit, Buffer, Angi, Lemonade and IMAX; the SDK job posting itself states the platform is used by "over 9,000 companies" to send "billions" of messages daily [9][10]. In April 2026 the company shipped its "biggest product release" to date: an AI Agent that builds, audits and reports on campaigns from natural-language prompts, LLM Actions (calling any LLM mid-workflow to personalize content or drive branching logic), and new WhatsApp/LINE channels [6][11]. The AI Agent product page frames the philosophy explicitly: "Most platforms fragment AI into specialist bots. Ours is a single agent that gets sharper with every task," and it commits to "equal access" for both the built-in agent and external agents via MCP-compatible environments, APIs, and SDKs [12].

## 4. Culture & voice
Customer.io describes itself as "distributed by design, not by default": no HQ-centric culture, employees spread across 36+ countries, and an emphasis on asynchronous work to make that function [3][13]. Stated values are compassion, ownership, openness, and "room to be ourselves," with a stated preference for "reducing unnecessary meetings" and a hiring bar the company describes as "ambitious, curious people who hold a high bar and a low ego... standards run high and elbows stay down here" [13]. On the engineering side specifically, a companion Greenhouse posting states the team culture in its own words: ownership of problems end to end, a product mindset ("frontend polish, backend performance, and everything in between"), "a healthy skepticism for 'the way things are done,'" and an expectation that engineers "raise the bar through sharing your progress publicly with short videos, thoughtful writing, and mentorship" [14]. Benefits include 100% covered medical/dental/vision/mental health for employees and families, unlimited PTO with a stated 20-day minimum recommendation, 16 weeks paid parental leave, a $250/month remote-work stipend, and a professional development budget [10][13]. Customer.io ranked #5 on Newsweek's 2025 Most Loved Workplaces list [3].

## 5. Recent news (last ~12 months)
- **September 2025**: Customer.io crossed $100M ARR, up 37% YoY from $78M at end of 2024, serving 8,000+ paying customers and delivering 64+ billion messages over the prior 12 months; CEO Colin Nederkoorn's note framed the milestone as a "capability unlock" for the next product phase rather than an end state [2][5].
- **April 2026**: Company-wide "biggest product release" launch: AI Agent, LLM Actions, Goals, and new WhatsApp/LINE channels, publicly demoed April 16, 2026 [6][11].
- **2026 (ongoing)**: Actively hiring across the product engineering org for fullstack, backend, and now SDK-specific roles, all explicitly built around "using AI agents to make multi-file changes" as a normal part of the workflow [14][15].
- Employee headcount is reported around 250 in 2026, down from roughly 305 in 2023; some third-party sources (Glassdoor reviews, not company-confirmed) describe leadership and culture turnover during this period. This is unverified beyond employee review commentary and is flagged as a watch-out below rather than stated as fact [4][16].

## 6. Engineering & AI direction
Company-stated stack across current product-engineering postings: Go for backend/distributed systems, React and Ember for frontend fullstack features (Ember is a real, current part of the surface, not purely legacy), TypeScript throughout, and increasing use of AI coding agents (Claude, Cursor, Codex) for day-to-day development, explicitly called out as an expected skill, not a novelty [14][15]. The SDK-specific posting (this job) asks for fluency across Swift, Kotlin, Node, and Go to build and maintain SDKs on Android, iOS, Node, and Go, plus ownership of the SDKs' CI, testing, versioning and release infrastructure, and direct engagement with the third-party developers who integrate those SDKs [15]. Customer.io's public GitHub org confirms an active, MIT-licensed mobile SDK surface: `customerio-ios` (Swift), `customerio-android` (Kotlin), `customerio-reactnative` and `customerio-expo-plugin` (TypeScript), `customerio-flutter` (Dart), and a Go-based `cli` [8]. On AI specifically, the company has an internal MCP-based "SDK Setup Tool" to help developers integrate the mobile SDKs correctly (addressing wrong-region and mixed-up-key integration failures), which is the same MCP pattern the AI Agent product exposes externally, suggesting a consistent, company-wide bet on MCP as the AI integration layer rather than one-off features [17][12].

## 7. Why-fit angles for Santiago
**Best hook to lead with**: Santiago has shipped and maintained cross-platform SDK-adjacent, multi-surface systems himself, not as an SDK vendor, but the underlying skill transfers directly: Kairos exposes the exact same internal logic through two different surfaces (an in-app Claude Agent SDK integration and a standalone MCP server) from one typed tool-definition layer, which is structurally the same problem this role is hiring for (one core capability, multiple platform-specific SDK surfaces, kept in sync) [master_resume.yaml]. Pair that with Pragma AI's MCP-based internal brain service (per-operator tokens, rate limits, 15 agent definitions) as evidence he has already built the kind of MCP tooling Customer.io is now productizing externally through its AI Agent [master_resume.yaml][12].

Additional angles:
- Santiago already treats "AI agents making multi-file changes" as normal workflow (Claude Code, Cursor, Windsurf are listed tools; Kairos and Pragma were built with heavy agentic-coding usage), which matches the posting's explicit ask for fluency with Claude/Cursor/Codex on unfamiliar codebases [15][master_resume.yaml].
- His full-stack range (React/TypeScript frontend across Plutus, Kairos, Hydrel; Python/Go-adjacent backend and API design at Online Basics and Eugenia.ai; Swift and Java mobile work at Nextia.mx) covers the posting's ask for "expert-level competency in at least one established language" plus "fluency across multiple languages/stacks," including real production Swift experience (iOS at Nextia.mx, 50,000+ users) which is one of the exact SDK languages named [15][master_resume.yaml].
- The remote-first, fundstrapped-to-scale culture (low ego, high ownership, "standards run high and elbows stay down") maps well to his founder background running lean teams at Online Basics and Eugenia.ai [13][master_resume.yaml].

**Honest concerns / watch-outs**:
- The role is explicitly SDK-focused (Android/iOS/Node/Go maintenance, release infra, developer-facing support), a narrower niche than the general full-stack product engineering Santiago has mostly done; he has not maintained a public, versioned SDK consumed by third-party developers at scale before, only internal/first-party integrations.
- His Kotlin and Go experience are not documented in the master resume (Java and Swift are, from Nextia.mx; Go is not listed as a skill anywhere in the resume). This is a real gap to name honestly rather than imply.
- The Ember.js half of the broader engineering stack is not something in his background at all; not directly relevant to this SDK req but worth knowing if conversations range into the wider product engineering org [14].
- Headcount has reportedly shrunk from ~305 (2023) to ~250 (2026); this is drawn from third-party aggregators and unverified employee-review commentary, not a company statement, and should be treated as a question to ask rather than a claim to repeat [4][16].

## 8. Application-question angles
- **Why this company**: Lead with the MCP/agent-surface parallel (Kairos, Pragma AI) rather than generic "I love your product" language; Customer.io is one of the few companies at this stage explicitly betting its next chapter on MCP-based agent tooling for both internal AI features and third-party SDK integrations, and that is the exact shape of system Santiago has already built twice on his own.
- **Why you fit**: Anchor on the structural overlap between "one core capability exposed as multiple SDK surfaces kept in sync" (his Kairos in-app agent + MCP server from one typed tool layer) and this role's job of maintaining Android/iOS/Node/Go SDKs from a shared foundation, then back it with the Swift production experience from Nextia.mx and the daily agentic-coding habit (Claude Code, Cursor, Windsurf) the posting calls out by name. Do not try to claim deep prior SDK-release-infrastructure experience he does not have; frame it as the closest adjacent problem he has solved repeatedly, not an exact match.
- **Anything else**: If asked about gaps, name the Go/Kotlin unfamiliarity directly and pair it with evidence of fast ramp-up (built a production-grade FastAPI/Celery backend for Plutus and a 166-channel typed IPC contract for Kairos essentially solo, both in 2026) rather than deflecting.

## 9. Sources
1. Customer.io Senior Fullstack SDK Engineer posting (Greenhouse), stack, comp band, responsibilities: https://job-boards.greenhouse.io/customerio/jobs/8076081
2. Customer.io crossed $100M ARR note from CEO (company announcement page, referenced via search; direct fetch returned 404 at time of research, corroborated by secondary coverage): https://customer.io/learn/announcements/customerio-crossed-100m-note-from-ceo
3. Careers page, remote-first culture, values, benefits, hiring philosophy: https://customer.io/careers
4. Sacra company profile, revenue/valuation/funding figures: https://sacra.com/c/customerio/
5. Silicon Florist coverage of $100M ARR milestone (secondary, corroborating #2): https://siliconflorist.com/2025/10/23/portland-startup-customer-io-reaches-100m-arr-milestone/
6. Customer.io "biggest product release" AI Agent announcement (referenced via search snippet): https://customer.io/learn/announcements/biggest-ai-marketing-release
7. Customer.io About page, mission statement, business overview: https://customer.io/about
8. Customer.io GitHub organization, SDK repos and languages: https://github.com/customerio
9. Customer.io homepage, customer/product overview: https://customer.io/
10. Senior Fullstack SDK Engineer posting, "About Customer.io" section and benefits detail: https://job-boards.greenhouse.io/customerio/jobs/8076081
11. AI marketing launch demo page, April 16 2026 demo date: https://customer.io/learn/announcements/ai-marketing-launch-demo
12. Customer.io AI Agent product page, MCP/equal-access philosophy: https://customer.io/platform/agent
13. Careers page, values (compassion, ownership, openness, room to be ourselves), hiring bar language: https://customer.io/careers
14. Senior Software Engineer, Full Stack posting, Go/React/Ember stack and engineering culture values: https://job-boards.greenhouse.io/customerio/jobs/7776591
15. Senior Fullstack SDK Engineer posting, SDK-specific requirements (Swift/Kotlin/Node/Go, AI agents for multi-file changes): https://job-boards.greenhouse.io/customerio/jobs/8076081
16. GetLatka company profile, headcount and revenue figures (secondary, corroborating #4): https://getlatka.com/companies/customerio
17. Customer.io Mobile SDK Setup with MCP Server, internal AI-assisted SDK integration tooling: https://customer.io/learn/mobile-marketing/supercharge-your-mobile-sdk-with-mcp

Additional corroborating source used for funding history: Spectrum Equity investment announcement, March 2022 Series A, $30M ARR context: https://www.spectrumequity.com/news/customerio-surpasses-30m-arr-and-raises-financing-from-spectrum-equity/

researched: 2026-08-25

---
This dossier is a draft for Santiago to review before it is used in any application materials.
