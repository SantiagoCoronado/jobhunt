# Ashby (ashbyhq.com)

Draft dossier for Santiago's review. Researched 2026-08-11 against local job id 9080
("Hiring Senior/Staff Product Engineers (Americas)", https://findwork.dev/nZlp9qM/hiring-seniorstaff-product-engineers-americas-at-ashby).

## 0. LOCATION SCOPE, READ THIS FIRST

The req title says "Americas" but the two live, currently-open requisitions behind it are
country-locked, and Mexico is not confirmed in scope:

- **Senior Product Engineer - Americas** (live req, id `751768c6-8d97-4e91-a57d-6b85ce4b5a37`,
  published 2026-04-30, `isListed: true` as of 2026-08-11). Ashby's own job-board API returns
  its structured location field as `"location": "Remote - US"`, `"address": {"addressCountry":
  "United States"}`, with 14 named secondary locations, all US cities (Austin, Boulder, LA,
  Portland, Atlanta, Salt Lake City, Boston, Seattle, New York, San Francisco, Denver, Ann
  Arbor, Chicago, Raleigh). No Mexico or LATAM city or country appears anywhere in the
  location data.
- **Staff Product Engineer - Americas** (live req, id `6a15668c-3f98-4404-8f1f-927cddfc5af7`,
  published 2026-04-30, `isListed: true`). Same pattern: `"location": "Remote - US"`, same
  14 US-only secondary locations.
- Ashby posts a **separate, distinct** requisition, "Senior Product Engineer - Canada" /
  "Staff Product Engineer - Canada," with `"location": "Remote - Canada"` and Canadian
  secondary cities only. This confirms Ashby splits Product Engineering hiring by country
  (US req vs. Canada req), not by "the Americas" as a single open region. The department is
  internally named "Americas Engineering" (paired against "EMEA Engineering"), which appears
  to label the org chart, not the hiring geography.
  (Source: `https://api.ashbyhq.com/posting-api/job-board/ashby`, Ashby's own public job-board
  API, fetched 2026-08-11.)
- The job description body itself (fetched from the same API) never states "US citizens
  only" or an explicit residency requirement in prose, but it also never mentions Mexico,
  LATAM, or "the Americas" as an eligible candidate location. It does say the team is "on
  track to double this year" and references timezone-spanning async work, which is why an
  aggregator or an HN "who's hiring" post could plausibly read as globally open.
- Ashby's own engineering compensation policy (see Comp section below, primary source:
  `https://www.ashbyhq.com/blog/engineering/leveling-and-compensation`) states plainly: "We
  have four regions with compensation bands: US, Canada, UK, and the EU. We do not have
  compensation bands for LATAM, Africa, APAC, and Switzerland... If you're in one of these
  unsupported regions..., we will do individual research to determine your compensation when
  we extend an offer." This confirms Ashby occasionally hires into LATAM as an exception
  (not as a standing, banded program), which is consistent with Mexico not appearing as an
  eligible location on this specific req.
- Company-wide, Ashby describes itself as "a remote-first company with colleagues working
  from 24 different countries in North America, South America, Europe, and Asia" (source:
  `https://www.ashbyhq.com/team`, fetched 2026-08-11), so South America-based hires exist
  somewhere in the company, department unconfirmed. The same page also mentions a "Company
  offsite in Mexico," which is a travel/retreat location, not evidence of a Mexico-based hire.

**Verdict:** the matcher's `location_ok: true` call on job 9080 (built from the generic HN
"who's hiring" text, which just says "Americas" and links to the general careers page) does
not hold up against the live req's own structured location data. The two open Product
Engineering "Americas" reqs are US-remote by every primary signal Ashby publishes; Mexico is
not listed, banded, or referenced as eligible anywhere Ashby controls. This matches the
pattern from three other recent misreads this session (a disqualifying scope living outside
the description text). Recommend Santiago either confirm directly with Ashby recruiting
before investing in a tailored application, or treat this as a likely-excluded location and
deprioritize accordingly. It is not a hard "no": Ashby's own comp policy leaves room for
individual-research offers outside its four banded regions, so a strong candidate could still
get a yes, but it would be the exception Ashby describes, not the norm the req implies.

Posting status: both reqs are currently live and listed on Ashby's own board as of
2026-08-11 (`isListed: true`), so this is not a stale/expired posting question, it is
specifically a geography question.

## 1. Snapshot

All-in-one recruiting platform (ATS, sourcing, scheduling, analytics, AI interviewing) for
high-growth companies; customers include Notion, Linear, Shopify, and Snowflake. Founded
2018 (YC W19 batch) by Benjamin "Benji" Encz (CEO) and Abhik Pramanik (Co-founder, VP of
Engineering), HQ San Francisco. Series D, $50M raised July 2025 at roughly 2x the Series C
valuation (exact figure undisclosed); $128M raised total across 4 rounds. Remote-first,
colleagues in 24 countries. 220 employees at the July 2025 Series D announcement; the April
2026 job posting says the team is "on track to double this year." Not stated as profitable,
but described as running a "burn multiple under 1x" with most of its Series C left untouched
before raising the D.
(Sources: ashbyhq.com/story, ashbyhq.com/blog/culture/series-d, ashbyhq.com/team)

## 2. Core narrative

Ashby was started because its founders spent two years steeped in recruiting operations,
interviewed 100+ talent leaders, and concluded that TA teams had leveled up faster than the
software built for them. Their engineering pitch mirrors that origin story directly: Product
Engineers own a feature end to end (spec, design, build, ship) with minimal process, in an
almost-no-meeting culture, judged on customer empathy and taste rather than credentials, on
a team where more than 80 to 90 percent of engineers are already Senior level or above.

## 3. Mission & product

Ashby builds a single-system alternative to point-solution recruiting tools: ATS core, plus
sourcing, interview scheduling ("Calendar Tetris" automation), analytics, offer signing, and
(as of 2026) AI interviewing and an AI assistant. It sells to "ambitious" high-growth
companies, with named customers Notion, Linear, Shopify, and Snowflake. Revenue grew 135%
year over year as of the July 2025 Series D announcement, customer count grew from 1,300 to
2,700+ in about a year, and enterprise-segment revenue grew 123% year over year.
(Sources: ashbyhq.com/story, ashbyhq.com/blog/culture/series-d)

## 4. Culture & voice

Culture is documented mostly through long, first-person engineering leadership posts rather
than social-media presence. Recurring, sourced themes:

- Engineer-as-product-owner: engineers write specs, do competitor research, make wireframes,
  and ship end to end; Product Managers hand off problem briefs rather than specs.
- Minimal process, deliberately: no daily standups, no sprint planning, no leetcode or
  whiteboard interviews. One shared example calendar of a 4-plus-year engineer shows about
  34 hours of focus time, 2.5 hours of interviews, and 3.5 hours of meetings in a week.
- Fast, small-team leverage: CI/CD runs about 10 minutes, the team deploys 15-plus times a
  day, and the description claims the team has "built the equivalent of three or more
  VC-backed startups" with a very small headcount.
- Long tenure is used as a selling point: the compensation blog explicitly promises equity
  refreshers so employees past their initial 4-year grant are not disadvantaged versus new
  hires, and the team page and job post both cite specific 3 to 4-plus-year engineers by
  name.
- Diversity is stated with numbers, not slogans: "25% of engineers and 50% of our engineering
  leaders at Ashby are from underrepresented groups."
- In-person cadence: one company-wide and one department-wide offsite per year, plus a small
  budget for regional meetups; team page references a company offsite held in Mexico.
(Sources: ashbyhq.com/blog/engineering/leveling-and-compensation, live job description text
via api.ashbyhq.com/posting-api/job-board/ashby, ashbyhq.com/team)

## 5. Recent news (last ~12 months)

- **2026-05-07**: Acquired Talent Llama, an AI-interviewing startup, and launched an AI
  Interviewer product at the "Ashby One" conference, letting teams run structured
  conversational screening interviews inside Ashby with results feeding scheduling and
  evaluation workflows. Talent Llama's two founders joined Ashby to rebuild the product on
  Ashby's infrastructure. (prnewswire.com/news-releases/ashby-expands-into-ai-interviewing...)
- **2026-05-07 (same event)**: Announced a broader AI expansion: an "Ashby Assistant"
  conversational interface over recruiting data, "AI Talent Rediscovery" to resurface past
  candidates, and a public MCP server so AI models/agents can access Ashby data in a
  structured way. (ashbyhq.com/ashby-one-whats-new, ashbyhq.com/product-updates/ashby-assistant)
- **2026-06-02**: Published "AI, Ashby Engineering, and the Future," disclosing that more
  than half of new production code since August 2025 has been AI-generated, with stated bug
  rates unchanged despite team and customer growth. (ashbyhq.com/blog/engineering/ai-ashby-engineering-and-the-future)
- **2025-07-22**: Raised a $50M Series D led by Alkeon Capital (co-led by existing investor
  Lachy Groom; F-Prime, Elad Gil, and Gaingels also participated), at roughly 2x the Series C
  valuation (undisclosed figure). (ashbyhq.com/blog/culture/series-d)

## 6. Engineering & AI direction

**Stack** (as stated on the live req): TypeScript on both frontend and backend, React,
GraphQL API, Node.js, Postgres, Redis. The posting explicitly says prior experience in this
exact stack is not required, "but a love of typed languages is helpful," and cites engineers
who switched in from Swift, Kotlin, iOS, and Windows backgrounds.

**AI in engineering** (from the June 2026 engineering blog post, author Colin Howe, Head of
EMEA Engineering): engineers get unlimited-token access to Cursor, Claude Max, and Codex; the
company does not mandate AI usage or measure token spend. Two named working modes: "sidekick"
(AI assists, engineer decides, the default) and "delegate" (AI runs autonomously on low-risk
work like prototyping). More than half of new production code has been AI-generated since
August 2025. Automated first-pass code review runs through linters, DangerJS, and CodeRabbit,
plus a custom internal tool the post says outperforms third-party tools on edge-case bugs.
Stated stance: "AI isn't coming for our jobs, it's coming for the mechanical parts of them:
syntax, glue code, and keystrokes," with human review still mandatory on everything shipped.

**Product Engineer role definition** (from the live req description, same for Senior and
Staff): a Product Engineer owns "a large portion of one of our products" end to end, doing
work traditionally split across engineering, product, and design: researching competitors,
writing specs, making wireframes, then implementing. The req states more than 90% of the
current team would be considered Senior or above in the industry, and explicitly warns the
role is a bad fit for anyone who wants a tech lead/staff/principal track built around project
management or architecture review rather than hands-on building, or who wants to mentor
junior engineers (the team skews too senior for that to be a regular part of the job).

**Seniority split (Senior vs. Staff)**: Ashby's public leveling scheme (see Comp section)
places Senior at internal level L3 and Staff at L4, with the same job description, interview
loop, and stack used for both; the practical difference is scope of ownership and comp band,
not a different day-to-day role. The req itself does not spell out a numeric Senior/Staff
headcount split beyond the "90%+ Senior or above" team-wide figure.

**Interview process** (stated on the live req): intro call with the hiring manager (15-30
min), a technical screen pairing in Ashby's real codebase (1 hour), then three non-coding
interviews on product thinking, technical design, and infrastructure (3h15m total, can span
multiple days). No leetcode or whiteboard exercises. Onboarding ships a first production
change on day one via a single setup script.
(Source for this whole section: live job description text, api.ashbyhq.com/posting-api/job-board/ashby,
plus ashbyhq.com/blog/engineering/ai-ashby-engineering-and-the-future)

## 7. Compensation

Ashby publishes full salary bands by level and metro on its engineering blog (dated
2026-07-27, ashbyhq.com/blog/engineering/leveling-and-compensation), targeting the 75th
percentile per band and offering salary/equity tradeoffs within each range. Level 3 = Senior,
Level 4 = Staff:

| Region / tier | Senior (L3) | Staff (L4) |
|---|---|---|
| US, SF Bay Area & NYC | $210,000 to $250,000 | $250,000 to $295,000 |
| US, Seattle | $204,000 to $245,000 | $239,000 to $284,000 |
| US, Tier 2 (e.g. LA, Boston, Chicago, Austin) | $189,000 to $225,000 | $232,000 to $270,000 |
| US, Tier 3 (all other US metros) | $178,000 to $216,000 | $232,000 to $270,000 |
| Canada, Toronto/Vancouver | CA$210,000 to CA$248,000 | CA$256,000 to CA$300,000 |
| Canada, other metros | CA$195,000 to CA$229,000 | CA$256,000 to CA$300,000 |
| UK, London | GBP123,000 to GBP149,000 | GBP151,000 to GBP184,000 |
| EU, Tier 1 (Amsterdam, Berlin, Dublin, Munich, Stockholm, Denmark) | EUR119,000 to EUR145,000 | EUR154,000 to EUR188,000 |

**LATAM (Mexico included): no published band.** Ashby names exactly four banded regions
(US, Canada, UK, EU) and states directly that LATAM, Africa, APAC, and Switzerland "don't
yet have" enough active candidate/employee volume to justify building a band. For those
regions: "we will do individual research to determine your compensation when we extend an
offer and at your annual reviews." In practice this means: if Ashby does make a Mexico-based
offer, there is no public number to anchor on, and the number is set case by case, not from
this table. Every published band above, at every level and tier, clears Santiago's 70,000
USD annual LATAM-scope floor several times over, so pay is not the risk here; eligibility is.

## 8. Why-fit angles for Santiago

**Lead hook, if location clears:** end-to-end feature ownership with product and design
folded into the engineering role, on a team where the norm (90%+ Senior+) matches how he has
already operated as a solo or near-solo builder. His resume is full of exactly this shape of
work: he wrote the specs, designed the UI, and shipped the backend himself on Plutus (11-route
React frontend, FastAPI/Celery backend, an autonomous discovery engine, an MCP control plane)
and on Kairos (Electron app, 46-tool MCP server, 23-table SQLite schema, 228 Vitest tests),
without a product or design team handing him a finished brief. That is close to a literal
match for what the req asks a Product Engineer to do day to day.

**Stack overlap:** the req's stack (TypeScript both sides, React, Node.js, Postgres, Redis)
lines up directly with his frontend and internal-tooling work (Plutus's React 18/TypeScript
frontend and FastAPI/Postgres backend, Kairos's React 19/TypeScript/SQLite stack, Eugenia.ai's
React/Node.js/AWS stack). GraphQL is the one gap flagged by the matcher (`missing_skills:
["GraphQL"]`); nothing in his resume shows GraphQL experience, and that should be named
honestly rather than glossed over if he applies.

**Second-order hook, use carefully:** Ashby is recruiting software, and Santiago is currently
building his own job-search pipeline system (this very repo: SQLite-backed job tracking,
matching, and application tooling). This is a genuine point of connection, not a stretch, but
it needs to be raised as a real fact about a real system he built and uses daily, not as a
theme he leans on to sound clever. A safe, specific version: he built a personal tool that
does triage, scoring, and pipeline tracking against a job database, so he understands the
shape of the workflow problem Ashby's customers have (matching people to roles, tracking
pipeline state, reducing manual busywork) from the inside, as a user of his own version of
that problem. Do not overstate it into "I basically built an ATS" or "we do the same thing,"
he built a single-user tool with an entirely different engineering scope (no multi-tenant
data model, no scheduling logic, no enterprise auth) and should not imply parity with a
$128M-raised recruiting platform.

**Honest concerns / watch-outs:**
- Location is the real blocker: see section 0. Every primary source Ashby controls scopes
  this exact req to US-remote, with a separate Canada req and no LATAM band. This should be
  resolved (directly with Ashby, or by deciding to accept the risk) before spending time on a
  tailored cover letter.
- GraphQL is a stated gap versus this specific stack.
- The req explicitly filters against people who want mentorship opportunities or a more
  process-heavy tech-lead role; that is not a concern for Santiago's fit, but worth knowing
  going in, since the team's seniority skew (90%+ Senior or above) means less structured
  onboarding support than a more junior-heavy team might offer.

## 9. Application-question angles

**Why this company:** lead with the specific engineering-culture claim that would actually
be different day to day: writing the spec and making the product/design calls himself before
implementing, which is how he has already built Plutus and Kairos solo. Do not restate
Ashby's pitch back to them ("recruiting software matters because...").

**Why you fit:** anchor on one concrete project, not a list. Plutus is the strongest single
proof point (spec to shipped multi-service product, React/TypeScript frontend, Postgres
backend, real-time layer, no team handing him requirements). Name the stack overlap (React,
TypeScript, Node.js, Postgres) as a fact, not a selling point. If GraphQL comes up, say
plainly that he has not used it and name the adjacent REST/data-layer work he has done
instead.

**Anything else:** this is the one place the job-search-tooling parallel belongs, stated as
a specific, bounded fact (what the system does, why he built it) rather than a pitch that he
understands their market. If location eligibility has not been resolved by application time,
consider naming it directly and asking, rather than letting it surface later in the process.

## Sources

- researched: 2026-08-11
- https://findwork.dev/nZlp9qM/hiring-seniorstaff-product-engineers-americas-at-ashby (the
  aggregator posting behind local job id 9080; generic "Americas" text, no structured location
  field)
- https://api.ashbyhq.com/posting-api/job-board/ashby (Ashby's own public job-board API;
  primary source for the live req list, structured location fields, full job description text,
  team names, and posting-live status for all currently open roles, fetched 2026-08-11)
- https://jobs.ashbyhq.com/ashby/751768c6-8d97-4e91-a57d-6b85ce4b5a37 (Senior Product Engineer
  - Americas, live req page)
- https://jobs.ashbyhq.com/ashby/6a15668c-3f98-4404-8f1f-927cddfc5af7 (Staff Product Engineer
  - Americas, live req page)
- https://www.ashbyhq.com/blog/engineering/leveling-and-compensation (published 2026-07-27;
  level definitions, full comp band tables by region/metro, LATAM/unsupported-region policy)
- https://www.ashbyhq.com/blog/engineering/ai-ashby-engineering-and-the-future (published
  2026-06-02; AI tooling, workflows, code-generation stats)
- https://www.ashbyhq.com/blog/culture/series-d (published 2025-07-22; funding, investors,
  ARR growth, customer count, headcount, burn multiple)
- https://www.ashbyhq.com/story (founding story, mission, product philosophy)
- https://www.ashbyhq.com/team (remote-first claim, 24 countries, tenure examples, Mexico
  offsite mention)
- https://www.prnewswire.com/news-releases/ashby-expands-into-ai-interviewing-with-talent-llama-acquisition-302765977.html
  (published 2026-05-07; Talent Llama acquisition and AI Interviewer launch)
- https://www.ashbyhq.com/ashby-one-whats-new and https://www.ashbyhq.com/product-updates/ashby-assistant
  (2026 AI product announcements: Ashby Assistant, AI Talent Rediscovery, MCP server)
- Company founders and founding year (Benjamin Encz, Abhik Pramanik, 2018, YC W19): corroborated
  via web search of Crunchbase/YC listings, not fetched as a primary page; used only for the
  low-risk factual claim of founder names/year, cross-checked against the founders' own bylines
  on ashbyhq.com/blog/engineering posts (both authors identify themselves as Ashby co-founders
  in their own posts).
