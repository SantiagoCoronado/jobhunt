# Cosuno

researched: 2026-08-24
draft: for Santiago's review, not a finished narrative

## 1. Snapshot

Berlin-based B2B SaaS startup digitizing construction tendering and subcontractor procurement (RFPs, bid comparison, awarding), founded 2019, roughly 100 employees, HQ in Berlin with a "100% remote or Berlin office" policy for many roles. Raised $45M+ total: a $15M Series A (2021, led by Spark Capital) and a $30M Series B (Feb 2022, led by Avenir Growth, $150M valuation); no newer round found in public records as of this research date. [cosuno.com/web/en/company](https://www.cosuno.com/web/en/company), [tech.eu Series A](https://tech.eu/2021/05/27/berlin-based-procurement-proptech-cosuno-raises-15-million-in-series-a-round/), [tech.eu Series B](https://tech.eu/2022/02/09/cosuno-brings-in-30-million-to-digitise-construction-industry/), [Build in Digital](https://buildindigital.com/berlin-contech-cosuno-bags-30m-to-expand-saas-platform/)

## 2. Core narrative

Cosuno takes a genuinely unglamorous, offline B2B workflow (construction tendering, historically run over phone, email, and spreadsheets between general contractors and 250,000+ subcontractors) and rebuilds it as an AI-native marketplace: an AI agent checks tenders for errors and drafts bills of quantities, an AI price assistant forecasts costs from historical tender data, and AI recommends which bidders to invite. That is the distinctive thread: real AI product surface area inside an unsexy, high-value vertical, not a demo. The current live job board (checked 2026-08-24) shows an active engineering hiring push through mid-2026, including a Principal and a Senior Full Stack Developer opened the same day (2026-03-01), a Senior ML Engineer (April), an "AI Automation Engineer" role built to automate Cosuno's own internal operations (June), and an Engineering Manager opening days before this research (Aug 18), suggesting the company is scaling its engineering org specifically around AI features and AI-run internal ops at the same time. [Ashby job board API, live 2026-08-24](https://jobs.ashbyhq.com/cosuno), [cosuno.com AI features](https://www.cosuno.com/web/en)

## 3. Mission & product

Cosuno's platform serves two sides of a marketplace: "clients" (general contractors, project developers, architects) who post tenders and compare bids, and "contractors" (subcontractors/trades) who bid on work. Stated network: 250,000+ qualified subcontractors, planners, and architects; offer/tender volume on the platform exceeds €100 billion. Cited platform outcomes: 50%+ time savings on manual procurement steps, a 14% average increase in bid response rates, and a 5.7% average rise in contract-award profit margin from receiving more competing bids. AI features called out on the marketing site: AI-generated bidder recommendations based on project criteria and bid history, an AI agent that checks tenders for errors before publishing, and an AI "Price Assistant" trained on tender data for cost forecasting. [cosuno.com/web/en](https://www.cosuno.com/web/en), [cosuno.com/en](https://www.cosuno.com/en)

## 4. Culture & voice

Company-page stated values: customer obsession, "raise the bar," collaboration, an ownership mentality, and "workplace joy." Self-description: "flat hierarchies, short communication channels at eye level, self-determined work and no bureaucracy," with an emphasis on continuous learning and an international team while explicitly protecting a "start-up culture" despite growth. [cosuno.com/web/en/company](https://www.cosuno.com/web/en/company)

Engineering-specific culture, per the live job posting for this exact role: trunk-based development with daily releases ("agile and fast-paced"), a comprehensive Cypress E2E suite plus strict typing/linting/formatting ("quality by default"), infrastructure as code via Terraform with CI/CD to AWS via Kubernetes ("DevOps mindset"), and code-review culture where "the best idea wins, regardless of who it comes from." [Ashby posting, Senior Full Stack Developer (TypeScript)](https://jobs.ashbyhq.com/cosuno/424ba681-0989-4961-82ad-10286e4aae71)

## 5. Recent news (roughly last 12 months, dated where possible)

- 2026-08-18: Engineering Manager role opened, live on the board. [Ashby job board API](https://jobs.ashbyhq.com/cosuno)
- 2026-06-16: "AI Automation Engineer" role opened, an internal role built to design and deploy AI-driven workflow automation across Finance, Sales, Ops, and Product, reporting to the CEO and CTO, using an orchestration stack including n8n and vector databases to build what the posting calls "a universal memory for Cosuno." Signals active internal investment in agentic automation beyond the customer-facing product. [Ashby: AI Automation Engineer](https://jobs.ashbyhq.com/cosuno/564a3a0b-4748-493c-84ba-d8625913bf85)
- 2026-04-17: Senior ML Engineer role opened. [Ashby job board API](https://jobs.ashbyhq.com/cosuno)
- 2026-03-01: Both a Principal Full Stack Developer (TypeScript) and this Senior Full Stack Developer (TypeScript) role opened the same day, still open as of 2026-08-24 (roughly 5.5 months live). [Ashby job board API](https://jobs.ashbyhq.com/cosuno)
- No funding round newer than the Feb 2022 Series B was found in the sources checked (company site, press coverage, funding-round trackers); treat any "hypergrowth" framing with caution and lean on the hiring-pace signal above instead of a funding-momentum claim.

## 6. Engineering & AI direction

Confirmed directly from the current live posting for this role: TypeScript across the stack, React on the frontend, Node.js on the backend, a modular-packages monorepo, AWS infrastructure deployed via Kubernetes, infrastructure as code with Terraform, and a Cypress E2E test suite. [Ashby posting](https://jobs.ashbyhq.com/cosuno/424ba681-0989-4961-82ad-10286e4aae71)

Additional stack detail from an older (2022-era, now closed) sibling "Senior Full Stack Developer (f/m/d)" listing for the same engineering org: GraphQL API with Prisma for database access, relational database plus Elasticsearch. Flagging this as an earlier snapshot of the same team's stack rather than confirmed-current, since it is not restated in the live 2026 posting. [LinkedIn (archived posting, via search cache)](https://www.linkedin.com/jobs/view/senior-full-stack-developer-f-m-d-at-cosuno-3416922177)

AI direction has two tracks: customer-facing product AI (bidder recommendations, an AI agent that edits/checks bills of quantities and tenders, an AI price-forecasting assistant, per the job description's "in your first few months" list and the marketing site) and internal operational AI (the AI Automation Engineer role's n8n/vector-database workflow automation across internal teams). [Ashby posting](https://jobs.ashbyhq.com/cosuno/424ba681-0989-4961-82ad-10286e4aae71), [Ashby: AI Automation Engineer](https://jobs.ashbyhq.com/cosuno/564a3a0b-4748-493c-84ba-d8625913bf85)

Current live posting for this role lists compensation of €80,000-100,000/year. [Ashby posting compensation data, live 2026-08-24](https://jobs.ashbyhq.com/cosuno/424ba681-0989-4961-82ad-10286e4aae71)

## 7. Why-fit angles for Santiago

Best hook to lead with: Santiago has repeatedly shipped exactly the pattern Cosuno is hiring for, an AI feature (agent, RAG, or automation) built and owned end-to-end inside a real, revenue-generating operation rather than a research demo. At Online Basics he built the internal React/Python/AWS ops platform (pricing, inventory, discounting) that ran an $8M business, and designed the LLM content-generation workflow on top of it. At Pragma AI he co-built "Pragma Brain," a RAG system with citation gating and an eval harness, productized as the firm's flagship offering, plus internal automations for quoting, reporting, onboarding, and collections, and a hosted MCP service exposing agent tools to operators. That is close in shape to Cosuno's own ask: TypeScript/React/Node ownership of product AI features (BoQ agent, bidder recommendations) alongside a company that is simultaneously building internal AI automation for its own ops (the AI Automation Engineer role), a dual pattern Santiago has lived on both sides of.

Secondary angle: strong React/TypeScript/Node full-stack depth (master resume: React 18/19, TypeScript, Node.js, REST APIs, plus Electron and FastAPI breadth) matches the posting's core ask almost verbatim, and the "modular packages in a monorepo" ask lines up with his recent large-scale TypeScript projects (Plutus, Kairos, the Hydrel client portal), each built and tested (Vitest, Playwright, Cypress-adjacent E2E discipline) as a solo or small-team owner.

Honest concerns/watch-outs:
- Location eligibility is genuinely unconfirmed (see below); this needs to be resolved before or early in the process, not assumed.
- Kubernetes and Terraform are explicitly "nice to haves" the posting lists as bonus points; Santiago's infra experience is AWS-centric (EC2, RDS) and Docker, not Kubernetes/Terraform specifically. This is a real, named gap, not disqualifying (it is a bonus, not a must-have) but worth acknowledging rather than overclaiming.
- No GraphQL/Prisma experience is listed in the master resume; if that stack detail is still current, it is unverified against his resume and should not be claimed.

## 8. Application-question angles (narrative-led, not full answers)

**Why this company:** Lean into the "AI inside an unglamorous, high-value vertical" narrative from the Core narrative section, not a generic "I love construction tech" line. Frame it as: most AI hiring right now chases flashy consumer demos; Cosuno is doing the harder, more durable thing, wiring AI into a real B2B workflow (tendering) with a real network (250,000+ subcontractors) and real operational stakes for both sides of the marketplace, and is investing in AI on both the product and the internal-ops side at once. That combination, not "construction" per se, is the hook.

**Why you fit:** Lead with the Online Basics and Pragma Brain pattern (AI feature built and owned end-to-end inside a live business, not a lab exercise), then land on the direct stack match (TypeScript, React, Node, AWS) and the "own a feature from concept to deployment" framing in the posting, which mirrors how he has always worked as a founder-engineer.

**Anything else:** Worth surfacing his TN-visa eligibility and full remote flexibility proactively, and asking directly whether this role is open to candidates based in Mexico, since the public posting does not state a country restriction but Cosuno's engineering roles have historically skewed Europe-scoped (see Watch-outs). Better to ask than assume.

## Watch-outs

**Location eligibility: genuinely unconfirmed, resolve before assuming fit.**
- The live Ashby posting for this exact role (checked directly via the Ashby public API on 2026-08-24) lists location as "Berlin/Remote," workplaceType "Remote," with no country restriction field set and no secondary-location lock. The same is true of the other current live engineering roles (Principal Full Stack Developer, Senior ML Engineer, Engineering Manager), all tagged "Berlin/Remote" with no country lock. By contrast, Cosuno's own board does explicitly country-lock some current roles: "Technical Product Manager" is listed simply as "Germany," and hybrid/on-site roles are tagged "Berlin (Hybrid)" or "Berlin (on-site)." This suggests Cosuno's Ashby setup is capable of country-locking a role and chose not to for this one, a mild positive signal but not a confirmation of worldwide eligibility. [Ashby job board API, live 2026-08-24](https://jobs.ashbyhq.com/cosuno)
- Against that: an older (now-closed) Cosuno LinkedIn posting for a predecessor "Senior Full Stack Developer (f/m/d)" role explicitly scoped hiring to the "European Economic Area." [LinkedIn (archived)](https://www.linkedin.com/jobs/view/senior-full-stack-developer-f-m-d-at-cosuno-3416922177)
- A Welcome to the Jungle mirror of a Cosuno "Senior Full Stack Developer" listing shows the location as "Remote from Europe, UK." [Welcome to the Jungle](https://app.welcometothejungle.com/jobs/U0VQYmpv)
- Third-party aggregator RemoteRocketship tags several current Cosuno roles (Senior Analytics Engineer, Senior Product Manager roles, Sales Development Representative) as "Germany Remote," but tags others (Founders Associate roles, Senior Product Designer) as "Worldwide Remote." That split looks more like inconsistent aggregator tagging than a documented company policy, since the primary source (Ashby/company site) does not state either. [Search results, RemoteRocketship listings](https://www.remoterocketship.com/company/cosuno)
- No primary source (the live job posting, the Ashby API, or cosuno.com) currently states an explicit country restriction for this specific role, and no evidence either way was found of a Cosuno engineer currently based outside Europe. Net read: eligibility from Mexico is plausible given the current posting's silence on country, but not confirmed, and the company's history suggests Europe-first hiring for engineering roles. Confirm directly with the recruiter early in the process rather than assuming either way.

**Compensation:** the current live listing states €80,000-100,000/year, a Berlin-scoped band; it is unknown whether a Mexico-based hire would be offered this band as-is, a contractor conversion, or something else. Ask directly; do not assume parity with `config/profile.yaml`'s USD comp targets, which are calibrated for US-scoped remote roles.

**Company scale and market:** roughly 100 employees, German-HQ'd, serving a construction industry customer base that per available evidence is Europe-centered (offer volume, marketing language, and customer references found are German/European). This is a narrower, more regional story than a global remote-first company; the "why this company" answer should own that rather than imply a bigger global footprint than is evidenced.

## 9. Sources

- researched: 2026-08-24
- [cosuno.com/web/en/company](https://www.cosuno.com/web/en/company): team size (~100+ employees), stated values, culture description
- [cosuno.com/web/en](https://www.cosuno.com/web/en): AI feature descriptions, subcontractor network size, platform metrics
- [cosuno.com/en](https://www.cosuno.com/en): product description, customer segments, business model
- [tech.eu, Series A coverage (2021-05-27)](https://tech.eu/2021/05/27/berlin-based-procurement-proptech-cosuno-raises-15-million-in-series-a-round/): Series A amount, lead investor, participants
- [tech.eu, Series B coverage (2022-02-09)](https://tech.eu/2022/02/09/cosuno-brings-in-30-million-to-digitise-construction-industry/): Series B amount, lead investor, participants, valuation
- [Build in Digital, Series B coverage](https://buildindigital.com/berlin-contech-cosuno-bags-30m-to-expand-saas-platform/): Series B amount, investors, valuation, date, founders
- [invest-in.berlin, Series B note](https://invest-in.berlin/n/30-m-series-b-for-construction-tech-firm-cosuno/): Series B date confirmation (10.02.2022), valuation
- [Ashby job board public API, live 2026-08-24](https://jobs.ashbyhq.com/cosuno): full current list of open roles, locations, workplace types, publish dates, used to build the hiring-pace timeline and the location-scoping comparison across roles
- [Ashby posting, Senior Full Stack Developer (TypeScript), the target role, live 2026-08-24](https://jobs.ashbyhq.com/cosuno/424ba681-0989-4961-82ad-10286e4aae71): full job description, engineering culture bullets, stack (TypeScript/React/Node/AWS/Kubernetes/Terraform/Cypress), compensation (EUR 80k-100k), "about us" text
- [Ashby posting, AI Automation Engineer, live 2026-08-24](https://jobs.ashbyhq.com/cosuno/564a3a0b-4748-493c-84ba-d8625913bf85): internal AI automation direction (n8n, vector databases), reporting line, publish date
- [LinkedIn, archived "Senior Full Stack Developer (f/m/d)" posting](https://www.linkedin.com/jobs/view/senior-full-stack-developer-f-m-d-at-cosuno-3416922177): older stack detail (GraphQL, Prisma, Elasticsearch), explicit "European Economic Area" location scoping on a predecessor role
- [Welcome to the Jungle, Cosuno Senior Full Stack Developer mirror](https://app.welcometothejungle.com/jobs/U0VQYmpv): "Remote from Europe, UK" location wording
- [RemoteRocketship, Cosuno company listings](https://www.remoterocketship.com/company/cosuno): third-party location tagging across multiple current Cosuno roles, used only to show inconsistency, not as a primary source

This dossier is a draft for Santiago to review before it is used in any cover letter or application answer, especially the location-eligibility Watch-out, which should be confirmed with Cosuno directly rather than assumed either way.
