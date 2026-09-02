# Constructor (constructor.io / constructor.com)

## Snapshot
AI-native ecommerce product search and discovery platform ("Commerce Reasoning Engine") for enterprise retailers and brands, including retail media (sponsored placements); Series B, $85M+ raised, ~$550M valuation (June 2024); 400+ employees across 40 countries, 100% remote-first; HQ not disclosed on site, operates as a distributed/remote company. (Sources: constructor.com/about, prnewswire Series B release)

## Core narrative
Constructor is a specialist, not a generalist: "product discovery for commerce is all we do," and it has parlayed that focus into back-to-back Leader placements in the Gartner Magic Quadrant for Search and Product Discovery, plus Leader status from Forrester and IDC, largely by pairing AI search/recommendations with what it calls "glassbox AI," explainable ranking rather than a black box. Retail Media is one of its newest product lines (an ads layer that lets brands buy placement inside a retailer's own search, browse, and recommendation results), built by a small, newer team inside a company that just posted 82% customer growth and 45% headcount growth in FY26.

## Mission & product
- Core product: an AI ranking/reasoning engine that powers search, autosuggest, browse, recommendations, collections, and quizzes for ecommerce sites, explicitly optimized for revenue, conversion, and profit rather than generic relevance. (constructor.com)
- Newer agentic layer: AI Shopping Agent (ASA, consumer-facing conversational shopping assistant) and Product Insights Agent (PIA, genAI tool for product detail pages), both listed as "award-winning" on the company site; ASA is also sold via AWS Marketplace's AI Agents and Tools category as of November 2025. Merchant Intelligence Agent (MIA), a conversational tool for merchandising teams, launched March 2026. (destinationcrm.com; prnewswire MIA release)
- Retail Media Suite: starts with Sponsored Listings, AI-ranked ad placements inside search results, browse pages, and recommendations, sold to brands, managed by retailers, with a shared dashboard giving retailers and advertisers separate profiles to manage listings, campaigns, and bids in real time. This is the product line the open role builds. (constructor.com/solutions/retail-media, constructor.com/blog/introducing-constructors-retail-media-suite)
- Business model: enterprise B2B SaaS sold to retailers and brands; customers named publicly include Sephora, Petco, American Eagle, Birkenstock, Target Australia, The Very Group, home24, Grove Collaborative, and Fisheries Supply. (prnewswire FY26 release, aithority interview)
- Recognition: named a Leader in the 2026 Gartner Magic Quadrant for Search and Product Discovery (furthest in vision, highest in execution, second year running), #1 in three of five Gartner Critical Capabilities use cases, Leader in Forrester Wave Q3 2025, IDC MarketScape 2025-2026, and the only vendor named a Gartner Peer Insights Customers' Choice in 2025. (prnewswire, finance.yahoo.com)

## Culture & voice
- Stated values (careers page): "empathetic decision-making" (getting to the right answer without ego), ownership through to shipped impact, and enjoying the work and problems. (constructor.com/about/careers)
- 100% remote-first, unlimited PTO with an explicit nudge to take at least 3 weeks, ~99% coverage of US health premiums, $500/year learning stipend, paid parental leave, company laptop and remote-work stipend, stock options. (constructor.com/about/careers, theorg.com job listing)
- Careers page invites unsolicited outreach to the talent team if no matching role is posted, a lightly informal, conversation-first hiring tone.
- Brand voice leans confident and technical rather than folksy: homepage copy talks about the product "reasoning" rather than "personalizing" and repeatedly stresses "glassbox AI" (explainable, not black-box) as a differentiator, backed by customer quotes on transparency and a 98.5% client retention stat. (constructor.com)

## Recent news (last ~12 months)
- November 2025: AI Shopping Agent listed in the new AWS Marketplace AI Agents and Tools category. (destinationcrm.com)
- March 12, 2026: FY26 results announced, 82% customer growth, 96% gross revenue retention, 116% EMEA revenue growth, 322 billion product-discovery interactions powered (266% up over two years), over 10,000 personalized shopping experiences per second, 45% global headcount growth; CEO Eli Finkelshteyn quoted on AI needing to "understand intent and drive clear, measurable outcomes," not just demo well. Also named #10 most innovative retail company by Fast Company that period. (prnewswire.com/news-releases/constructor-reports-82-customer-growth...)
- March 2026: Merchant Intelligence Agent (MIA) launched, a conversational AI tool giving merchandising teams instant insight and faster action on merchandising decisions, the latest addition to the agentic product suite alongside ASA and PIA. (prnewswire MIA release)
- 2026: Constructor named a Leader in the Gartner Magic Quadrant for Search and Product Discovery for the second consecutive year, and included in the "2026 Agentic List" (120 companies) as the only ecommerce search and discovery company on it; also won 3 Gold "Company of the Year" awards across 3 Stevie Awards programs. (finance.yahoo.com, prnewswire Stevie release)
- CEO Eli Finkelshteyn appeared on theCUBE's NYSE Wired / Mixture of Experts AI Agent Conference coverage in 2026. (YouTube listing found via search)
- No Series C or new funding round has been publicly announced since the $25M Series B (June 2024, led by Sapphire Ventures, valuing the company at $550M, total raised $85M+). Treat funding stage as unchanged since 2024 absent a newer disclosure. (prnewswire Series B release, crunchbase)

## Engineering & AI direction
- The Retail Media Full-Stack Engineer role itself: TypeScript/React on the frontend, Python/FastAPI (also Flask/Django mentioned in the broader posting) on the backend, SQL/relational databases (MySQL/PostgreSQL), cloud on AWS (also Azure/GCP mentioned), ad-tech background called out as a plus. Team is described as new, building the customer-facing Retail Media dashboard for both retailers and brands from early stages. (theorg.com job listing, torre.ai posting)
- Company-wide engineering org: described (via search-indexed release notes) as organized into roughly 15 globally distributed teams shipping continuous production changes; a public "This Week in Engineering" release log exists at releases.constructor.io. (search result summary; not independently fetched in full, treat team-count as lower-confidence)
- Public engineering writing exists on a Medium publication ("Constructor Engineering"), including at least one piece on feature store design for their ML ranking systems (could not fetch full content directly due to a 403 on this pass; title and author confirmed via search only). Flag for a human follow-up read before quoting technical specifics from it.
- Core AI investment is in ranking/relevance ML (the "Commerce Reasoning Engine") plus a newer layer of generative/agentic products: AI Shopping Agent, Product Insights Agent, and Merchant Intelligence Agent, all pitched around measurable revenue outcomes and explainability ("glassbox AI") rather than novelty.
- GitHub presence exists at github.com/Constructor-io (public SDKs/client libraries per search index; not deep-audited this pass).

## Why-fit angles for Santiago
- Best hook: direct ecommerce-operator domain match. He ran Online Basics for five years, an $8M USD multi-marketplace ecommerce business on Amazon and Mercado Libre, and personally built its internal pricing dashboard, inventory admin, and ad-campaign tooling, on a React frontend with Python/SQL ETL pipelines behind it. That is close to a literal description of the Retail Media dashboard this role builds: a merchant/advertiser-facing tool for pricing, campaign, and discounting decisions. Few candidates can say they were the retailer/seller on the other side of a tool like this.
- Secondary hook: stack match is close to exact, TypeScript/React frontend over Python/FastAPI backend on AWS, which is precisely his Plutus and Online Basics stack (React 18/TS/Vite frontend, FastAPI/Python backend, AWS). Low ramp-up risk on tooling.
- The Retail Media team is explicitly new and building the dashboard from an early stage, which fits his founder/0-to-1 pattern (Eugenia.ai concept-to-acquisition, Online Basics internal platform built from scratch) better than joining a mature, already-scaled team would.
- Honest concerns: the wider job posting lists a GMT+00:00 to GMT+03:00 timezone band on at least one mirrored listing (theorg.com), which would conflict with Mexico City (GMT-6) if that band is a hard requirement; the Torre listing itself did not state a timezone restriction, so this needs direct confirmation before leaning on the role in an application. Company culture research surfaced no explicit LATAM hiring signal (no Mexico or LATAM office/remote language found on the careers page); confirm work-authorization/contractor structure once in conversation. No independent confirmation was found of the engineering blog's technical depth (Medium 403'd on fetch), so do not over-claim familiarity with their specific ML architecture in an application.

## Application-question angles
- Why this company: lead with the operator-not-just-engineer angle, he has sat in the exact seat this dashboard serves (a multi-marketplace seller doing pricing, inventory, and ad-campaign decisions off internal tooling), not just built similar software for someone else.
- Why you fit: pair the stack match (React/TS + Python/FastAPI/AWS, used daily at Online Basics and in his own Plutus project) with the fact he built that kind of tool from zero for an $8M revenue business, so he understands both the engineering and the merchandising/ad-ops decisions the dashboard needs to support.
- Anything else: keep it to one line if used at all, that his domain experience is on the seller/retailer side of retail media, not the ad-tech vendor side, which is a genuine, differentiated angle rather than a generic "I'm passionate about ecommerce" line. Do not reach for the AI-agent products (ASA/PIA/MIA) as a fit hook for this specific role since the posting is about the dashboard, not the agentic product line.

## Sources
- https://constructor.com/about (company overview: product, headcount, remote-first)
- https://constructor.com/about/careers (values, benefits, hiring philosophy)
- https://constructor.com/ (homepage: product positioning, "glassbox AI" voice)
- https://constructor.com/solutions/retail-media (Retail Media Suite: Sponsored Listings, dashboard for retailers/advertisers)
- https://constructor.com/blog/introducing-constructors-retail-media-suite (Retail Media Suite introduction, found via search)
- https://apply.workable.com/constructor-1/j/9561B03510/ (canonical posting: role scope, stack, comp band, benefits)
- https://theorg.com/org/constructor-io/jobs/full-stack-engineer-retai-6613c957 (mirrored posting: requirements, timezone band GMT+0 to +3, comp)
- https://torre.ai/jobs/qdP99pLr (the actual applied-to posting, job id 18645; confirmed appears active/open, no closure indicator, as of this research)
- https://www.prnewswire.com/news-releases/constructor-reports-82-customer-growth-in-fy26-with-its-platform-powering-322-billion-shopping-interactions-302711286.html (FY26 metrics, CEO quote, dated March 12, 2026)
- https://www.destinationcrm.com/Articles/CRM-News/CRM-Across-the-Wire/Constructors-AI-Shopping-Agent-Now-Available-in-AWS-Marketplace-AI-Agents-and-Tools-Category-170718.aspx (AWS Marketplace listing, November 2025)
- https://www.prnewswire.com/news-releases/constructor-unveils-merchant-intelligence-agent-mia-bringing-instant-insight-and-faster-action-to-ecommerce-merchandising-302723004.html (MIA launch, March 2026)
- https://finance.yahoo.com/technology/ai/articles/constructor-named-leader-gartner-magic-163600819.html (Gartner Magic Quadrant Leader placement, 2026)
- https://www.prnewswire.com/news-releases/constructor-has-the-most-1-rankings-in-gartner-critical-capabilities-for-search-and-product-discovery-report-302821039.html (Gartner Critical Capabilities #1 rankings)
- https://www.prnewswire.com/news-releases/ai-innovation-at-constructor-leads-to-3-gold-company-of-the-year-wins-across-3-stevie-awards-programs-302861732.html (Stevie Awards, 2026)
- https://www.prnewswire.com/news-releases/constructor-raises-25m-series-b-led-by-sapphire-ventures-tripling-valuation-to-550m-302174068.html (Series B funding, June 2024, most recent disclosed round)
- https://www.crunchbase.com/organization/constructor-io (funding record cross-check, no Series C found)

researched: 2026-08-27
