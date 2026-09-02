DRAFT: automated research, not yet human-fact-checked by Santiago. Verify before relying on
any figure in an application, especially the compensation section below.

# Grupo Mariposa: company dossier

Prepared for job id 17497, "AI Engineer Senior" (GetOnBrd, confirmed live and Mexico-eligible on
2026-08-06; posting URL below).

## 1. Snapshot

Guatemala City-headquartered, family-owned Latin American food and beverage conglomerate,
founded 1885, ~15,000+ employees across 14+ countries, organized into four business units: apex
(digital/transformation), cbc (PepsiCo/AB InBev beverage bottling and distribution), beliv
(beverage innovation), and bia (coffee, culinary, sweet snacks). Privately held (no public
funding rounds; this is a mature conglomerate, not a startup). [Grupo Mariposa GetOnBrd company
profile](https://www.getonbrd.com/companies/grupo-mariposa); [Grupo Mariposa
homepage](https://grupomariposa.com/); [Grupo Mariposa business
units](https://grupomariposa.com/business-units); [Built In company
profile](https://builtin.com/company/grupo-mariposa) (lists 10,001+ employees, HQ Guatemala).

## 2. THE DECISIVE QUESTION: does this role plausibly clear Santiago's $70,000 USD/year floor?

**No compensation is published on the posting itself.** [The live JD (fetched via proxy since
GetOnBrd blocks direct scraping)](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote)
ends with "Compensation: not disclosed."

Signals gathered, all independent of the actual offer (no Grupo Mariposa-specific pay data for
this exact req exists anywhere public):

- **General Mexico market ceiling for the closest comparable title.** [payrollmexico.com's Data
  Engineer Mexico salary page](https://www.payrollmexico.com/insights/data-engineer-salary-mexico)
  (dated June 26 2026) puts "Senior (6+ years)" Data Engineer pay in Mexico at MXN 78,000-125,000
  per month, i.e. MXN 936,000-1,500,000 per year. At the requested 17.1 MXN/USD rate that is
  **USD ~54,700-87,700/year**, so the upper half of the general senior-market band, for a
  Mexico City tech-market hire, clears Santiago's floor while the bottom half does not. This is a generic market
  ceiling, not a Grupo Mariposa figure, and it is for a plain "senior data engineer," not
  specifically an AI-premium role.
- **Indeed's Mexico senior-data-engineer aggregate** shows an average of "$51,861 por año" (label
  ambiguous, likely MXN, self-described as low-confidence with only 3 data points) via
  [mx.indeed.com/career/senior-data-engineer/salaries](https://mx.indeed.com/career/senior-data-engineer/salaries).
  Directionally consistent with "modest," not confirmatory of an exact figure; flagged as
  low-reliability.
- **Company-specific pay reputation.** No Glassdoor page exists for "Grupo Mariposa" itself
  (searches only surface unrelated companies named "Mariposa"). The closest verifiable signal is
  [Indeed reviews for Grupo CBC](https://co.indeed.com/cmp/Grupo-Cbc/reviews?ftopic=paybenefits)
  (Colombia operation, part of the same cbc business unit): pay/benefits rated 3.9/5, with
  employees describing payments as punctual and legally compliant but explicitly "el sueldo es
  bajo aunque pagan lo de ley" (salary is low, though they pay what the law requires). This is a
  reputational signal for the broader cbc unit's pay philosophy, not proof of this role's band,
  and it is for local Colombian staff, not a remote senior AI hire.
- **Likely employment mechanism cuts against the ask, not for it.** The req is hosted under a
  legal entity called "Global Mobility Apex, S.A." (a Guatemala corporation; see section 3),
  hiring simultaneously across Central America, Chile, Argentina, Peru, Colombia, Mexico, and
  Ecuador. A single Guatemala-based entity recruiting across seven-plus countries at once strongly
  suggests bands are set to a regional LATAM cost base (Guatemala/Central America salary levels
  are lower than Mexico City), not to Mexico City or US tech-market rates, and the arrangement is
  more likely contractor-like than a local Mexican payroll hire. Per `config/profile.yaml`'s
  `contractor_note`, a contractor rate needs to sit ABOVE the equivalent employee salary to be
  fair (it must absorb benefits, IMSS, aguinaldo, self-paid ISR); nothing here suggests Grupo
  Mariposa is pricing in that premium.
- **Multiple simultaneous LATAM-wide corporate data/AI reqs** (Data Engineer Senior, Data
  Scientist Senior, Data Architect Sr, Analytics & Innovation Lead, this AI Engineer Senior role)
  are all posted through the same GetOnBrd channel with the same broad residency net, consistent
  with a standardized regional band rather than a premium, US-competitive AI-market rate.

**Verdict: could clear the $70,000 USD/year LATAM floor, but not comfortably.** Every available
proxy (general Mexico senior-market ceiling, sister-unit pay reputation, the wide-net regional
hiring pattern, the Guatemala-entity/contractor-like structure) points at a regional band that
straddles the floor rather than sitting above it, and none of them is an actual quote for this
role. Confidence is moderate
(no hard number exists to fully confirm or rule this out), but the honest read is that Santiago
should treat compensation as a likely dealbreaker here and confirm pay explicitly and early (first
recruiter contact) before investing in a full tailored application, rather than assume it clears
the floor because the role title says "Senior" and "AI."

## 3. Corporate IT vs. genuine product engineering, and employment mechanism

This sits inside **Apex Digital / M5**, the group's internal digital-transformation arm, in its
**Data & Analytics** area, which "develops analytical products and advanced capabilities" that
serve the CBC, Beliv, and BIA business units plus cross-cutting transformation initiatives
[(JD)](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote).
That is a genuine, staffed internal data/AI function (not a one-off IT ticket role): the same
GetOnBrd channel simultaneously runs a Tech Lead, Data Engineer Senior, Data Scientist Senior,
Data Architect Sr (Data & AI), Analytics & Innovation Lead, DevOps Engineer, and multiple frontend
roles, all reporting into what looks like a shared digital/data organization [(search of GetOnBrd
Grupo Mariposa listings)](https://www.getonbrd.com/companies/grupo-mariposa). The org is explicitly
"advancing toward an enterprise AI Agents architecture based on Databricks, ADLS Gen2, Unity
Catalog, Azure AI / Microsoft Foundry, Copilot Studio and Power Automate," per the same listings.

Characterization: this reads as **enterprise/internal AI platform engineering** (connecting a
Microsoft-stack knowledge base, agents, and copilots to internal systems for internal and
frontline users), not consumer product engineering. It is closer to Santiago's "internal
tooling / internal platforms" strength (family D in his profile) than to shipping a customer-facing
product, though the responsibilities (RAG architecture, agent orchestration, Python APIs) overlap
his AI-engineering strength (family A) too. Separately, Grupo Mariposa's broader digital arm has
built at least one real external-facing product: a McKinsey-co-developed conversational-commerce
platform for corner-store retailers built on WhatsApp with partner Yalo, which the group is now
also marketing to other CPGs [(McKinsey "Rewired in Action" case
study)](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action/grupo-mariposa-harnessing-connected-technology-in-the-latam-food-and-beverage-market).
That product is not what this specific req builds, but it is evidence the group's digital function
ships real things, not just internal dashboards.

No named reporting manager, team size, or org chart is public; could not verify who this role
reports to.

**Employment mechanism.** The job URL and at least one sibling posting resolve under the legal
entity name **"Global Mobility Apex, S.A."**, a Guatemala corporation, evidently the group's
umbrella employer/EOR-like vehicle for cross-country remote hires (seen across multiple GetOnBrd
Grupo Mariposa reqs) [(example
listing)](https://www.getonbrd.com/jobs/data-science-analytics/analista-business-intelligence-global-mobility-apex-s-a-remote-27de);
[(Dun & Bradstreet profile of Global Mobility Apex
S.A.)](https://www.dnb.com/business-directory/company-profiles.global_mobility_apex_sa.fa3b99ad377d11bb79ba73dcb7815ab7.html).
Could not verify whether Grupo Mariposa/CBC has a separate Mexican operating entity that would put
a Mexico-resident hire on local Mexican payroll; CBC's bottling network is documented in Guatemala,
El Salvador, Honduras, Nicaragua, Puerto Rico, Trinidad & Tobago, Barbados, Jamaica, Ecuador, and
Peru (plus reported operations in Mexico and offices in New York and Miami), but that is the
beverage-bottling business, not evidence of a Mexican entity for this digital/data hire
[(CBC "About")](https://cbc.co/en/about-2/). **Best read: this is most likely a contractor or
Guatemala-entity engagement for a Mexico-resident hire, not direct Mexican employment.** Flag this
explicitly to Santiago as unconfirmed and worth asking the recruiter directly.

## 4. Tech stack (from the posting)

Azure AI, Microsoft Foundry / Foundry Agent Service, Copilot Studio, Databricks, Azure Data Lake
Storage Gen2 (ADLS Gen2), Unity Catalog, Azure AI Search, Power Automate, Microsoft Teams
integration, Python (APIs, FastAPI, SDKs), containers, CI/CD, Azure platform services (Storage,
Key Vault, Entra ID, App Service, Functions, monitoring/security), Kafka (event-driven
architecture), vector databases and embeddings for RAG, MCP / tool-calling, AWS Bedrock and
LangGraph mentioned as alternative acceptable agent-framework experience [(JD, fetched via
proxy)](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote).
This is a **Microsoft-first enterprise stack**, notably different from Santiago's usual
Anthropic/OpenAI-API-plus-self-hosted-infra pattern (Plutus, Pragma Brain); the Azure/Databricks/
Copilot Studio surface is not something his resume currently evidences directly, though the
underlying RAG, agents, tool-calling, Python/FastAPI, and API-integration skills transfer.

## 5. Full role requirements (for the tailor agent)

**Responsibilities:**
- Design and deploy generative AI solutions and enterprise agents on Azure AI/Microsoft Foundry.
- Establish reference architecture for RAG, agents, tools, evaluation, security, and observability.
- Build Python-based APIs and microservices integrating models with corporate systems.
- Connect AI solutions to Databricks, Unity Catalog, ADLS Gen2, Azure AI Search, Power Automate,
  Copilot Studio, Teams, and web channels.
- Implement the enterprise knowledge-base pattern (Databricks + ADLS Gen2 + Foundry IQ / search
  and grounding).
- Configure and develop agents/copilots on Copilot Studio / Foundry with action invocation via
  Power Automate or backend services.
- Implement grounding, access controls, versioning, testing, and monitoring; guardrails and
  prompt-injection defenses; PII handling.
- Collaborate with Data Engineering, BI, Architecture, Security, Product, and business teams to
  bring use cases to production.

**Required:**
- 4+ years in software engineering, with 1-2+ years building AI solutions in production.
- Practical experience with enterprise agent platforms (Azure AI Foundry, AWS Bedrock, or
  frameworks like LangGraph).
- Strong RAG knowledge: vector databases, embeddings, chunking, enterprise data integration.
- MCP or tool-calling/function-calling experience with LLMs.
- Security expertise: guardrails, prompt-injection defense, PII handling.
- Event-driven architecture knowledge (Kafka).
- REST APIs and cloud proficiency (Azure preferred).
- Solid Python, APIs, FastAPI, SDKs, containers, CI/CD, software-engineering best practices.
- Familiarity with Azure services: Storage, Key Vault, Entra ID, App Service, Functions,
  monitoring, security.
- Knowledge of Databricks, Unity Catalog, ADLS Gen2, data governance, integration patterns with
  analytics platforms.
- Fluent Spanish and English (English at a level sufficient for documentation, architecture
  review, and vendor/official-docs work).

**Desirable:** AI governance experience (NIST AI RMF, ISO 42001), Microsoft Teams integration,
FinOps for AI applications, CPG/FMCG or multi-business-unit corporate experience.

Source for all of the above: [JD, fetched via proxy since GetOnBrd blocks direct
scraping](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote).

## 6. Language

Working language requirement is explicitly **fluent Spanish and English**, with English
positioned as sufficient for documentation and vendor/architecture reading rather than
native-level [(JD)](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote).
Given the org spans Guatemala HQ and business units across Central America and the Caribbean, and
the posting itself is bilingual (Spanish job title/body with English technical terms), Spanish is
very likely the default working language day to day. Santiago's native Spanish is a genuine
advantage here relative to non-Spanish-speaking AI-engineer candidates, and worth naming plainly
rather than treating as a throwaway line.

## 7. Reputation, risks, recent news (2025-2026)

- **April 2025:** Apex Capital (Grupo Mariposa's affiliated private-equity arm) acquired a
  majority stake in Juanita's Foods, a US Mexican-style foods manufacturer [(Food Business
  News)](https://www.foodbusinessnews.net/articles/28187-apex-capital-acquires-mexican-food-manufacturer).
- **2025 (deal expected to close Q4 2025):** Grupo Mariposa/CBC agreed to acquire Gaseosas
  Postobón in Colombia, expanding into the Andean beverage market [(Abasto
  news)](https://abasto.com/en/news/grupo-mariposa-buys-gaseosas-postobon-expands-in-colombia/).
  Net read: the group is actively expanding via M&A, a sign of financial health and growth, but
  also of a conglomerate integrating new business units rather than a focused product company.
- **McKinsey partnership** on a proprietary WhatsApp-based "conversational commerce" platform
  (with technology partner Yalo) for corner-store retailers, now also being commercialized to
  other CPGs [(McKinsey case
  study)](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action/grupo-mariposa-harnessing-connected-technology-in-the-latam-food-and-beverage-market).
  No publication date found on the case study itself; treat as recent but not precisely dated.
- **Reputation:** thin public review footprint (no dedicated Glassdoor page found for "Grupo
  Mariposa"); the closest proxy, Grupo CBC Colombia on Indeed, rates 3.9/5 for pay/benefits and
  4.1/5 overall, with reviewers calling pay reliable and legally compliant but modest [(Indeed
  reviews)](https://co.indeed.com/cmp/Grupo-Cbc/reviews?ftopic=paybenefits). Could not verify any
  negative press, layoffs, or controversies in the 2025-2026 window; none surfaced in search.

## 8. Engineering & AI direction

Two distinct threads, both sourced:
1. A real, McKinsey-advised digital-transformation program (conversational commerce via WhatsApp
   and partner Yalo) aimed at frontline retail customers across the group's 3M+ points of sale
   [(McKinsey case
   study)](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action/grupo-mariposa-harnessing-connected-technology-in-the-latam-food-and-beverage-market).
2. An internal enterprise-AI build-out inside Apex Digital / M5's Data & Analytics function,
   explicitly moving toward "an enterprise AI Agents architecture" on Databricks, Unity Catalog,
   ADLS Gen2, Azure AI/Microsoft Foundry, Copilot Studio, and Power Automate, hiring a cluster of
   data/AI roles concurrently [(GetOnBrd Grupo Mariposa
   listings)](https://www.getonbrd.com/companies/grupo-mariposa). This is this specific role's
   home. It is a Microsoft-ecosystem enterprise build, not a from-scratch AI product team; the
   emphasis on governance (NIST AI RMF, ISO 42001), security (prompt-injection defense, PII
   handling), and FinOps signals a maturing internal platform with real production stakes rather
   than an early experimental team.

## 9. Why-fit angles for Santiago

**Best hook to lead with:** Santiago has hands-on production RAG and agent experience (Pragma
Brain: RAG "company brain" with citation gating and an eval harness; MCP tool servers at Kairos
and Pragma AI) that maps directly onto this role's core ask (RAG reference architecture, agents,
tool-calling, MCP, grounding, evaluation). The role's language requirement (fluent Spanish and
English) and its home region (Guatemala HQ, LATAM-wide team) also line up with his native Spanish
and Mexico City base, a real advantage over most AI-engineer applicants to a Microsoft-stack
enterprise role.

**Secondary hook:** his internal-tooling track record (Online Basics' internal ops platform,
Kairos, Pragma's internal MCP-brain tooling) supports the "connect AI to corporate systems for
internal users" framing this role actually is, more than a generic "AI product builder" pitch
would.

**Honest concerns / watch-outs:**
- **Compensation may well land below his $70,000 floor** (see section 2); this is the single
  biggest risk and should be raised early, not discovered after a full tailor/apply cycle.
- **Stack mismatch on the Microsoft side.** His resume shows zero direct Azure, Databricks,
  Copilot Studio, or Entra ID experience; his AI work is Anthropic/OpenAI-API and self-hosted
  infrastructure (AWS, Postgres, FastAPI), not the Microsoft enterprise-AI stack this role is
  built on. He would need to frame this honestly as "transferable RAG/agent architecture skills
  applied to a new cloud ecosystem," not claim direct Azure experience he does not have.
- **Employment mechanism is unclear** (contractor vs. employee vs. Guatemala-entity payroll); if
  it is contractor, the effective ask needs to be higher than $70,000 to be fair per his own
  comp rule, making the pay gap even more likely.
- **Corporate/CPG culture** is a real shift from his founder/consultancy background; a large,
  100+ year old family conglomerate moves differently than the startups and small consultancy he
  has built. Not disqualifying, but worth acknowledging rather than pretending this is a scrappy
  AI startup.

## 10. Application-question angles

- **Why this company:** lead with the RAG/agents/MCP overlap between what Santiago has actually
  shipped (Pragma Brain's RAG brain with grounding and citation gating, MCP tool servers) and what
  this specific role is building (enterprise RAG and agent architecture with grounding, security,
  and evaluation, connected to real corporate systems). Do not lead with "I love beverages" or
  generic CPG-industry enthusiasm; the genuine hook is the technical shape of the work, not the
  industry.
- **Why you fit:** anchor on production RAG/agent architecture experience plus native Spanish
  fluency for a Guatemala-HQ, Spanish-speaking team, and be candid that the specific cloud stack
  (Azure/Databricks/Copilot Studio) is new to him but the underlying architecture patterns (RAG,
  grounding, tool-calling, evaluation, security) are the same discipline he has already shipped
  in production, just on different infrastructure.
- **Anything else:** if there is a chance to ask a question back, compensation and employment
  structure (contractor vs. Mexican payroll vs. Guatemala entity) are the two things actually
  worth clarifying early, given everything above.
- **Avoid:** do not checklist the McKinsey/Yalo consumer product story, the M&A activity, and the
  internal AI platform all in one answer; pick the RAG/agents/MCP technical overlap as the one
  throughline. Do not imply Azure/Databricks experience he does not have.

## Sources

researched: 2026-08-11

- [AI Engineer Senior at Grupo Mariposa, GetOnBrd JD](https://www.getonbrd.com/jobs/machine-learning-ai/ai-engineer-senior-grupo-mariposa-remote) (also seen as `.../ai-engineer-sr-azure-ai-microsoft-foundry-grupo-mariposa-remote`): full responsibilities, requirements, tech stack, language requirement, "compensation not disclosed," remote/residency policy. Fetched via proxy because GetOnBrd returns HTTP 403 to direct fetches.
- [Grupo Mariposa GetOnBrd company profile](https://www.getonbrd.com/companies/grupo-mariposa): company blurb (15,000+ employees, 14+ countries, 4 business units), list of concurrently open data/AI/tech roles, general benefits language.
- [Grupo Mariposa homepage](https://grupomariposa.com/): mission statement, brand list overview.
- [Grupo Mariposa business units page](https://grupomariposa.com/business-units): apex/cbc/beliv/bia structure and descriptions.
- [Grupo Mariposa CBC business unit page](https://grupomariposa.com/business-units/cbc): CBC portfolio and distribution scale ("35+ countries exported to," "2M+ points of sale").
- [Built In company profile: Grupo Mariposa](https://builtin.com/company/grupo-mariposa): 10,001+ employee size band, founded 1885, HQ Guatemala.
- [McKinsey "Rewired in Action" Grupo Mariposa case study](https://www.mckinsey.com/capabilities/tech-and-ai/how-we-help-clients/rewired-in-action/grupo-mariposa-harnessing-connected-technology-in-the-latam-food-and-beverage-market): WhatsApp conversational-commerce platform built with McKinsey and partner Yalo, now commercialized to other CPGs.
- [Food Business News: Apex Capital acquires Juanita's Foods](https://www.foodbusinessnews.net/articles/28187-apex-capital-acquires-mexican-food-manufacturer): April 2025 acquisition.
- [Abasto: Grupo Mariposa buys Gaseosas Postobón](https://abasto.com/en/news/grupo-mariposa-buys-gaseosas-postobon-expands-in-colombia/): 2025 Colombia acquisition, expected close Q4 2025.
- [CBC "About" page](https://cbc.co/en/about-2/): CBC's anchor-bottler markets (Guatemala, El Salvador, Honduras, Nicaragua, Puerto Rico, Trinidad & Tobago, Barbados, Jamaica, Ecuador, Peru), PepsiCo relationship since 1942.
- [payrollmexico.com: Data Engineer Salary in Mexico](https://www.payrollmexico.com/insights/data-engineer-salary-mexico): senior-level Mexico Data Engineer salary bands (MXN and USD), dated June 26 2026. Compensation research only; not a Grupo Mariposa figure.
- [Indeed Mexico: Senior Data Engineer salaries](https://mx.indeed.com/career/senior-data-engineer/salaries): low-sample-size (3 data points) average pay figure, flagged low-confidence.
- [Indeed: Grupo CBC pay/benefits reviews](https://co.indeed.com/cmp/Grupo-Cbc/reviews?ftopic=paybenefits): 3.9/5 pay rating, employee comments on modest-but-compliant pay, Colombia operation.
- [Global Mobility Apex, S.A. listing example on GetOnBrd](https://www.getonbrd.com/jobs/data-science-analytics/analista-business-intelligence-global-mobility-apex-s-a-remote-27de) and [Dun & Bradstreet profile of Global Mobility Apex S.A.](https://www.dnb.com/business-directory/company-profiles.global_mobility_apex_sa.fa3b99ad377d11bb79ba73dcb7815ab7.html): evidence for the likely Guatemala legal hiring entity behind these cross-country remote reqs.
- Search-only signals (no single fetchable page, used for corroboration, treat as lower-confidence): general web search results confirming ~15,000 employees / 14+ countries claim, and CBC's reported Mexico operations plus New York/Miami offices (could not verify with a primary source; flagged in section 3 as unconfirmed).

## What could not be verified

- The exact salary/compensation band for this specific role: not published anywhere found.
- Whether Grupo Mariposa/CBC has a Mexican legal entity that would employ a Mexico-resident hire
  directly (vs. contractor or Guatemala-entity arrangement): not confirmed by a primary source.
- Named reporting manager, team size, or org chart for this specific role.
- Exact publication date of the McKinsey case study.
- Any Grupo Mariposa-specific (as opposed to CBC-Colombia-specific) employee review or pay data.
