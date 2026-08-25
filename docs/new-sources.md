# New job-discovery sources for jobhunt

Research report: candidate sources to wire into `src/adapters/` + `config/sources.yaml`.

- **Generated:** 2026-07-06 via `/deep-research` (104 agents, 22 sources fetched, 25 claims
  adversarially verified with 3-vote fact-checking: 20 confirmed, 5 refuted).
- **Scope:** Only sources NOT already connected. Current system already has aggregators
  (RemoteOK, Remotive, WeWorkRemotely, HN Who-is-Hiring, GetOnBrd, Jobicy, Arbeitnow,
  Himalayas, Recruitee, SmartRecruiters) and ATS APIs (Greenhouse, Lever, Ashby, Workable).
- **Risk stance:** User accepts any risk level; every source is labeled so it can be decided
  per-source. Labels are directional, not legal advice.
- **Confidence:** "Verified" = survived 3-vote adversarial check. "Unconfirmed" = surfaced in
  search results but filtered before final verification; confirm with a live request before building.

---

## TL;DR, priority order

Today only **GetOnBrd** touches Mexico/LATAM. Highest-leverage additions:

1. **Adzuna** (has an `mx` country code): best new Mexico source, trivial to wire.
2. **Consider VC boards + YC Work-at-a-Startup**: thousands of exact-match titles
   (Applied AI / Founding Engineer / Member of Technical Staff).
3. **Torre**: the real remote-LATAM network (undocumented public JSON endpoints).
4. **Personio + Workday CxS + BambooHR**: three net-new ATS platforms on the pattern you have.
5. **ATS meta-discovery job**: auto-grow the ~130 hand-curated Greenhouse/Lever/Ashby tokens.

---

## Tier 1: drop-in free-key aggregators (verified)

All confirmed 3-0. These fit the existing `ADAPTERS` list + `sources.yaml` shape.

| Source | Endpoint | Auth | Geo / role fit | Limits | Risk | Effort |
|---|---|---|---|---|---|---|
| **Adzuna** (MX) | `api.adzuna.com/v1/api/jobs/{country}/search/{page}` (country=`mx`) | Free `app_id`+`app_key` query params | 12+ countries incl. Mexico; general | ~25/min, 250/day | LOW | Trivial |
| **The Muse** | `themuse.com/api/public/jobs` | None (optional free key) | US/global tech, remote filter | 500/hr anon, 3,600/hr keyed | LOW | Trivial |
| **Careerjet** (MX) | `search.api.careerjet.net/v4/query` | Free key via HTTP Basic (key=user, empty pass) | 80+ countries incl. MX via locale | Publisher tier | LOW | Moderate |
| **Findwork.dev** | `findwork.dev/api/jobs/` | Free Bearer token (account signup) | Remote/tech-focused | Per-account | LOW | Trivial |
| **USAJOBS** | `data.usajobs.gov/api/Search` | Free key (`Authorization-Key` + `User-Agent` headers) | US federal | Free | LOW | Moderate |

**Notes:**
- **Skip USAJOBS for now.** Most US federal roles require citizenship, so it is low-value for a
  TN candidate despite easy wiring.
- **Verify live before building:** Adzuna `mx` result volume and Careerjet MX locale coverage are
  the two Mexico plays worth a quick manual `curl` first.

Sources: developer.adzuna.com, themuse.com/developers/api/v2, careerjet.com/partners/api,
findwork.dev/developers, developer.usajobs.gov/api-reference.

---

## Tier 2: AI + startup boards (best role fit)

- **Consider-powered VC boards** (verified 3-0). Pattern `consider.com/boards/vc/<firm>/jobs`.
  Sequoia's board alone renders 253 companies / 9,134 jobs. Generalizes across firms (a16z, etc.).
  JSON-backed but the internal endpoint is undocumented, so inspect the network calls.
  Risk MEDIUM (aggregator scrape). Effort Moderate.
- **Y Combinator Work-at-a-Startup** (verified 3-0). `workatastartup.com`, ~6,000 to 11,000 roles.
  Confirmed live titles: "Founding Engineer (Applied AI)", "Founding Applied AI Engineer",
  "Founding Full-Stack Engineer". The claim that listings are login-gated was REFUTED (readable).
  Risk MEDIUM. Effort Moderate.
- **AI Dev Jobs** (`aidevboard.com`), UNCONFIRMED. Dedicated AI/ML board advertising a public REST
  API + MCP server, ~5,000 to 8,400 roles, daily updates, remote/hybrid filters. Near-perfect fit
  if the API is real. Confirm before committing. Effort likely Trivial.
- **Getro** (verified 3-0, gated). Powers many VC/accelerator talent networks. Real v2 REST API at
  `api.getro.com/v2/networks/{network_id}/jobs`, but requires auth (`X-User-Email` + `X-User-Token`)
  and per-network numeric IDs. Effort Hard. Lower priority than Consider (which needs no credentials).

Sources: consider.com/boards/vc/sequoia-capital/jobs, workatastartup.com, github.com/codenpy/getro-api-jobs-wp.

---

## Tier 3: net-new ATS platforms (extend existing pattern)

Same architecture as your `greenhouse.py` / `lever.py` adapters, added coverage:

- **Personio** (unconfirmed endpoint, plausible). No-auth public XML feed:
  `https://{company}.jobs.personio.de/xml?language=en` (some accounts use `.com`). Big in EU
  startups. Risk LOW. Effort Trivial (XML parse).
- **Workday CxS** (unconfirmed endpoint, plausible). `https://{company}.wd1.myworkdayjobs.com/wday/cxs/{tenant}/External/jobs`
  (HTTP POST with a search filter, returns paginated JSON). Unlocks large enterprises on Workday,
  a segment currently missed entirely. Risk LOW. Effort Moderate (POST body + tenant discovery).
- **BambooHR via Jobber** (verified 3-0). `github.com/plibither8/jobber` (MIT) exposes a unified
  proxy `jobber.mihir.ch/:jobBoard/:companySlug` covering Ashby/Greenhouse/Lever/Workable + BambooHR.
  Live-tested working. Do not depend on the free Cloudflare Worker at runtime; copy the BambooHR
  adapter pattern natively. Effort Trivial.

Sources: github.com/plibither8/jobber, fantastic.jobs/article/ats-with-api, jobspipe.dev/blog/workday-api-guide.

---

## Mexico / LATAM (focused answer)

The hardest area: official APIs are mostly gated. Honest picture:

| Source | Reality | Path | Risk |
|---|---|---|---|
| **Adzuna `mx`** | Best option | Official free-key API (Tier 1) | LOW |
| **Careerjet MX locale** | Works | Official free-key API (Tier 1) | LOW |
| **Torre** | Official API is private-beta / request-access. Undocumented public JSON endpoints exist: `search.torre.co/opportunities/_search/`, `/opportunities/{id}`. Runs daily remote-LATAM "subtorre" boards (e.g. `remote-latam-python-developers`). Used by repos `behagoras/torre-api`, `bellom/torre-jobs`. | Reverse-engineered public JSON (grey-zone) or request official access | MED-HIGH |
| **Bumeran** | Official API behind Cloudflare Access login + OAuth2 password-grant needing a real account. No open endpoint. | Scrape only | HIGH |
| **OCC Mundial, Computrabajo, Indeed MX, El Empleo, Talently** | No verified public API surfaced. | Scraping only, per-site | HIGH |

**Practical Mexico stack:** Adzuna + Careerjet (official, low-risk) for breadth, plus Torre's
undocumented endpoints for remote-LATAM engineering depth. That trio meaningfully beats the current
single GetOnBrd source. Scraping OCC/Computrabajo is possible given the "any risk" stance but is the
highest maintenance for the coverage.

Sources: torre.ai/api, github.com/behagoras/torre-api, github.com/rfernand/bumeran, developers.bumeran.com.

---

## Creative connection ideas

1. **ATS meta-discovery to auto-grow the token list.** The ~130 Greenhouse/Lever/Ashby tokens are
   hand-curated and will bit-rot. No turnkey method surfaced (open question), but the concrete
   techniques are: crawl platform subdomains (`boards.greenhouse.io/*`, `jobs.ashbyhq.com/*`,
   `job-boards.workable.com/*`), mine Common Crawl for those hostnames, or use BuiltWith-style
   fingerprinting. Turn token maintenance into a discovery job.
2. **hiring.cafe internal API** (verified endpoint, auth unresolved). `POST hiring.cafe/api/search-jobs`
   returns up to 1,000 jobs/request and aggregates ~2.8M listings across 46 ATS platforms. The
   "no auth" claim was REFUTED (needs browser-like session headers), so budget for session
   reverse-engineering. Risk HIGH. Effort Moderate. Biggest-volume grey-zone lever.
3. **JSearch (RapidAPI).** Meta-aggregator over Google-for-Jobs that indirectly pulls
   LinkedIn/Indeed/Glassdoor/ZipRecruiter. Free tier via a RapidAPI key. Touches boards you cannot
   hit directly without running scrapers yourself.
4. **Ever Jobs catalog** (`github.com/ever-jobs/ever-jobs`, MIT). Not a runtime dependency
   (TypeScript), but a reference catalog of adapter patterns for 160+ sources (auth + query shapes
   for Adzuna, Reed, Jooble, Careerjet, USAJobs, and dozens more). Mine it when building adapters.
5. **RSS/Atom + newsletter-to-feed** for LATAM/AI communities without APIs. A lightweight
   `feedparser` adapter class covers a long tail cheaply.

Sources: github.com/umur957/hiring-cafe-job-scraper, rapidapi.com/.../jsearch, github.com/ever-jobs/ever-jobs,
github.com/lukasz-madon/awesome-remote-job, github.com/emredurukn/awesome-job-boards.

---

## Killed by verification (do not pursue)

Adversarial fact-checking refuted these 5 claims:

- Bumeran has an open official developer API. FALSE (gated).
- Getro is a free public endpoint. FALSE (needs credentials).
- YC WaaS listings are login-gated. FALSE (readable).
- hiring.cafe needs no auth. FALSE (needs session headers).
- Torre's pages expose zero integration detail. FALSE (undocumented endpoints exist).

---

## Recommended next steps

Build adapters in the existing `src/adapters/` + `sources.yaml` style, in ROI order:

1. **Adzuna** (trivial, best Mexico source). Get a free `app_id`/`app_key` at `developer.adzuna.com`.
2. **The Muse** (trivial, zero-config to test).
3. **Personio + BambooHR** (trivial, extends ATS pattern, net-new company coverage).
4. **Consider VC boards** (moderate, best AI-role fit).
5. **Torre** (moderate, remote-LATAM depth).

---

## Caveats

- VC-board and YC counts (Sequoia ~9,134; YC 6k to 11k) drift constantly and may include
  cross-location duplicates.
- The ~130 curated ATS tokens and any hardcoded network IDs (e.g. Getro `1113`) will bit-rot.
- Several sources could not be live-probed in-sandbox (Findwork, Torre were DNS-blocked); those
  rest on secondary evidence, confidence medium.
- The strongest refutations were "no-auth" claims: hiring.cafe and Getro both need
  session headers/credentials. Budget for auth reverse-engineering on grey-zone sources.
- Ever Jobs (TypeScript) and Jobber (single free Cloudflare Worker) are blueprints to reimplement
  natively, not runtime dependencies.

---

## Wired after this report

### PostHog "Cool tech jobs" (`posthog`), added 2026-08-25

- **Page:** https://posthog.com/cool-tech-jobs, a curated list of dev-tool companies picked for
  engineer-friendly culture (engineers decide what to build, meeting-free days, remote-only, ...).
- **Endpoint:** `GET https://better-animal-d658c56969.strapiapp.com/api/jobs?populate=company`
  with Strapi params `pagination[page]` / `pagination[pageSize]` (capped at 100) and
  `sort[0]=postedDate:desc`. No key, no session, no headers.
- **How it was found:** the page's Gatsby `page-data.json` is empty (`pageContext: {}`); every
  listing is client-fetched. The Strapi base URL is in the page chunk
  `component---src-pages-cool-tech-jobs-tsx-*.js`, which builds the same query we send.
- **Size:** ~159 live roles across ~10 companies (Supabase, Antithesis, Mintlify, PostHog,
  Resend, SigNoz, Zapier, Railway, Converge, Nango). Two requests cover the whole board.
- **Fields:** title, apply URL (Ashby or Gem), company, department, location, `isRemote`,
  `postedDate`, and full plain-text descriptions on ~90% of rows. No salary.
- **Overlap:** several of these companies are already Ashby tokens, so `canonical_key` collapses
  the duplicates and the ATS row wins the `canonical_jobs` view. The net-new value is the
  companies we do not track directly plus the culture curation.
- **Risk:** LOW-ish. Public unauthenticated read API backing a public page, tiny request volume,
  no auth bypass. Grey-zone only in that the API is undocumented, same footing as Torre.
- **Caveat:** `department` is free text ("Engineering", "Data + Growth", and sometimes a company
  name), so the optional `departments:` filter matches loosely and defaults to off.
