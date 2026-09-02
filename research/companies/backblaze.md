# Backblaze (Nasdaq: BLZE)

Draft dossier for Santiago Coronado, refreshed for job id 33178, "Software Engineer, Open Source
AI" (https://job-boards.greenhouse.io/backblaze/jobs/5398676008). Originally researched for job
id 2158, "AI Workflow Engineer | LATAM." This is Santiago's THIRD application to Backblaze; see
section 7 for the rejection history and what it implies. This is a draft: review before use and
refresh if it goes stale.

## 1. Snapshot

Publicly traded, loss-narrowing cloud storage company (Nasdaq: BLZE, IPO 2021 after bootstrapping
on under $3M outside funding since founding in 2007); sells B2 Cloud Storage (S3-compatible object
storage) and Computer Backup; HQ San Mateo, California, fully remote-first workforce of about 320
full-time employees as of Dec 31, 2025; Q2 2026 revenue $42.7M (up 18% YoY, beat guidance by
$2.5M), B2 Cloud Storage revenue $26.6M (up 34% YoY), net loss narrowed to $5.1M (from $7.1M in
Q2 2025), FY2026 guidance raised to $172.0-174.0M revenue and 27-29% adjusted EBITDA margin; 500K+
customers in 175+ countries, 3+ exabytes stored [job posting; SEC 10-K FY2025; Q2 2026 earnings
release].

## 2. Core narrative

Backblaze's whole identity is "the open cloud": the anti-hyperscaler challenger that
open-sources its hard-drive reliability data (since 2013) and its Reed-Solomon erasure-coding
code, prices storage at roughly a fifth of AWS S3, and publicly attacks egress fees as a
lock-in tax [Backblaze blog: Drive Stats, Reed-Solomon, egress-fees posts]. It is now riding
the AI infrastructure boom as a "storage backbone" for neoclouds and AI-native builders (AI
customers paying $50K+ ARR grew 67% YoY and 57% in count in Q2 2026, plus a $335M multi-year
CoreWeave deal) [Q2 2026 earnings; CoreWeave press release]. That same "open, build it yourself"
instinct is now running two parallel but distinct AI tracks. Internally, CEO Gleb Budman put the
company's CHRO, not a CTO or CPO, in charge of a company-wide AI Program Office, explicitly
because "real results come from changing how people work"; this is the LATAM-based enablement
team behind the AI Enablement Director and AI Workflow Engineer roles Santiago previously
interviewed for and was rejected from [Budman LinkedIn post; prior job postings]. Separately, and
on the product/engineering side, Backblaze is now building and open sourcing developer-facing AI
integrations, most visibly a Claude Code skill for managing B2 storage released in March 2026,
positioning B2 as the storage layer developers reach for inside AI coding agents [Backblaze blog,
"Managing Backblaze B2 with Claude"]. The "Software Engineer, Open Source AI" role Santiago is now
applying for sits in this second track (reporting toward Product/QA per the job description, not
the CHRO's enablement org), which matters for how he frames a third application to this company.

## 3. Mission & product

- Products: B2 Cloud Storage (S3-compatible object storage) and Computer Backup (consumer/SMB
  backup for Mac and PC) [job posting; backblaze.com/company/about].
- Stated mission: "make customers unstoppable" by removing the lock-in, complexity, and cost of
  legacy/hyperscaler cloud storage [backblaze.com/company/about].
- Business model: usage-based cloud storage pricing, free egress up to 3x average monthly
  storage, egress beyond that at $0.01/GB, positioned at about one-fifth the cost of AWS S3 for
  storage plus egress combined [Backblaze blog, "Escaping Egress" / egress-fees explainer].
- Customers: 500K+ across 175+ countries, from individual/SMB backup users to hundreds of AI
  companies (model training, audio/video generation, app development) and neocloud/GPU providers
  [job posting; Q2 2026 earnings].
- Growth engine right now is B2 Cloud Storage, specifically AI and neocloud demand: B2 revenue
  $26.6M in Q2 2026 (up 34% YoY, B2 ARR reaching $113M, up 39% YoY) versus Computer Backup revenue
  $16.1M (down 2% YoY) [Q2 2026 earnings release].
- Flamethrower, a startup program (launched Feb 18, 2026) giving early-stage AI/ML, media, gaming,
  and SaaS founders storage credits and direct access to engineers, explicitly positioned against
  "short-term credits, upcharges, and automated onboarding" [Backblaze blog, "Introducing the
  Backblaze Flamethrower Startup Program"].

## 4. Culture & voice

- Founding story is a real part of the brand: seven co-founders started the company in a
  one-bedroom Palo Alto apartment in 2007 and scaled to IPO on under $3M in outside funding
  [backblaze.com/company/about; job posting].
- Stated values: trust, building a good product, charging fairly, being "open, honest, and
  accepting" with customers and each other, long-term thinking, and being "rationally frugal"
  [backblaze.com/company/about].
- Radical transparency is a real, load-bearing habit, not just messaging: Drive Stats (hard-drive
  failure data, open sourced quarterly since 2013) and the newer Performance Stats (benchmarking
  themselves against competitors publicly) [Backblaze blog: Drive Stats, Q1 2026 Drive Stats
  businesswire release].
- Historically an irreverent, humor-forward blog voice (recurring April Fools posts, informal
  "adventures in the cloud" tone), though the company noted in 2020 it skipped the April Fools
  tradition given COVID-19 uncertainty, showing some judgment about when levity fits
  [Backblaze blog, "An April 1st Post"].
- Remote-first by design, workforce distributed across the US and internationally; company frames
  it as "great work can happen anywhere" [backblaze.com/company/about].
- Glassdoor: 3.3/5 overall (82 reviews), 3.6/5 work-life balance, 52% would recommend to a friend;
  recurring themes are founder accessibility/transparency and flexibility, career growth rated
  lower (3.0/5); an April 2026 review specifically cites layoffs as having "severed trust" with
  some employees, worth weighing against the otherwise positive tone [Glassdoor: Working at
  Backblaze].
- CEO Gleb Budman is a visible, first-person voice: he still authors blog posts and publicly
  explains leadership calls (e.g. why he put the CHRO in charge of AI) rather than routing
  everything through comms [Backblaze blog author page; Budman LinkedIn post].

## 5. Recent news (last ~12 months, dated)

- Nov 5, 2025: "Making the Backblaze Network AI Ready", engineering blog on redesigning network
  infrastructure (PAM4 optics, MTP-16 fiber, 100G to 400G upgrades) for bursty, low-entropy AI
  traffic [Backblaze blog].
- Nov 1, 2025 (plan inception, disclosed later): Backblaze began a "2025 Restructuring and
  Transformation Plan" focused on sales, marketing, and product, incurring $6.1M in cumulative
  charges (workforce reductions, office lease impairment, other costs) through June 30, 2026, with
  an additional phase of severance announced in July 2026 and $2.4-3.7M more expected through Q1
  2027 [Backblaze 10-Q, via StockTitan SEC filing summary].
- Feb 18, 2026: Launched Flamethrower, a startup program for AI/ML, media, gaming, and SaaS
  founders [Backblaze blog / IR release].
- Feb 25, 2026: Q4/FY2025 results: FY2025 revenue $145.8M (up 14% YoY); first-ever eight-figure
  neocloud contract (over $15M total contract value); targeting ~200 neocloud accounts within a
  ~$14B TAM by 2030 [Blocks & Files coverage of Q4 2025 earnings].
- Mar 26, 2026: Released and open sourced the "B2 Cloud Storage Skill for Claude," a Claude
  Code/Codex/Cursor-compatible skill for inspecting, auditing, and managing B2 buckets via natural
  language, built on the Agent Skills spec, described as "intentionally lightweight and open" and
  "meant to be extended"; led by Jeronimo De Leon, Senior Product Manager, AI [Backblaze blog,
  "Managing Backblaze B2 with Claude"; github.com/backblaze-labs/claude-skill-b2-cloud-storage].
- Apr 15, 2026: Hired Anuj Kumar as Chief Revenue Officer (ex-NetApp, where he grew cloud revenue
  from $100M to ~$600M ARR) to run all sales/GTM; prior CRO Jason Wakeam moved to Chief Enterprise
  Sales Officer focused on major enterprise AI deals [Blocks & Files, "Backblaze doubles up on
  sales chiefs..."].
- Jun 23, 2026: Announced a five-year, multi-exabyte, $335M strategic storage agreement with
  CoreWeave to support CoreWeave's AI Object Storage HDD tier [Backblaze/CoreWeave press release,
  ir.backblaze.com].
- Aug 3, 2026: Q2 2026 results: revenue $42.7M (up 18% YoY, beat guidance by $2.5M), B2 Cloud
  Storage revenue $26.6M (up 34% YoY, B2 ARR $113M up 39% YoY), Computer Backup revenue $16.1M
  (down 2% YoY), net loss $5.1M (narrowed from $7.1M a year earlier), adjusted EBITDA $12.8M (30%
  of revenue), FY2026 guidance raised to $172.0-174.0M revenue and 27-29% adjusted EBITDA margin;
  CEO quote: "We exceeded the high end of our revenue and Adjusted EBITDA guidance, with B2 growth
  accelerating to 34% year over year" [Backblaze Q2 2026 earnings release, ir.backblaze.com].
- Aug 4-6, 2026: Exhibited and presented as a Platinum sponsor at Ai4 2026 (The Venetian Las
  Vegas), a ~12,000-attendee applied-AI conference, on "keeping GPUs fed at multimodal scale"
  [Businesswire, "Backblaze to Present at Ai4 2026"].
- Ongoing (as of this refresh, Aug 2026): the LATAM AI Program Office build-out from mid-2026
  (AI Enablement Director, AI Workflow Engineer) has narrowed. The "AI Enablement Director | LATAM"
  posting is no longer live on the Greenhouse board (job id redirects to an error page as of
  2026-08-31); "AI Workflow Engineer | LATAM" is still posted. A separate, newer thread has opened
  on the product/engineering side: "Software Engineer, Open Source AI" (this role, job id 33178)
  and "Software Engineer, AI," both LATAM-remote, sitting alongside a "Sr. AI Security Engineer"
  posting and 30+ other open reqs (36 total as of this refresh) [Greenhouse job board,
  job-boards.greenhouse.io/backblaze; direct URL checks of prior job ids].

## 6. Engineering & AI direction

Three distinct AI-adjacent stories worth separating in interview prep:

**Core infrastructure engineering (product side).** Backblaze runs custom "Storage Pod" hardware
with a Debian/Apache/EXT4/Tomcat stack, and built and open-sourced its own Java implementation of
Reed-Solomon erasure coding (files split into 17 data pieces plus 3 parity pieces, MIT licensed)
for durability [Backblaze blog, "Erasure Coding: Backblaze Open Sources Reed-Solomon Code";
GitHub, Backblaze/JavaReedSolomon]. Network engineering has been actively re-architected in the
last year specifically for AI traffic patterns (sustained multi-gigabit to terabit flows, low
entropy, high sensitivity to jitter/loss), including PAM4 optics and 400G upgrades [Backblaze
blog, "Making the Backblaze Network AI Ready," Nov 2025].

**Open source AI integrations and developer relations (the team THIS role sits in).** New and
growing in 2026: a public docs hub, "Open Source AI Integration Guides," covering data
ingestion/active-archive tools, data processing and orchestration platforms, model training and
experimentation frameworks, and inference/generative-AI applications for B2 storage
[backblaze.com/docs/cloud-storage-ai-and-ml-integrations]. The most concrete public artifact is the
open-sourced "B2 Cloud Storage Skill for Claude" (Mar 2026), maintained across two GitHub orgs
(backblaze-b2-samples and backblaze-labs), built on the open Agent Skills spec and explicitly
compatible with Claude Code, Codex CLI, Cursor, and Gemini CLI, with a companion blog post framing
it as a foundation "meant to be extended" [Backblaze blog, "Managing Backblaze B2 with Claude";
github.com/backblaze-b2-samples; github.com/backblaze-labs/claude-skill-b2-cloud-storage]. Jeronimo
De Leon, Senior Product Manager, AI, is the named lead on this work per the blog post byline
context [same source]. This role's own JD asks for Python, TypeScript, Go, and Rust; B2 SDKs and
REST APIs; hands-on daily use of AI coding agents (Claude Code, Antigravity, Codex) as part of
development itself; and ownership of public, externally-adopted GitHub repos (sample apps, SDK
extensions, notebooks) built in collaboration with Product and QA, explicitly not the internal
enablement org [job posting, job id 33178].

**Internal AI Program Office (the team Santiago previously interviewed with).** Reports up through
the CHRO (Robert Fitt, joined Oct 2022), a deliberate choice CEO Gleb Budman explained publicly as
"AI is incredible technology, but real results come from changing how people work" [Budman
LinkedIn post; Backblaze blog, "Welcoming CHRO Robert Fitt"]. The AI Enablement Director role
(US-based, base pay $165k-215k) owned intake, prioritization, an "AI Tool Registry," and a
hard success bar tied to a single-slide "what has AI actually delivered" readout; the AI Workflow
Engineer role was the hands-on build layer under that Director, embedded inside non-GTM,
non-Engineering functions (Finance, HR, Legal, Marketing Ops, Customer Success) [AI Enablement
Director JD; AI Workflow Engineer JD]. This is a materially different team, manager, and mandate
from the Open Source AI role: internal process/automation work for business functions versus
public, developer-facing open source software for Product.

## 7. Why-fit angles for Santiago

**Application history (read this first).** Santiago has applied to Backblaze twice before, both
into the CHRO's internal AI Program Office: "AI Enablement Director" (rejected) and "AI Workflow
Engineer" (rejected 2026-08-12, after two interview rounds, so he got real signal and was
evaluated in depth, not screened out on paper). This is his third application, and it lands in a
genuinely different org (Product/Engineering, open source developer tooling, not internal
business-function enablement), reporting to a different likely hiring chain (the AI/ML product
team, evidenced by PM Jeronimo De Leon's public work) rather than the CHRO. That is a real,
defensible reason to try again rather than a pattern of reapplying into the same closed door. It
is also worth being honest that Backblaze has now evaluated him twice and passed both times; if
asked directly in an interview why he is applying a third time, the honest answer is that this
specific role (hands-on open source engineering, public repos, AI coding agents used daily) is
closer to his actual strongest lane (shipping code, not internal process design) than the two
roles he was previously rejected from, and that the two prior processes, especially two full
rounds on AI Workflow Engineer, gave him real, current visibility into how Backblaze evaluates and
what it values.

**Best single hook to lead with:** this role is squarely his strongest lane, not an adjacent
enablement/strategy role he had to argue his way into. He already ships production open source
software solo (Kairos: an Electron/TypeScript app open sourced with a public MCP server and 52
tools; Plutus: a full Dockerized multi-service stack), and he already builds AI coding-agent
tooling as an everyday practice, not a novelty: Pragma AI's internal platform runs 15 agent
definitions and 10 reusable routines as tools inside Claude Code, and Kairos exposes the same 52
tools to both an in-app agent (Claude Agent SDK) and a standalone MCP server so Claude Code can
operate on live user data [resume/master_resume.yaml]. That is a close, direct analog to what this
JD asks for: build and maintain open source AI integrations and example apps, use AI coding agents
(explicitly including Claude Code) as part of daily development, and own public repos meant for
external adoption [job posting, job id 33178].

**Supporting fit points:**
- Native Spanish, Mexico City based, and this posting explicitly lists Mexico as an eligible
  remote location, plus TN-visa eligible for any future US-side work [config/profile.yaml; job
  posting].
- Multi-language range matches the JD's language list (Python, TypeScript, Go, Rust): his resume
  covers Python/FastAPI, TypeScript, and JavaScript/Node.js at production depth; Go and Rust are
  not on the resume and should not be claimed without confirming real hands-on time
  [resume/master_resume.yaml; job posting].
- Testing and documentation discipline the JD explicitly asks for ("high standards for testing,
  documentation, reproducibility") shows up concretely in his own projects: 494 Vitest tests in
  Kairos, 114 Vitest unit tests plus 10 Playwright E2E flows in the Hydrel portal, an automated
  eval harness for Pragma's RAG system [resume/master_resume.yaml].

**Honest gaps and watch-outs:**
- Two prior rejections at this company are real signal, not nothing. Even though this role sits in
  a different org, an interviewer may reasonably ask why he is reapplying; have a direct, honest
  answer ready (see application history above) rather than avoiding the topic.
- No public open source contribution history to *external* (non-Santiago-owned) projects is
  evident on the resume; his open source work (Kairos) is his own project, not contributions to
  someone else's widely-used repo. The JD wants "experience contributing to open source projects,"
  which could mean either owning public repos or contributing to others'; be ready to speak
  precisely to which one his experience actually is.
- Go and Rust are named languages in the JD's tooling list but are not on the resume; do not claim
  them without confirming real experience first.
- No salary is listed on this posting; the sibling US-based "AI Enablement Director" role posted
  $165k-215k previously, but that was a US, director-level, different-org number and is not a
  reliable proxy for this LATAM IC band [AI Enablement Director JD, no longer live].
- Backblaze is a small, still GAAP-unprofitable public company that just ran a company-wide
  restructuring (2025 Restructuring and Transformation Plan, $6.1M in cumulative charges through
  Q2 2026, an additional severance phase announced July 2026, explicitly touching sales,
  marketing, AND product) even as B2/AI revenue accelerates and guidance keeps getting raised
  [Backblaze 10-Q, via StockTitan SEC filing summary; Q2 2026 earnings release]. Worth having an
  honest, informed view on stability and on why a product-side open source AI role is being hired
  for during a product-adjacent restructuring, rather than treating either the growth story or the
  restructuring in isolation.
- A 2025 short-seller report (Morpheus Research, published April 2025, so predates most of the
  numbers above and should be weighed as an inherently biased source) alleges accounting and
  governance issues tied to two 2024 lawsuits from former finance employees; unverified beyond the
  report itself and not corroborated by any of the primary sources used in this dossier, included
  here only so Santiago is not blindsided if it comes up [Morpheus Research report on Backblaze,
  April 2025].

## 8. Application-question angles

**Why this company:** Lead with the open source AI story, not the storage product in the
abstract. Backblaze just shipped and open sourced a Claude Code skill for managing B2 storage
(March 2026), built on the open Agent Skills spec and explicitly designed to be extended by the
community, the same "open, DIY, transparent" instinct the company has applied to hard-drive
reliability data since 2013. This role is the next step of that bet: hands-on engineering that
makes B2 a natural, well-documented part of how developers build AI workflows, not a marketing
claim about AI.

**Why you fit:** Do not checklist the four research areas, lead with what he actually ships. He
already builds and open sources AI-agent tooling as daily practice, not a resume line: Kairos
exposes 52 tools to both an in-app Claude agent and a standalone MCP server from one codebase, and
Pragma AI's internal platform runs 15 agent definitions as tools inside Claude Code for the whole
team. That is close to a direct rehearsal for building public, externally-adopted open source AI
integrations and example apps while using AI coding agents as an everyday tool, which is exactly
what this JD describes.

**Anything else:** If asked why he is applying to Backblaze a third time (he previously
interviewed for AI Enablement Director and AI Workflow Engineer and was not selected for either),
answer directly rather than avoiding it: those two roles sat in the CHRO's internal enablement
org, this one sits in Product/Engineering building public open source software, which is closer to
his strongest, most concrete work. He also picked up real, current visibility into how Backblaze
evaluates candidates from two full interview rounds on the prior role.

## 9. Sources

researched: 2026-08-31 (refresh; originally researched 2026-07-14)

- https://job-boards.greenhouse.io/backblaze/jobs/5398676008 (this role's JD, job id 33178:
  company overview blurb, Open Source AI Engineer responsibilities, tools/technologies,
  qualifications, "Why Backblaze" bullets)
- /Users/santiagocoronado/jobhunt (`.venv/bin/python -m src.query job 33178`, full posting record
  including status, match score, and location eligibility)
- https://job-boards.greenhouse.io/backblaze/jobs/5287532008 (AI Workflow Engineer JD, job id
  2158: still live as of 2026-08-31, used for the internal Program Office comparison)
- https://job-boards.greenhouse.io/backblaze/jobs/5257964008 (AI Enablement Director JD: now
  redirects to an error page on the Greenhouse board as of 2026-08-31, confirming the posting has
  closed; content preserved from original 2026-07-14 research for the Program Office description)
- https://job-boards.greenhouse.io/backblaze (live job board, checked 2026-08-31: confirms current
  open reqs, including Software Engineer Open Source AI, Software Engineer AI, AI Workflow
  Engineer LATAM, Sr. AI Security Engineer, and 30+ other roles)
- https://www.backblaze.com/company/about (mission, founding story, values, remote-first culture)
- https://www.backblaze.com/blog/managing-backblaze-b2-with-claude-introducing-the-b2-cloud-storage-skill-for-claude/
  (Mar 26, 2026: B2 Cloud Storage Skill for Claude launch, open source AI strategy, Jeronimo De
  Leon byline)
- https://www.backblaze.com/docs/cloud-storage-ai-and-ml-integrations (Open Source AI Integration
  Guides docs hub)
- https://github.com/backblaze-b2-samples/claude-skill-b2-cloud-storage and
  https://github.com/backblaze-labs/claude-skill-b2-cloud-storage (open source repos for the
  Claude skill, engineering culture evidence)
- https://ir.backblaze.com/news/news-details/2026/Backblaze-Announces-Second-Quarter-2026-Financial-Results/default.aspx
  (Aug 3, 2026: Q2 2026 financials, AI customer growth, guidance raise, CEO quote)
- https://www.businesswire.com/news/home/20260803072886/en/Backblaze-to-Present-at-Ai4-2026-on-Keeping-GPUs-Fed-at-Multimodal-Scale
  (Aug 4-6, 2026: Ai4 2026 Platinum sponsorship and presentation)
- https://www.stocktitan.net/sec-filings/BLZE/10-q-backblaze-inc-quarterly-earnings-report-b08f6342729b.html
  (Q2 2026 10-Q summary: 2025 Restructuring and Transformation Plan charges, July 2026 severance
  phase, sales/marketing/product scope)
- https://www.blocksandfiles.com/public-cloud/2026/04/15/backblaze-doubles-up-on-sales-chiefs-to-chase-ai-storage-demand/5217702
  (Apr 15, 2026: CRO Anuj Kumar hire, neocloud/AI sales strategy, $14B TAM by 2030)
- https://www.blocksandfiles.com/public-cloud/2026/02/25/backblaze-secures-major-neocloud-deal-as-revenue-climbs-12/4091815
  (Feb 25, 2026: Q4/FY2025 results, first eight-figure neocloud deal)
- https://www.backblaze.com/blog/making-the-backblaze-network-ai-ready/ (Nov 5, 2025: network
  engineering redesign for AI traffic)
- https://www.backblaze.com/blog/reed-solomon/ (open-sourced Reed-Solomon erasure coding)
- https://github.com/Backblaze/JavaReedSolomon (open-source repo, engineering culture evidence)
- https://www.businesswire.com/news/home/20260709916379/en/Backblaze-Publishes-Q1-2026-Drive-Stats-Reliability-Improves-as-92-of-New-Deployments-Exceed-20TB
  (Drive Stats transparency tradition, ongoing quarterly cadence)
- https://www.glassdoor.com/Overview/Working-at-Backblaze-EI_IE1197085.11,20.htm (employee
  ratings/culture signals, including an April 2026 review referencing layoffs)
- https://www.backblaze.com/blog/escaping-egress-hidden-cloud-fees-every-cfo-should-know/
  (open-cloud/anti-egress-fee positioning)
- https://www.backblaze.com/blog/introducing-the-backblaze-flamethrower-startup-program/ (Feb 18,
  2026: Flamethrower startup program launch)
- https://ir.backblaze.com/news/news-details/2026/Backblaze-Announces-Five-Year-Multi-Exabyte-Data-Storage-Agreement-with-CoreWeave/default.aspx
  (Jun 23, 2026: $335M CoreWeave deal)
- https://www.sec.gov/Archives/edgar/data/1462056/000162828026016395/blze-20251231.htm (FY2025
  10-K: HQ San Mateo CA, ~320 full-time employees as of Dec 31, 2025)
- https://www.linkedin.com/posts/glebbudman_controversial-take-the-exec-i-put-in-activity-7373409399907807232-2ZU4
  (CEO Gleb Budman on why the CHRO leads AI at Backblaze)
- https://www.backblaze.com/blog/welcoming-chief-human-resources-officer-robert-fitt-to-backblaze/
  (CHRO Robert Fitt background, joined Oct 2022)
- https://www.backblaze.com/blog/an-april-1st-post/ (blog voice/tone evidence)
- https://www.morpheus-research.com/backblaze/ (short-seller report, April 2025; included only as
  a flagged, unverified, inherently biased source per the honest-watch-outs rule)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile, location and
  visa constraints, flagged this Backblaze role family as ideal)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's real experience used for
  fit angles)
