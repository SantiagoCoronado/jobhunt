# Omilia: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: "Senior Conversational AI Delivery Engineer Lead - LATAM" (job id 15781), location
field "México" in Santiago's pipeline database. Aggregator mirror: Adzuna
https://www.adzuna.com.mx/details/5758543738 (posted 2026-06-10, source description confirms
title and "About Omilia" framing). No distinct posting was found on Omilia's own careers domain
(omilia.com/careers redirects to a client-rendered board with no crawlable listings); the most
complete and consistent copy of this exact requisition is the LinkedIn mirror:
https://ar.linkedin.com/jobs/view/senior-conversational-ai-delivery-engineer-lead-latam-at-omilia-4426754980
(also reachable as https://www.linkedin.com/jobs/view/4426754980).

## Location verdict (read first): ELIGIBLE, with one caveat

**Verdict: ELIGIBLE.** No source found requires the candidate to live or sit outside Mexico, and
multiple independent sources place this specific requisition's location inside Mexico City.

Evidence:
- The LinkedIn listing's own location tag reads (fetched twice, slightly different Mexico City
  borough each time, likely LinkedIn's geo-normalization): "Senior Conversational AI Delivery
  Engineer Lead - LATAM in Miguel Hidalgo, CMX" and, on a second fetch, "...en Benito Juárez, CMX"
  [ar.linkedin.com/jobs/view/senior-conversational-ai-delivery-engineer-lead-latam-at-omilia-4426754980].
  Both are Mexico City boroughs, not a location outside Mexico.
- The Adzuna mirror lists the job's location field simply as "México"
  [adzuna.com.mx/details/5758543738; local pipeline database, job id 15781].
- The posting body itself never states a residency requirement, on-site mandate, or a country
  exclusion. It describes the hire as the "founding" technical lead for "the emerging LATAM
  Delivery pod," serving "North and South American client engagements" and "coordinating
  cross-time-zone with Athens HQ," language that describes a distributed, region-wide remit rather
  than a single-office job [ar.linkedin.com/jobs/view/... (full description fetch)].
- The employer entity attached to the listing shows as "Omilia Argentina" in one LinkedIn render,
  which is a corporate/legal detail (the LATAM hiring entity), not a stated work-location
  requirement; nothing in the text says the person must be based in Argentina.

Caveat: no source I fetched contains an explicit sentence such as "this role is remote" or "open
to candidates based anywhere in Mexico/LATAM." The workplace-type tag (Remote/Hybrid/On-site) was
not visible in any fetch of this listing. The verdict above is a well-supported inference from
consistent Mexico City location tagging across two independent aggregators plus the absence of any
onsite-elsewhere requirement, not a directly quoted confirmation. Santiago should confirm directly
with the recruiter that the role is fully remote from Mexico City before assuming a specific work
arrangement (fully remote vs. periodic travel).

**Still live:** Yes, as of this research date. The job remains active in Santiago's discovery
pipeline (`last_seen: 2026-07-28`, status `shortlisted`, not expired) and the LinkedIn copy shows
"Posted about 1 month ago" with "Among the first 25 applicants" at fetch time
[ar.linkedin.com/jobs/view/senior-conversational-ai-delivery-engineer-lead-latam-at-omilia-4426754980;
local pipeline database, job id 15781].

## 1. Snapshot

Omilia is a Cyprus-registered (Larnaca) enterprise conversational and agentic AI vendor, founded in
2002 by CEO Dimitris Vassos, that spent its first 18 years bootstrapped before taking outside
capital [leadiq.com/c/omilia; tech.eu/2020/05/05/omilia-funding]. It raised $20M in Series A
funding from Grafton Capital in May 2020, and Expedition Growth Capital (whose founder Oliver
Thomas had sat on Omilia's board since 2020) invested in December 2021
[tech.eu/2020/05/05/omilia-funding; expedition.capital/omilia-and-expeditions-partnership;
expedition.capital/expedition-invests-in-conversational-ai-leader-omilia]. Third-party estimates
put headcount at roughly 460 to 480 employees across five continents as of mid-2026
[leadiq.com/c/omilia (about 481 as of June 2026); other aggregator estimates cited in this
dossier's sources range 359 to 462, flagged as directional]. Athens, Greece hosts a large
operational and R&D hub even though the registered headquarters is in Larnaca, Cyprus
[leadiq.com/c/omilia; glassdoor.com/Location/Omilia-Athens-Location search summary]. Omilia is
privately held (Grafton Capital and Expedition Growth Capital as disclosed investors), not
publicly traded.

## 2. Core narrative

Omilia is an 20+ year old conversational AI specialist (originally built around telephony speech
recognition and dialogue management for banks, telcos, and insurers) that spent the 2020s
generative-AI wave repositioning itself, not as a chatbot vendor bolting on GenAI, but as an
"agentic CX" platform for the highest-stakes, highest-volume voice channel: regulated enterprise
contact centers running IVR at massive scale. The company's calling card is scale and trust in
voice: it says it processes roughly 3 billion calls a year for major financial, utility, and QSR
brands, and it just expanded Taco Bell's drive-thru voice AI deployment past 890 locations across
38 US states [omilia.com/resources/news/omilia-appoints-armando-trivellato-as-evp-growth-latin-america-and-iberia
(3 billion calls figure, CEO quote); indexbox.io/blog/taco-bell-expands-voice-ai-partnership-with-omilia-in-2026
and restaurantdive.com/news/taco-bell-omilia-drive-thru-ai-deployment (Taco Bell 890+ locations)].
In 2025 it earned back-to-back third-party validation for that repositioning: named a Leader in
IDC's 2025 MarketScape for worldwide general-purpose conversational AI software, and a Visionary
(for the second year running, per one summary) in Gartner's 2025 Magic Quadrant for Conversational
AI Platforms [omilia.com/idc-marketscape-2025-worldwide-general-purpose-conversational-artificial-intelligence-software;
omilia.com/resources/analyst-reports/omilia-is-a-visionary-in-the-2025-gartner-magic-quadrant-for-conversational-ai-platforms].
The role Santiago is looking at exists because Omilia is now making a deliberate, dated push into
LATAM: it hired a 25-year contact-center-industry veteran (ex-Five9, ex-Atento, ex-Avaya) as EVP
Growth for Latin America and Iberia on July 2, 2026, and struck a strategic alliance with Atento
(a major LATAM contact-center outsourcer) in January 2026, both aimed at a regional market where,
per the new LATAM executive's own framing, "contact center markets in these regions hit
containment ceilings around mid-60% with automation" and Omilia is betting its self-learning
architecture beats that ceiling
[omilia.com/resources/news/omilia-appoints-armando-trivellato-as-evp-growth-latin-america-and-iberia;
omilia.com/resources/news/cx-industry-leaders-atento-and-omilia-establish-strategic-partnership-to-lead-the-next-wave-of-conversational-ai-innovation].
This delivery role is explicitly the first LATAM technical hire meant to stand up that region's
delivery capability from scratch.

## 3. Mission & product

- Product: the Omilia Cloud Platform (OCP), a unified conversational and agentic AI platform
  spanning voice (IVR/IVA), chat, authentication, fraud prevention (including voice biometrics),
  and agent-assist, deployable on public, private, or hybrid cloud with consumption-based pricing
  and managed-service support [omilia.com/idc-marketscape-2025-...; ar.linkedin.com job posting
  full description].
- February 2026 flagship launch: "Omilia Self-Learning Agentic CX," pitched as an
  enterprise-grade platform that "autonomously understands, improves, and optimizes customer
  conversations across voice and digital channels" without manual retraining cycles
  [WebSearch summary of finance.yahoo.com/news/omilia-unveils-world-first-enterprise-130000985.html;
  the article itself returned a 404 on direct fetch, so this claim is corroborated only via the
  search summary and should be treated as directional, not independently re-verified].
- Named enterprise customers: Capital One, Discover, and Taco Bell (drive-thru voice AI, 890+
  locations as of July 2026), plus government/utility references (a UK "DWP" reference appears in
  one company-overview fetch) [omilia.com/company (via WebFetch summary);
  indexbox.io/blog/taco-bell-expands-voice-ai-partnership-with-omilia-in-2026;
  restaurantdive.com/news/taco-bell-omilia-drive-thru-ai-deployment]. Treat the DWP/Discover/Capital
  One list as a company-page summary, not independently cross-checked against a press release for
  each name.
- Business model: enterprise B2B software and managed services sold to regulated, high-call-volume
  verticals (banking, insurance, utilities, telco, QSR/retail), sold direct and, increasingly,
  through partners like Atento in LATAM [omilia.com/resources/news/cx-industry-leaders-atento-and-omilia-...;
  ar.linkedin.com job posting full description ("Certified Partners" listed as a cross-functional
  stakeholder group)].
- Market position: Leader, 2025 IDC MarketScape for Worldwide General-Purpose Conversational AI
  Software Platforms (published September 2025); Visionary, 2025 Gartner Magic Quadrant for
  Conversational AI Platforms (published August 13, 2025), and again named a Visionary in the 2026
  edition of the same Gartner report
  [omilia.com/idc-marketscape-2025-worldwide-general-purpose-conversational-artificial-intelligence-software;
  omilia.com/resources/analyst-reports/omilia-is-a-visionary-in-the-2025-gartner-magic-quadrant-for-conversational-ai-platforms;
  omilia.com/resources/analyst-reports/omilia-visionary-gartner-mq-2026]. Both analyst claims in
  the job posting and on Adzuna are confirmed as accurate against Omilia's own analyst-report pages.

## 4. Culture & voice

- Stated core values: Deliver Results, Be Passionate, Build Trust through Honesty, Pursue
  Excellence as Habit, Be Curious and Innovate, Dream Big and Tackle Tough Challenges, Lead by
  Example [omilia.com/company (via WebFetch summary)].
- Careers-page framing emphasizes diversity and inclusion ("every person we meet has something to
  teach us"), continuous learning, collaborative teamwork, and a stated passion for innovation
  [omilia.com/careers (via WebFetch summary)].
- Employee sentiment (Athens office specifically, via Glassdoor category ratings, not independently
  re-verified beyond a search summary): work-life balance 4.1/5, diversity and inclusion 4.5/5,
  culture and values 4.3/5, career opportunities 4/5 [WebSearch summary of
  glassdoor.com/Location/Omilia-Athens-Location and related Glassdoor Athens pages; direct fetch of
  Glassdoor's company overview page returned 403, so the aggregate company-wide rating could not be
  independently confirmed in this pass].
- The job posting's own language for this specific role is notably candid about scope and risk: it
  frames the hire explicitly as a "founding" regional hire who must be "comfort[able]...defining
  ways of working, not just executing them," and lists direct responsibilities to "scope, interview,
  and onboard pod members" as the team scales, a build-the-team-from-zero tone rather than a
  join-an-established-org tone [ar.linkedin.com job posting full description].

## 5. Recent news (last ~12 months)

- August 13, 2025: named a Visionary in the 2025 Gartner Magic Quadrant for Conversational AI
  Platforms [omilia.com/resources/analyst-reports/omilia-is-a-visionary-in-the-2025-gartner-magic-quadrant-for-conversational-ai-platforms].
- September 2025: named a Leader in the IDC MarketScape Worldwide General-Purpose Conversational
  AI Platforms 2025 Vendor Assessment (IDC #US52972625e)
  [omilia.com/idc-marketscape-2025-worldwide-general-purpose-conversational-artificial-intelligence-software].
- January 20, 2026: strategic alliance announced with Atento (major LATAM/global contact-center
  outsourcer), targeting the United States, EMEA, and Latin America to scale agentic virtual agents
  [omilia.com/resources/news/cx-industry-leaders-atento-and-omilia-establish-strategic-partnership-to-lead-the-next-wave-of-conversational-ai-innovation].
- February 2026: launched "Omilia Self-Learning Agentic CX," described as an enterprise-grade,
  self-learning agentic platform across voice and digital channels (claim corroborated only via a
  WebSearch summary of a Yahoo Finance article; direct article fetch returned 404, flagged as such)
  [WebSearch summary of finance.yahoo.com/news/omilia-unveils-world-first-enterprise-130000985.html].
- May 7 to 8, 2026: CEO Dimitris Vassos spoke at the EU-Startups Summit 2026 in Malta [WebSearch
  summary, no direct primary source fetched, flagged as unverified detail].
- Circa June 2026: named a Visionary again in the 2026 Gartner Magic Quadrant for Conversational AI
  Platforms, for the second consecutive year per one summary
  [omilia.com/resources/analyst-reports/omilia-visionary-gartner-mq-2026].
- June 10, 2026: this dossier's target posting first appears in the discovery pipeline via Adzuna
  [local pipeline database, job id 15781].
- July 2, 2026: appointed Armando Trivellato (25+ years, ex-Five9 VP Iberia/LATAM, ex-Atento Head
  of Tech Sales, ex-Polycom/Avaya/Lucent) as EVP Growth for Latin America and Iberia, explicitly to
  build commercial presence in LATAM, Spain, and Portugal targeting financial services, utilities,
  and telecom
  [omilia.com/resources/news/omilia-appoints-armando-trivellato-as-evp-growth-latin-america-and-iberia].
- July 2026: Taco Bell voice-AI drive-thru deployment reported at 890+ locations across 38 US
  states [indexbox.io/blog/taco-bell-expands-voice-ai-partnership-with-omilia-in-2026;
  restaurantdive.com/news/taco-bell-omilia-drive-thru-ai-deployment].
- July 13, 2026: appointed Nick Delis as Chief Revenue Officer [WebSearch summary of
  omilia.com/resources/news/omilia-appoints-nick-delis-as-chief-revenue-officer; not independently
  re-fetched, flagged as summary-level].
- July 22, 2026: appointed Ryan Kam as Chief Marketing Officer [WebSearch summary of
  finance.yahoo.com/technology/ai/articles/omilia-appoints-ryan-kam-chief-120000835.html; not
  independently re-fetched, flagged as summary-level].

Pattern worth naming: three C-suite/EVP hires in July 2026 alone (Growth-LATAM, CRO, CMO), on top
of the Atento alliance and the Gartner/IDC recognitions, reads as a company mid-scale-up on the
commercial side specifically, right as this LATAM delivery requisition opened. That is a real,
dated growth signal, not generic "fast-growing company" language.

## 6. Engineering & AI direction

- This specific role's technical surface is voice-first and telephony-heavy, not a general
  software-engineering or pure-GenAI role: 7+ years "delivering conversational AI, IVR, or IVA
  solutions in enterprise environments with significant voice/telephony channel experience" is
  listed as a hard requirement, alongside hands-on VUI/voice-dialog design (call-flow architecture,
  disambiguation, confirmation strategy, error-recovery/retry handling for spoken interactions) and
  working knowledge of ASR/NLU behavior under telephony conditions (narrowband audio, barge-in,
  DTMF fallback, confidence thresholds, multilingual Spanish/Portuguese recognition)
  [ar.linkedin.com job posting full description].
- GenAI is present but secondary to the voice/IVR core: the posting asks for "familiarity"
  integrating GenAI/LLM capabilities (RAG, embeddings, prompt engineering, APIs from OpenAI,
  Gemini, Claude) and Python (preferred) or Node.js for backend integrations and automation, framed
  as an added layer on top of the voice/telephony delivery work, not a replacement for it
  [ar.linkedin.com job posting full description].
- Contact-center infrastructure integration is explicitly in scope: IVR, SIP, CTI, and omnichannel
  API integrations, plus bot analytics/AI quality monitoring tooling and KPI fluency (containment
  rate, CSAT) [ar.linkedin.com job posting full description].
- Platform-level AI direction (product, not this role specifically): the February 2026
  "Self-Learning Agentic CX" launch and the IDC/Gartner recognitions both emphasize a
  continuously-learning system across voice and digital channels, enterprise-grade security
  including voice biometrics and anti-fraud, and flexible (public/private/hybrid cloud, white-label)
  deployment for regulated industries
  [omilia.com/idc-marketscape-2025-worldwide-general-purpose-conversational-artificial-intelligence-software;
  omilia.com/resources/analyst-reports/omilia-is-a-visionary-in-the-2025-gartner-magic-quadrant-for-conversational-ai-platforms;
  WebSearch summary of the Yahoo Finance Self-Learning Agentic CX article].
- Org structure signal: engineering/R&D appears centered in Athens with cross-time-zone
  coordination expected from this LATAM hire, and the role sits under a "Solution Delivery"
  function that collaborates with separate Solution Architecture, Product, Platform, R&D, Sales,
  and Pre-Sales teams, plus "Certified Partners," implying Omilia already runs a partner-delivery
  model in some markets [ar.linkedin.com job posting full description;
  glassdoor.com/Location/Omilia-Athens-Location search summary].

## 7. Why-fit angles for Santiago

Best hook to lead with, with an honest caveat attached: Santiago's strongest, most literal match to
this specific opening is not the voice/IVR stack, it is the "founding regional hire" framing itself.
The posting explicitly wants someone comfortable "defining ways of working, not just executing them"
and asks the hire to "scope, interview, and onboard pod members" while acting as the technical
point of contact across every client engagement in a brand-new region
[ar.linkedin.com job posting full description]. That is close to the actual shape of Santiago's
career: he founded and ran Online Basics (raised capital, led a 7-person team, built the company's
entire internal platform from zero) and founded, built, and exited Eugenia.ai (owned the full
product lifecycle and led on-site client deployments, translating "complex, conflicting needs" into
working software for HOAs and property administrators), and today co-founded Pragma AI, where he
personally runs client AI diagnostics and ships conversational AI agents and automations directly
into client operations [resume/master_resume.yaml]. The pitch that fits is "founder who has stood
up delivery capability from nothing multiple times, now doing it for Omilia's first LATAM pod,"
not "voice AI specialist."

Concrete transferable evidence:
- Pragma AI: "Ship conversational AI agents and internal automations for quoting, reporting,
  onboarding, and collections, and run client diagnostics" is direct, current evidence of
  conversational-AI delivery into real client operations, plus a RAG "company brain" with
  deterministic no-answer and citation gating, i.e. the same trustworthy-AI-in-production emphasis
  Omilia's platform pitch (self-learning, enterprise-grade, security-first) leans on
  [resume/master_resume.yaml; omilia.com/idc-marketscape-2025-...].
- Bilingual Spanish (native) and English (fluent) matches the posting's language requirement almost
  exactly: "professional fluency in Portuguese OR Spanish (required)," with both "strongly
  preferred" [resume/master_resume.yaml; ar.linkedin.com job posting full description].
- Python proficiency (FastAPI, backend integrations across Plutus and Online Basics) covers the
  posting's "Python (preferred) or Node.js" backend-integration ask, and REST API integration work
  at Online Basics (10+ third-party APIs) is a real, if adjacent, match to the posting's
  "omnichannel API integrations" language [resume/master_resume.yaml; ar.linkedin.com job posting
  full description].
- Founder-level client-facing ownership (raised capital, owned P&L, led on-site deployments) maps
  directly to the posting's "trusted advisor," "primary technical point of contact," and
  "cross-functional collaboration" language [resume/master_resume.yaml; ar.linkedin.com job posting
  full description].

Honest concerns and watch-outs:
- The single biggest gap, and it is a real one, not a nitpick: Santiago has zero voice, telephony,
  or IVR background. The posting's 7+ year experience bar is explicitly "delivering conversational
  AI, IVR, or IVA solutions in enterprise environments with significant voice/telephony channel
  experience," plus hands-on requirements around VUI dialog design, barge-in, DTMF fallback, ASR
  confidence thresholds, and SIP/CTI contact-center infrastructure, none of which appear anywhere in
  his resume [ar.linkedin.com job posting full description; resume/master_resume.yaml]. His
  conversational AI work (Pragma AI agents, the personal-finance agent) is text/chat and
  agentic-workflow based, not voice/telephony. This should be named directly rather than glossed
  over; it is the kind of gap that could sink the application on its own if the requirement is
  enforced strictly.
- Seniority framing mismatch: the role is pitched as the region's founding technical hire and
  implicitly a senior individual-voice-engineering role first, people-manager/mentor second. Santiago's
  strongest leadership evidence is founder-level (raised money, ran a 7-person team, owned full
  P&L), which is real seniority but in a different shape than "senior IVR delivery engineer who
  also mentors junior engineers."
- Location is very likely fine (see verdict above) but not explicitly confirmed as remote in the
  posting text; this should be the first question asked, not assumed.
- No salary or compensation band is stated anywhere in the sources found for this posting; nothing
  to check against Santiago's comp floor until a recruiter shares one.

## 8. Application-question angles

- Why this company: lead with the moment, not the product category. Omilia just made its first
  dedicated LATAM growth hire (July 2, 2026) and struck a partnership with Atento to scale agentic
  virtual agents across the region, right as this requisition opened to build the delivery side of
  that same bet from zero. Frame the interest as wanting to be the person who builds a region's
  delivery practice from the ground up, the same motion Santiago has already run twice as a
  founder (Online Basics, Eugenia.ai) and is running now at Pragma AI, not as generic interest in
  conversational AI or IVR as a category.
- Why you fit: anchor on the founder pattern (raise the resources, own the client relationship,
  ship the product, do it again) rather than claiming voice/IVR depth he does not have. Be direct
  that the telephony/IVR specifics (SIP, CTI, DTMF, ASR tuning) are new territory, and frame the
  pitch as "fast learner with a demonstrated record of standing up delivery capability and
  client trust from nothing," backed by the bilingual ES/EN fluency and the hands-on conversational
  AI and RAG systems he has actually shipped.
- Anything else: if the voice/IVR gap comes up, address it head-on rather than downplaying it,
  and ask directly what mix of hands-on telephony work versus regional delivery leadership the role
  really needs in year one, since the posting reads as asking for both a deep IVR specialist and a
  from-scratch team builder in one person. If location comes up, confirm plainly that Santiago is
  Mexico City based, will not relocate, and ask whether the role is fully remote or expects periodic
  travel to Athens or to LATAM client sites (he is fine with occasional travel, not with a required
  base outside Mexico).

## Sources

- https://www.adzuna.com.mx/details/5758543738 (target posting mirror; direct WebFetch returned
  403, so this dossier relies on the cached description text already captured in the local pipeline
  database for this listing)
- Local pipeline database, job id 15781 (`python -m src.query job 15781`): posting title,
  location field "México," remote flag, posted_at 2026-06-10, current status/last_seen confirming
  the listing is still tracked as live
- https://ar.linkedin.com/jobs/view/senior-conversational-ai-delivery-engineer-lead-latam-at-omilia-4426754980
  and https://www.linkedin.com/jobs/view/4426754980 (fullest available copy of this exact
  requisition: location tag, full "About Omilia," "Why LATAM Why Now," responsibilities,
  requirements, language requirements, and benefits text; posted-date and applicant-count signals)
- https://omilia.com/idc-marketscape-2025-worldwide-general-purpose-conversational-artificial-intelligence-software
  (IDC MarketScape Leader recognition, September 2025, IDC #US52972625e)
- https://omilia.com/resources/analyst-reports/omilia-is-a-visionary-in-the-2025-gartner-magic-quadrant-for-conversational-ai-platforms
  (Gartner 2025 Magic Quadrant Visionary recognition, published August 13, 2025)
- https://omilia.com/resources/analyst-reports/omilia-visionary-gartner-mq-2026 (2026 Gartner
  Magic Quadrant, Visionary again)
- https://omilia.com/resources/news/omilia-appoints-armando-trivellato-as-evp-growth-latin-america-and-iberia
  (July 2, 2026: EVP Growth LATAM & Iberia appointment, LATAM expansion strategy, CEO and
  executive quotes, 3-billion-calls-a-year figure)
- https://omilia.com/resources/news/cx-industry-leaders-atento-and-omilia-establish-strategic-partnership-to-lead-the-next-wave-of-conversational-ai-innovation
  (January 20, 2026: Atento strategic partnership, target regions US/EMEA/LATAM)
- https://omilia.com/company/ (company overview: founding year, leadership, values, customer
  names, fetched via WebFetch summary)
- https://omilia.com/careers/ (careers page framing: diversity, culture language; job listings
  themselves were not crawlable via WebFetch, fetched via WebFetch summary)
- https://leadiq.com/c/omilia---conversational-intelligence/5a1d9d4c23000053008d25a6 (headcount
  estimate ~481 as of June 2026, HQ address in Larnaca Cyprus, founding year 2002)
- https://tech.eu/2020/05/05/omilia-funding/ (2020 Series A history, 18-year bootstrapping,
  Grafton Capital investment, CEO quote)
- https://expedition.capital/omilia-and-expeditions-partnership/ and
  https://expedition.capital/expedition-invests-in-conversational-ai-leader-omilia/ (Expedition
  Growth Capital's December 2021 investment and board relationship since 2020)
- https://www.indexbox.io/blog/taco-bell-expands-voice-ai-partnership-with-omilia-in-2026/ and
  https://www.restaurantdive.com/news/taco-bell-omilia-drive-thru-ai-deployment/824564/ (Taco Bell
  drive-thru voice AI deployment, 890+ locations across 38 states, as of July 2026)
- WebSearch summary only, not independently re-fetched (flagged in-text where used):
  finance.yahoo.com/news/omilia-unveils-world-first-enterprise-130000985.html (Self-Learning
  Agentic CX launch, February 2026; direct fetch returned 404);
  omilia.com/resources/news/omilia-appoints-nick-delis-as-chief-revenue-officer (CRO appointment,
  July 13, 2026); finance.yahoo.com/technology/ai/articles/omilia-appoints-ryan-kam-chief-120000835.html
  (CMO appointment, July 22, 2026); glassdoor.com/Location/Omilia-Athens-Location and related
  Glassdoor Athens pages (Athens office employee-sentiment category ratings; direct fetch of the
  main Glassdoor company overview page returned 403)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience: Online
  Basics, Eugenia.ai, Nextia, Pragma AI, Plutus, Kairos, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile, location rule,
  and salary floor, used to frame the location verdict and comp watch-out)

Note for Santiago: this is a draft dossier, please review before it feeds a cover letter or
application answers. The location verdict (ELIGIBLE) is well supported by consistent Mexico City
tagging across two independent sources plus the absence of any onsite-elsewhere requirement in the
posting text, but no source explicitly states "this role is remote" or names Mexico by name as an
eligible base; confirm this directly with the recruiter as the first question, not an assumption.
The bigger open risk for this specific application is the total absence of voice/telephony/IVR
experience on his resume against a hard 7+ year requirement for exactly that background; decide
before applying whether to address that gap head-on in the cover letter or lean entirely on the
founding-hire/delivery-leadership angle instead. Some company facts (2026 Self-Learning Agentic CX
launch, CRO and CMO appointments, Athens Glassdoor ratings) are corroborated only by WebSearch
summaries because the underlying pages returned 404 or 403 on direct fetch; treat those specific
facts as lower-confidence than the rest of this dossier and re-verify before quoting them precisely
in an application.
