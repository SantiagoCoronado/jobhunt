# Splitero

Draft dossier for Santiago's review. Researched: 2026-09-01. Target role: job id 36819, Applied AI
Engineer (https://job-boards.greenhouse.io/splitero/jobs/5162723008, posted band 135,000 to
175,000 USD, location "Remote").

## 1. Snapshot

Splitero is a San Diego based fintech offering home equity investments (HEI), cash to homeowners
in exchange for a share of future home value, no monthly payments, no debt. Founded 2021.
Approximately 39 to 107 employees depending on source (BuiltIn lists 39 total, other people-data
aggregators estimate higher; treat headcount as approximate, unverified precisely).
[Splitero on BuiltIn](https://builtin.com/company/splitero) Operating in 17 states as of August
2026. [HousingWire, Aug 2026](https://www.housingwire.com/articles/splitero-home-equity-investment-expansion-five-new-states/)
Raised a $11.7M Series A led by Fiat Ventures plus Gemini Ventures, Joint Effects, PBJ Capital,
and others; National Mortgage News, no date on the search snippet, treat as unverified for exact
date. [National Mortgage News](https://www.nationalmortgagenews.com/news/equity-share-fintech-splitero-receives-multimillion-dollar-investment)
Since raised very large institutional capital commitments for its HEI portfolio: a $350M purchase
commitment from Blue Owl Capital managed funds announced December 2024, and a $283.3M rated HEI
securitization with Blue Owl, Antarctica Capital, and Kingsbridge Investment Partners that closed
November 25, 2025. [Nasdaq press release](https://www.nasdaq.com/press-release/splitero-funds-managed-blue-owl-and-antarctica-capital-close-2833-million-home-equity)
[HousingWire](https://www.housingwire.com/articles/splitero-350m-funding-blue-owl-capital/)

## 2. Core narrative

Splitero is not a typical venture-funded consumer fintech chasing a Series B. It is a young HEI
originator (product category itself is only a few years old across the industry) that has pivoted
its growth story toward institutional capital markets: Blue Owl and Antarctica Capital buying
hundreds of millions of dollars of its home equity investments and packaging them into a rated
securitization. That is the story to lean on: Splitero is scaling a new asset class from
origination-stage startup into something Wall Street will buy in bulk, and it is doing that while
still small enough (roughly a few dozen employees) that one applied AI hire embedded with sales,
underwriting, and servicing can move the needle on how the whole operation runs.

## 3. Mission & product

Splitero gives homeowners a lump sum of cash, up to $500,000, in exchange for a share of the
home's future appreciation, with no new debt and no monthly payments, positioned against
traditional HELOCs and cash-out refinancing.
[HousingWire](https://www.housingwire.com/articles/splitero-raises-12m-to-expand-home-equity-investment-operations/)
It operates in 17 US states as of August 2026: Arizona, California, Florida, Idaho, Nevada, New
Jersey, Montana, Missouri, Ohio, Oregon, Pennsylvania, South Carolina, Tennessee, Utah, Virginia,
Washington, and Wyoming. [HousingWire](https://www.housingwire.com/articles/splitero-home-equity-investment-expansion-five-new-states/)
Customers are individual homeowners (B2C); the business model depends on state-by-state licensing
and on institutional capital partners (Blue Owl, Antarctica Capital) that buy or fund the HEI
portfolio. [Nasdaq](https://www.nasdaq.com/press-release/splitero-funds-managed-blue-owl-and-antarctica-capital-close-2833-million-home-equity)
HEI as a category is young and non-standardized: the Consumer Financial Protection Bureau has
publicly warned consumers about HEI disclosure and calculation risk, and a Senate bill (the Home
Equity Lending Integrity Act) would reclassify HEIs as mortgages subject to Truth in Lending Act
disclosure and CFPB oversight, unverified whether it has passed. [search summary, needs primary
source if used in writing; treat CFPB/Senate-bill claim as directionally correct but not
independently re-fetched from a primary government source in this pass]

## 4. Culture & voice

Public-facing culture signals are thin. BuiltIn's company page states the mission line directly
from the company: "we are on a mission to help these homeowners access their home equity without
new debt or monthly payments." [BuiltIn](https://builtin.com/company/splitero) The Applied AI
Engineer posting itself is the clearest voice sample available: it frames the hire as an internal
thought leader on AI capability who partners across product, operations, and business teams,
language that reads more operationally pragmatic than mission-evangelist.
[Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008) No engineering
blog, no distinct social-media voice, and no all-hands or values deck were found in this pass;
mark company voice/tone beyond the job posting itself as unverified.

## 5. Recent news (last ~12 months)

- August 2026: expanded HEI offering to four more states (Idaho, Missouri, Montana, Wyoming),
  bringing total to 17 states. [HousingWire](https://www.housingwire.com/articles/splitero-home-equity-investment-expansion-five-new-states/)
- November 25, 2025: closed a $283.3M rated HEI securitization with Blue Owl Capital managed
  funds, Antarctica Capital, and Kingsbridge Investment Partners, described as the first rated
  securitization of its kind for Splitero. [Nasdaq](https://www.nasdaq.com/press-release/splitero-funds-managed-blue-owl-and-antarctica-capital-close-2833-million-home-equity)
- December 2024: announced a $350M capital commitment from Blue Owl Capital managed funds to
  purchase Splitero HEIs, alongside expansion into Tennessee and Virginia.
  [HousingWire](https://www.housingwire.com/articles/splitero-350m-funding-blue-owl-capital/)
- A separate $300M commitment from Antarctica Capital was also reported; exact date unverified in
  this pass, treat as directionally consistent with the securitization partnership above.
- A law firm (Wilshire Law Firm) is soliciting homeowners for a potential class action, examining
  whether Splitero's HEI contracts function like undisclosed home-secured loans. This is
  explicitly an investigation and client-solicitation page, not a filed lawsuit: "No court has
  made a final determination, and the matter remains an investigation into these questions."
  [Wilshire Law Firm](https://wilshirelawfirm.com/blog/splitero-lawsuit/) No filed class action or
  regulatory action against Splitero was found in this pass; treat litigation status as
  unverified beyond "under law-firm investigation as of this research."

## 6. Engineering & AI direction

No public engineering blog was found. What is known comes from the Applied AI Engineer posting
itself: the team works in Python and TypeScript/Node.js, deploys on AWS and Vercel, uses
PostgreSQL, and is already using Claude Code, Cursor, and GitHub Copilot as day-to-day AI coding
tools. [Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008) The AI
mandate for this specific role is applied and workflow-first, not research: ship production LLM
features on OpenAI and Anthropic APIs, RAG pipelines, and agentic frameworks (LangChain,
LlamaIndex), plus low/no-code orchestration (n8n, Make, Zapier), aimed at automating the
Salesforce-heavy sales, underwriting, closing, and servicing workflows the company already runs
on. [Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008) The role
reports directly to the VP of Product and Engineering, sits embedded in product engineering, and
is explicitly framed as the company's first dedicated applied AI hire acting as internal thought
leader on where AI fits the business. [Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008)

## 7. Work location and employment reality: can Splitero hire someone based in Mexico?

This is the load-bearing question and the honest answer, based on public sources, is that this
role is very likely US-only in practice, even though the posting itself never states a country
restriction.

Evidence pointing to US-only:
- The Greenhouse application for this exact role includes a required screening question: "Are you
  authorized to work in the United States without employment sponsorship?"
  [Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008) Greenhouse boards
  sometimes carry this question as EEOC boilerplate even on globally-open roles, so on its own it
  is not conclusive, but combined with the rest of the evidence here it reads as a real gate.
- Every other open role on Splitero's Greenhouse board is listed as either "Remote" (US
  convention, no country named) or a hybrid San Diego, CA role. No role on the board names a
  non-US location or an international/LATAM scope.
  [Splitero Greenhouse board](https://job-boards.greenhouse.io/splitero)
- Benefits described (premium healthcare from day one, US-style flexible PTO, WeWork access,
  monthly cell/internet stipend) match standard US employee benefits packaging, not a contractor
  or EOR arrangement typically used to hire from Mexico. [Greenhouse posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008)
- Splitero's core product, home equity investments, is a state-licensed consumer financial
  product; the company operates in 17 named US states and its growth story is built on US
  institutional capital (Blue Owl, Antarctica Capital) buying US-originated HEIs.
  [HousingWire](https://www.housingwire.com/articles/splitero-home-equity-investment-expansion-five-new-states/)
  This is a heavily US-regulated business end to end, sales through servicing, which makes a
  Mexico-based employee for a role embedded in sales/underwriting/servicing workflows a harder fit
  operationally even if not explicitly barred.
- No evidence was found of Splitero using an employer-of-record service or otherwise hiring
  internationally. A direct search for Splitero plus EOR/Deel/international hiring returned no
  matches.
- LinkedIn profiles found for named Splitero employees (a handful sampled) list San Diego as their
  location; this is a small, non-representative sample and does not by itself prove a US-only
  policy, but it is consistent with everything else above.
  [search result, unverified beyond the sampled names]

What would change this assessment: a public statement from Splitero explicitly welcoming
international or LATAM remote candidates (none found), or evidence of non-US employees on
LinkedIn at scale (not found in this pass, worth a deeper LinkedIn search before applying).

Bottom line: nothing in the JD text says "US only" in as many words, but every other signal
(screening question, board-wide US-only locations, benefits shape, and the regulated,
US-state-licensed nature of the business) points the same direction. Treat this as a US-based
role in practice unless Splitero says otherwise directly, and confirm work-location flexibility
explicitly before investing significant time in the application. Santiago is TN-visa eligible for
US employment but not currently US-resident; that gap should be surfaced early rather than
discovered late in the process.

## 8. Why-fit angles for Santiago

Best hook: Santiago has already built the exact shape of this role twice, not as a hire but as
the founder who needed it. At Online Basics he built the internal operations platform (pricing
dashboard, inventory admin, discounting and ad-campaign tooling) that ran an $8M revenue business
end to end. At Pragma AI he is currently shipping the same category of work Splitero is hiring
for: LLM workflow automation, a RAG "company brain," and conversational agents built for
non-technical operators inside a real operating business, not a research lab. That is a closer
match to "sit inside sales, underwriting, closing, and servicing and automate their workflows"
than almost anything else on his resume.

Supporting angles:
- Direct tool overlap: the JD names OpenAI/Anthropic APIs, RAG, agentic frameworks, n8n/Make/
  Zapier-style orchestration, Python and TypeScript, Claude Code and Cursor. Santiago's Pragma AI
  and Plutus/Kairos work covers RAG (scoped retrieval, citation gating), agent tool-use and MCP,
  Python/FastAPI and TypeScript/React, and he already builds inside Claude Code daily.
- Salesforce-adjacent operations automation: the specific mandate (automate sales, underwriting,
  closing, servicing workflows) mirrors what he built for Online Basics's internal operators
  (pricing, inventory, discounting, alerting used daily by 4 operators) and for Pragma AI clients
  (quoting, reporting, onboarding, collections automation).
- Founder-to-embedded-operator framing: this is explicitly a role reporting to a VP and embedded
  cross-functionally, not a research seat; his profile's Family B fit (deployment, enablement,
  stakeholder management) applies directly.

Honest concerns and watch-outs:
- Work location, addressed at length in section 7. This is the real risk on this application, not
  a stretch skill gap.
- No fintech/proptech-regulated-lending experience specifically; the JD lists this as preferred,
  not required, so it is a minor gap, not a blocker.
- No public engineering blog or culture material to verify team size, engineering practices, or
  actual maturity of the "AI stack" beyond the job posting's own claims; company is still small
  (double-digit to low-hundred employees) and this would be Splitero's first dedicated applied AI
  hire, which is upside (green field, high leverage) but also risk (no existing AI infra or
  playbook to lean on, and reporting structure/support depends entirely on one VP).
- HEI as a category is under active regulatory attention (CFPB warnings, a pending Senate bill,
  and at least one law firm actively soliciting clients for a potential case against Splitero
  specifically). This is a reputational and business-continuity risk worth naming honestly, not a
  reason to avoid applying, but something to ask about if a conversation happens.

## 9. Application-question angles

Why this company: lead with the applied, embedded nature of the role, not the HEI product pitch.
Santiago has run this exact function before, building the internal automation and tooling layer
that operators actually use, for his own $8M business and for Pragma AI's clients now. Mention
that concretely rather than restating Splitero's mission back to them.

Why you fit: name the overlap directly, RAG, agentic workflows, and automation tooling shipped in
production (Pragma AI's RAG "company brain," Online Basics's internal ops platform), and that he
is used to being the first or only person building this kind of system inside a real operating
business, which is what this role is (Splitero's first dedicated applied AI hire).

Anything else: if asked, be direct about work location rather than let it surface as a surprise
later: confirm early whether this role can in fact be filled from Mexico, given every other
Splitero posting is US-located and the application itself asks about US work authorization.

## 10. Sources

- researched: 2026-09-01
- [Greenhouse: Applied AI Engineer posting](https://job-boards.greenhouse.io/splitero/jobs/5162723008), primary JD text: responsibilities, requirements, comp band, benefits, screening question, tools/stack, reporting line
- [Greenhouse: Splitero jobs board](https://job-boards.greenhouse.io/splitero), all open roles and their listed locations
- [BuiltIn: Splitero company page](https://builtin.com/company/splitero), headcount, founding year, HQ, mission line
- [HousingWire: five new states expansion, Aug 2026](https://www.housingwire.com/articles/splitero-home-equity-investment-expansion-five-new-states/), 17-state footprint, product description
- [HousingWire: $12M raise](https://www.housingwire.com/articles/splitero-raises-12m-to-expand-home-equity-investment-operations/), business model description (up to $500K, no monthly payments)
- [HousingWire: $350M Blue Owl commitment](https://www.housingwire.com/articles/splitero-350m-funding-blue-owl-capital/), December 2024 capital commitment, Tennessee/Virginia expansion
- [Nasdaq press release: $283.3M securitization](https://www.nasdaq.com/press-release/splitero-funds-managed-blue-owl-and-antarctica-capital-close-2833-million-home-equity), November 25 2025 close, Blue Owl/Antarctica/Kingsbridge partners
- [National Mortgage News: Series A](https://www.nationalmortgagenews.com/news/equity-share-fintech-splitero-receives-multimillion-dollar-investment), $11.7M Series A, Fiat Ventures lead, investor list
- [Wilshire Law Firm: Splitero investigation page](https://wilshirelawfirm.com/blog/splitero-lawsuit/), confirms this is a law-firm client-solicitation investigation, not a filed lawsuit
- `config/profile.yaml`, `resume/master_resume.yaml`: Santiago's background used for fit angles (read, not web sources)

Not independently re-verified in this pass and flagged as such above: exact current headcount
(sources disagree, 39 vs. 107), exact Series A close date, CFPB/Senate bill claims (sourced only
from an aggregated web-search summary, not a primary CFPB or Congress.gov page), and whether any
Splitero employee is genuinely based outside the US (sampled from a small, non-representative set
of LinkedIn profiles). Splitero's own site (splitero.com) returned HTTP 403 to automated fetches
in this pass and could not be read directly; the About/culture sections in this dossier lean on
BuiltIn and the job posting instead.
