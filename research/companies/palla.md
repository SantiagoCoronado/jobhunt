status: DRAFT, not yet human-fact-checked by Santiago
researched: 2026-08-11

# Palla

## 1. Snapshot
Palla is a Miami-based fintech (YC S21) that provides embedded, instant cross-border P2P payments
infrastructure: APIs and white-label components that banks and fintechs plug into their own apps
to let customers send and receive international transfers in seconds instead of days [ycombinator.com/companies/palla]
[palla.com]. Stage: Series A, ~22-23 employees as of early 2026 [ycombinator.com/companies/palla]
[tracxn.com/d/companies/palla-financial]. HQ: Coral Gables, Miami, FL; hiring is remote across the
US and much of LATAM/Caribbean [businesswire.com 2025-05-28] [ycombinator.com/companies/palla].
Funding: $14.5M Series A closed May 28, 2025, led by Revolution Ventures with Y Combinator, Cowboy
Ventures, Ardent, Dash Fund, Uncommon Capital, Meta Fund, Evolution VC, First Check Ventures,
Vitalize, and DeepWork Capital participating [businesswire.com 2025-05-28]. One secondary
aggregator (Tracxn, via search snippet) cites $17.45M total raised, which is not corroborated by
the primary funding announcement; treat that figure as unverified.

## 2. Core narrative
Palla's pitch is that traditional remittance rails (Western Union style, cash-based) charge up to
8% and take days; Palla routes money over existing debit-card rails at a roughly 1 to 1.5% FX
markup, in seconds, embedded invisibly inside a bank's or fintech's own app rather than as a
separate consumer brand [refreshmiami.com] [businesswire.com 2025-05-28]. It is explicitly a B2B2C
infrastructure play: Palla does not compete for the end remittance customer, it sells the rails to
30+ financial institutions (Banco Pichincha in Ecuador, Hey Banco and Albo in Mexico, Nequi,
Afirme, Zinli in Panama) who already have 150M+ combined end users across LATAM and the Caribbean
[palla.com] [refreshmiami.com]. The engineering pitch layered on top (from the job posting itself)
is an "AI-native," small, fast-shipping team: weekly ships, engineers who talk directly to
customers, and Claude Code / Cursor treated as core tooling rather than a side experiment
[findwork.dev job posting, id 9118].

## 3. Mission & product
- Product: pre-built payment blocks (payment links, transfer connections/profiles, FX calculator,
  transaction history, receipts) plus a full API and white-label app that a partner brands as its
  own [palla.com].
- Claimed performance: median transfer time under 10 seconds, 50+ live payment corridors, 99.999%
  platform uptime and 99.99% API uptime in 2025, 2.5M+ enrolled end users across partner apps
  [palla.com]. These are the company's own published metrics; independently unverified.
- Business model: B2B2C, sells to banks/fintechs/marketplaces/remittance providers rather than to
  consumers directly [palla.com] [refreshmiami.com].
- Named customers/partners: Banco Pichincha (Ecuador), Hey Banco and Albo (Mexico), Nequi, Afirme,
  Zinli (Panama), and 30+ financial institutions total [palla.com] [refreshmiami.com].
- Regulatory framing: CEO Enrique Perezalonso frames the FX markup (1-1.5%) as the underlying
  economics versus 8% cash-remittance competitors [refreshmiami.com].

## 4. Culture & voice
- No dedicated culture/values page or public social presence with distinct voice was found; the
  company's public tone (site, YC page, job posting) is plain, metrics-driven fintech-infrastructure
  language, not consumer-brand marketing [palla.com] [ycombinator.com/companies/palla].
- The job posting is the clearest culture signal available: "we ship weekly, not quarterly,"
  "engineers talk directly to customers," "generalists own vertical slices end-to-end," "agents
  handle the toil, humans handle the judgment," explicit use of Claude Code and Cursor across the
  SDLC, "direct access to leadership, partners, and customers, no layers between you and the
  decisions" [findwork.dev job posting, id 9118]. This reads as a deliberately small, high-leverage,
  AI-forward engineering culture, consistent with a ~22-person Series A team.
- Board addition of Heidi Miller (former president of JPMorgan International) alongside Revolution
  Ventures managing partner David Golden signals an institutional/regulatory-credibility push
  alongside the scrappy engineering story [refreshmiami.com].
- No verified news of layoffs, controversy, or negative press was found in the 2025-2026 window
  searched.

## 5. Recent news (last ~12 months)
- 2025-05-28: Closed $14.5M Series A led by Revolution Ventures, joined by YC, Cowboy Ventures,
  Ardent, Dash Fund, Uncommon Capital, Meta Fund, Evolution VC, First Check Ventures, Vitalize,
  DeepWork Capital; Heidi Miller (ex-JPMorgan International president) and David Golden (Revolution
  Ventures) joined the board [businesswire.com] [refreshmiami.com] [ffnews.com].
- 2025-05-29: Broader trade coverage of the raise framed Palla alongside Conduit as part of a wave
  of cross-border payments fundraising [paymentsdive.com] [fintech.global].
- Early 2026: Reported headcount 22-23 employees (Jan 31, 2026 snapshot) [tracxn.com/d/companies/palla-financial].
- No specific 2025-2026 product launch, leadership change beyond the Series A board additions, or
  negative-news item was found in this research pass. If something more recent exists, it was not
  surfaced by the sources checked; flag as unverified rather than assumed absent.

## 6. Engineering & AI direction
- Stack, as stated directly in the open Senior Full-Stack Engineer, Payments job posting: AWS, Go,
  React, TypeScript, and DynamoDB [ycombinator.com job posting 9jq5CH2] [findwork.dev job posting,
  id 9118].
- Engineering model described in the posting: small "AI-native" team, weekly production ships onto
  real payment rails, engineers own vertical slices end-to-end (API design, backend, partner
  integrations, white-label clients, infra), on-call for what they build, AI agents (Claude Code,
  Cursor, "the agent stack across our SDLC") treated as core infrastructure rather than optional
  tooling, fully expensed AI tooling [findwork.dev job posting, id 9118].
- A GitHub organization (github.com/palla-financial) is referenced by third-party aggregators as
  hosting card-encryption sample code and a web SDK for embedding Palla's flows, but the org
  returned a 404 on direct check during this research pass (private or renamed); could not verify
  its contents directly. Treat as unverified.
- No dedicated public engineering blog was found.

## 7. Why-fit angles for Santiago
Best hook to lead with: Santiago is a founder who has shipped and owned full-stack systems end to
end (frontend, backend, infra, data pipelines) with no handoffs, at Online Basics, Eugenia.ai, and
in his personal projects (Plutus, Kairos), and he already builds daily with Claude Code and agent
tooling rather than dabbling in it. That maps directly onto Palla's stated engineering model:
generalist ownership of vertical slices, AI agents as core SDLC infrastructure, weekly shipping,
small team, direct customer contact [findwork.dev job posting, id 9118] vs. [resume/master_resume.yaml
Online Basics, Plutus, Kairos, Pragma AI entries].

Supporting angles:
- LATAM fluency is a stated "bonus point" in the posting, not a requirement: Santiago is Mexico
  City based, bilingual, and has run a Mexican business through 10+ third-party API integrations
  (Amazon, Mercado Libre, Inflow) at real transaction volume, which is directly relevant texture
  for integrating partner APIs (banks, card networks, KYC providers) even though it is not payments
  specifically [findwork.dev job posting, id 9118] vs. [resume/master_resume.yaml Online Basics].
- Founder ownership and 0-to-1 building (Eugenia.ai built and exited, Online Basics scaled to $8M)
  matches "owner mindset, measure yourself in shipped outcomes" and "product instinct, you'd rather
  talk to a customer than read a PRD" language in the posting [findwork.dev job posting, id 9118].

Honest concerns/watch-outs:
- The posting's "what you bring" section explicitly requires a fintech or payments background:
  "You've shipped code that moved money, handled PII, or interacted with regulated infrastructure
  (banks, card networks, KYC/AML, ledgers, settlement)." Santiago has none of this. This is a real,
  named gap, not a stretch requirement, and the matcher already flagged it (missing_skills:
  "production payments or fintech experience", "KYC/AML rails") [findwork.dev job posting, id 9118]
  [job 9118 match_verdict, data/jobs.db].
- The posting asks 5+ years of full-stack production experience at "meaningful scale," not 6+; his
  7+ years founder-engineer background covers this, but he should not claim more payments-specific
  seniority than he has.
- Compensation floor risk: see section 6 (comp) below, the posted $80K-$200K band bottom clears
  his $70,000 LATAM floor by only $10,000 and there is no verified statement of how the band splits
  by geography.

## 8. Compensation (read before tailoring an ask)
- Posted band on the live req: $80,000 to $200,000 USD, with the line "*salary range is experience
  & location dependent" appended directly in the job description text [findwork.dev job posting,
  id 9118, description field] [ycombinator.com job posting 9jq5CH2].
- No source found states explicitly whether $80K is the LATAM/Mexico number and $200K is the US
  number, or whether the spread is purely seniority-based (5+ years vs. much more senior). This
  could not be verified from the YC listing, the company site, Glassdoor, or Levels.fyi (no Palla
  entry exists on Levels.fyi; Glassdoor searches returned unrelated companies named "Pall" and
  "PayPal," not Palla) [glassdoor.com search, no Palla-specific result] [levels.fyi search, no
  Palla-specific result].
- Circumstantial signals worth weighing (not proof): the posting lists "Health, dental, and vision
  coverage" as a benefit without a location qualifier, and lists LATAM/Spanish fluency as a bonus
  rather than a requirement, which suggests the role is genuinely open to non-US hires rather than
  US-only with token remote flexibility [findwork.dev job posting, id 9118]. At a 22-23 person
  Series A company hiring across nine-plus countries on one req, a single flat band spanning junior
  senior to staff-plus seniority is at least as plausible as a strict geography split; both
  explanations fit the evidence equally well.
- Bottom line for Santiago: this is unverified and should be treated as a real risk, not resolved
  by assumption. Recommended approach per `config/profile.yaml` band_rule (anchor at or above the
  midpoint of a known band, floor comp.min_usd_latam_scope = $70,000): do not self-select down to
  the $80K floor. Anchor conversation expectations near or above the band midpoint (~$140,000) and
  ask directly, early in process, how the band is set for a Mexico City hire before naming a number
  first. If a recruiter states a hard LATAM sub-band, compare it against the $70,000 floor before
  proceeding.

## 9. Employment mechanism for a Mexico-based hire
Not stated anywhere found: no source specifies whether a Mexico-based hire would be a direct
employee, a contractor, or hired through an EOR (Employer of Record). The posting's benefits line
("Health, dental, and vision coverage") reads like a US-employee benefits package and was not
qualified as international-inclusive [findwork.dev job posting, id 9118]. No evidence was found
that Palla currently has any Mexico-based (or other LATAM-based) staff; the company's own
descriptions list Mexico among hiring-eligible countries but list HQ and the founding team in
Miami, and no LinkedIn/team-page evidence of existing LATAM-based engineers surfaced in this
search [ycombinator.com/companies/palla] [businesswire.com 2025-05-28]. Flag explicitly as
unverified: Santiago should ask directly in a screen whether Mexico hires go through an EOR
(affecting take-home vs. gross), a contractor arrangement (per `config/profile.yaml`
contractor_note, a contractor rate should sit above the equivalent employee salary), or direct
local employment.

## 10. Role requirements (for the tailor agent)
From the live req (findwork.dev, sourced from YC job 9jq5CH2), verbatim substance:
- Must-haves: 5+ years shipping production systems at meaningful scale; Bachelor's in CS/Software
  Engineering or related technical field; fintech or payments background (shipped code that moved
  money, handled PII, or touched regulated infrastructure such as banks, card networks, KYC/AML,
  ledgers, settlement); true full-stack range across frontend, backend, and infra with no handoffs;
  owner mindset measured in shipped outcomes; product instinct (prefers talking to customers over
  reading PRDs); AI fluency (already builds with agents, has opinions on where they work and where
  they break); scrappy and fast (ships a working v1 over a perfect v2).
- Bonus: cross-border payments, remittances, or FX experience; LATAM market experience or Spanish
  fluency; has operated a real agentic system in production, not a demo; early engineer experience
  at a Seed or Series A startup.
- What the role does day to day: full-stack feature design/build/ship across APIs, backend
  services, partner integrations, white-label clients, and infra; owns production systems including
  on-call; integrates partner APIs (banks, card networks, payout rails, KYC providers) and
  compresses weeks of integration into days; works directly with partners and product to turn real
  customer needs into shipped code; builds with AI agents (Claude Code, Cursor) as core to the
  SDLC; helps shape engineering bar, hiring loop, and culture of an early team.
- Benefits stated: competitive base salary plus founding-team equity, fully remote across US and
  LATAM with occasional in-person team gatherings, fully expensed top-tier AI tooling, direct access
  to leadership/partners/customers, health/dental/vision coverage, a learning budget.
[findwork.dev job posting, id 9118]

## 11. Payments domain gap, named precisely
Santiago has no fintech or payments background. What he would specifically need to learn or credibly
speak to, that is not covered by his existing resume:
- Money movement mechanics: how funds actually settle across a debit-card rail versus an ACH/wire
  versus a card network, and where Palla's stated 1-1.5% FX markup sits in that chain
  [refreshmiami.com].
- KYC/AML compliance basics: what a KYC provider integration entails (identity verification,
  sanctions screening, transaction monitoring) and how PII handling differs from a typical SaaS
  integration; the posting names this explicitly as a required background, not a nice-to-have
  [findwork.dev job posting, id 9118].
- Ledger and settlement concepts: double-entry ledger design, reconciliation, and idempotency
  requirements specific to regulated money movement (distinct from the general idempotent-pipeline
  experience he has from Plutus's market-data ingestion, which is a related but not equivalent
  skill) [resume/master_resume.yaml Plutus project].
- Card network and payout-rail integration patterns: how partner integrations with banks and card
  networks differ operationally from the e-commerce marketplace APIs (Amazon, Mercado Libre) he has
  integrated at Online Basics; the API shapes, compliance gates, and failure-handling stakes are
  materially different when the payload is money movement rather than inventory or pricing data
  [resume/master_resume.yaml Online Basics].
This gap is real and should not be minimized in an application; the honest angle is that his
adjacent experience (regulated-adjacent PII handling at Eugenia.ai's building-access product,
high-volume API orchestration at Online Basics, agentic system building) is transferable scaffolding,
not equivalent domain experience.

## 12. Reputation, risks
- No negative press, litigation, or controversy surfaced in this research pass (searches covered
  general news, fintech trade press, and company-news queries through August 2026).
- Risk: very small team (22-23 people) at Series A means concentration risk (loss of a few
  engineers or a partner bank matters a lot) and likely thinner HR/benefits infrastructure for
  international hires than a larger company; consistent with the unresolved EOR/contractor question
  in section 9 [tracxn.com/d/companies/palla-financial].
- Risk: the job posting's own "salary range is experience & location dependent" caveat, combined
  with no public comp data, means Santiago cannot pre-verify the number before a conversation; he
  should surface this directly rather than assume the top of the band applies to him.
- The $14.5M total raised (Series A only, per the primary funding announcement) versus a
  $17.45M figure from a secondary aggregator is an unresolved discrepancy; use $14.5M as the
  sourced figure and do not repeat $17.45M as fact.

## 13. What a cover letter should do, and what to avoid
Lead with: Santiago's track record of owning full-stack systems end to end, including regulated-
adjacent infrastructure work (Online Basics' 10+ API integrations processing 100K+ daily data
points, Eugenia.ai's access-control and PII-adjacent building-management product), paired with his
genuine daily use of AI agents (Claude Code, MCP, the Claude Agent SDK across his own projects),
which mirrors Palla's stated "AI-native," agent-as-teammate engineering culture more concretely than
most candidates can claim. Mention LATAM/Mexico City base and bilingual fluency as a natural fit for
a company whose end customers are 150M+ people across LATAM and the Caribbean, briefly, not as the
main pitch.

Avoid: claiming payments or fintech domain experience he does not have; do not stretch the Online
Basics API integrations or Eugenia.ai's PII handling into "payments experience," name them for what
they are (adjacent, not equivalent). Avoid checklisting mission, culture, news, and engineering
stack in one letter; pick the ownership plus AI-native hook and go deep on it. Do not name a
compensation number in the letter; that gap is a conversation topic, not a cover-letter topic. Zero
em-dashes throughout, per house style.

## Sources
- https://www.ycombinator.com/companies/palla (company overview, founders, YC batch S21, headcount ~22, HQ regions, hiring geography)
- https://www.ycombinator.com/companies/palla/jobs/9jq5CH2-senior-full-stack-engineer-payments-remote-us-latam-engineering (live req: comp band, tech stack, full requirements, benefits, hiring countries)
- job id 9118 description field, data/jobs.db, sourced from findwork.dev (mirrors the YC req text verbatim, used for exact requirement wording)
- https://www.businesswire.com/news/home/20250528284383/en/Palla-Secures-$14.5-Million-Series-A-Funding-to-Drive-Expansion-and-Innovation-in-Cross-Border-Payments (Series A amount, investors, board additions, date 2025-05-28)
- https://refreshmiami.com/news/palla-raises-14-5m-to-power-instant-cross-border-payments-for-banks/ (Series A detail, HQ Miami, FX markup quote, partner count, board quote)
- https://www.paymentsdive.com/news/conduit-palla-raise-cross-border-payments-fundraising-capital/749431/ (trade-press context on the raise)
- https://fintech.global/2025/05/29/palla-secures-14-5m-to-transform-international-payments-infrastructure/ (secondary funding coverage)
- https://www.palla.com/ (product description, named partners, platform metrics, business model)
- https://tracxn.com/d/companies/palla-financial (headcount snapshot Jan 2026, competitor ranking; secondary aggregator, used only for headcount corroboration)
- GitHub org github.com/palla-financial referenced by third-party aggregators (card-encryption sample, web SDK); returned 404 on direct check 2026-08-11, contents unverified
- Glassdoor and Levels.fyi searched directly for Palla-specific compensation data; no Palla-specific entries found on either platform as of 2026-08-11
- config/profile.yaml (Santiago's comp floor, location rule, contractor note, band rule)
- resume/master_resume.yaml (Santiago's verified work history used for fit-angle mapping)
