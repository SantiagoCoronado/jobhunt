# CINC Systems

Draft dossier for Santiago's review. Researched: 2026-09-02.

## Core narrative
CINC Systems has spent 20 years turning back-office HOA and community association accounting into a modern SaaS platform, and it is now layering an AI-native product suite (Cephai, Community Intelligence) plus a resident-facing app (CINC Connect) on top of that operational core. The pitch from CEO Ryan Davis is explicit: "AI alone won't drive adoption, and engagement without automation creates inefficiency," so the company is building automation and engagement as two halves of one strategy rather than bolting AI onto an existing product (prnewswire.com, cinc-connect release, 2025-09-16).

## Mission & product
- Community association management (CAM) software: accounting, banking integration, operations, compliance, and resident engagement on one platform for property management companies that serve HOAs and condo associations (cincsystems.com).
- Three product pillars: Management + Accounting (financial/operational tools for management teams), Boards + Residents (CINC Connect, a branded web/mobile resident experience with payments and self-service), and Community Intelligence, an AI layer powered by Cephai that surfaces insights and suggested next steps across the platform (cincsystems.com; cepien.ai/Cephai blog).
- Business model: B2B SaaS sold to property/community management companies, not directly to homeowners. Serves 1,000+ management companies and more than 6 million residential units / 50,000+ communities (cincsystems.com; prnewswire.com 2026 State of the Industry report reference).
- Founded 2005 by a banker as the industry's first SaaS offering; pioneered accounting/banking integration for the CAM industry (JD text pulled via src.query job 34063; cincsystems.com).
- CINC Connect (resident portal/app) was announced September 16, 2025 at the company's CINC Up client conference, with client upgrades beginning Q1 2026: news feeds, group chat, amenity reservations, e-voting, package tracking, and a manager Communications Center, sold across Essential/Lifestyle/Premium tiers (prnewswire.com, 2025-09-16).
- AI direction: Cephai is described as the "cornerstone of CINC's entire product suite," with trust patterns built in (citations, explicit approval requirements, confidence signals, feedback loops, auditability) rather than an unchecked-automation approach (cincsystems.com/resources/blog/building-the-ai-native-stack).

## Recent news (last ~12 months)
- 2025-09-16: Launched CINC Connect, a resident/board portal and mobile app, at the CINC Up conference; client rollout began Q1 2026 (prnewswire.com).
- 2025-01-06: Acquired ONR Applications Inc. to expand its HOA management experience (crunchbase.com acquisition record; prnewswire.com release title referenced in search results).
- 2026 (month unspecified in search results): Released a "2026 State of the Industry Report" on the value, capacity, and trust squeeze reshaping community association management (cbinsights/crunchbase summary of CINC news).
- Backed by growth-equity investors Hg (Hg Capital) and Spectrum Equity; total disclosed funding around $102M across the company's history (cbinsights.com, crunchbase.com). Exact recent round dates were not confirmed in this pass; treat funding recency as unverified beyond the ONR acquisition and Hg/Spectrum backing.
- Headcount: sources disagree slightly, roughly 275 to just under 400 employees depending on source and date (cincsystems.com search summary vs. job posting text, both accessed 2026-09-02); the job posting itself says "nearly 400 people."

## Culture & hiring signals
- CINC's own careers listings (via the Spectrum Equity portfolio careers page) describe multiple open roles as "Global Remote-first (hybrid optional)" or "Worldwide (Remote-first / Hybrid optional)," for example a Staff Application Support Engineer and a Security Engineer (careers.spectrumequity.com/companies/cinc-systems, accessed via search 2026-09-02). This matches the Senior Applied AI Engineer posting's own "Worldwide (Remote/Hybrid)" line.
- CTO Duri Chitayat is described as leading "AI development, globally distributed engineering, and core platform operations," which points to an already-distributed engineering org rather than a US-only team (cincsystems.com/resources/blog/building-the-ai-native-stack).
- What is NOT confirmed: whether CINC hires engineers as contractors versus employees outside the US, and whether Mexico specifically is an eligible hiring country. The job posting carries no explicit country restriction or work-authorization clause in the text retrieved, but a note already in the jobs database flags that a sibling CINC requisition was scoped "Remote, US" and that CINC's JazzHR board was unreachable during verification (src.query job 34063, notes field, verified 2026-09-01). Treat "worldwide" as stated by the posting, not as independently confirmed with a recruiter.
- No dedicated public engineering blog beyond product-marketing posts (the "Building the AI-Native Stack" piece leans toward design-system/product marketing voice) and no distinct public social presence on engineering culture was found in this pass; culture signal here is thinner than for the product side.

## Target role: Senior Applied AI Engineer (job id 34063)
Source: `src.query job 34063` (Adzuna, posted 2026-08-31) and the Adzuna listing page.
- Location as stated in the JD: "Worldwide (Remote/Hybrid)." Reports to a Staff Applied AI Engineer.
- Salary as captured in the jobs database: 134,119 USD (single figure, likely a midpoint or a specific quoted number rather than a stated range).
- Responsibilities (JD summary): design and deploy AI features in production SaaS environments; integrate large language models into existing systems; design AI workflows with retrieval and orchestration components; partner with product teams; collaborate with platform/security teams; build evaluation strategies; contribute to system architecture; apply software engineering best practices; mentor colleagues; stay current with AI developments.
- Requirements (JD summary):
  - Technical: 8+ years of professional software engineering experience, hands-on production AI experience, system design expertise, LLM/ML model experience, familiarity with AI evaluation and monitoring, cloud-native architecture knowledge, comfort across the stack.
  - Collaboration: strong communication, structured thinking, comfort with ambiguity, cross-functional collaboration, bias toward incremental value delivery.
  - Mindset: builder orientation, belief that AI amplifies engineering practices (for better or worse), customer focus, learning orientation, composure under pressure, teamwork.
- Equal Opportunity Employer statement is present in the posting; no explicit citizenship or work-authorization clause was found in the retrieved text.

## Why-fit angles for Santiago
- Best hook: Santiago already built and exited a building-management SaaS (Eugenia.ai) for HOAs and property administrators, deploying to 20+ buildings and 10,000+ users with QR access control, resident communication, and fee/parcel management (resume/master_resume.yaml). That is close to a direct precedent for CINC's own CAM plus resident-app strategy (Management + Accounting paired with CINC Connect), not a generic AI-engineer analogy.
- Second hook: hands-on production LLM/RAG work (Pragma AI's "Pragma Brain" RAG system with citation gating and an eval harness; Online Basics' LLM content-generation pipeline) maps to the role's asks for retrieval/orchestration design and building evaluation strategies.
- Honest concern: the posting asks for 8+ years of professional software engineering experience; Santiago's resume states 7+ years. Close but a real gap worth acknowledging rather than glossing over, and worth raising early with the recruiter rather than in the cover letter.
- Honest concern: the "worldwide remote" claim in this specific posting is not yet confirmed against CINC's actual hiring-country practice. A sibling CINC requisition was scoped "Remote, US," and no direct recruiter confirmation exists yet for Mexico-based hiring (see notes on job 34063). This should be clarified before or during the application, not assumed.

## Application-question angles
- Why this company: lead with the Eugenia.ai precedent, a builder who has personally lived the HOA/property-management problem CINC solves (accounting, resident communication, board operations) and shipped a working version of the resident-app half of what CINC now calls Connect. That is a specific, provable connection to CINC's product, not a generic "I like SaaS" pitch.
- Why you fit: pair the Eugenia.ai domain match with recent hands-on RAG/agent work (Pragma Brain's citation-gated retrieval, eval harness) to speak directly to the JD's asks (LLM integration into production systems, retrieval and orchestration design, evaluation strategies) without listing every skill in the profile.
- Anything else: if it comes up, be upfront and ask about the location/hiring-country question directly rather than assuming "Worldwide" covers Mexico; this is a real open question, not a rhetorical one.

## Sources
- researched: 2026-09-02
- https://cincsystems.com/ , company overview, product pillars, HQ, customer counts (accessed via WebFetch 2026-09-02)
- https://www.prnewswire.com/news-releases/cinc-redefines-community-association-management-with-launch-of-cinc-connect-302557803.html , CINC Connect launch details, date, AI/engagement strategy quote from CEO Ryan Davis (accessed 2026-09-02)
- https://www.crunchbase.com/acquisition/cinc-systems-acquires-onr--537664d9 , ONR Applications acquisition, dated 2025-01-06 (via search summary, accessed 2026-09-02)
- https://www.cbinsights.com/company/cinc-systems/financials and https://www.crunchbase.com/organization/cinc-systems , funding total (~$102M), investors Hg and Spectrum Equity, 2026 State of the Industry Report mention (via search summary, accessed 2026-09-02)
- https://cincsystems.com/resources/blog/building-the-ai-native-stack , engineering stack (unified repo, lint/type/a11y/visual-regression checks), Cephai trust patterns, CTO Duri Chitayat's role over distributed engineering (accessed via WebFetch 2026-09-02)
- https://careers.spectrumequity.com/companies/cinc-systems , remote-first / hybrid-optional language on multiple open CINC roles (via search summary, accessed 2026-09-02)
- Job posting text and metadata: `.venv/bin/python -m src.query job 34063` (Adzuna source, id 34063), plus https://www.adzuna.com/details/5862791589 for the full responsibilities/requirements text (accessed via WebFetch 2026-09-02)
