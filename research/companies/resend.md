# Resend: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: "Product Engineer" (job id 4923), Americas / Remote, Ashby,
https://jobs.ashbyhq.com/resend/9b68ba51-3895-4d29-8fd1-364bdf8956e7

## LOCATION ELIGIBILITY VERDICT: ELIGIBLE

Confirmed directly from the live posting via Ashby's public job-board API
(`https://api.ashbyhq.com/posting-api/job-board/resend`), which returns this exact job
(`id: 9b68ba51-3895-4d29-8fd1-364bdf8956e7`, `isListed: true`, `jobUrl` matching the canonical
posting URL) with `location: "Americas / Remote / Full-time"` and `workplaceType: "Remote"`
[api.ashbyhq.com/posting-api/job-board/resend]. The posting's own body text states, verbatim:

> "This role is fully remote based in Americas or European timezones, with some expected travel
> for team offsites, conferences, meetups, and more."

and:

> "Our fully remote team of 45 spans 13 countries and counting. We're backed by a16z, Y
> Combinator, and others."

[api.ashbyhq.com/posting-api/job-board/resend, descriptionHtml field for job
9b68ba51-3895-4d29-8fd1-364bdf8956e7]. There is no country-level restriction (no "US only" or
"must reside in the United States" language anywhere in the posting); the requirement is a
timezone band (Americas or Europe), not a specific country, and Mexico City sits squarely inside
Americas timezones (GMT-6). Note: the JSON's `address.postalAddress.addressCountry` field shows
"United States", but this reads as Ashby/Resend's default HQ address for the posting record, not a
work-location requirement; it is contradicted by the explicit "Americas / Remote" location label
and the "fully remote... 13 countries" text in the same record. The company's public team roster
independently corroborates a genuinely distributed, non-US-centric team: at least 14 countries
represented including Brazil, Portugal, Ireland, Netherlands, Canada, South Africa, Spain, New
Zealand, Poland, UAE, Austria, Albania, and the UK, alongside the US [resend.com/humans]. Ashby is
a client-side SPA, so a plain fetch of the human-facing URL would only return the page shell; the
facts above come from the structured public API response, not scraped HTML.

Compensation is explicitly listed in the posting itself: "Comp: $150,000 - $170,000 USD,
commensurate with experience" [api.ashbyhq.com/posting-api/job-board/resend], which clears
Santiago's stated floors (`comp.min_usd: 70000`, `comp.min_usd_latam_scope: 70000` in
`config/profile.yaml`) with meaningful room. There is a separate, identically-titled "Product
Engineer" req for Europe/Remote (`61dbb0e7-95a6-4cd9-ab2d-1a5471fe0dd8`), confirmed distinct from
the Americas req this dossier targets [api.ashbyhq.com/posting-api/job-board/resend].

## 1. Snapshot

Resend is a developer-first transactional and marketing email API platform (YC W23), founded in
early 2023 by Zeno Rocha (CEO), Bu Kinoshita (CTO), and Jonni Lundy (COO), out of the earlier
open-source React Email project [resend.com/about, resend.com/blog/y-combinator]. Backed by
Andreessen Horowitz (Series A lead), Y Combinator, and angel investors including Guillermo Rauch
(Vercel) and Michael Grinich [resend.com/blog/series-a]. Fully remote team of 45 across 13+
countries, HQ nominally San Francisco [api.ashbyhq.com/posting-api/job-board/resend,
resend.com/humans]. As of June 2026: 3,000,000 users, profitable since 2025, 6.8M weekly npm
downloads [resend.com/blog/3-million-users]. Total disclosed funding: roughly $21.5M across
pre-seed, seed, and Series A [resend.com/blog/resend-raises-3m-seed-round,
resend.com/blog/series-a]; no valuation was disclosed in any source found.

## 2. Core narrative

Resend's distinctive story is "build the email API developers actually want, then let craft and
compounding trust do the growth." It started as a frustration project (React Email, an
open-source library for building email templates in React) before the founders built a company
around it, and it has stayed unusually product-first and small: 45 people getting 3 million users
and profitability, largely by shipping fast, writing in a voice that "reads as though written by a
developer," and publishing its engineering failures (public incident postmortems) as openly as its
wins [resend.com/about, resend.com/blog/3-million-users, resend.com/handbook/marketing/what-is-our-brands-voice-and-tone,
resend.com/blog/incident-report-for-february-15-2026]. The Product Engineer role this dossier
targets is a direct expression of that: it explicitly wants someone who cares as much about "how
the product feels" as how it works, moving across frontend, backend, product thinking, and design
details on a small team with no separate PM layer implied [api.ashbyhq.com/posting-api/job-board/resend].

## 3. Mission & product

- Core product: a REST email-sending API (single POST request to send an email), SDKs across
  Node.js, Python, PHP, Ruby, Go, Java, Laravel, Rust, and .NET, a CLI, and native support for
  React Email (build email templates as React components) [resend.com, resend.com/about].
- Product surface has broadened well beyond "send an email": Templates, pay-as-you-go pricing,
  inbound email receiving, idempotency keys, Automations (workflow/automation runs), an AI email
  editor (subject lines, preview text, alt text), and an MCP server for AI agents to send email
  [resend.com/blog (post titles: "Introducing Automations", "One More (AI) Thing", "Resend MCP
  Hackathon"), resend.com/one-more-ai-thing].
- Business model: freemium/usage-based. Free tier (3K transactional emails/mo, 1K marketing
  contacts/mo, 10K automation runs/mo, 5 AI credits); paid tiers scale from ~$20 to ~$1,150/mo
  by volume, with per-thousand-email overage pricing down to $0.46/1K at the highest tier;
  Enterprise is custom [resend.com/pricing].
- Customers: named logos include Warner Bros, Decathlon, Braintrust, Raycast, and Gumroad; 59% of
  Y Combinator's W25 batch reportedly uses Resend [resend.com/blog/series-a; growth/customer
  figures corroborated via search summary of resend.com blog content, treat the "59% of YC W25"
  figure as a secondary-source citation pending direct confirmation].
- Grew acquisitively in 2025: acquired Mergent (serverless background-job scheduling service),
  announced April 23, 2025, and Briefer (YC S23, data notebook/analysis tooling), announced August
  5, 2025, both framed as strengthening data processing and job-scheduling infrastructure behind
  the growing email volume [resend.com/blog/resend-acquires-mergent, resend.com/blog/resend-acquires-briefer].

## 4. Culture & voice

- Stated values: "Do phenomenal work" / "raise the bar" (quality over merely meeting industry
  norms), humility (ask for help, communicate with kindness and directness, low ego), speed
  (ruthless prioritization, fast decisions, ship frequently over perfecting), and initiative (act
  on problems instead of waiting to be told) [resend.com/about].
- Brand voice is codified in its public handbook: "All Resend content should read as though
  written by a developer," with three named principles: Simple ("get to the point... avoid
  verbal garnish"), Factual ("use positive assertions you can provide evidence for," example given
  is "Resend delivers emails under 600ms (p95)"), and Technical ("we expect our audience to feel
  comfortable reading a fairly technical piece") [resend.com/handbook/marketing/what-is-our-brands-voice-and-tone].
  This is an unusually explicit, engineering-native marketing voice for a company this size.
  Notably, Santiago's own writing-voice rules (plain, no intensifiers, no invented claims) are a
  close philosophical match to this stated brand voice.
- The Product Engineer posting itself repeats the same DNA: "autonomy to just ship it," "honest
  and low-ego team," "default to action mindset," "low ego and enjoy collaborating"
  [api.ashbyhq.com/posting-api/job-board/resend].
- Publishes detailed, first-person incident postmortems (root cause, what went wrong internally,
  concrete fixes) rather than boilerplate status-page language; the February 15, 2026 report
  explicitly admits "internal escalation process took way longer than it should have"
  [resend.com/blog/incident-report-for-february-15-2026]. This is a credible, verifiable
  transparency signal, not marketing copy.
- Celebrates and publicizes milestones in detail and with specific numbers rather than vague
  claims (72,000 support tickets solved, 2 launch weeks shipped, 5 international offsites, 28
  changelogs and 90 blog posts published in 2025) [resend.com/blog/1-million-users].
- Public "humans" page individually profiles every team member with their country, a personal,
  humanizing format uncommon at this scale [resend.com/humans].

## 5. Recent news (last ~12 months, dated)

- August 5, 2025: acquired Briefer (YC S23, notebook-style data analysis tool), framed around
  needing better tooling to process the "terabytes of data every week" the platform now handles
  [resend.com/blog/resend-acquires-briefer].
- November 18, 2025: public incident, service degraded by a third-party provider outage; Resend
  publicly apologized and characterized the impact as unacceptable
  [resend.com/blog/incident-report-for-november-18-2025].
- December 18, 2025 (post later updated July 9, 2026): crossed 1,000,000 users (from 249,000
  at start of 2025), team grew from 12 to 28 employees over the year, revenue "5x'd," weekly npm
  downloads grew from 189,000 to 1.4 million, shipped React Email 5.0, ran 2 launch weeks, closed
  the Data Privacy Framework certification and a SOC 2 renewal with zero findings
  [resend.com/blog/1-million-users].
- February 15, 2026: a 3-hour-31-minute outage from database connection exhaustion (a
  misconfigured service spiked connections from ~60 to over 330 across a mixed
  serverless/long-lived/cron Postgres deployment); no emails were lost, but the dashboard was
  inaccessible and delivery was delayed roughly 2 hours on average
  [resend.com/blog/incident-report-for-february-15-2026].
- June 3, 2026: crossed 3,000,000 users (team at 43-45 people depending on source/date), stated
  explicitly "Resend is profitable. It has been since last year," weekly npm downloads at 6.8M
  [resend.com/blog/3-million-users; team count of 45 per the July 2026 job posting
  api.ashbyhq.com/posting-api/job-board/resend].
- Ongoing product cadence through the period: Templates, pay-as-you-go pricing, inbound email,
  idempotency keys, Automations, an AI email editor (subject line/preview text/alt-text
  generation), an MCP server for AI agents, and CLI 2.0, per the company's own blog index
  [resend.com/blog post titles, resend.com/one-more-ai-thing]. No layoffs, executive departures, or
  negative press beyond the two dated incident reports above were found in this research; absence
  of coverage is not proof none occurred.

## 6. Engineering & AI direction

- Primary stack, per the target posting itself: "Work primarily with TypeScript, React, Next.js,
  and modern web technologies," plus being "comfortable working across the stack, including APIs,
  databases, server-side logic, and product infrastructure" [api.ashbyhq.com/posting-api/job-board/resend].
  The same posting lists the team's broader tools as "Next.js, Raycast, Notion, etc."
- Infrastructure, per its own incident postmortem: PostgreSQL as the primary datastore, a mix of
  long-lived, serverless, and cron-based deployments, and per-role connection-limit tuning across
  multiple Postgres configurations, indicating a deliberately heterogeneous, cloud-native backend
  rather than a single monolith [resend.com/blog/incident-report-for-february-15-2026].
- AI direction is product-embedded and framed cautiously rather than hype-driven: AI-assisted
  subject lines, preview text, and image alt text ("when used tastefully, AI can help you craft
  better emails and reach humans instead of spam filters"), multilingual generation, and an MCP
  server so AI agents can send email directly, alongside a public "Resend MCP Hackathon" and posts
  on "Agent Experience (AX)" [resend.com/one-more-ai-thing, resend.com/blog post titles]. This
  reads as AI-as-craft-feature (deliverability, developer/agent experience) rather than
  AI-as-headcount-replacement.
- Engineering culture signals: detailed, engineer-authored, publicly posted incident reports with
  named root causes and committed follow-ups; a handbook covering RFCs, CI/CD, incident
  management, separating deployments from releases, PR standards, and post-incident reviews
  [resend.com/handbook, resend.com/blog/incident-report-for-february-15-2026]. The target role
  itself is explicitly cross-functional (frontend, backend, product, design, UX, instrumentation,
  launch, iteration owned end to end by one engineer) rather than siloed by discipline
  [api.ashbyhq.com/posting-api/job-board/resend].

## 7. Competitive position

Resend competes most directly with SendGrid (Twilio), Postmark (ActiveCampaign), Mailgun, and
newer entrants like Loops (marketing-focused). Third-party comparisons converge on a consistent
positioning: Resend's differentiator is a minimal, modern API surface (a single POST call to send
an email) and native React Email integration, making it the default pick for React/Next.js
developers who want to build emails as code; SendGrid carries two decades of API surface area and
enterprise breadth; Postmark wins on pure transactional deliverability discipline (refusing to mix
marketing traffic on the same infrastructure); Loops focuses specifically on marketing/lifecycle
email for smaller SaaS teams. These characterizations come from third-party review/comparison
sites (dev.to, courier.com, and similar), not from Resend or its competitors directly, and should
be treated as informed secondary-source consensus rather than verified fact
[dev.to/supertrained/email-apis-for-ai-agents-resend-vs-sendgrid-vs-postmark, courier.com best
email API providers comparison]. Resend's own stated growth (3M users, profitable, YC W25 batch
adoption) suggests real traction against these incumbents in the developer segment specifically,
though it remains far smaller in absolute revenue/scale than SendGrid or Mailgun.

## 8. Risks and red flags

- Two dated production incidents in the last 12 months (November 2025 third-party-driven outage;
  February 2026 database-connection-exhaustion outage, 3h31m, dashboard down and delivery delayed)
  show real operational strain as the platform scales into the tens of millions of daily emails
  [resend.com/blog/incident-report-for-november-18-2025, resend.com/blog/incident-report-for-february-15-2026].
  This is a legitimate signal about reliability at current scale, though the public, detailed,
  accountable postmortems are themselves a positive culture signal.
- Still a small team (45 people) supporting 3,000,000 users and rapid acquisitive growth (2
  acquisitions in 2025); this concentrates operational and product risk on a small number of
  people, which cuts both ways for a "Product Engineer" (high ownership, but also high blast
  radius if something breaks).
- No valuation was disclosed in any source found; total disclosed funding (~$21.5M) is modest
  relative to the stated 3M-user, profitable-since-2025 scale, which suggests either efficient
  capital use or that a more recent, larger round exists but was not found in this research. Flag
  as worth asking about directly rather than assuming either way.
- Address country field on the Ashby posting ("United States") is a minor internal inconsistency
  worth noting even though the explicit "Americas / Remote" location label and body text
  supersede it (see eligibility verdict above).

## 9. Why-fit angles for Santiago

Best hook to lead with: Resend's own stated brand voice, "content should read as though written by
a developer... use positive assertions you can provide evidence for," is close to how Santiago
already builds and talks about his own work: React 18/19 + TypeScript + Vite + Tailwind product
frontends (Plutus, Kairos, the Hydrel client portal) shipped with real, checkable numbers (114
Vitest tests, 10 Playwright E2E flows, zero-console-error assertions, 45+ components) rather than
vague claims [resume/master_resume.yaml, resend.com/handbook/marketing/what-is-our-brands-voice-and-tone].
The posting explicitly wants someone who cares "both how the product works and how the product
feels," moves across "frontend, backend, product thinking, design details, and user experience,"
and can "take an ambiguous customer problem and turn it into a clear, shippable solution"
[api.ashbyhq.com/posting-api/job-board/resend]; that is a close match to how Santiago has operated
as a founder at Eugenia.ai and Online Basics: owning the full product lifecycle, not just a slice
of the stack.

Concrete transferable evidence:
- Full-stack, product-owning craft: the Hydrel portal (React 18 + TypeScript, Radix UI design
  system with CVA variant APIs, dark/light themes, 114 Vitest unit tests, 10 Playwright E2E flows,
  responsive audits at 4 breakpoints) is direct evidence of the "polish, craft, accessibility,
  reliability" bar the posting names explicitly [resume/master_resume.yaml,
  api.ashbyhq.com/posting-api/job-board/resend].
- Debugging/observability UX for developers: Plutus's real-time layer (WebSocket quote feed with
  auth tickets and reconnect logic, hand-rolled SSE client for streaming agent responses with
  cancellation) is a direct analog to the posting's ask to "build debugging and observability
  experiences that help users understand what happened to their emails, webhooks, domains, and API
  requests" [resume/master_resume.yaml, api.ashbyhq.com/posting-api/job-board/resend].
- Developer-facing API/integration instincts: Online Basics' cloud microservices orchestrating
  10+ third-party APIs and Pragma AI's MCP-based tool layers (Claude Agent SDK and a standalone MCP
  server exposing the same 46 tools) show direct, hands-on familiarity with the exact kind of
  API-and-agent-facing product surface Resend is building (its own MCP server, agent-facing email
  sending) [resume/master_resume.yaml].
- AI/LLM depth beyond typical "product engineer" candidates: RAG pipeline design (Pragma Brain),
  prompt engineering, and an eval harness, which maps onto Resend's own AI-email-editor and MCP/AX
  work, should it come up as a plus rather than a requirement [resume/master_resume.yaml,
  resend.com/one-more-ai-thing].
- Comp: the posted $150,000 to $170,000 USD band clears his profile floor comfortably and sits
  well above his default US-scope target anchor of $100,000 [config/profile.yaml].

Honest concerns and watch-outs:
- 6+ years of experience "building and shipping high-quality web products" is the stated bar
  [api.ashbyhq.com/posting-api/job-board/resend]. Santiago's total professional experience since
  Nextia.mx (2017) exceeds 6 years, but a meaningful share of his strongest, most polished frontend
  work (Plutus, Kairos, the Hydrel portal) is recent (2026) personal/consulting project work rather
  than years of continuous employment at a single product company; this is worth framing honestly
  as founder-generalist experience rather than implying a traditional multi-year single-employer
  track record he does not have.
- Next.js specifically is named as the team's framework, and while Santiago's resume shows deep
  React/Vite experience, it does not explicitly name Next.js project work; this is a real, narrow
  gap worth naming rather than glossing over (React and Vite fundamentals transfer significantly,
  but the App Router/server-component model is its own learning curve).
- No fintech/email-infrastructure-specific experience (deliverability, DNS, DMARC/SPF, webhooks at
  scale) is on the resume; the posting lists this as an "exceptional fit" plus, not a hard
  requirement, so it is a differentiator gap rather than a disqualifier.
- The role is explicitly craft- and design-sensibility-heavy ("strong visual taste," "interfaces
  that feel fast, simple, and polished"). Santiago's design-system work (Radix + CVA tokens at
  Hydrel and Pragma AI) is real evidence here, but he should be ready to show, not just describe,
  visual taste specifically, since that is harder to prove from a resume line alone.
- Small, fully remote, 45-person team with real operational load (two dated production incidents
  in the last year); worth going in with eyes open that on-call/incident involvement is plausible
  even in a product-facing role, given how cross-functional the posting describes the job.

## 10. Application-question angles

- Why this company: lead with the direct match between Resend's stated brand voice (developer-
  authored, evidence-based, no verbal garnish) and how Santiago already builds and communicates:
  concrete, testable product work (Vitest/Playwright suites, measurable UX details) rather than
  vague claims. Pair that with genuine enthusiasm for a company that grew from an open-source
  frustration project (React Email) to 3 million users while staying at 45 people, since that
  founder-to-scale arc mirrors his own path from solo founder to hands-on builder. Do not recite
  the funding history or acquisitions; the resonant thread is the craft-and-voice match, not the
  cap table.
- Why you fit: anchor on the Hydrel portal and Plutus as the clearest single proof points for "own
  features end-to-end: product thinking, UX details, implementation, instrumentation, launch, and
  iteration": both are full-stack, tested, design-system-backed products he built and shipped
  solo or near-solo, not scoped slices of a larger team's work. Use the Plutus real-time
  debugging/observability layer (WebSocket + SSE with reconnect and cancellation) as the sharpest
  echo of the posting's own "help users understand what happened to their API requests" ask.
- Anything else: if it comes up, be direct that Next.js specifically (versus React/Vite generally)
  is new ground worth naming honestly, and that his strongest recent work is founder/consulting
  project work rather than years inside one product company, framed as a strength (broader surface
  area, real ownership) rather than hidden. Do not raise compensation unprompted; the posted band
  already clears his floor.

## Sources

- https://api.ashbyhq.com/posting-api/job-board/resend (Ashby public job-board API: full,
  structured job list confirming the target posting is live and listed, its exact location/
  workplace fields, full description text including the Americas/Europe timezone line, the
  "45... 13 countries" line, and the posted $150,000 to $170,000 USD comp band; also used to
  confirm the separate Europe req exists as a distinct posting)
- https://jobs.ashbyhq.com/resend/9b68ba51-3895-4d29-8fd1-364bdf8956e7 (canonical human-facing
  posting URL, confirmed to match the API's jobUrl field for this job id)
- https://resend.com/humans (team roster: 46 "makers" listed, at least 14 countries represented,
  used to corroborate the distributed-team claim independently of the job posting)
- https://resend.com/handbook (top-level handbook: structure showing RFCs, CI/CD, incident
  management, remote-work philosophy, hiring process documentation)
- https://resend.com/handbook/marketing/what-is-our-brands-voice-and-tone (direct quotes on brand
  voice: "read as though written by a developer," Simple/Factual/Technical principles and
  examples)
- https://resend.com/about (mission/founding story, founders named: Zeno Rocha, Bu Kinoshita,
  Jonni Lundy; stated values: quality, humility, speed, initiative)
- https://resend.com/blog/y-combinator (Y Combinator W23 batch confirmation, founding narrative)
- https://resend.com/blog/resend-raises-3m-seed-round (seed round: $3M, angel investors including
  Guillermo Rauch and Paul Copplestone)
- https://resend.com/blog/series-a (Series A: $18M, led by Andreessen Horowitz, December 2024,
  investor list, 200,000 developers at the time, named customers Warner Brothers/Decathlon/
  Braintrust/Raycast, React Email metrics at the time)
- https://resend.com/blog/1-million-users (December 2025 milestone post: 249K to 1M users in 2025,
  team 12 to 28, revenue 5x, npm downloads, acquisitions of Mergent and Briefer referenced,
  SOC 2/DPF certification)
- https://resend.com/blog/3-million-users (June 3, 2026 milestone post: 3M users, team of 43,
  6.8M weekly npm downloads, explicit "profitable... since last year" statement)
- https://resend.com/blog/resend-acquires-mergent (April 23, 2025 Mergent acquisition:
  serverless background-job scheduling)
- https://resend.com/blog/resend-acquires-briefer (August 5, 2025 Briefer acquisition: data
  notebook/analysis tooling, "terabytes of data every week" framing)
- https://resend.com/blog/incident-report-for-november-18-2025 (November 2025 outage: third-party
  provider driven, public apology)
- https://resend.com/blog/incident-report-for-february-15-2026 (February 2026 outage: database
  connection exhaustion, 3h31m, root cause and remediation detail, infrastructure/stack signals)
- https://resend.com/one-more-ai-thing (AI email editor feature announcement: subject line/preview
  text/alt-text generation, multilingual, "used tastefully" framing)
- https://resend.com/pricing (pricing tiers, free-tier limits, pay-as-you-go rates)
- https://resend.com/ (homepage: product description, SDK list, MCP server and CLI mentions)
- https://dev.to/supertrained/email-apis-for-ai-agents-resend-vs-sendgrid-vs-postmark-le8 and
  https://www.courier.com/blog/best-email-api-providers-for-developers (third-party competitive
  positioning versus SendGrid and Postmark; treated as secondary-source consensus, not verified
  fact, and labeled as such in section 7)
- https://theorg.com/org/resend/org-chart/bu-kinoshita and
  https://theorg.com/org/resend/org-chart/zeno-rocha (secondary-source corroboration of founder
  names and titles; used only to cross-check resend.com/about, not as a standalone source for any
  claim not otherwise verified)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience: Online
  Basics, Eugenia.ai, Nextia.mx, Pragma AI, Plutus, Kairos, Hydrel, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile, comp floors and
  target anchor, location rule, used for the eligibility verdict and comp comparison)

Note for Santiago: this is a draft dossier, please review before it feeds into a cover letter or
application answers. The strongest verified hook is the direct match between Resend's own codified
brand voice (developer-authored, evidence-based, no filler) and how you already build and describe
your work. The most honest gap to be ready to address is Next.js specifically (versus your deep
React/Vite background) and that your strongest recent full-stack proof points are founder/
consulting project work rather than multi-year employment at a single product company; both are
real but narrow gaps, not disqualifiers given the posting's own "6+ years building and shipping
high-quality web products" framing (which you clear) and its "exceptional fit" (not required)
list. The two dated production incidents are a legitimate, if minor, reliability signal worth
being aware of, not a red flag disqualifying the role.
