# Rimini Street (RMNI)

Draft dossier for Santiago's review. Researched 2026-08-11.

## 1. Snapshot

Publicly traded (Nasdaq: RMNI, listed October 2017), founded 2005. Third-party enterprise
software support and, since 2025, "Agentic AI ERP solutions" provider, the leading
alternative-support vendor for Oracle, SAP and VMware. Over 1,980 employees in 23 to 30
countries (figures vary slightly by source/date) [10, 11]. Q2 2026 revenue $111.1M, up 6.7%
year over year [4]. Headquartered in Las Vegas, Nevada; this specific req is remote.

## 2. Core narrative

Rimini Street spent 15 years fighting Oracle in court over the legality of its
lower-cost, third-party support model, a fight that ended in a July 2025 settlement [8].
It is now using that stabilized position, plus a large existing base of 3,132 enterprise
support clients [4], to sell a second product line: "Agentic AI ERP," AI agents layered on
top of the SAP/Oracle/JD Edwards systems it already supports, sold to the same buyers as
a way to modernize old ERP stacks without a costly RISE/S4HANA migration [3, 9]. The
company is, in effect, trying to convert a 20-year support relationship into an AI upsell.

## 3. Mission & product

Three service pillars ("Rimini Smart Path"): Support (the original, still-dominant
third-party maintenance business for Oracle, SAP, VMware and other systems of record),
Optimize, and Innovate [9]. The newest layer is a set of agentic AI products announced in
2025 to 2026: Rimini Agentic UX (an AI-driven UX layer over existing ERP screens, launched
December 2025), Rimini AgentWorks (an AI agent lifecycle/delivery service), and Rimini
Govern for AI (agent governance/security, launched late July 2026) [6, 9]. Customers are
Fortune Global 100, Fortune 500, midmarket, public sector and government organizations;
the company has signed 6,300+ contracts to date [9, job posting]. Business model: recurring
support subscriptions (its core, still the large majority of revenue) plus newer
professional-services and AI-agent engagements sold into that same install base.

## 4. Culture & voice

Glassdoor: 3.2/5 overall (390 reviews), 3.5 work-life balance, 3.0 culture and values, 2.9
career opportunities, 3.6 compensation and benefits [12]. Recurring positive theme: flexible,
work-from-home, family-friendly. Recurring negative themes: "nepotistic culture," frequent
reprioritization ("fire drills"), CEO-centralized leadership, and complaints about layoffs
handled abruptly [12]. Public-facing voice (careers page, press releases) is standard
enterprise-B2B: "Four Cs" values (Company, Colleagues, Clients, Community), a company
foundation that has supported 425+ charities across six continents [job posting]. No
distinctive irreverent or engineering-led public voice; social presence and blog are sales-
and analyst-oriented, not a developer-culture brand.

## 5. Recent news (last ~12 months)

- July 7 to 9, 2025: Rimini Street and Oracle signed a confidential settlement ending the
  15-year "Rimini II" litigation (Case No. 2:14-cv-01699). Rimini Street received about
  $37.9M of the roughly $58.7M in fees/costs it had paid Oracle in late 2024. The deal also
  formalizes wind-down of Oracle PeopleSoft support services by July 31, 2028 [8].
- December 3, 2025: launched Rimini Agentic UX, an AI layer for ERP process execution [6].
- July 30, 2026: launched Rimini Govern for AI, an AI-agent governance/security managed
  service, the third piece of its agentic AI suite alongside AgentWorks and Agentic UX [6].
- July 30, 2026: reported Q2 2026 results, revenue $111.1M (+6.7% YoY), adjusted revenue
  (ex-PeopleSoft) $108.0M (+10.0% YoY), gross margin 60.9%, cash $123.4M, debt paid down to
  $48.4M, active clients 3,132 (+2.4% YoY). FY2026 guidance: revenue growth of 4 to 6% [4].
- Restructured its North American sales organization into a "hunters" (new logos) and
  "farmers" (retention/cross-sell) model during 2026, with management acknowledging
  higher-than-desired sales rep turnover as the AI pitch requires more technical
  sophistication from sellers [5].
- Employee count has drifted down from a peak of about 2,140 (mid-2024) to about 1,950 to
  1,980 through mid-2026, roughly a 7 to 9% decline, alongside continued revenue growth,
  consistent with margin-focused headcount discipline rather than a announced mass layoff
  [13].

## 6. Engineering & AI direction

Stack signals come from the job posting itself rather than a public engineering blog (Rimini
Street does not appear to run a developer-facing tech blog): production Python plus one of
TypeScript, Java, Go, C#, or Scala; SQL and data modeling; RAG (chunking, embeddings, vector
stores, reranking); agentic platforms named as in scope include AWS Bedrock, Azure AI, Google
Vertex AI, and ServiceNow AI; MCP for tool governance; front end in Angular or React "sufficient
to build or extend the user-facing layer" [job posting]. The AI bet is explicit and recent
(all three named AI products launched between December 2025 and July 2026) and is being sold
as a modernization layer for the ERP systems the company already supports, not a standalone AI
product line independent of the support business [6, 9].

## 7. Why-fit angles for Santiago

Best hook: he has shipped RAG and agentic systems end to end (Pragma AI's "company brain,"
Plutus's LLM research agent and MCP control plane, Kairos's dual Claude Agent SDK / MCP
surfaces) and has run direct client deployments before (Eugenia.ai on-site HOA onboarding,
Pragma AI client diagnostics), which maps onto the forward-deployed engineer's mandate of
embedding with a client, shipping production agentic code inside their stack, and handing off
to support. His founder background also gives him the "own it end to end, including the
unglamorous handover" instinct the posting explicitly asks for.

Honest concerns:
- **Location.** The specific req Santiago found (findwork listing, job id 8831) is scoped to
  "Remote – Singapore" [job posting text, confirmed against Workday req R-102255, same title,
  posted 26 days before this research date]. Rimini Street runs near-identical Forward
  Deployed Engineer (Agentic AI) reqs per region on Workday: Remote United States (R-102260,
  posted 5 days ago, $140k to $180k, "Location: Remote – U.S."), Remote Singapore (R-102255),
  Dubai UAE (R-102256), Remote South Korea (R-102258), and Tokyo (R-102259) [Workday CXS API,
  fetched 2026-08-11]. None of the five live reqs is scoped to Mexico, LATAM, or "Americas"
  broadly; the US req explicitly says "Remote – U.S." and lists benefits "for US employees."
  The Singapore req Santiago has is not fillable from Mexico as posted, and the US req as
  worded also reads as US-resident-scoped rather than Americas-remote. This should be
  confirmed directly with a recruiter before applying to either.
- **ERP depth is weighted, not optional.** Direct SAP or Oracle E-Business Suite / JD Edwards
  experience is called out as "highly valued" and, per the US req's fine print, "required for
  ERP-anchored regional seats." Santiago has no ERP background; his fit rests entirely on the
  "equivalent experience from adjacent disciplines... senior backend engineering with recent
  agentic shipping" carve-out the posting explicitly allows, which is a real but narrower door.
- **Enterprise support culture, not a 0-to-1 shop.** Rimini Street is a 20-year-old, Nasdaq-
  listed support company (60.9% gross margin, 3,132 support clients) layering AI products onto
  an existing sales-led, process-heavy organization, not a startup. Glassdoor culture
  complaints (nepotism, frequent reprioritization, centralized leadership) and the recent sales
  reorg point to a large-company operating rhythm. The Innovation/Forward Deployed team itself
  is closer to a founder-style 0-to-1 pocket (small, newly built, shipping fast on a young
  discipline) inside a much larger, more bureaucratic parent, which is a real but narrower fit
  than the company as a whole.

## 8. Application-question angles

Why this company: lead with the forward-deployed mandate itself, not the parent company. The
role asks for someone who can walk into a client's existing systems (source control, CI/CD,
release governance) and ship a working agent, then stay through cutover and handoff, which is
close to what he already does end to end at Pragma AI and did on-site at Eugenia.ai. Do not
open with Rimini Street's Oracle/SAP support pitch; he is not applying to be a support
consultant.

Why you fit: anchor on one concrete build, not a list. Pragma Brain's retrieval-augmented
"company brain" (scoped retrieval, no-answer gating, citation checks, an eval harness) is the
closest match to the posting's ask for guardrails, evaluation suites, and production
observability. Pair it with Kairos's MCP server as evidence of hands-on agent tool-execution
and governance work, since MCP is named explicitly in the posting.

Anything else: worth a direct, plain question rather than a filler answer, given the location
finding above: confirm whether this specific req, or any Forward Deployed Engineer (Agentic
AI) opening, can be filled from Mexico, since the live postings on Rimini Street's own careers
site are scoped per country (US, Singapore, UAE, South Korea, Japan) with no Mexico or
Americas-wide seat currently open.

## 9. Sources

researched: 2026-08-11

1. Job posting text, findwork listing (job id 8831): https://findwork.dev/nD56ZYQ/forward-deployed-engineer-agentic-ai-at-rimini-street, full req description including "Location and Travel: Remote – Singapore," fetched from local jobs.db.
2. Rimini Street careers site (Workday), US req R-102260: https://riministreet.wd1.myworkdayjobs.com/RiminiStreet/job/Remote-United-States/Forward-Deployed-Engineer--Agentic-AI-_R-102260, confirms "Location: Remote – U.S.", salary range 140k to 180k, benefits "for US employees."
3. Rimini Street Workday jobs search API (CXS), queried 2026-08-11: lists all five live Forward Deployed Engineer (Agentic AI) reqs and their locations (US, Singapore, UAE, South Korea, Tokyo).
4. Rimini Street Q2 2026 press release: https://www.riministreet.com/press-releases/rimini-street-announces-q2-2026-financial-operating-results/, revenue, adjusted revenue, guidance, cash and debt, active clients.
5. Motley Fool, Rimini Street (RMNI) Q2 2026 earnings call transcript: https://www.fool.com/earnings/call-transcripts/2026/07/30/rimini-street-rmni-q2-2026-earnings-call-transcript/, agentic AI strategy, sales reorg, hiring/turnover commentary.
6. Rimini Street press releases on AI products: https://www.riministreet.com/press-releases/rimini-street-launches-rimini-agentic-ux/ and Rimini Govern for AI launch coverage, e.g. https://www.businesswire.com/news/home/20260730389723/en/Rimini-Street-Launches-Rimini-Govern-for-AI-to-Deliver-Comprehensive-AI-Agent-Governance-Security-Interoperability-as-a-Service.
7. Rimini Street solutions pages: https://www.riministreet.com/solutions/oracle/ and https://www.riministreet.com/solutions/sap/, core support business description.
8. Panabee / Licenseware coverage of the July 2025 Oracle settlement: https://www.panabee.com/news/rimini-street-ends-15-year-oracle-legal-battle-securing-37-8-million-cash-inflow and https://licenseware.io/rimini-street-and-oracle-reach-historic-settlement-ending-15-year-legal-battle/, settlement date, $37.9M payment, PeopleSoft wind-down by July 2028.
9. Rimini Street About Us page: https://www.riministreet.com/company/about-us/, founding year 2005, Rimini Smart Path pillars, customer base, employee/office counts.
10. Rimini Street 10-K FY2025 (SEC EDGAR): https://www.sec.gov/Archives/edgar/data/1635282/000163528226000014/rmni-20251231.htm, "over 1,980 professionals" as of period end.
11. Job posting boilerplate ("Accelerating Company Growth" section, same across all reqs): Nasdaq listing since October 2017, 6,300+ signed contracts, 2,000+ team members in 23 countries.
12. Glassdoor Rimini Street reviews summary: https://www.glassdoor.com/Reviews/Rimini-Street-Reviews-E314503.htm, overall 3.2/5, category ratings, recurring review themes (nepotism, reprioritization, layoffs).
13. Stockanalysis.com employee headcount trend: https://stockanalysis.com/stocks/rmni/employees/, quarterly headcount from mid-2023 through mid-2026 showing a peak near 2,140 (mid-2024) declining to about 1,950 to 1,980 (2026).
14. Supreme Court / historical litigation background: https://en.wikipedia.org/wiki/Rimini_Street_Inc._v._Oracle_USA_Inc. and https://www.oyez.org/cases/2018/17-1625, background on the original 2010 to 2019 phase of Oracle v. Rimini Street (2015 jury verdict, 2018 injunction, 2019 Supreme Court ruling on costs).
