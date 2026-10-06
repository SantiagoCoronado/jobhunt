# European sources, verified

Verification pass for `docs/spec-pre-release.md` decision 10 and PR 3 story 2, in the form of
`docs/history/new-sources.md`: a live request, the terms and robots.txt, the yield, and what a
response carries. Run on 2026-10-06 from a residential connection with curl, the project's own
User-Agent (`src/adapters/__init__.py` `UA`) unless noted.

Bar (the hard rule in `CLAUDE.md`): free, ToS-safe, no login. A source qualifies when it is a
public API, a public ATS board endpoint, or an RSS/JSON feed or sitemap the site itself offers;
a key is fine only when a free tier is documented and self-serve. Referral marketplaces,
anything behind a session, anything robots.txt disallows and undocumented internal endpoints
are out. Every European board ships with `regions:` naming its country, so the region gate
keeps it off for a profile that does not cover it (a `[sweden]` board meets a profile covering
`europe`, `eu` or `sweden`, and not one covering only `portugal`).

Already in the tree before this pass: **Arbeitnow** (`[europe]`, a public JSON API, Germany
heavy), **Personio**, **Recruitee** and **Teamtailor** (EU-popular ATS families, `[global]`),
and **Adzuna**, whose country list already takes `gb`, `de`, `fr`, `nl`, `pl`, `at`, `it`, `es`
and others from `sources.local.yaml` (`[global]`).

## Verdicts at a glance

| Source | Country | Path | Key | Verdict |
|---|---|---|---|---|
| JobTech JobSearch (Arbetsförmedlingen) | Sweden | official REST API | none | **wire** |
| Jobindex | Denmark | per-search RSS the site advertises | none | **wire** |
| Berlin Startup Jobs | Germany | category RSS feed | none | **wire** |
| Reed | United Kingdom | official REST API | free, self-serve | verified as documented; wire once a key gives a real fixture |
| France Travail Offres d'emploi v2 | France | official REST API | free, OAuth client credentials | same as Reed |
| InfoJobs | Spain | official REST API | free app registration | same as Reed |
| ITJobs.pt | Portugal | official REST API | free key on request | same as Reed |
| NAV pam-stilling-feed | Norway | official change feed | public token for testing, registration for production | not wired |
| Bundesagentur für Arbeit Jobsuche | Germany | the web client's endpoint | the web client id | rejected |
| Landing.jobs | Portugal | `/api/` | none | rejected |
| No Fluff Jobs | Poland | `/api/posting` | none | rejected |
| Just Join IT | Poland | `api.justjoin.it` | none | rejected |
| germantechjobs.de, swissdevjobs.ch | Germany, Switzerland | `/api/jobsLight` | none | rejected |
| EuroTechJobs | EU | no feed | none | rejected |
| EURES | EU | portal search | none | rejected |
| Welcome to the Jungle | France, EU | Algolia behind the site | embedded key | rejected |
| Työmarkkinatori | Finland | `/api/` | none | rejected |
| AMS eJob-Room | Austria | `/public/emps/` | none | rejected |
| StepStone | Germany, EU | none public | none | rejected |
| EU Remote Jobs | EU | WordPress feeds | none | rejected |

## Wire

### JobTech JobSearch (Sweden)

- **Live request:** `GET https://jobsearch.api.jobtechdev.se/search?q=developer&limit=0` answered
  200 with `total.value` 666; `software engineer` 145, `frontend` 216, `react` 3 pages of hits.
  `limit` up to 100 per call, `offset` pages.
- **Terms:** the API's own OpenAPI document (`/swagger.json`, `info.license`) says "Ads are
  licensed under CC0". No key, no registration. Run by the Swedish Public Employment Service as
  open data (links to `data.arbetsformedlingen.se` in the same document). The API host has no
  robots.txt (404); it is an API, not a site.
- **What a hit carries:** `id`, `headline`, `webpage_url` (the Platsbanken ad),
  `employer.name`, `workplace_address.{city, municipality, region, country}`,
  `description.text` (the full ad, about 4,600 chars on the sample), `publication_date`,
  `application_deadline`, `employment_type.label`, `workplace_model`,
  `application_details.url` (the employer's apply page).
- **Yield and fit:** hundreds of developer ads, mostly Swedish-language, almost all on-site or
  hybrid in Sweden. Useful for a candidate who covers Sweden or the EU.
- **Wired as** `jobtech`, `regions: [sweden]`, queries from `sources.local.yaml`.

### Jobindex (Denmark)

- **Live request:** `GET https://www.jobindex.dk/jobsoegning.rss?q=developer` answered 200,
  `application/rss+xml`, 20 items; `software engineer`, `frontend` and `react` 20 each. The feed
  is one page per query (robots.txt disallows `page=` on `/jobsoegning`), so depth comes from
  more queries, not more pages.
- **Terms and robots:** every search page advertises its own feed
  (`<link rel="alternate nofollow" type="application/rss+xml" href=".../jobsoegning.rss?q=...">`).
  robots.txt (`User-agent: *`) disallows `/annoncer/`, `/cache/`, `/jobsoegning*page=`,
  `/jobsoegning*sort=`, `/jobsoegning*jobage=` and multi-parameter searches; a single `q=`
  feed is allowed. The terms (`jobindex.dk/betingelser`) cover user profiles and say nothing
  about feeds or automated access.
- **What an item carries:** `title` as "Role, Company", `link` (`/vis-job/h<id>`), `guid`,
  `pubDate`, `category` (the Danish job category) and a `description` HTML block holding the
  area (`jix_robotjob--area`, e.g. "Bjerringbro, Hybrid position") and the ad's first lines.
- **Yield and fit:** 20 fresh rows per query, Danish and English titles, on-site or hybrid in
  Denmark.
- **Wired as** `jobindex`, `regions: [denmark]`, queries from `sources.local.yaml`.

### Berlin Startup Jobs (Germany)

- **Live request:** `GET https://berlinstartupjobs.com/engineering/feed/` answered 200 with 12
  items; `?paged=2` 12, `?paged=3` 8, `?paged=5` 404, so about 32 engineering ads, the newest
  dated the day before the check and the oldest January 2026. A browser User-Agent got 403 after
  a few requests while the project's honest one kept getting 200.
- **Terms and robots:** robots.txt allows `/` for `*` (it blocks only `/wp-admin/` and a few SEO
  crawlers by name); the feed is the WordPress feed the site publishes. No key.
- **What an item carries:** `title` as "Role // Company", `link`, `guid`, `pubDate`,
  `category`, and `description` with the ad's text. No location field: the board is Berlin
  startups, and "Remote" shows up in titles when it applies.
- **Yield and fit:** small (a few new rows a week) but every row is a Berlin startup
  engineering role, in English more often than not.
- **Wired as** `berlinstartupjobs`, `regions: [germany]`, no targeting needed.

## Verified, not wired (keyed)

All four answer 401 without credentials, which is the documented behaviour; the spec asks for a
fixture from a real response per wired board, and that needs a key this pass did not have.
Each is a small adapter once a user with the key records one response.

- **Reed (UK):** `GET https://www.reed.co.uk/api/1.0/search?keywords=developer` answered 401.
  Self-serve key at `reed.co.uk/developers/jobseeker`, HTTP Basic with the key as the user and
  an empty password, 100 results a page, a details call for the full description. The developer
  page itself sits behind a Cloudflare challenge for curl.
- **France Travail (France):** `GET https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search`
  answered 401. Free account on francetravail.io, an application subscribed to "Offres
  d'emploi", OAuth2 client credentials. Results cap at 1,150 per query and the reuse licence
  asks that the whole offer be displayed with its logo.
- **InfoJobs (Spain):** `GET https://api.infojobs.net/api/9/offer?q=developer` answered 401
  "Client credentials not valid". Free app registration at `developer.infojobs.net`.
- **ITJobs.pt (Portugal):** `GET https://api.itjobs.pt/job/list.json` answered 200 with
  `{"error":{"message":"API key required."}}`. robots.txt allows the site (`Crawl-delay: 1`).

## Not wired

- **NAV pam-stilling-feed (Norway):** official and live. `GET /api/publicToken` hands out a
  shared token and `GET /api/v1/feed` with it answered 200 with 1,000 entries, but the feed is
  a change log that starts in 2023 (the first entry was an inactive 2023 ad) and has to be
  walked to the present, each ad then fetched one by one. The project README
  (`github.com/navikt/pam-stilling-feed`) registers production consumers by name, e-mail and
  phone. Revisit if someone in Norway wants it.

## Rejected

- **Bundesagentur für Arbeit Jobsuche (Germany):** `pc/v6/jobs` answers 200 with
  `X-API-Key: jobboerse-jobsuche` (3,476 hits for "Softwareentwickler") and 403 without it. The
  key is the agency's own web client id, documented by the community project
  `github.com/bundesAPI/jobsuche-api`, whose README says the agency "bietet ... bis heute keine
  offizielle API an". Not offered by the site, so out under the bar above.
- **Landing.jobs (Portugal):** robots.txt `Disallow: /api/`.
- **No Fluff Jobs (Poland):** `/api/posting` answered 200 with a 132 MB dump, and robots.txt
  says `Disallow: /api/`.
- **Just Join IT (Poland):** `api.justjoin.it/v2/user-panel/offers` answered 503; the endpoint is
  the site's internal panel API, undocumented.
- **germantechjobs.de and swissdevjobs.ch:** every path, robots.txt included, now answers with a
  JobCopilot "Sign Up" page.
- **EuroTechJobs:** no feed (`/rss` 404); robots.txt disallows ClaudeBot and GPTBot by name.
- **EURES:** the portal's search runs on an internal endpoint (the obvious path 404s); there is
  no public jobs API.
- **Welcome to the Jungle:** robots.txt `Disallow: /*?`; listings come from an Algolia index
  through a key embedded in the page, not an offered API.
- **Työmarkkinatori (Finland):** robots.txt `Disallow: /api/`.
- **AMS eJob-Room (Austria):** robots.txt `Disallow: /public/emps/` for `*`.
- **StepStone:** robots.txt itself answers 403 "Access Denied"; no public API.
- **EU Remote Jobs:** `/feed/` is the blog; the job feed (`?feed=job_feed`) answered 401.
- Global boards seen on the way (Working Nomads' `exposed_jobs` JSON, Jooble's keyed API) are
  not European and not part of this pass.

## The pick

The spec leaves the pick to Santiago. PR 3 wires the three that pass the bar without a key
(JobTech, Jobindex, Berlin Startup Jobs), so the PR carries story 3 for review; dropping any
of them is deleting one adapter, one block and one test.
