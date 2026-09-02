# Eigen Labs

**Status: DRAFT, not yet human-fact-checked.** Written for job id 8844, "Senior Agentic AI
Engineer" (Ashby req `c02fa001-23c9-4d68-8c0a-e27a742d76a4`). Researched: 2026-08-11.

## 1. Snapshot

Eigen Labs is a Seattle-based company founded in 2021 by Sreeram Kannan, the team behind the
EigenLayer restaking protocol, EigenDA, and the EigenCloud verifiable-compute platform, now
publicly repositioning around "post-AGI coordination" and agentic AI infrastructure
(eigenlabs.org, job posting, both fetched 2026-08-11). Raised roughly $220M+ across a $14.5M
seed (Aug 2022), $50M Series A (Mar 2023), $100M Series B at a reported $1B valuation (Feb 2024,
a16z crypto), and a further $70M direct token investment from a16z crypto (June 2025)
(iq.wiki/wiki/eigenlayer; coindesk.com layoffs article; theblock.co deal article, all 2026-08-11).
Headcount is reported inconsistently across third-party data aggregators (getlatka.com ~107 as of
Aug 2026, ZoomInfo ~142, ContactOut ~87; unverified, third-party estimates, fetched via search
2026-08-11), against a confirmed baseline of roughly 116 before a July 2025 layoff of 29 people
(25%) (coindesk.com, fetched 2026-08-11). HQ per the job posting's structured data is Seattle,
Washington, US; the role is listed remote (Ashby JSON-LD, fetched 2026-08-11). Posted comp band
for this role: $187,000-$253,000 (job posting).

## 2. Core narrative

Eigen Labs invented "restaking" (reusing staked ETH to secure additional protocols) and built the
infrastructure around it (EigenLayer, EigenDA, EigenCloud). In 2025-2026 the company visibly
pivoted its public narrative and hiring pitch away from "restaking protocol company" toward "frontier
lab building coordination technologies for the post-AGI world," arguing that a handful of AI labs
are consolidating power and that open networks (agentic research, inference infrastructure, capital
formation) are the counterforce (job posting description, fetched 2026-08-11; eigenlabs.org, fetched
2026-08-11). CEO Sreeram Kannan presented this thesis publicly at Manifest 2026 in Berkeley, June 13,
2026, in a talk titled "Post-AGI Coordination: Conquering Yudkowsky's Demon" (found via a public
LinkedIn post referencing the event; I could not independently verify against an official Manifest
conference program page, flagged as lower-confidence). This "Senior Agentic AI Engineer" role sits
inside that pivot: it is about building production agent infrastructure (runtimes, orchestration,
reliability, observability, cost control), not smart-contract or protocol engineering.

## 3. Mission & product

- **EigenLayer**: the original restaking protocol on Ethereum. Validators re-commit already-staked
  ETH to additional modules ("Actively Validated Services," AVSs), accepting extra slashing risk in
  exchange for extra yield, letting new services borrow Ethereum's validator security instead of
  bootstrapping their own trust network from scratch. Mainnet Stage 1 launched June 14, 2023
  (iq.wiki/wiki/eigenlayer, fetched 2026-08-11).
- **EigenDA**: a data-availability service (one of the first AVSs) offering high-throughput,
  tamper-resistant data availability for rollups (eigencloud.xyz homepage, fetched 2026-08-11).
- **EIGEN token**: a "work token" used to secure tasks that require external, subjective judgment
  (things that can't be verified purely on-chain), launched April 29, 2024, alongside a
  two-token model (EIGEN for governance/DeFi, bEIGEN for staking) (iq.wiki/wiki/eigenlayer;
  search-derived token-launch summary, fetched 2026-08-11). Reformed under proposal ELIP-12 in May
  2026 to tie the token's economic weight more directly to platform usage rather than pure
  speculation (search-derived, fetched 2026-08-11, could not independently confirm against a primary
  governance-proposal source).
- **EigenCloud** (launched ~June 2025): a broader "verifiable cloud" platform built on the restaking
  trust anchor, bundling EigenDA with newer products **EigenCompute** and **EigenAI**, positioned for
  both Web2 and Web3 developers, including AI and finance use cases (coindesk.com; eigencloud.xyz,
  fetched 2026-08-11).
- **Darkbloom**: an Eigen Labs project building distributed AI infrastructure from idle hardware
  around the world, cited in the job posting as a live example of the "open networks" thesis
  (job posting, fetched 2026-08-11).
- **ecdsa.fail**: an Eigen Labs community-challenge project inviting researchers, amateurs, and AI
  agents to collaborate on breaking ECDSA cryptography; the job posting cites it as evidence the
  company "showed how a community of scientists, amateurs, and agents can collaborate to surpass
  Google's unpublished quantum breakthrough" (ecdsa.fail, fetched 2026-08-11; job posting).

**Plain-English restaking explainer** (for cover-letter use, keep this simple): normally, if you
want to secure a new blockchain service you have to convince people to buy and stake a brand-new
token from scratch, which is slow and thin on trust. EigenLayer lets people who already staked ETH
opt in to also back new services with that same stake, so new protocols can rent Ethereum-level
security instead of building their own from zero. That's restaking.

## 4. Founders and leadership

- **Sreeram Kannan**, Founder and CEO. PhD in Information Theory and Wireless Networks (University
  of Illinois Urbana-Champaign, 2008-2012); prior research roles at Microsoft Research, Qualcomm,
  and USC; joined University of Washington as faculty in 2014 and remains an affiliate associate
  professor of electrical and computer engineering there; became EigenLayer's CEO in July 2021;
  credited with originating the "restaking" concept; NSF CAREER Award recipient
  (iq.wiki/wiki/sreeram-kannan, fetched 2026-08-11).
- The EIGEN token launch (April 2024) drew heavy community criticism over tokenomics complexity and
  distribution favoring larger depositors; Kannan has publicly acknowledged the backlash
  ("I think the first time the negativity hit was after the token launch... it just blew up in the
  most negative possible manner") (iq.wiki/wiki/sreeram-kannan, fetched 2026-08-11).
- I could not verify a full current leadership/exec roster (CTO, VP Eng, etc.) from public sources
  in this pass; flagged as unverified, worth confirming before an interview.

## 5. Funding, stage, investors, HQ

| Round | Amount | Date | Lead / notable investors | Source |
|---|---|---|---|---|
| Seed | $14.5M | Aug 2022 | Polychain Capital, Ethereal Ventures | iq.wiki/wiki/eigenlayer |
| Series A | $50M | Mar 8, 2023 | Blockchain Capital (Coinbase Ventures, Polychain Capital also cited as participants in search-derived summaries, not independently confirmed) | iq.wiki/wiki/eigenlayer |
| Series B | $100M | Feb 22, 2024 | a16z crypto; reported ~$1B valuation | iq.wiki/wiki/eigenlayer; coindesk.com |
| Token investment | $70M (direct EIGEN token purchase) | June 17, 2025 | a16z crypto, to support the EigenCloud launch | theblock.co |

Total disclosed funding is commonly cited at "$220 million" (coindesk.com, fetched 2026-08-11). HQ:
Seattle, Washington, US, per the job posting's structured location data (Ashby JSON-LD, fetched
2026-08-11).

## 6. What "Senior Agentic AI Engineer" means here (full requirements, for the tailor agent)

This is **agent infrastructure engineering**, not blockchain/smart-contract engineering and not
protocol research. Straight from the job posting (fetched directly, JSON-LD description, 2026-08-11):

**Role framing**: "work on the core systems that make AI agents actually usable in production...
You will own large parts of the system and move quickly from idea to working product. You will
spend most of your time building. Not managing. Not talking about roadmaps. Building."

**What you will do**:
- Build agent runtimes and orchestration systems (planning, tool use, memory, coordination)
- Make agents reliable (retries, failure handling, state management)
- Make agents observable (tracing, debugging, evaluation)
- Make agents cheap (cost-aware execution, performance optimization)
- Make agents useful in production, not demos
- Integrate LLMs, APIs, and external data into coherent working systems
- Define how developers build, debug, and extend agent behavior

**What they look for (evidence over years of experience)**:
- Shipped real systems people depend on
- Turned ambiguous problems into working products
- Built or deeply explored agent systems, LLM pipelines, or automation beyond demos
- Understands production system behavior: failure modes, tradeoffs, reliability
- Moves fast, iterates without waiting for perfect specs
- Strong backend/systems experience (distributed systems, APIs, infrastructure)
- Proficiency in Python, Go, TypeScript, Rust, or similar
- Reliability patterns (state, retries, observability)
- Comfortable across the stack when needed

**Nice to have**: agent frameworks (LangChain, AutoGen, CrewAI, or custom), multi-agent/orchestration
systems, LLM evaluation/prompting/performance tuning, workflow engines (Temporal, Airflow, Dagster),
developer platforms/SDKs/internal tools, retrieval systems/vector databases/memory architectures,
and (last on the list, explicitly framed as a nice-to-have, not a requirement) "interest in crypto,
distributed systems, or verifiable compute."

Notably: no Solidity, no smart-contract, no protocol-research requirement anywhere in the listing.
Crypto is one "nice to have interest" line, not a job qualification.

## 7. Tech stack signals

From this posting: Python, Go, TypeScript, Rust listed as acceptable core languages (no single one
mandated). Agent frameworks named as reference points: LangChain, AutoGen, CrewAI. Workflow engines
named: Temporal, Airflow, Dagster. The company's own product surface (from the mission section)
touches distributed systems, verifiable compute, and data-availability infrastructure, but that is
protocol-side context, not stated as this role's day-to-day stack. The other open req on their Ashby
board, "Future Builders, General Interest" (`2f08d719-09b3-493e-ae9e-f3eba2ade188`, posted 2025-10-01),
is a generic rolling-pipeline posting with no additional stack detail (fetched 2026-08-11).

## 8. Employment mechanism and the location/EOR question

**The conflict, as given**: the job posting's structured `applicantLocationRequirements` field says
Country "United States," while the posting body explicitly contemplates non-US hires: "If hired
outside of the US through an EOR, benefits will be offered based on specific country requirements
and EOR offerings." The body also describes the role as "remote-friendly, with a preference for U.S.
time zones and close collaboration with the Seattle-based team" (job posting, fetched 2026-08-11).
"Preference" is not "requirement" language.

**Supporting evidence found**:
- Eigen Labs has at least one team member based outside the US in a substantive, named role: a
  person titled "India AI Lead," based in Pune, India, running an "Agentic by Eigen" meetup series
  and demoing EigenCompute/Darkbloom at developer events in Bangalore and Hyderabad (found via web
  search of a public LinkedIn-style profile; I could not re-fetch a stable primary URL to confirm
  directly, so this is lower-confidence corroboration, not a primary source).
- The company describes itself in search-indexed material as "a remote-friendly team with hubs in"
  multiple locations (exact hub list not retrieved) (found via web search, not independently
  re-verified against a primary page).
- No named EOR provider (Deel, Remote.com, Oyster, Velocity Global) was found in any public source
  checked; a targeted search for this returned no results.
- The second open req on their board uses identical boilerplate (Seattle jobLocation, TELECOMMUTE,
  applicantLocationRequirements "United States"), suggesting this structured field may simply be an
  Ashby form default tied to the primary Seattle office location rather than a deliberately curated
  restriction, since it appears verbatim on a "general interest, any role" posting too.

**Read on the evidence**: it leans toward Eigen Labs being genuinely open to hiring outside the US
through an EOR, including this role, given the explicit EOR clause in the body text and at least one
confirmed non-US team member in a different function. Confidence is **medium**, not high: I could
not confirm a non-US *engineering* hire specifically, and the structured JSON-LD field still says
United States, which could reflect either a stale/default form field or an actual internal
requirement for this specific team that the boilerplate benefits paragraph doesn't override.
**Recommendation for Santiago**: apply, but treat the location question as open and confirm directly
with the recruiter early (e.g., in the "anything else" answer or first screen) rather than assuming
Mexico-based hire is settled. The stated preference for "close collaboration with the Seattle-based
team" and US time zones is real and worth acknowledging, not glossing over. Mexico City (CST,
UTC-6, no DST) overlaps well with Seattle (PT, UTC-8/-7): 1 to 2 hours' difference depending on the
season, meaningfully closer than most of LATAM or any European timezone, and closer than most of the
Mexico-friendly remote roles Santiago typically targets. That overlap is a legitimate, honest point
in his favor if the location question resolves favorably.

## 9. Compensation context

Posted band: $187,000-$253,000 for this role (job posting, fetched 2026-08-11), well above
Santiago's `comp.target_usd` of $100,000 and `min_usd` floor of $70,000 (config/profile.yaml). Per
the profile's `band_rule`, an ask should anchor at or above the band midpoint (~$220,000), not at his
default target.

**Is the band location-adjusted?** The posting does not state this explicitly. It lists this range
as "the target salary range for this role," determined by "skillset, prior relevant experience,
quality of interviews and market factors at the point in time of offer," with no separate
non-US/EOR band disclosed. Given the same $187K-$253K figure sits under a "US Benefits" heading
that is explicitly distinguished from the "hired outside the US through an EOR" case, it is
reasonable to read this specific number as the US-employee figure; whether an EOR-hired,
Mexico-based offer would land at, below, or the same as this band is unconfirmed. Flag this
explicitly in any comp conversation rather than assuming parity.

**Token/equity comp**: the "US Benefits" list includes "Competitive salary and non-cash compensation
(tokens and equity)" (job posting, fetched 2026-08-11). No vesting schedule, cliff, token type
(EIGEN vs. company equity), or valuation methodology is disclosed publicly. Given EIGEN's price
history (see Risks below), Santiago should treat any token component as high-variance, not a
guaranteed cash-equivalent, and ask directly in an offer conversation: which token, what vesting
cliff, and how (if at all) that changes for an EOR-based hire, since the EOR clause implies
country-specific benefit substitutions that may or may not include token grants.

## 10. Risks and watch-outs

- **Crypto market exposure**: any token-based compensation is directly exposed to EIGEN's price,
  which fell from an all-time high of $5.65 (Dec 17, 2024) to roughly $0.176-0.18 as of early August
  2026, a decline of about 97% (coinmarketcap.com, fetched 2026-08-11). This is a real, material risk
  if part of comp is token-denominated.
- **Restructuring history**: Eigen Labs laid off 29 people (25% of staff) on July 9, 2025, explicitly
  reframing around EigenCloud; leadership characterized it as a strategic reallocation, not a
  cash-crunch move, and offered three months' severance, accelerated token vesting, continued health
  coverage, and job-placement help to departing staff (coindesk.com, fetched 2026-08-11). Worth
  understanding team stability and how recently the "post-AGI" pivot (2026) has settled internally,
  given it followed a major reorg roughly a year prior.
- **Regulatory posture**: EIGEN's April 2024 launch drew community criticism over tokenomics and
  distribution; no specific SEC or other regulatory enforcement action was found in this pass, but
  crypto-token compensation generally sits in an unsettled regulatory environment (search-derived,
  fetched 2026-08-11, not confirmed against a primary regulatory filing or notice).
- **Token price volatility as a signal**: a near-97% drawdown from ATH is a legitimate business-risk
  data point to weigh (not just a personal-comp risk), since it reflects broader market sentiment on
  the EigenLayer/EIGEN ecosystem the company is still tied to even as it pivots toward "EigenCloud"
  and agentic AI.
- **Santiago's own gap**: his crypto exposure is as a personal investor since 2017 and as the builder
  of Plutus, a self-hosted personal research and portfolio-tracking tool covering stocks, crypto, and
  forex (research and analysis only, no trade execution; github.com/SantiagoCoronado/plutus). He has
  no professional blockchain, smart-contract, or protocol-engineering experience. This role does not
  require that (see section 6), so it is not a disqualifying gap, but he should not imply otherwise.

## 11. Recent news (last ~12 months, dated)

- **July 9, 2025**: Eigen Labs lays off 29 employees (25% of staff), reorienting around EigenCloud;
  CEO Sreeram Kannan calls it "one of the hardest days we've had at Eigen Labs" (coindesk.com,
  fetched 2026-08-11).
- **June 17, 2025**: a16z crypto purchases $70M in EIGEN tokens directly, following its earlier
  Series B lead, to support the EigenCloud launch (theblock.co, fetched 2026-08-11).
- **~June 2025**: EigenCloud launches as a "verifiable cloud" developer platform bundling EigenDA
  with new products EigenCompute and EigenAI (coindesk.com; eigencloud.xyz, fetched 2026-08-11).
- **May 2026**: EIGEN tokenomics reform proposal (ELIP-12) aims to tie the token's economic weight to
  platform utility rather than speculative trading metrics (search-derived summary, fetched
  2026-08-11; not independently confirmed against a primary governance document).
- **June 13, 2026**: Kannan presents "Post-AGI Coordination: Conquering Yudkowsky's Demon" at
  Manifest 2026 in Berkeley, publicly articulating the company's pivot toward open, agentic
  coordination networks as a counterweight to centralized AI labs (found via a public post
  referencing the event; primary conference-program source not independently re-verified).
- **~April 2026** (job posting's `datePosted`): this Senior Agentic AI Engineer req and the "Future
  Builders" general req both go live, both carrying the new "post-AGI" company description, framing
  Darkbloom and ecdsa.fail as flagship proof points of the open-coordination thesis (Ashby JSON-LD,
  fetched 2026-08-11).

## 12. Why-fit angles for Santiago

**Best hook to lead with**: Santiago has already built exactly the class of system this role
describes, on his own initiative, twice. Plutus exposes an LLM research agent and an autonomous
discovery engine through an MCP control plane, with scheduled vectorized scans, a ranked
evidence-backed candidate inbox, and a hand-rolled SSE streaming client for cancellable agent
responses. Kairos integrates Claude on two surfaces from one codebase (an in-app agent via the
Claude Agent SDK and a standalone MCP server), exposing 52 tools through a single typed
tool-definition layer so both a desktop app and Claude Code can operate on the same live data. Both
are runtime/orchestration/tool-use problems, not demos, matching this role's explicit "not demos,
real systems people depend on" framing (resume/master_resume.yaml).

**Supporting evidence**:
- Reliability and production instincts: Online Basics ran a Python/AWS microservice architecture
  orchestrating 10+ third-party APIs processing 100K+ daily data points on hourly sync, with
  incident-response and data-validation systems that cut data-entry errors 90%, used daily by
  operators running an $8M business (resume/master_resume.yaml). That is exactly the "make agents
  reliable, observable, useful in production" muscle the JD asks for, even though it predates LLM
  agents specifically.
- RAG with real evaluation discipline: Pragma AI's "Pragma Brain" ships scoped retrieval with
  deterministic no-answer and citation gating and an automated eval harness, and Santiago
  root-caused an over-firing no-answer gate to chunking parameters from dogfooding on a 147-file,
  1,429-passage vault (resume/master_resume.yaml). This is direct evidence of the "make agents
  reliable" and "LLM evaluation" nice-to-have.
- Tool-use/function-calling agent experience: the Pragma AI personal-finance agent uses the Hermes
  agent framework for autonomous tool-use categorization and Q&A (resume/master_resume.yaml),
  directly matching the "agent frameworks... or custom systems" nice-to-have.
- Backend/systems range: FastAPI, SQLAlchemy 2/Alembic on PostgreSQL 16 with TimescaleDB, Celery and
  Redis workers running idempotent nightly ingestion (Plutus), matching "strong backend/systems
  experience" and "Python" as a core language (resume/master_resume.yaml).

**The crypto angle, used carefully**: Santiago has been a personal crypto investor since 2017, a real
and unmanufactured overlap with a company whose entire original product is crypto infrastructure.
Plutus explicitly covers crypto alongside stocks and forex. This is usable in a cover letter as a
one-line note of authentic interest and context for why Eigen's mission lands, and as light color for
why Plutus covers what it covers. It should NOT be used to imply professional blockchain, protocol,
or smart-contract engineering experience, which he does not have and which this role does not
require. The honest framing is: personal investor and builder of a research tool, not a protocol
engineer, applying for an agent-infrastructure role that explicitly does not require blockchain
engineering.

**Honest concerns / watch-outs**:
- The US-time-zone preference and Seattle-collaboration language is real; Mexico City's overlap with
  Pacific time is a genuine mitigant, not a full answer.
- The EOR/location question (section 6) is unresolved and should be raised directly, not assumed.
- No professional crypto/blockchain experience; do not let the 2017 investor note read as more than
  it is.
- The company underwent a real reorg 13 months before this posting and a public strategic pivot as
  recently as this year; some interview time should go toward understanding whether the "post-AGI"
  framing is durable roadmap or recent rebranding, for Santiago's own diligence as much as the cover
  letter.

## 13. Application-question angles (not full answers)

**Why this company**: Lead with the specific thing that's actually true and interesting: Eigen Labs
built the technology (restaking) that let new protocols borrow Ethereum's trust instead of
bootstrapping their own, and it is now pointing that same "borrow trust, don't rebuild it from
scratch" instinct at AI agents, betting that open coordination beats centralized AI labs. Santiago
can connect this to his own founder pattern (Eugenia.ai, Online Basics, Pragma AI: build things from
zero that people actually depend on) and, briefly, to being a crypto investor since 2017 who has
watched this specific problem space from the outside for years. Avoid a checklist of "great culture,
great mission, great comp"; pick the coordination-technology thesis and one product example (Plutus's
MCP control plane or Kairos's dual-surface agent) as the through-line.

**Why you fit**: Lead with Plutus and/or Kairos as evidence of already having built the thing the JD
asks for (agent runtime, orchestration, tool-use, memory, a real evaluation/reliability discipline
from Pragma Brain), not with a list of technologies. One sharp example beats four shallow ones. If
space allows, one line on production reliability instincts from Online Basics grounds the "reliable,
observable, cheap, useful in production" bullets in something that shipped and mattered at scale
before LLM agents existed.

**Anything else**: good place to raise the location question directly and plainly (confirm whether a
Mexico City, EOR-based hire is workable for this specific role, and note the Seattle/Pacific overlap
as a genuine plus), rather than leaving it as a silent assumption. Optionally, a brief, honest
one-liner on being a crypto investor since 2017 and a personal-finance/portfolio tool builder, framed
explicitly as personal interest and not professional blockchain experience, so it reads as authentic
color rather than an inflated claim.

## Sources

- researched: 2026-08-11
- https://jobs.ashbyhq.com/eigen-labs/c02fa001-23c9-4d68-8c0a-e27a742d76a4 (fetched directly, HTML +
  embedded JSON-LD): full JD text, requirements, comp band, location/EOR language, datePosted,
  applicantLocationRequirements
- https://jobs.ashbyhq.com/eigen-labs/2f08d719-09b3-493e-ae9e-f3eba2ade188 (fetched directly): second
  open req ("Future Builders, General Interest"), confirms boilerplate location fields repeat across
  postings
- https://jobs.ashbyhq.com/eigen-labs (fetched directly): confirms only two open reqs
- https://www.eigenlabs.org (fetched directly): company mission/self-description ("post-AGI",
  coordination technologies)
- https://www.eigencloud.xyz (fetched directly, redirect target of eigenlayer.xyz): EigenLayer,
  EigenDA, EigenCloud, EigenCompute, EigenAI product descriptions
- https://www.ecdsa.fail (fetched directly): Darkbloom/ecdsa.fail community-challenge project,
  confirmed "An Eigen Labs Project"
- https://iq.wiki/wiki/sreeram-kannan (fetched directly): Sreeram Kannan bio, education, career,
  EIGEN token launch controversy quote
- https://iq.wiki/wiki/eigenlayer (fetched directly): restaking explainer, EigenDA, EIGEN token
  mechanics, mainnet launch date, seed/Series A/Series B funding figures and dates
- https://www.coindesk.com/business/2025/07/09/eigen-labs-axes-25-of-staff-to-focus-on-building-eigencloud
  (fetched directly): July 9, 2025 layoffs, headcount, $220M total funding, $1B Series B valuation,
  severance terms, Kannan quotes
- https://coinmarketcap.com/currencies/eigenlayer/ (fetched directly): current EIGEN price, all-time
  high ($5.65, Dec 17, 2024), price decline, market cap
- The Block, "a16z crypto buys $70M of EIGEN tokens to back EigenCloud," June 17, 2025,
  www.theblock.co/news/deals/2025-06-17-a16z-crypto-eigen-token-eigencloud-358511 (found via search,
  content summarized from search snippet, not independently re-fetched in full): $70M token
  investment date and purpose
- Manifest 2026 conference talk by Sreeram Kannan, June 13, 2026, "Post-AGI Coordination: Conquering
  Yudkowsky's Demon" (found via a public post referencing the event; I could not independently
  re-verify against an official conference program page; flagged lower-confidence)
- Third-party headcount estimates (getlatka.com ~107 as of Aug 2026, ZoomInfo ~142, ContactOut ~87)
  found via search, not independently re-fetched or reconciled; flagged as unverified and
  inconsistent
- "India AI Lead" team member based in Pune, India, running Eigen community events (found via search
  of a public profile; could not re-fetch a stable primary URL to confirm directly; used only as
  lower-confidence corroborating signal for the EOR/location question, not a standalone claim)
- resume/master_resume.yaml, config/profile.yaml (internal, Santiago's own verified background and
  targeting rules, used for the fit-angle sections)

## What I could not verify

- The exact current headcount (three conflicting third-party figures, none confirmed against a
  primary company statement).
- A named EOR provider used by Eigen Labs for non-US hires.
- A confirmed non-US, specifically *engineering*, hire (the one non-US hire found is in a
  community/marketing function).
- Full current executive/leadership roster beyond Sreeram Kannan.
- Primary-source confirmation of the ELIP-12 tokenomics reform and the exact Manifest 2026 program
  listing (both relied on search-derived summaries rather than a direct fetch of a primary document).
- Whether the posted $187K-$253K band would be paid identically, reduced, or adjusted for a
  Mexico-based EOR hire.
