# Socket (socket.dev)

*Draft dossier for Santiago's review, researched: 2026-08-25*

## 1. Snapshot

Socket is a developer-first open source supply-chain security platform (dependency
scanning, SBOM, malware and zero-day detection) founded in 2021 by Feross Aboukhadijeh,
HQ in San Francisco, remote-first (BuiltIn lists "OnSite Workspace: None"), roughly
100+ employees, raised a $60M Series C at a $1B valuation in May 2026 (total funding
$125M) [1][2][3][7].

## 2. Core narrative

Socket is the security company built by an open-source insider, not a security vendor
retrofitting itself for developers. Feross Aboukhadijeh spent over a decade as one of
the most prolific npm maintainers (WebTorrent, StandardJS, 100+ packages, over a
billion downloads a month) before founding Socket to fix the problem he saw from
inside the ecosystem: most vulnerability scanners just match known CVEs, while the
real damage now comes from packages that behave maliciously the moment they land
(exfiltrating env vars, obfuscated install scripts, typosquats) [4][8][9]. That
"analyze behavior, not just CVEs" bet, plus a customer list that reads like a
who's-who of fast-moving engineering orgs (Anthropic, xAI, Figma, Vercel, Replit,
Cursor), is the throughline for how they talk about the product and the team [3][5][9].

## 3. Mission & product

- Product: a hosted platform (API, CLI, GitHub App, IDE extensions, MCP server,
  Firewall package-installer proxy) that scans dependencies across npm, PyPI, Go,
  Maven, Cargo, NuGet, RubyGems and more, flags 70+ categories of risk (malware,
  typosquats, install scripts, telemetry, native code, crypto wallets, license
  issues), and exports SBOMs (CycloneDX, SPDX, OpenVEX) [9].
- 2026 expansion: Socket Firewall (blocks malicious installs before they land,
  including compromised VS Code / Open VSX extensions), Socket Certified Patches,
  and protection extending to browser extensions, code editor extensions, MCP
  servers, and AI coding tools [6][7].
- Scale claims (Series C announcement, May 2026): 27,000+ organizations (up from
  7,500 at the October 2024 Series B), 1.5 million repositories protected, 11.6
  million commits secured monthly, 10,000+ supply-chain attacks blocked per week
  [2][7].
- Customers named in their own materials and testimonials: Anthropic, xAI, Figma,
  Vercel, Replit, Cursor, and unnamed Fortune 100 financial-services and media
  companies; individually quoted customer leaders include Replit's VP of
  Engineering, UiPath's CISO, Vercel's Head of Security, Figma's Head of Security,
  and Lyft's CISO [2][3][5].
- Business model: appears to be a tiered SaaS platform; SBOM import/export is
  called out as a Business-tier feature on their pricing page per third-party
  review sources [9]. (Not independently verified against socket.dev/pricing,
  which is Cloudflare-gated; flagged unverified.)

## 4. Culture & voice

- Stated values (from the live job posting, six numbered principles): "Pursue
  Excellence," "Move with urgency and focus," "Think rigorously" (reasoning from
  first principles, welcoming alternative perspectives), "Trust and amplify"
  ("overtrust, always assume good intent"), "Feel a strong sense of ownership"
  ("wear many hats," "non-territorial"), "Are customer obsessed" [1].
- Hiring language leans founder/early-stage: "join at the genesis of something
  totally new," "form the defining DNA for the company's culture," explicit ask
  for people who've worked 0-to-1 on an early-stage team and want to do it again
  [1].
- Public voice: their X account (@SocketSecurity) posts real-time attack
  disclosures (e.g. a "TrapDoor" crypto-stealer campaign across npm/PyPI/Crates.io,
  a pnpm 11 security-defaults writeup) in a terse, technical, slightly urgent
  register rather than corporate marketing copy [10].
- Feross himself is a known figure in the JS/open-source community (Node.js
  Foundation board, Stanford security lecturer CS253) which shows up in the
  caliber of investors and quoted fans (Brendan Eich, Nat Friedman, Dylan Field,
  Arash Ferdowsi all publicly congratulated the company) [4][5].

## 5. Recent news (last ~12 months)

- May 20, 2026: Series C, $60M led by Thrive Capital at a $1B valuation, new
  investors Capital One Ventures and individuals from Anthropic; total funding
  $125M; framed explicitly as "to secure AI-driven software development" [2][7].
- June 18-19, 2026: shipped Custom Roles and repo-level access permissions; Socket
  MCP extended so AI assistants can review org alerts and investigate threats, not
  just score dependencies; Socket Firewall extended to block malicious VS Code and
  Open VSX extensions before install [6].
- July 2026: published research on 17 malicious npm/PyPI packages typosquatting
  Paysafe, Skrill, and Neteller SDKs to steal developer secrets, and on "PolinRider"
  malware expanding across npm, Packagist, Go modules, and Chrome extensions [6].
- March 2026 (referenced in later coverage): during the Axios npm compromise,
  Socket's automated detection flagged a malicious dependency carrying a
  remote-access trojan within six minutes of publication [6].

## 6. Engineering & AI direction

- Confirmed stack, direct from this req's requirements: Node.js, JavaScript,
  React, TypeScript on the frontend/product side, PostgreSQL for relational data,
  with GraphQL, ElasticSearch, headless browsers, and data pipeline experience
  called out as bonus skills [1].
- AI angle is now core to the roadmap, not a bolt-on: the Series C round is framed
  around "securing AI-driven software development," and the product already uses
  AI/LLM-powered deep package inspection to catch obfuscated code and zero-day
  threats, plus an MCP server that lets AI coding assistants query Socket's threat
  feed directly [2][6][9].
- The team is explicitly still building foundational systems: the JD asks this
  hire to help "set up foundational frameworks" and build "design systems that
  will serve as guide rails," language consistent with a company that only
  crossed 100 employees this year [1][7].

## 7. Why-fit angles for Santiago

- **Best hook to lead with:** Socket is a security-and-devtools company built by
  an open-source maintainer who wanted better tooling for the ecosystem he already
  lived in, and it is scaling its product surface (web app, APIs, MCP, AI-assisted
  threat detection) fast post-Series C. Santiago's strongest, most concrete
  evidence set (Plutus: React 18 + TypeScript + Vite frontend, FastAPI/Postgres
  backend, an MCP control plane, WebSocket/SSE real-time layers; Kairos: an MCP
  server exposing 52 tools plus a Claude Agent SDK integration) is a near-literal
  match to this JD's stack (Node.js, React, TypeScript, Postgres, APIs
  aggregating multiple data sources) and to Socket's own AI-and-MCP direction.
  Lead a cover letter with the MCP/agent-tooling overlap plus the "0-to-1,
  full-stack, ships product end to end" framing, not a generic security pitch.
- Founder-to-founder resonance: Santiago has twice built and shipped 0-to-1
  products solo or with a small team (Eugenia.ai to acquisition, Online Basics
  to $8M revenue) and the JD explicitly wants someone who has "worked on an
  early-stage team in a 0-1 role and would like to get back to building the
  foundations again." That is a real, defensible match, not a stretch.
- Concerns / watch-outs (be honest about these):
  - **Location is unresolved and this must lead any risk assessment.** This req's
    Ashby location field says only "Remote" with no country. Most other Socket
    listings say "United States," and this JD itself contains zero location or
    work-authorization language. Socket's own BuiltIn profile lists the company
    as San Francisco HQ with no required on-site time, which is compatible with
    hiring outside the US but does not confirm it. Silence on this posting is not
    the same as permission to apply from Mexico; this needs to be asked directly
    (informational call is stage one of their process) before assuming fit [1][11].
  - No published salary band on this posting (their own JD promises "market
    competitive salary bands" but does not state a number); comp fit is unknown
    until asked.
  - Security-domain depth is a real, admitted gap (flagged by the matcher too):
    Santiago's LLM/RAG/agent and full-stack experience is strong, but he has no
    direct supply-chain-security or SCA-tooling background to point to. The
    honest angle is "fast learner who has shipped in adjacent infra (auth
    tickets, sensitivity labeling, rate limits)," not overclaiming security
    expertise.
  - This posting's `publishedAt` timestamp from Ashby's API is 2024-03-14, over
    two years old, while the aggregator (Jobicy) first surfaced it on
    2026-08-24. This may be a rolling/evergreen requisition rather than a fresh
    opening; worth a light gut-check in the informational call rather than
    treating the req as brand new. (Unverified: could not confirm whether the
    role is still actively being filled.)

## 8. Application-question angles

- **Why this company:** Lead with the maintainer-turned-founder story and the
  behavior-based detection bet (not "CVE matching"), tied to Santiago's own
  history of shipping developer- and operator-facing tooling from scratch
  (Online Basics's internal ops platform, Pragma's internal agent tooling). Do
  not recite the funding numbers or the full feature list; pick the detection
  philosophy as the one specific thing that differentiates Socket from a generic
  "security company."
- **Why you fit:** Anchor on the MCP/agent-tooling overlap (Kairos's MCP server,
  Plutus's MCP control plane and real-time layers) mapped directly against this
  JD's stack and Socket's own MCP-for-AI-assistants work, plus the 0-to-1 founder
  pattern the JD explicitly asks for. Keep it to the one or two strongest
  parallels; do not walk through every project.
- **Anything else:** A short, honest note that he is applying from Mexico City
  fully remote and wants to confirm early whether this specific req is open to
  candidates outside the US, since the posting itself does not say either way.
  This turns the location gap into a direct, low-drama question rather than a
  hidden risk.

## 9. Sources

1. Socket "Sr. Software Engineer" job posting, full JSON via Ashby posting API
   (https://api.ashbyhq.com/posting-api/job-board/socket, job id
   c1625d37-2c92-4455-8d3a-5ed3cefe3410; canonical listing
   https://jobs.ashbyhq.com/socket/c1625d37-2c92-4455-8d3a-5ed3cefe3410). Backs:
   role requirements, location field ("Remote," no country), stated values,
   benefits language, interview process, publishedAt timestamp.
2. Socket blog, Series C announcement:
   https://socket.dev/blog/series-c (dated May 20, 2026). Backs: $60M Series C,
   $1B valuation, $125M total funding, investor list, customer/repo/commit growth
   numbers, "secure AI-driven software development" framing.
3. Socket "About" page: https://socket.dev/about. Backs: mission statement,
   founding year (2021), Feross Aboukhadijeh bio, investor names, "100+ zero-day
   attacks weekly" claim (pre-Series-C figure), Socket for Asana integration
   (2025).
4. Feross Aboukhadijeh background (WebTorrent, StandardJS, Node.js Foundation
   board, Stanford CS253 lecturer):
   https://www.linkedin.com/in/feross/ and search summary of public profiles.
   Backs: founder pedigree claims in Core narrative and Culture sections.
5. Socket customer testimonials page: https://socket.dev/love. Backs: named
   quoted customers and their roles (Replit, UiPath, Vercel, Figma, Lyft,
   JupiterOne) and public congratulations from Brendan Eich, Nat Friedman, Dylan
   Field, Arash Ferdowsi.
6. Socket blog / news roundup, 2026 product and research posts (Custom Roles and
   repo permissions, Socket MCP threat-feed access, Socket Firewall for VS
   Code/Open VSX, Paysafe/Skrill/Neteller typosquat research, PolinRider malware,
   Axios compromise detection): aggregated via web search of socket.dev/blog,
   dated June-July 2026 and March 2026 respectively. Backs: Recent news and
   Engineering & AI direction sections.
7. Press coverage of the Series C round, cross-checked against the primary
   Socket blog post: TechCrunch
   (https://techcrunch.com/2024/10/22/socket-lands-a-fresh-40m-to-scan-software-for-security-flaws/)
   for the earlier Series B context, and general search aggregation of Series C
   coverage. Backs: funding history context (Series B $40M, October 2024) used
   to corroborate the Series C blog's own "since Series B" framing.
8. Search aggregation on Feross Aboukhadijeh / Socket founding story. Backs:
   "over 90% of codebase is open source" framing and founder motivation
   (secondary corroboration of the About page).
9. Third-party product-review aggregation (Vulert SCA comparison, AppSecSanta
   review) cross-checked against Socket's own site content fetched via search
   snippets, since socket.dev's main site and pricing page are Cloudflare-gated
   and returned HTTP 403 to direct fetch. Backs: product feature list (SBOM
   formats, 70+ alert categories, ecosystem coverage, Firewall/MCP/CLI tooling),
   flagged where not independently confirmed against the primary site.
10. Socket's X/Twitter presence (@SocketSecurity), sampled via search snippets of
    live posts (TrapDoor malware disclosure, pnpm 11 security defaults post).
    Backs: public voice and tone description in Culture & voice.
11. BuiltIn San Francisco company profile: https://www.builtinsf.com/company/socket-0.
    Backs: HQ San Francisco, "OnSite Workspace: None" remote-friendly note used
    in the location watch-out (does not confirm Mexico eligibility).

Note on an unresolved discrepancy: Socket's About page states the company was
founded in 2021; one third-party aggregator (BuiltIn) lists 2020. The primary
source (About page) is used in the Snapshot; the discrepancy is noted here rather
than silently resolved.
