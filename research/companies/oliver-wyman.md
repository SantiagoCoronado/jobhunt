# Oliver Wyman: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: job id 8161, "Oliver Wyman - GenAI Engineer - Mexico City" (Adzuna mirror,
https://www.adzuna.com.mx/land/ad/5785455191, itself 403-blocked to direct fetch)

## Eligibility and liveness verdict (read first)

**Verdict: NOT ELIGIBLE TO APPLY as of 2026-07-28: the matching requisition on Oliver Wyman's own
careers site is filled/closed.** Location itself is not the problem (the role is Mexico City
based, which fits Santiago's rule); the problem is the specific requisition is no longer open.

What was checked:
- The Adzuna posting's description text ("We are looking for an experienced LLM / GenAI Engineer
  to design, develop, and deploy enterprise Generative AI solutions using...") matches, almost
  verbatim, a Mexico City requisition on Oliver Wyman's own ATS (Marsh careers, a Marsh McLennan/
  Oliver Wyman-operated site): "Oliver Wyman - ML Engineer - Generative AI & Unstructured Data -
  Mexico City," listed at "Avenida Paseo de la Reforma 505, Torre Mayor, 06500 Mexico City,
  Mexico" [careers.marsh.com/global/en/job/R_352810/Oliver-Wyman-ML-Engineer-Generative-AI-Unstructured-Data-Mexico-City].
  This is Oliver Wyman's real Mexico City office (Torre Mayor, Reforma 505), confirmed
  independently on the firm's own site [oliverwyman.com/our-expertise/global-locations/americas/mexico/mexico-city.html].
- Fetching that URL directly on 2026-07-28 returns: **"We're sorry... the job you are trying to
  apply for has been filled."** [careers.marsh.com/global/en/job/R_352810/Oliver-Wyman-ML-Engineer-Generative-AI-Unstructured-Data-Mexico-City,
  fetched 2026-07-28].
- Independently, a live search of Indeed Mexico for "oliver wyman" on 2026-07-28 returned zero
  results ("La busqueda Empleos de oliver wyman no ha producido ningun resultado")
  [mx.indeed.com/q-oliver-wyman-empleos.html, fetched 2026-07-28], and Oliver Wyman's own careers
  search page for Mexico City returned no results either [careers.marsh.com/global/en/oliver-wyman-search,
  fetched 2026-07-28; note this page is JS-rendered and may not fully reflect live listings to a
  non-browser fetch, so this second point is corroborating, not conclusive on its own].
- Timing is consistent with expiry: the Adzuna record shows `posted_at` 2026-07-02,
  `first_seen` 2026-07-08, and `last_seen` 2026-07-22, six days stale as of today
  [local jobs.db, job id 8161].

What could not be fully pinned down: the Adzuna listing's exact title reads "GenAI Engineer"
while the matching Oliver Wyman requisition is titled "ML Engineer - Generative AI & Unstructured
Data." These are almost certainly the same underlying role (Adzuna's own title normalization is
looser than the source ATS, and the description text overlaps closely), but this dossier flags
the title mismatch rather than asserting identity with certainty. No separate, currently live
Oliver Wyman requisition titled exactly "GenAI Engineer" in Mexico City was found on any source
checked.

**Recommendation: do not build a cover letter or application around this specific job id.** If
Santiago wants in, the live path is a direct approach (LinkedIn message to a Mexico City Oliver
Wyman recruiter, or recruitingmexico@oliverwyman.com, an address surfaced in search results but
not independently confirmed on oliverwyman.com by this dossier) rather than applying to a dead
requisition. The rest of this dossier stays useful as a reusable company profile for that
approach, or for any future Oliver Wyman GenAI/Digital posting.

## 1. Snapshot

Oliver Wyman is a global management consulting firm (strategy, operations, risk management,
organization transformation), founded in 1984 in New York, over 7,000 professionals across 60+
offices in 30+ countries, reporting roughly US$3.6 billion in 2025 revenue
[en.wikipedia.org/wiki/Oliver_Wyman]. It operates as a wholly owned business of Marsh McLennan,
which rebranded corporately to "Marsh" in January 2026; Oliver Wyman itself keeps its
client-facing name as "Oliver Wyman, a Marsh business," with its internal operating unit renamed
"Marsh Management Consulting" [oliverwyman.com/media-center/2025/oct/marshmclennan-and-its-businesses-will-brand-as-marsh.html].
Oliver Wyman has a real Mexico City office in Torre Mayor on Paseo de la Reforma 505
[oliverwyman.com/our-expertise/global-locations/americas/mexico/mexico-city.html]. Third-party
employee-count estimates for the wider firm vary (LinkedIn approximately 8,935; PitchBook
approximately 9,197; Revelio Labs approximately 4,980 as of December 2025), a spread this dossier
flags rather than resolves [search summary of linkedin.com/company/oliver-wyman,
pitchbook.com/profiles/advisor/51280-48, reveliolabs.com/companies/oliver-wyman/employees].

## 2. Core narrative

Oliver Wyman is a century-removed-from-its-founders, financial-services-heavy strategy shop
(second only to McKinsey in revenue per consultant, on one third-party estimate) that has spent
the last two years consolidating its scattered AI work into a single named practice, Quotient
(AI By Oliver Wyman), launched June 2024 with 300+ consultants, data scientists, engineers, and
designers under Global Head Jad Haddad, run out of Dubai
[consultancy-me.com/news/8695/oliver-wyman-brings-ai-offerings-together-under-one-roof-quotient].
That consolidation is happening at the same moment Marsh McLennan is restructuring its own
corporate brand and centralizing technology/data/AI investment into a new "Business and Client
Services" unit [oliverwyman.com/media-center/2025/oct/marshmclennan-and-its-businesses-will-brand-as-marsh.html].
In other words: this is a firm whose core product has always been human expert judgment sold by
the hour, now actively building out a hands-on engineering bench (ML Engineer, GenAI Engineer,
Data Engineer roles openly posted against a Mexico City office that historically has looked more
like a strategy/advisory outpost) to make GenAI a delivered capability rather than a slide.
Santiago's specific target requisition sits exactly at that seam, and its closure this fast (open
roughly 3 weeks per the timeline above) says either strong demand for the role or a small
headcount allocation per market, or both; worth asking a recruiter directly which it was.

## 3. Mission & product

- Core business: management consulting sold across strategy, operations, risk management, and
  organization transformation, with financial services as the historically dominant vertical,
  alongside automotive, defense, energy, healthcare, telecommunications, transportation, and
  travel [en.wikipedia.org/wiki/Oliver_Wyman; oliverwyman.com/index.html].
- Business model: professional-services time-and-materials/project fees; the firm's own homepage
  now foregrounds "deep industry insight, practical AI expertise, and true collaboration" and
  leads with an AI client case (Nippon Life: generative AI used to evaluate 10 years of
  stewardship data and identify patterns across thousands of records) [oliverwyman.com/index.html].
- Digital and Technology as a formal career track: Oliver Wyman's own careers site organizes this
  into four paths, Software Engineering, Data Science and Data Engineering, IT Support, and
  Digital Consulting, described as delivering "breakthrough impact for our clients" through
  engineering and data science capability, not just advisory slides
  [oliverwyman.com/careers/digital-technology.html].
- Quotient (AI By Oliver Wyman): the firm's unified AI offering since June 2024, a single entry
  point spanning AI strategy and investment planning, use-case prototyping, solution development,
  and AI-driven operational improvements, with cited examples in vaccine distribution, banking
  compliance, and risk intelligence [consultancy-me.com/news/8695/oliver-wyman-brings-ai-offerings-together-under-one-roof-quotient].
  No Mexico or LATAM-specific Quotient mention was found in the sources checked; the practice's
  named regional emphasis in available coverage is the Middle East
  [consultancy-me.com/news/8695/oliver-wyman-brings-ai-offerings-together-under-one-roof-quotient].
- Recent expansion by acquisition: Oliver Wyman acquired Veritas Total Solutions (commodity
  trading optimization expertise) [stocktitan.net/news/MMC/marsh-mc-lennan-s-oliver-wyman-to-acquire-veritas-total-d3n537ak9xyd,
  date of acquisition not independently confirmed by this dossier beyond the headline].

## 4. Culture & voice

- Recruiting message: "We Hire You To Be You" [oliverwyman.com/careers/digital-technology.html].
  Standard big-consultancy tone: polished, industry-insight-forward, case-study-driven.
- Glassdoor, Ciudad de Mexico specifically: 4.2 out of 5 overall rating (22 reviews), but only 3
  out of 5 on work-life balance (35.6% below the company-wide rating), and 81% would recommend to
  a friend versus 92% company-wide [glassdoor.com/Reviews/Oliver-Wyman-Ciudad-de-Mexico-Reviews
  search summary, fetched 2026-07-28].
- Recurring Mexico-specific review themes: "poor work life balance in some practices," "long
  hours and lots of travel (as in most consulting firms)," one review citing "13h a day
  Monday-Thursday, 8h on Friday"; countered by positive notes on culture, colleagues "willing to
  roll up their sleeves," and "good travel policies" / "good expense policies"
  [glassdoor.com/Reviews/Oliver-Wyman-Ciudad-de-Mexico-Reviews and related Glassdoor review
  search results, fetched 2026-07-28; treat as self-selected anecdote, not a verified statistic].
- Firm-wide Glassdoor comp/benefits satisfaction in Mexico specifically: 4.2 out of 5
  [glassdoor.com search summary, fetched 2026-07-28].

## 5. Recent news (last ~12 months)

- October 14, 2025: Marsh McLennan announced its parent corporate rebrand to "Marsh" (effective
  January 2026, ticker MRSH); Oliver Wyman keeps its name as "Oliver Wyman, a Marsh business," its
  operating unit renamed "Marsh Management Consulting"; a new "Business and Client Services" unit
  was created to centralize technology, data, and operations investment across the group
  [oliverwyman.com/media-center/2025/oct/marshmclennan-and-its-businesses-will-brand-as-marsh.html].
- November 20, 2025: Oliver Wyman announced 40 newly elected Partners and 4 newly elected
  Executive Directors for 2026 [barchart.com/story/news/36231136/oliver-wyman-announces-newly-elected-partners-and-executive-directors-for-2026].
- March 2026 (per search summary; not independently re-verified against a primary press release
  by this dossier): Ted Moynihan became President and CEO of Marsh Management Consulting and
  Oliver Wyman, succeeding Nick Studer, who moved to lead Marsh Risk
  [stocktitan.net/news/MMC/marsh-appoints-ted-moynihan-president-and-ceo-of-marsh-management-ze4yl4dvrrif].
- Acquisition of Veritas Total Solutions (commodity trading optimization), date not independently
  pinned down beyond the headline [stocktitan.net/news/MMC/marsh-mc-lennan-s-oliver-wyman-to-acquire-veritas-total-d3n537ak9xyd].
- Ongoing hiring signal: multiple Mexico City technology roles posted in 2026 alongside the target
  GenAI/ML Engineer requisition, including Data Engineer and Associate Software Engineer
  [builtin.com/job/oliver-wyman-data-engineer-mexico-city/3132696;
  builtin.com/job/oliver-wyman-associate-software-engineer-mexico-city/3132690], and a companion
  ML Engineer, Generative AI & Unstructured Data requisition in Lisbon, suggesting this is a role
  the firm is opening in multiple hub cities at once, not a one-off
  [careers.marsh.com/global/en/job/R_355039/Oliver-Wyman-Machine-Learning-Engineer-Generative-AI-Unstructured-Data-Lisbon].

## 6. Engineering & AI direction

- Named unified AI practice: Quotient (AI By Oliver Wyman), launched June 2024, 300+ people
  globally (consultants, data scientists, engineers, designers), led by Jad Haddad out of Dubai
  [consultancy-me.com/news/8695/oliver-wyman-brings-ai-offerings-together-under-one-roof-quotient].
- Target requisition's stated stack (from the Adzuna mirror and the matching Mexico City ML
  Engineer posting, both now closed): Python and SQL as core languages; PySpark and Databricks (or
  similar distributed compute) for scalable data/ML workflows; Generative AI and LLM ecosystems
  including OpenAI, Azure OpenAI, or open-source models; orchestration frameworks such as
  LangChain or LlamaIndex; vector databases such as Azure AI Search, Pinecone, or pgvector;
  RAG pipelines, embedding pipelines, semantic search, and LLM-powered APIs; monitoring,
  observability, and model-performance tracking for SLA compliance; CI/CD and MLOps practices in
  collaboration with Data Scientists; 3+ years of ML Engineering / Applied AI / Data Science
  experience with a production-systems focus [search summary corroborated across
  glassdoor.com.mx job listing text and local jobs.db description for job id 8161; treat the
  responsibility bullets as reconstructed from search snippets since the live posting itself is
  gone, not independently re-verified word for word].
- Client-facing framing example: Oliver Wyman's own homepage leads with a GenAI client case
  (Nippon Life, evaluating 10 years of stewardship data with generative AI to identify patterns
  across thousands of records), i.e. the visible AI engineering work is embedded inside client
  advisory engagements, not a pure internal product team [oliverwyman.com/index.html].
- No independent Oliver Wyman engineering blog, public GitHub, or public tech-talk series was
  found in this research pass; unlike a product company, the firm's AI-engineering signal lives
  mostly in press coverage of Quotient and in job postings, not in an engineering-culture blog.
  This is a real information gap, flagged rather than papered over.

## 7. Comp signals

- Oliver Wyman, Mexico City, general (all roles, not tech-specific): Glassdoor reports salaries
  ranging from roughly $82,887 (Intern) to roughly $397,699 (Partner) annually, based on 2,485
  submitted salaries as of December 2025 [search summary of glassdoor.com Oliver Wyman Mexico
  City salaries page, fetched 2026-07-28; currency not explicitly confirmed as USD vs MXN in the
  summary, treat as unverified on currency].
- Oliver Wyman, Software Engineer, firm-wide (not Mexico-specific): Glassdoor-reported total pay
  range of roughly $146K-$211K per year, average base around $158K, based on a large pooled sample
  (47,840 salaries submitted across the title, not filtered to this role or location)
  [glassdoor.com/Salary/Oliver-Wyman-Software-Engineer-Salaries-E40206_D_KO13,30.htm search
  summary, fetched 2026-07-28]. This is very likely US/high-cost-market weighted and should not be
  assumed to transfer to a Mexico City-based role; no Mexico City-specific tech-role salary figure
  was found in this research pass.
- The now-closed target posting itself listed no salary range or band in any source checked
  (Adzuna mirror description, search-engine summaries of the matching careers.marsh.com listing).
  Treat comp entirely as unverified for this specific role; do not anchor a number before a
  recruiter states one, per profile.yaml's comp rules.

## 8. Risks and red flags

- **Consulting-firm travel and utilization model**: even a technically-scoped GenAI/ML Engineer
  role sits inside a firm whose Mexico City reviews explicitly cite "long hours and lots of
  travel (as in most consulting firms)" and a below-average work-life-balance score (3/5 in Mexico
  vs the firm-wide average) [glassdoor.com Ciudad de Mexico reviews, fetched 2026-07-28]. Santiago
  is fine with occasional travel per his location rule, but should ask explicitly in interviews
  whether this specific engineering role carries the same billable-utilization and travel
  expectations as consulting staff, or is treated as a Digital/Technology-track role with a
  different rhythm.
- **This specific requisition is dead.** See the eligibility verdict above; do not treat this
  dossier as evidence the exact posted role is still applyable.
- **AI practice is centralized outside Mexico.** The named unified AI practice (Quotient) is run
  out of Dubai with a Middle East regional emphasis in the one detailed article found; no
  Mexico/LATAM-specific Quotient work was surfaced. A Mexico City hire may sit organizationally
  far from where the practice's headline client work and leadership visibility live. Worth asking
  directly what Mexico City-based GenAI engineers actually work on day to day.
- **No independent engineering-culture signal.** No public engineering blog, GitHub, or
  tech-conference presence was found for Oliver Wyman's technology org; the only visible technical
  detail came from the (now closed) job posting's own requirements list. Culture/stack claims here
  are thinner than they would be for a product company research pass.
- **Corporate rebrand in progress.** Marsh McLennan's shift to "Marsh," with Oliver Wyman
  becoming "Oliver Wyman, a Marsh business" and its operating unit "Marsh Management Consulting,"
  is a live organizational change as of January 2026; job titles, career pages, and reporting
  lines may still be settling, which is one plausible reason postings open and close quickly.

## 9. Why-fit angles for Santiago

Best hook to lead with (for the next live Oliver Wyman GenAI opening, since this specific job id
is closed): Oliver Wyman's actual hiring need, visible in the (now closed) posting's own
requirement list, is someone who ships production RAG pipelines, embedding search, and
LLM-powered APIs with real monitoring and SLA discipline, inside client-facing engagements, not a
pure research role. That is close to Santiago's daily operating mode at Pragma AI: he built
"Pragma Brain," a RAG "company brain" with scoped retrieval, deterministic no-answer and citation
gating, multilingual ES/EN embeddings, and an automated eval harness, productized as a client
offering, and ships conversational agents and internal automations directly against client data
[resume/master_resume.yaml]. The client-diagnostic, ambiguous-problem-to-shipped-system motion
that Pragma AI runs for Mexican SMBs is structurally the same motion Oliver Wyman is trying to
buy engineering capacity for inside consulting engagements, just at enterprise/financial-services
scale instead of SMB scale.

Concrete transferable evidence:
- RAG and retrieval engineering: Pragma Brain's scoped retrieval, citation/no-answer gating, and
  eval harness map directly onto the target posting's "RAG, embedding pipelines, semantic search,
  LLM-powered APIs" and "monitoring, observability, model-performance tracking for SLA compliance"
  language [resume/master_resume.yaml].
- Agent/tool-use engineering: the MCP brain service (per-operator tokens, rate limits), 15 agent
  definitions, and Plutus's LLM research agent exposed via MCP demonstrate the orchestration
  layer (LangChain/LlamaIndex-equivalent thinking) the posting asks for, even though Santiago's
  specific tooling differs from the named stack [resume/master_resume.yaml].
- Client-facing delivery under real constraints: founder-level ownership of client deployments at
  Eugenia.ai (on-site onboarding, translating conflicting requirements into shipped product) and
  Pragma AI (client diagnostics, delivery workflows) is direct evidence of the "embedded with
  client engagements" reality of consulting-adjacent engineering work [resume/master_resume.yaml].
- Bilingual ES/EN and Mexico City based: a genuine, low-friction fit for a firm whose Mexico City
  office serves Spanish-speaking financial-services and industrial clients directly
  [oliverwyman.com/our-expertise/global-locations/americas/mexico/mexico-city.html].

Honest concerns and watch-outs:
- No big-consultancy background. Santiago has never worked inside a traditional strategy/
  consulting firm's delivery model (utilization targets, staffing rotations, up-or-out promotion
  structure). This is a real, nameable gap, not something to paper over; frame it honestly as
  "founder who has run client engagements end to end, new to the specific rhythms of a global
  consulting firm."
- PySpark/Databricks depth is unconfirmed. Santiago's data-engineering work (Online Basics ETL
  pipelines, Plutus's Celery/Redis/TimescaleDB stack) is real but does not include hands-on
  PySpark or Databricks; this should be named directly if asked, not implied.
- Consulting travel/utilization culture (see Risks) is a genuine open question for someone who
  values founder-level autonomy; worth probing in any interview rather than assuming it away.
- The single requisition this dossier was built around is closed; there is no live role to apply
  to as of 2026-07-28.

## 10. Application-question angles

(For use if a live Oliver Wyman GenAI/Digital & Technology opening reappears; do not use these
against job id 8161, which is closed.)

- Why this company: lead with the specific shape of the work, not the brand name. Oliver Wyman is
  visibly trying to turn GenAI from an advisory slide into a delivered engineering capability
  (Quotient's 300+ engineers/data scientists/designers, a Mexico City ML/GenAI Engineer req built
  around RAG, embeddings, and production SLAs), and that is exactly the kind of build embedded in
  a real client relationship that Pragma AI already does at SMB scale. Frame the pitch as wanting
  to run that same motion against harder, higher-stakes enterprise problems. Avoid reciting the
  firm's consulting pedigree or generic "impact" language; anchor on the engineering-inside-client-
  work pattern.
- Why you fit: point to Pragma Brain (scoped RAG, citation gating, eval harness) and the MCP agent
  layer as concrete, shipped evidence of the exact posting requirements (RAG, embeddings, LLM
  APIs, monitoring), then be direct that the specific tools (Databricks, PySpark) and the
  big-consultancy delivery model are new territory he is ready to learn fast, not something he is
  overstating experience in.
- Anything else: if it comes up, be upfront that this application follows an earlier Oliver Wyman
  Mexico City requisition that closed before Santiago could apply, and that he is bilingual ES/EN,
  Mexico City based with no relocation needed, and comfortable with the travel this kind of
  client-facing role implies. Do not raise compensation unprompted; Oliver Wyman's own postings
  and public data give no reliable Mexico City-specific technical-role number to anchor against.

## Sources

- https://careers.marsh.com/global/en/job/R_352810/Oliver-Wyman-ML-Engineer-Generative-AI-Unstructured-Data-Mexico-City
  (Oliver Wyman's own careers site; matching Mexico City GenAI/ML Engineer requisition, confirmed
  filled/closed on direct fetch 2026-07-28, quoted verbatim above)
- https://www.adzuna.com.mx/land/ad/5785455191 (original job aggregator mirror; returns HTTP 403
  to direct fetch, description text pulled instead from local jobs.db record for job id 8161)
- /Users/santiagocoronado/jobhunt/data/jobs.db, job id 8161 (posted_at, first_seen, last_seen
  timestamps used to establish the posting's staleness timeline)
- https://mx.indeed.com/q-oliver-wyman-empleos.html (live search returning zero Oliver Wyman
  results in Mexico as of 2026-07-28, corroborating liveness verdict)
- https://careers.marsh.com/global/en/oliver-wyman-search (Oliver Wyman/Marsh's own careers search
  page; returned no results for Mexico City on fetch, JS-rendered so treated as corroborating only)
- https://www.oliverwyman.com/our-expertise/global-locations/americas/mexico/mexico-city.html
  (Mexico City office address and practice-area description)
- https://www.oliverwyman.com/careers/digital-technology.html (Digital and Technology career
  tracks: Software Engineering, Data Science/Data Engineering, IT Support, Digital Consulting)
- https://www.oliverwyman.com/index.html (firm's own homepage framing: "practical AI expertise,"
  Nippon Life GenAI client case)
- https://en.wikipedia.org/wiki/Oliver_Wyman (founding year 1984, headquarters, employee count,
  2025 revenue, history, practice areas)
- https://www.oliverwyman.com/media-center/2025/oct/marshmclennan-and-its-businesses-will-brand-as-marsh.html
  (October 2025 Marsh McLennan to Marsh rebrand announcement, Oliver Wyman's naming status,
  Business and Client Services unit)
- https://www.consultancy-me.com/news/8695/oliver-wyman-brings-ai-offerings-together-under-one-roof-quotient
  (Quotient AI practice: launch date, size, leadership, Middle East regional emphasis)
- https://www.barchart.com/story/news/36231136/oliver-wyman-announces-newly-elected-partners-and-executive-directors-for-2026
  (November 2025 partner/executive director promotions)
- https://www.stocktitan.net/news/MMC/marsh-appoints-ted-moynihan-president-and-ceo-of-marsh-management-ze4yl4dvrrif
  (Ted Moynihan CEO appointment, per search summary; not independently re-verified against a
  primary press release)
- https://www.stocktitan.net/news/MMC/marsh-mc-lennan-s-oliver-wyman-to-acquire-veritas-total-d3n537ak9xyd
  (Veritas Total Solutions acquisition headline)
- https://builtin.com/job/oliver-wyman-data-engineer-mexico-city/3132696 and
  https://builtin.com/job/oliver-wyman-associate-software-engineer-mexico-city/3132690 (other
  Mexico City technology postings, used as evidence of broader Mexico City tech hiring; the Data
  Engineer link itself returned HTTP 404 on direct fetch, so treated as a search-result title only)
- https://careers.marsh.com/global/en/job/R_355039/Oliver-Wyman-Machine-Learning-Engineer-Generative-AI-Unstructured-Data-Lisbon
  (companion Lisbon requisition with the same title, evidence the role is being opened in
  multiple hub cities)
- Glassdoor search summaries (fetched 2026-07-28, not directly fetchable due to HTTP 403 on
  glassdoor.com.mx and glassdoor.com): Ciudad de Mexico reviews and ratings
  (glassdoor.com/Reviews/Oliver-Wyman-Ciudad-de-Mexico-Reviews-EI_IE40206.0,12_IL.13,29_IC5017436.htm),
  Mexico City salary ranges
  (glassdoor.com/Salary/Oliver-Wyman-Mexico-City-Salaries-EI_IE40206.0,12_IL.13,24_IM1176.htm),
  Software Engineer salary pool
  (glassdoor.com/Salary/Oliver-Wyman-Software-Engineer-Salaries-E40206_D_KO13,30.htm)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience: Pragma
  AI, Eugenia.ai, Online Basics, Plutus, Kairos, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's location rule, comp rules, and
  target-role families, used to frame the eligibility verdict and comp caution)

Note for Santiago: this is a draft dossier, please review before it feeds any application
material. The headline finding is that the specific requisition (job id 8161) is closed as of
2026-07-28 on Oliver Wyman's own careers site; this dossier is built to be reusable if a similar
GenAI/Digital & Technology role reopens in Mexico City, but should not be used to justify tailoring
a resume or cover letter to a dead posting. Employee-count estimates, the exact Mexico City tech
comp band, and the CEO-appointment date are all flagged above as coming from secondary sources or
search summaries rather than a directly fetched primary document; re-verify before quoting them
in anything client-facing.
