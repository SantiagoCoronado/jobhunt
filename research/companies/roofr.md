# Roofr

## 1. Snapshot
Roofr builds an all-in-one roofing CRM (instant estimates, aerial measurements, digital proposals, payments, material ordering) for small and growing roofing contractors. Founded 2016, San Francisco HQ with a Toronto office, fully remote-first (~300 people, no central office), Y Combinator alum (2017), raised a Series B in January 2025 led by TCV with participation from ABC Supply, Crosslink Capital, Euclid Ventures, MGFO, and i2BF (amount undisclosed). Serves over 12,000 roofing companies.

## 2. Core narrative
Roofr was started by a third-generation roofer (Richard Nelson) and a CTO co-founder (Kevin Redman) who built the product by talking directly to roofers in Facebook groups, on calls, and at trade shows, then consolidated a fragmented toolchain (measurements, proposals, payments, material ordering) into one CRM. It has since scaled from about 10 to roughly 150-300 people while staying fully remote and explicitly hiring contract engineers across Mexico, Colombia, Argentina, and Brazil, and it markets itself hard on "people-first," mental-health-forward remote culture (Great Place to Work and Built In "best remote places to work" recognitions in 2025).

## 3. Mission & product
- Stated mission: "To be the trusted foundation for roofing professionals to build their success." (roofr.com/about)
- Core product is an all-in-one roofing CRM: lead capture and pipeline, satellite/aerial roof measurements, instant estimates, branded digital proposals, invoicing and payments, material ordering (including an ABC Supply integration for real-time pricing), and automations (job-status changes, proposal updates, task assignment). (roofr.com/crm, roofr.com more-info page)
- Customer base: small and growing roofing contractors, not enterprise; over 12,000 roofing companies use the platform. (Series B announcement, roofr.com/blog)
- Business model: SaaS with a free CRM tier and paid tiers layering on estimating, measurement, and payment tools (roofr.com/more-info/roofing-software-for-small-businesses).
- Product cadence: twice-yearly "Roofr Builds" release drops; Fall 2025 drop shipped a unified inbox (Gmail sync, job-specific messaging, automated follow-ups), an upgraded Measurements page, and Work Orders. (roofr.com/roofr-builds)

## 4. Culture & voice
- Six stated values: think unconventionally, utilize positive discontent, welcome collaboration, high performance, be customer obsessed, embody resiliency. (roofr.com/about)
- Fully remote, no central office, described in its own careers copy as "work from wherever you work best... if that happens to be from your couch in your PJs, we don't judge." (4dayweek.io/company/roofr, sourced from Roofr's careers materials)
- Concrete remote-culture mechanics: rotating monthly "laundry day" (a paid Friday off), mandatory first week of PTO for new hires, flexible/unlimited PTO, year-end company shutdown, home-office and internet stipend, biannual company retreats. (4dayweek.io; roofr.com careers)
- January 2025: recognized as a Built In Top 100 Best Midsize Place to Work in San Francisco, Built In Top 100 Best Remote Midsize/Overall Place to Work, and a Great Place to Work Canada "Best Workplace for Young Talent." Roofr also says it was named a 2025 Best Workplace for Mental Health, treating mental health days as a norm rather than a perk. (roofr.com/blog/roofr-earns-dual-recognition...)
- Internal quotes lean earnest, not irreverent: an engineering manager says the culture lets him "focus on doing work I love without worrying about unresolved issues," and Talent Acquisition leadership calls it "the healthiest work environment" in a 15-year career. (same source)

## 5. Recent news (last ~12 months)
- January 28, 2025: closed a Series B led by TCV, with ABC Supply, Crosslink Capital, Euclid Ventures, MGFO, and i2BF participating (amount undisclosed); headcount had grown from about 10 to 150+ since the prior round, with plans to keep hiring across product, engineering, sales, support, and marketing. (roofr.com/blog/roofr-raises-series-b-funding-from-tcv-and-abc-supply-to-expand-roofing-crm; prnewswire.com)
- January 28, 2025: dual recognition as a top remote workplace (Built In) and a Canada Great Place to Work for young talent. (roofr.com/blog/roofr-earns-dual-recognition-as-a-top-place-to-work-for-its-people-first-culture)
- 2025-2026: launched "Roofr Builds," a bi-annual bundled product-release format; the Fall 2025 edition added a unified homeowner inbox (Gmail sync, job-specific messaging, automated follow-ups), an upgraded Measurements page, Work Orders, an ABC Supply real-time pricing integration, a smarter Instant Estimator, and custom invoice numbering. (roofr.com/roofr-builds; roofr.com/product-blog/new-year-new-features-heres-whats-happening-at-roofr)
- The CEO has publicly teased 3-4 upcoming AI features on the roadmap, including AI data reporting and an AI lead-capture agent (specifics and ship dates not yet confirmed in primary sources at time of research). (roofingcontractor.com/articles/101474-roofr-unveils-roofr-builds-bi-annual-product-drops)

## 6. Engineering & AI direction
- Backend: PHP/Laravel following domain-driven design patterns; frontend: React with Redux, SCSS styling. (himalayas.app/companies/roofr/tech-stack; the Senior Frontend Engineer - Contract job posting itself)
- Supporting infra/tools referenced in third-party tech-stack listings: Varnish, Cloudflare, Amazon CloudFront, Fastly, Segment (analytics), HubSpot, Lever. Treat as directionally accurate rather than exhaustive since it is a third-party aggregation, not a company-published stack page. (himalayas.app/companies/roofr/tech-stack)
- No dedicated public engineering blog was found; engineering context comes from job postings and third-party culture write-ups rather than primary technical writing.
- AI direction is product-facing and customer-value oriented so far (AI-assisted measurements/roof visualization referenced in press, plus teased AI data reporting and an AI lead-capture agent) rather than a public AI-infrastructure or platform-engineering narrative. (roofingcontractor.com/articles/101474-roofr-unveils-roofr-builds-bi-annual-product-drops)
- The company explicitly hires contract engineers from Mexico, Colombia, Argentina, and Brazil alongside its US/Canada employee base, which matches this job's contract-from-Mexico framing. (4dayweek.io/company/roofr)

## 7. Why-fit angles for Santiago
- Strongest hook: Santiago spent five years running Online Basics, an $8M multi-marketplace ecommerce business, and personally built its internal operations platform: a React front end on AWS backed by SQL and Python ETL, with a pricing dashboard, inventory admin, and cross-marketplace tooling used daily by operators. That is functionally the same shape of problem as Roofr's CRM: giving a non-technical, operationally busy small-business user (a roofer instead of a marketplace seller) one clean web app to run leads, pricing, jobs, and payments instead of juggling spreadsheets and disconnected tools. He has built the exact category of product Roofr sells, not just used similar technologies.
- Direct stack match: the posting asks for strong JavaScript, React + Redux, SCSS, REST API integration, and automated testing, which lines up with his React 18/19, TypeScript, Vite, Tailwind, Playwright/Vitest experience across Eugenia.ai, the Hydrel portal, Plutus, and Kairos (master_resume.yaml). Redux specifically is not on his current resume; call this out honestly rather than overclaim it.
- Location and format fit is clean: this is a Mexico-based contract role, and Roofr openly staffs contract engineers out of Mexico, Colombia, Argentina, and Brazil, so the arrangement is a known pattern for them, not an edge case.
- Founder-to-founder resonance: Roofr's own story (a domain practitioner plus a technical co-founder building for an underserved, non-technical small-business customer) mirrors Santiago's founder background at Online Basics and Eugenia.ai, both built by talking directly to end users and shipping internal tools that ran the business.
- Concerns/watch-outs: it is a contract role with no listed pay (comp is unverified, follow the profile's annualize-and-floor rule once a number appears); Redux is a real skill gap versus his more recent Zustand/Context-based React work and should be framed as "comfortable learning it" rather than claimed as existing expertise; the AI angle Santiago usually leads with (RAG, agents, LLM workflows) is not what this specific req is testing, this is a pure frontend/CRM engineering role, so cover letters should not force an AI pivot here.

## 8. Application-question angles
- Why this company: lead with the product-shape match, not generic praise for roofing. Santiago has already built the thing Roofr sells (an internal, non-technical-user-facing operations app that replaces spreadsheets and disconnected tools for a small operator business), just for ecommerce sellers instead of roofers. Frame Roofr as a company solving a familiar problem in an adjacent, unglamorous, operationally real industry.
- Why you fit: anchor on the React/CRM-building overlap (Online Basics internal platform, Eugenia.ai's full-stack build, the Hydrel portal's design-system and testing discipline) rather than the AI portfolio; the req is explicitly senior frontend, SDLC ownership, testing, and mentoring, which matches his track record of owning full builds end to end on small teams.
- Anything else: the honest note to add if asked is that he is comfortable and fast learning Redux specifically (he has used comparable state-management patterns, Zustand and Context, at similar scale) rather than pretending prior Redux depth. Optionally mention the Mexico-based contract fit is a known, supported arrangement for Roofr, not something they'd need to figure out for the first time.

## 9. Sources
- https://roofr.com/about: mission statement, founding story, values
- https://roofr.com/blog/roofr-raises-series-b-funding-from-tcv-and-abc-supply-to-expand-roofing-crm: Series B details, investors, headcount growth, customer count
- https://www.prnewswire.com/news-releases/roofr-raises-series-b-funding-from-tcv-and-abc-supply-to-expand-roofing-crm-302362118.html: corroborates Series B announcement
- https://roofr.com/blog/roofr-earns-dual-recognition-as-a-top-place-to-work-for-its-people-first-culture: 2025 workplace awards, culture quotes
- https://4dayweek.io/company/roofr: remote policy, team distribution, contract hiring in Mexico/Colombia/Argentina/Brazil, benefits, values
- https://roofr.com/crm: CRM product feature description
- https://roofr.com/more-info/roofing-software-for-small-businesses: product/business model description
- https://roofr.com/roofr-builds: bi-annual product release cadence, Fall 2025 features
- https://roofr.com/product-blog/new-year-new-features-heres-whats-happening-at-roofr: recent feature launches
- https://www.roofingcontractor.com/articles/101474-roofr-unveils-roofr-builds-bi-annual-product-drops: Roofr Builds format, teased AI roadmap features
- https://himalayas.app/companies/roofr/tech-stack: third-party aggregation of Roofr's tech stack (Laravel, React, Redux, SCSS, supporting infra)
- https://jobicy.com/jobs/151742-senior-frontend-engineer-contract: the target job posting itself (Senior Frontend Engineer, Contract, Mexico): stack, responsibilities, team context
- https://builtin.com/company/roofr/offices: HQ location corroboration (San Francisco, plus Toronto office)

researched: 2026-08-27
