# Backblaze (Nasdaq: BLZE)

Draft dossier for Santiago Coronado. Researched for job id 2158, "AI Workflow Engineer | LATAM"
(https://job-boards.greenhouse.io/backblaze/jobs/5287532008). This is a draft: review before use
and refresh if it goes stale.

## 1. Snapshot

Publicly traded, profitable-trending cloud storage company (Nasdaq: BLZE, IPO 2021 after
bootstrapping on under $3M outside funding since founding in 2007); sells B2 Cloud Storage
(S3-compatible object storage) and Computer Backup; HQ San Mateo, California, fully remote-first
workforce of about 320 full-time employees as of Dec 31, 2025; FY2025 revenue $145.8M (up 14% YoY);
Q1 2026 revenue $38.7M (up 12% YoY); 500K+ customers in 175+ countries, 3+ exabytes stored [job
posting; SEC 10-K FY2025; Q1 2026 earnings release].

## 2. Core narrative

Backblaze's whole identity is "the open cloud": the anti-hyperscaler challenger that
open-sources its hard-drive reliability data (since 2013) and its Reed-Solomon erasure-coding
code, prices storage at roughly a fifth of AWS S3, and publicly attacks egress fees as a
lock-in tax [Backblaze blog: Drive Stats, Reed-Solomon, egress-fees posts]. It is now riding
the AI infrastructure boom as a "storage backbone" for neoclouds and AI-native builders (76%
YoY AI-customer growth, a $335M multi-year CoreWeave deal, a dedicated Flamethrower startup
program) [Q1 2026 earnings; CoreWeave press release; Flamethrower launch]. At the same time it
is running the same "open, transparent, build it yourself" instinct inward: CEO Gleb Budman put
the company's CHRO, not a CTO or CPO, in charge of a company-wide AI Program Office, explicitly
because "real results come from changing how people work," and the company is standing up that
whole builder function (Director roles plus hands-on engineers) as a brand-new, LATAM-based team
[Gleb Budman LinkedIn post; AI Enablement Director JD; AI Workflow Engineer JD; Greenhouse job
board].

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
  [job posting; Q1 2026 earnings].
- Growth engine right now is B2 Cloud Storage, specifically AI and neocloud demand: B2 ARR $93.0M
  (up 28% YoY) versus flat Computer Backup ARR ($65.2M) in Q1 2026 [Q1 2026 earnings release].
- New GTM motion: Flamethrower, a startup program (launched Feb 18, 2026) giving early-stage
  AI/ML, media, gaming, and SaaS founders storage credits and direct access to engineers, explicitly
  positioned against "short-term credits, upcharges, and automated onboarding" [Backblaze blog,
  "Introducing the Backblaze Flamethrower Startup Program"].

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
  recurring themes in reviews are founder accessibility/transparency and flexibility, with career
  growth rated lower (3.0/5) [Glassdoor: Working at Backblaze].
- CEO Gleb Budman is a visible, first-person voice: he still authors blog posts and publicly
  explains leadership calls (e.g. why he put the CHRO in charge of AI) rather than routing
  everything through comms [Backblaze blog author page; Budman LinkedIn post].

## 5. Recent news (last ~12 months, dated)

- Nov 5, 2025: "Making the Backblaze Network AI Ready", engineering blog on redesigning network
  infrastructure (PAM4 optics, MTP-16 fiber, 100G to 400G upgrades) for bursty, low-entropy AI
  traffic [Backblaze blog].
- Nov 10, 2025: Q3 2025 Network Stats release: neocloud traffic already ~25% of total network
  ingress/egress [Backblaze/Businesswire, Q3 2025 Network Stats].
- Feb 18, 2026: Launched Flamethrower, a startup program for AI/ML, media, gaming, and SaaS
  founders [Backblaze blog / IR release].
- Feb 25, 2026: Q4/FY2025 results: FY2025 revenue $145.8M (up 14% YoY); first-ever eight-figure
  neocloud contract (over $15M total contract value); targeting ~200 neocloud accounts within a
  ~$14B TAM by 2030 [Blocks & Files coverage of Q4 2025 earnings].
- Apr 15, 2026: Hired Anuj Kumar as Chief Revenue Officer (ex-NetApp, where he grew cloud revenue
  from $100M to ~$600M ARR) to run all sales/GTM; prior CRO Jason Wakeam moved to Chief Enterprise
  Sales Officer focused on major enterprise AI deals [Blocks & Files, "Backblaze doubles up on
  sales chiefs..."].
- May 4-5, 2026: Q1 2026 results: revenue $38.7M (up 12% YoY), B2 Cloud Storage revenue $22.4M (up
  24% YoY), AI customer count up 76% YoY, adjusted EBITDA $10.1M (26% of revenue, up from 18% a
  year earlier), FY2026 guidance raised to $161.5-163.5M revenue and 23-25% adjusted EBITDA margin
  [Q1 2026 earnings release, ir.backblaze.com].
- Jun 23, 2026: Announced a five-year, multi-exabyte, $335M strategic storage agreement with
  CoreWeave to support CoreWeave's AI Object Storage HDD tier [Backblaze/CoreWeave press release,
  ir.backblaze.com].
- Ongoing (as of this research, Jul 2026): actively building out a brand-new, LATAM-based AI
  Program Office alongside its existing US "AI Enablement Director" role: open reqs include
  "AI Enablement Director | LATAM," "AI Workflow Engineer | LATAM" (this role), multiple
  "Software Engineer, AI" LATAM postings, and a "Sr. AI Security Engineer" LATAM posting, alongside
  broader LATAM engineering hires (SRE II, backend engineers, technical program managers)
  [Greenhouse job board, job-boards.greenhouse.io/backblaze].

## 6. Engineering & AI direction

Two distinct AI stories worth separating in interview prep:

**Core infrastructure engineering (product side).** Backblaze runs custom "Storage Pod" hardware
with a Debian/Apache/EXT4/Tomcat stack, and built and open-sourced its own Java implementation of
Reed-Solomon erasure coding (files split into 17 data pieces plus 3 parity pieces, MIT licensed)
for durability [Backblaze blog, "Erasure Coding: Backblaze Open Sources Reed-Solomon Code";
GitHub, Backblaze/JavaReedSolomon]. Network engineering has been actively re-architected in the
last year specifically for AI traffic patterns (sustained multi-gigabit to terabit flows, low
entropy, high sensitivity to jitter/loss), including PAM4 optics and 400G upgrades [Backblaze
blog, "Making the Backblaze Network AI Ready," Nov 2025].

**Internal AI Program Office (the team this role sits in).** This is new and distinct from the
storage engineering org. It reports up through the CHRO (Robert Fitt, joined Oct 2022), a
deliberate choice CEO Gleb Budman explained publicly as: "AI is incredible technology, but real
results come from changing how people work" [Budman LinkedIn post; Backblaze blog, "Welcoming
CHRO Robert Fitt"]. The companion "AI Enablement Director" role (US-based, reports to CHRO, base
pay $165k-215k) owns intake, prioritization, an "AI Tool Registry" for governance/security review,
and a hard success bar: "by Q3, we should be able to answer 'what has AI actually delivered this
year?' in a single slide with numbers" [AI Enablement Director JD, Greenhouse]. The AI Workflow
Engineer role (this one, LATAM) is the hands-on build layer under that Director: prompt
architectures, automation flows, lightweight agents, RAG implementations, and API integrations,
embedded directly inside non-GTM, non-Engineering business functions (Finance, HR, Legal,
Marketing Ops, Customer Success), explicitly not a research or strategy role. Stated bonus tooling
signals in the JD: Make, Zapier, n8n or equivalent automation platforms, plus "working familiarity"
with RAG and agent frameworks [AI Workflow Engineer JD, job id 2158].

## 7. Why-fit angles for Santiago

**Best single hook to lead with:** Santiago has already run the exact motion this role is built
around, as the business owner rather than as an assigned builder. At Eugenia.ai he embedded
on-site with HOAs and property administrators, mapped their real (messy, non-technical) workflows,
and shipped a deployable full-stack tool without waiting on anyone else. At Online Basics he
designed and owned an LLM workflow (Anthropic and OpenAI APIs, custom prompt engineering, a
multi-stage validation pipeline) that cut content-creation time 70% for a real operating business,
not a demo. At Pragma AI (current) he is literally doing internal-AI-enablement-as-a-service for
Mexican SMBs: a RAG "company brain" plus conversational agents and automations for quoting,
reporting, onboarding, and collections [resume/master_resume.yaml]. That is close to a direct
analog of what Backblaze's AI Program Office is trying to build internally, just previously sold
externally to clients instead of delivered to internal business teams.

**Supporting fit points:**
- Native Spanish, Mexico City based, listed among the eligible LATAM locations (Mexico) on this
  posting, and TN-visa eligible for any future US-side work [config/profile.yaml; job posting].
- "Strong enough with code or no-code tools to get solutions to a deployable state
  independently, you do not need an engineer to ship your work" (JD language) matches his history
  of shipping solo/lean: Python/FastAPI backends, React/Node front ends, agent frameworks with
  tool-use and function calling, without a larger engineering org behind him
  [resume/master_resume.yaml].
- The JD's "genuinely curious about how companies work: the org chart, the incentives, the
  handoffs, the bottlenecks" is close to describing what running two companies (Online Basics,
  Eugenia.ai) as founder/CEO actually requires day to day.

**Honest gaps and watch-outs:**
- The JD's ideal background is explicitly someone who *started* in a business-facing function
  (finance, ops, marketing, CS, HR) and later picked up AI/automation skills, "not just in
  Engineering or IT." Santiago's arc runs the other direction: engineer-founder who owned the P&L,
  hiring, pricing, and vendor decisions for two companies, which is real business-function
  exposure but earned from the CEO seat, not as a functional specialist. Worth naming this
  directly rather than glossing over it, and reframing around the specific finance/ops/HR
  decisions he actually owned (9-person team leadership, unit economics, vendor and investor
  relationships).
- JD stresses this is explicitly "not a research role or a strategy role," you take scoped use
  cases from a Director and execute; Santiago's whole career has been founder-level, owning the
  roadmap himself. Be ready to speak concretely to comfort taking direction and scope from someone
  else and executing fast within it, versus setting the strategy.
- Named no-code automation tools in the JD (Make, Zapier, n8n) are not explicitly on his resume,
  which leans custom code and agent frameworks (LangChain-style, Claude Agent SDK, MCP). Confirm
  real hands-on time with at least one of the named tools before the interview, or be ready to
  explain the custom-code equivalent honestly.
- No salary is listed on this posting (consistent with profile rule to not treat missing pay as a
  dealbreaker), but the sibling US-based "AI Enablement Director" role posts $165k-215k, which is
  a US, director-level number and not a reliable proxy for this LATAM IC band; get real numbers
  before any comp conversation [AI Enablement Director JD].
- Backblaze is a small, still-unprofitable-on-GAAP public company (~320 employees, Q1 2026 GAAP
  net loss of $6.1M, though adjusted EBITDA is positive and improving, and 2026 guidance was just
  raised); worth having an honest, informed view on stability if asked, rather than treating it as
  a risk-free bet [Q1 2026 earnings release; SEC 10-K FY2025].

## 8. Application-question angles

**Why this company:** Lead with the structural signal, not the storage product. Backblaze put its
CHRO, not a CTO or CPO, in charge of company-wide AI adoption because leadership believes "real
results come from changing how people work," and it is standing up a brand-new, LATAM-based,
hands-on builder team to prove that thesis with production tools, not decks. That is an unusually
honest bet on the same principle Santiago has built his whole career around: AI only creates value
when it is embedded in how a real, non-technical team actually works, not when it stays a research
demo.

**Why you fit:** Do not checklist the four research areas, lead with the founder-operator pattern.
He has already run "embed with a non-technical team, map the real workflow, ship a deployable
prototype in days, iterate on real usage" repeatedly, at Eugenia.ai with property administrators,
at Online Basics with an LLM content pipeline that had to hit real revenue numbers, and now at
Pragma AI building the same kind of internal-AI-enablement tooling (RAG company brain, workflow
automations) for other companies' business teams. This role asks for exactly that motion, just
inside Backblaze instead of for an outside client.

**Anything else:** Native Spanish, Mexico City based (an explicitly eligible location on this
posting), and genuinely energized to join while this specific LATAM AI Program Office team is
still being built out from scratch, ground-floor team-building is the environment he has chosen
every time as a founder.

## 9. Sources

researched: 2026-07-14

- https://job-boards.greenhouse.io/backblaze/jobs/5287532008 (this role's JD, job id 2158: company
  overview blurb, founding/revenue/customer numbers, AI Workflow Engineer responsibilities,
  qualifications, bonus points)
- https://job-boards.greenhouse.io/backblaze/jobs/5257964008 (AI Enablement Director JD: AI
  Program Office structure, CHRO reporting line, use-case lifecycle, governance model, pay range)
- https://job-boards.greenhouse.io/backblaze (live job board: confirms the LATAM AI Program Office
  build-out, AI Enablement Director LATAM, AI Workflow Engineer LATAM, Software Engineer AI x
  LATAM, Sr. AI Security Engineer LATAM, plus broader LATAM engineering reqs)
- https://www.backblaze.com/company/about (mission, founding story, values, remote-first culture)
- https://ir.backblaze.com/news/news-details/2026/Backblaze-Announces-First-Quarter-2026-Financial-Results/default.aspx
  (Q1 2026 financials, AI customer growth, guidance raise, CEO quote)
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
  ratings/culture signals)
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
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's target profile, location and
  visa constraints, flagged this Backblaze role family as ideal)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's real experience used for
  fit angles)
