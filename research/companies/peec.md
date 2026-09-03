# Peec AI: Company Dossier (DRAFT for Santiago's review)

researched: 2026-09-02

## Core narrative
Peec AI rode the shift from Google search to AI answer engines (ChatGPT, Perplexity, Gemini,
Claude) from a January 2025 founding to over 10 million USD in annualized revenue by May 2026,
crossing 4 million USD ARR in its first 10 months and then more than doubling that in the six
months after its Series A [2][4]. It is building the analytics category for "how brands show up
inside an AI answer" before that category has a settled name, backed by a visibly
performance-driven culture: a founding CEO with a competitive esports background, revenue
dashboards every employee can see, and recruiting billboards placed around Berlin to pitch
applicants, not just customers [3].

## Mission & product
Peec AI is a B2B SaaS analytics platform that tracks how brands are mentioned, cited, and
ranked inside AI-generated answers from ChatGPT, Perplexity, Gemini, and Claude, the practice
known as generative engine optimization (GEO), the AI-era analogue of SEO [1][2]. The product
tracks prompts (what people actually ask) rather than keywords, adds competitive benchmarking
against other brands inside the same AI answers, and layers on sentiment analysis and source
attribution to explain visibility gaps [2]. Data ships out through an API, a Looker Studio
connector, and CSV export [1]. Pricing is freemium with paid tiers plus enterprise sales
consultations [1]. The company states over 3,000 brands and agencies use the platform as of
this research date [1]; press coverage from the Series A names customers including Attio,
Squarespace, TUI, and Hugo Boss [6]. Stated frontend stack (from the open Senior Frontend
Engineer role): TypeScript and CSS, with React, Tailwind CSS, and Firebase/Firestore as the
core frontend technologies [7].

## Recent news
- 2025-07: Raised a 7 million EUR seed round, about four months after launch [5].
- 2025-11-17/18: Raised a 21 million USD Series A led by Singular, with Antler, Combination VC,
  identity.vc, and S20 participating; total funding to date about 29 million USD, valuation
  reported above 100 million USD (roughly tripling from the seed). ARR had passed 4 million USD
  in the first 10 months, with about 1,300 customers and roughly 300 new customers added per
  month. The company announced plans to hire about 40 people within six months, mostly in
  Berlin, and to open a sales-focused New York office in Q2 2026 [2].
- 2026-05-23: ARR reached 10 million USD, more than doubling in the roughly six months since the
  Series A; the New York expansion had launched [4].

## Culture & hiring signals
Founder-led, performance-oriented culture: CEO Marius Meiners was formerly a top-100 ranked
League of Legends esports player before co-founding Peec with CTO Tobias Siwonia and CRO Daniel
Drabo, the three having met in Antler's Winter 2024 cohort [2][3]. The company keeps running
revenue dashboards visible to all employees and has run recruiting billboard ads across Berlin,
treating hiring as a growth-marketing problem the same way it treats customer acquisition [3].
The open Senior Frontend Engineer posting is Berlin, on-site, not remote, and its "what we
offer" list signals a fast, in-office, long-hours environment: an "aggressive equity
compensation package," paid dinner and Uber home when working late, regular team events and
off-sites, and what the posting calls "the most beautiful office space... in Berlin" [7]. The
company was hiring roughly 40 people over six months as of the November 2025 raise, mostly into
Berlin, with the new New York office skewed sales rather than engineering [2]. No source
reviewed states a policy on visa sponsorship for non-EU engineering hires; that is unverified
and should be confirmed directly with the company before applying. Internally, Santiago's
profile.yaml lists Peec AI as a dream company with the curated note: "Ashby slug 'peec', mostly
Berlin on-site, a few NYC" (config/profile.yaml, dream_companies list, set 2026-09-01); this is
his own prior judgment on the company, not an external source.

## Target role
Senior Frontend Engineer, Berlin (on-site), posted 2025-10-09, Ashby job id
6b91aeeb-f051-4f48-8d16-44d3f0a6f186, https://jobs.ashbyhq.com/peec/6b91aeeb-f051-4f48-8d16-44d3f0a6f186/application
[7]. Scope: own complex frontend features end to end (scoping through polished delivery), build
pixel-perfect UI matching Figma specs, work closely with Product, Design, and Backend, and help
evolve the component library and design system for "rapid iteration at scale." Requirements: 5+
years of professional frontend engineering, deep TypeScript and React expertise, experience
building or maintaining a shared component library or design system, a portfolio or GitHub
showing real shipped work, strong CSS and Tailwind, and a demonstrated eye for translating
Figma into pixel-accurate UI. Bonus points for AI-product background, complex data-heavy or
real-time UIs, Firebase/Firestore experience, and a CS or related technical degree [7]. This is
a Berlin, on-site role: it requires a German or EU work visa, not a TN visa, and Santiago is
based in Mexico City. Peec AI is on his dream-company list, so the location and comp
constraints in his profile are waived for this role, but the visa reality (Germany/EU
sponsorship, not the US TN path he otherwise relies on) is a genuine open question that is not
answered by any source reviewed here [7][8].

## Sources
1. https://peec.ai, homepage: product description, customer count, freemium model, hiring
   banner. Fetched 2026-09-02.
2. https://techcrunch.com/2025/11/17/as-consumers-ditch-google-for-chatgpt-peec-ai-raises-21m-to-help-brands-adapt/,
   Series A funding amount, investors, valuation, founders, ARR/customer metrics, hiring and NYC
   expansion plans. Fetched 2026-09-02.
3. https://sifted.eu/articles/peec-ai-fundraise-new-valuation, CEO's esports background,
   revenue-dashboard and recruiting-billboard culture, NYC expansion. Fetched via search summary
   2026-09-02 (direct fetch returned HTTP 403).
4. https://techcrunch.com/2026/05/23/peec-one-of-berlins-rising-startups-more-than-doubled-annualized-revenue-in-months-to-10m-sources-say/,
   10 million USD ARR milestone, growth timeline, NYC office. Fetched 2026-09-02.
5. https://www.eu-startups.com/2025/07/berlin-based-peec-ai-raises-e7-million-four-months-after-launch-to-empower-companies-to-improve-their-geo/,
   seed round amount and date. Found via search 2026-09-02.
6. https://sifted.eu/articles/peec-ai-raises-21m-series-a, named customers (Attio, Squarespace,
   TUI, Hugo Boss) and Series A investor list. Found via search 2026-09-02.
7. Job posting (job id 41810), pulled via `.venv/bin/python -m src.query job 41810`, source URL
   https://jobs.ashbyhq.com/peec/6b91aeeb-f051-4f48-8d16-44d3f0a6f186/application: role scope,
   requirements, stack, benefits, on-site Berlin location. Read 2026-09-02.
8. config/profile.yaml, dream_companies entry for Peec AI and dream_rule: internal curated note
   and waiver logic, not an external source about the company.

This dossier is a draft. Santiago should sanity-check the visa/sponsorship question directly
with Peec AI before leaning on this role in application materials, since no source here
confirms non-EU sponsorship.
