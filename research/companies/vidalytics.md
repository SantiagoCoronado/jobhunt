# Vidalytics: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: "AI Automation Engineer, In-House MarTech Video SaaS" (job id 7686), Vidalytics'
own careers page, https://www.vidalytics.com/career/ai-automation-engineer (mirrored on
LinkedIn and We Work Remotely; WWR blocks automated fetchers with a 403, so the primary source
used here is Vidalytics' own site, fetched directly).

## Location and eligibility verdict (read first): ELIGIBLE

Vidalytics' own job page states the requirement twice, and both times it is framed as a
timezone-overlap ask, not a country restriction: "Your working hours overlap strongly with US
Eastern time. We can discuss further." and "Most of your available working hours overlaps (or
can) w/ the Eastern US time zone." [vidalytics.com/career/ai-automation-engineer]. No sentence
anywhere on that page requires a specific country of residence, US work authorization, or
in-office presence.

The We Work Remotely mirror of this same requisition carries a structured "Region: Anywhere in
the World" field and lists it as Full-Time with an application deadline of August 6, 2026
[weworkremotely.com/remote-jobs/vidalytics-ai-automation-engineer-in-house-martech-video-saas,
via search index since WWR 403s direct fetches]. That "Anywhere in the World" framing is also
corroborated by contrast: two sibling Vidalytics requisitions posted around the same time (GTM
MarTech Engineer, and AI Native Performance Marketing Manager) are explicitly titled "[EUROPE
ONLY]" on We Work Remotely, showing Vidalytics does apply country locks to some roles and chose
not to on this one [weworkremotely.com/remote-jobs/vidalytics-europe-only-gtm-martech-engineer-growth-attribution-at-video-martech-saas;
weworkremotely.com/remote-jobs/vidalytics-europe-only-ai-native-performance-marketing-manager-in-house-martech-video-saas].

Mexico City runs on Central Time (UTC-6), one hour behind US Eastern (UTC-5). A standard 9am to
5pm Eastern workday is 8am to 4pm in Mexico City, so the stated overlap requirement is easily
satisfiable without relocation.

Posting liveness, confirmed 2026-07-28: Vidalytics' own careers page shows an active "Apply Now"
button on the posting, and the We Work Remotely listing shows a live application deadline eight
days out (Aug 6, 2026) [vidalytics.com/career/ai-automation-engineer;
weworkremotely.com/remote-jobs/vidalytics-ai-automation-engineer-in-house-martech-video-saas].

Employee vs. contractor: UNVERIFIED. The posting uses employee-flavored language ("You're more
than an employee, you're a person") but never states a formal employment classification, payroll
country, or entity of hire for a worldwide-remote candidate [vidalytics.com/career/ai-automation-engineer].
For a ~16 to 18-person US company hiring "anywhere in the world," a contractor agreement or an
EOR arrangement is at least as likely as direct employment; this needs a direct question to the
recruiter/CEO before assuming either.

Pay: not listed. No salary range, equity, or contractor rate appears anywhere on the company's own
posting, the LinkedIn mirror, or the We Work Remotely listing found in this research
[vidalytics.com/career/ai-automation-engineer]. Per `config/profile.yaml`'s comp rule, an unlisted
band keeps the role in play rather than triggering a pay-floor rejection, but the actual number
(and whether it is quoted as an employee salary or a contractor rate) should be raised early in
the process.

## 1. Snapshot

Vidalytics is a bootstrapped, profitable video hosting and marketing SaaS built specifically for
direct-response marketers (video sales letters, funnels, course creators, e-commerce), founded in
2016/2017 by Patrick Stiles and headquartered in Austin, Texas
[linkedin.com/company/vidalytics; starterstory.com/vidalytics-breakdown]. LinkedIn lists an
employee-count band of 11 to 50; a leadership-org tracker (The Org) puts the actual team closer to
16 to 18 people across engineering, marketing, sales, and operations, reporting up to founder and
CEO Patrick Stiles [linkedin.com/company/vidalytics; theorg.com/org/vidalytics/org-chart/patrick-stiles].
No external funding has been found; third-party revenue estimators (Starter Story, Getlatka) put
annual revenue in the high six figures as of late 2024, which is far smaller than the company's
own marketing claims of $5.7B+ in customer sales tracked through the platform and 27,645+ users of
the product, a gap best explained by "revenue Vidalytics collects" versus "sales volume its
customers process through hosted videos" being two very different numbers; treat both figures as
self-reported and unverified against any audited source
[starterstory.com/vidalytics-breakdown; getlatka.com/companies/vidalytics;
vidalytics.com/ai-suite].

## 2. Core narrative

Patrick Stiles built Vidalytics after working as a video marketer himself and concluding that
general-purpose video hosts (Wistia, Vimeo, YouTube, Vidyard) were built for "views," not for the
conversion mechanics that direct-response marketers actually optimize against: exact drop-off
timestamps, play gates, exit-intent saves, and branching "Smart Vid" question flows that route a
viewer to a different follow-up video based on their answer
[starterstory.com/vidalytics-breakdown; vidalytics.com]. He funded the build himself, personally
taking on six figures of debt during a development phase that ran three times longer than planned,
and the company has stayed bootstrapped and profitable since
[starterstory.com/vidalytics-breakdown]. That founder story (a marketer-turned-operator who built
the tool he needed, kept full control, and grew it slowly on word of mouth among "eight-,
nine-, and ten-figure" direct-response brands like Frank Kern, Mike Dillard, and Golden Tree
Nutrition) is the frame this dossier should lean on: a small, scrappy, founder-led company betting
that deep specialization in one high-intent niche beats being a generic video platform
[getlatka.com/companies/vidalytics; vidalytics.com/testimonials]. The AI Automation Engineer role
is the next step of that same bet: instead of hiring a generic ops or automation hire, Stiles is
hiring one senior engineer who reports directly to him to make the whole ~16-person company
"AI native," starting with the revenue teams, a founder-led, high-ownership motion consistent with
how he has run the company from day one [vidalytics.com/career/ai-automation-engineer].

## 3. Mission & product

- Core product: a video player and hosting platform built around conversion analytics rather than
  view counts, including per-second engagement/drop-off tracking, Smart Vids (branching
  question-and-answer video flows), play gates, exit-intent save prompts, auto-start, countdown
  timers, and native A/B "Experiments" testing on hooks, offers, and thumbnails
  [vidalytics.com; vidalytics.com/blog/4-2026-monthly-marketing-update].
- 2026 AI Suite layer: Vids AI (benchmarks a video against an aggregated dataset the company says
  spans $3.5B+ in tracked video revenue to flag underperforming moments), an AI Script Analyzer
  (line-by-line script critique for hooks and persuasion), a Vid Settings Wizard, AI captions and
  translation (French, German, Portuguese, Spanish, Italian), and an "AI-Optimized Embed" that
  auto-generates SEO-style summaries and chapter markers so hosted videos are indexable by Google
  and by AI answer engines (ChatGPT, Perplexity) [vidalytics.com/ai-suite;
  vidalytics.com/blog/4-2026-monthly-marketing-update].
- Customers and market: direct-response marketers, video-sales-letter and funnel builders, course
  creators, e-commerce brands, and agencies; named customers/testimonials include Frank Kern, Mike
  Dillard, Brendon Burchard, Jon Benson, and Golden Tree Nutrition
  [vidalytics.com/testimonials; starterstory.com/vidalytics-breakdown].
- Business model: subscription SaaS starting at $17/month with a 14-day free trial, tiered up
  through an "Advanced Stats API" for BI integrations at higher plans
  [starterstory.com/vidalytics-breakdown; help.vidalytics.com/en/articles/2928645-api-functions].
- Recognition: G2 badges including Momentum Leader (Spring 2025) and High Performer (Winter 2023)
  [starterstory.com/vidalytics-breakdown].

## 4. Culture & voice

- Explicitly small and flat: "We're small and flat. There is no bullshit of trying to dance
  around sensitive topics... We're direct, we're honest, we're here to accomplish big audacious
  goals." [vidalytics.com/career/ai-automation-engineer].
- Founder-adjacent, high-ownership framing: the AI Automation Engineer reports directly to CEO
  Patrick Stiles, and the posting explicitly floats the possibility of the hire eventually
  co-founding a "sister corp" as Vidalytics tries to build a small portfolio of companies
  [vidalytics.com/career/ai-automation-engineer].
- Voice is informal and outcome-obsessed rather than corporate: postings use phrases like "LFG,"
  "GSD (get shit done)," and "You're loyal to outcomes, not hype," and explicitly reject
  "prompt-only" or hobbyist AI work in favor of production-grade, measured systems
  [vidalytics.com/career/ai-automation-engineer].
- Employee sentiment (small sample, only 3 Glassdoor reviews as of this research): reviewers
  describe a flat structure with real decision-making freedom and a "solid company" but call out
  internal communication as an area to improve
  [glassdoor.com/Reviews/Employee-Review-Vidalytics-RVW53802209.htm search summary;
  glassdoor.com/FAQ/Vidalytics-Question-FAQ200085-E1645156.htm search summary]. Treat this as a
  weak signal given the very small review count, not a settled verdict.
- Founder Patrick Stiles has publicly told a personal turnaround story (expulsion from school,
  addiction, jail time, then multiple eight-figure businesses before Vidalytics), which shows up in
  interviews as part of the company's public voice
  [inspiredinsider.com/patrick-stiles-interview].

## 5. Recent news (last ~12 months)

- October 2025: shipped Vids AI (instant video-performance insights) and a Vid Stats Funnel View
  for viewer-journey analysis [vidalytics.com/blog/4-2026-monthly-marketing-update summary of
  prior releases].
- February 2026: shipped native Experiments (in-platform A/B testing) and Storybar, a feature
  aimed at increasing conversion and reducing drop-off on long-form video
  [vidalytics.com/blog/4-2026-monthly-marketing-update summary of prior releases].
- April 2026: shipped AI-Optimized Embed (auto-generated summaries/chapters for AI-search and
  Google indexability), expanded native Experiments, and Interactive Smart Vids with clickable
  hotspots and branching logic [vidalytics.com/blog/4-2026-monthly-marketing-update].
- Ongoing 2026 hiring push: five roles posted on the company's careers page in the past roughly 14
  months span Marketing (AI-Native Conversion Copywriter, AI Native Performance Marketing Manager,
  AI Native Creative Strategist), Engineering (GTM MarTech Engineer), and Operations (this AI
  Automation Engineer role), suggesting a company-wide push to bake AI into both the product and
  the internal operations at the same time [vidalytics.com/careers].
- No funding announcement, acquisition, or leadership change was found in the last 12 months; the
  absence of any funding or press coverage beyond the company's own blog and product marketing is
  itself notable for a company this size (see Risks below).

## 6. Engineering & AI direction

- Public tech stack (third-party aggregator, not confirmed by the company directly): a
  polyglot, mostly older-generation web stack, Node.js, PHP (Symfony, Zend, Slim), Go, TypeScript,
  AngularJS on the frontend side, MySQL/Kafka/BigQuery/Bigtable for data, hosted across AWS (EC2,
  S3, CloudFront) and Google Cloud (GKE, Pub/Sub, BigQuery), with Stripe/Chargify for billing and
  Sentry for monitoring [himalayas.app/companies/vidalytics/tech-stack]. This is a third-party
  inference, not a company-published stack page, and should be treated as directional only.
- The AI Automation Engineer posting itself names a much narrower, more current tool set for the
  role specifically: Claude as the primary frontier model, daily use of "Claude Code and Claude
  Cowork," n8n and Zapier for cross-system automation, custom orchestration where those tools fall
  short, RAG/retrieval for grounding, evals and observability "by default," and AI-native hosting
  such as Vercel; the "nice to have" stack list is HubSpot, Fathom, Slack, Google Workspace,
  PostHog, Intercom, BigQuery, GCP, Vercel, v0, Lovable, and GitHub
  [vidalytics.com/career/ai-automation-engineer].
- The role's explicit mandate is anti-hallucination by design: "Ground AI outputs in our own
  company data (retrieval / RAG) so they're accurate, not confidently wrong" and "Diagnose
  failures, kill hallucinations, and build the guardrails that keep systems reliable in
  production." [vidalytics.com/career/ai-automation-engineer]. This is a company betting on
  production AI agents doing real revenue-team work (sales, marketing, customer success first,
  then the rest of the org), not chatbots, and explicitly says it is "already doing all of this"
  internally and needs an expert to take ownership rather than build from zero
  [vidalytics.com/career/ai-automation-engineer].
- No public engineering blog was found; Vidalytics' public writing is product/marketing-focused
  (the company blog covers feature releases, not engineering practice), so the only first-hand
  signal on how this team actually builds AI systems is the job posting itself.

## 7. Why-fit angles for Santiago

Best hook to lead with: this role is not "add AI to a product," it is "make a whole ~16-person
company operationally AI-native, starting with revenue teams, reporting straight to the CEO." That
is close to what Santiago has already built and owned at Pragma AI and Online Basics: internal
automations for quoting, reporting, onboarding, and collections at Pragma AI, and a company-wide
internal operations platform (pricing dashboard, inventory admin, discounting/ad-campaign tooling)
at Online Basics that ran a lean 7-person team to $8M in revenue
[resume/master_resume.yaml]. Vidalytics wants someone who has already made a small,
resource-constrained organization run on automation rather than headcount, which is exactly
Santiago's Family D (internal tooling) track record, not a hypothetical.

Concrete transferable evidence:
- Pragma AI's "Pragma Brain" is a direct match for the posting's central anti-hallucination
  requirement: scoped retrieval with deterministic no-answer and citation gating, an automated eval
  harness, and LLM-at-ingest sensitivity labeling, exactly the "ground outputs in company data" and
  "build evals and observability by default" asks in the posting
  [resume/master_resume.yaml; vidalytics.com/career/ai-automation-engineer].
- Pragma AI's internal operating platform (a hosted, authenticated MCP brain service, 15 agent
  definitions, 10 reusable routines, session hooks) is close in kind to the "agents, chains,
  reusable skills, cross-system automations" the posting asks for, and Santiago has daily,
  first-hand experience with Claude Code (the posting names Claude Code and Claude Cowork
  specifically) [resume/master_resume.yaml; vidalytics.com/career/ai-automation-engineer].
- Founder-level ownership and direct-to-CEO reporting is familiar territory: he ran Online Basics
  and Eugenia.ai end to end, including client-facing rollout, not just backend build
  [resume/master_resume.yaml].

Honest concerns and watch-outs:
- No martech or video-platform domain background. Santiago's automation experience is in
  e-commerce operations, PropTech, personal finance, and investment research, not marketing/sales
  tooling, video hosting, or the direct-response marketing world Vidalytics sells into. This is a
  real gap to name plainly rather than gloss over, since the posting explicitly wants someone
  "familiar with marketing, sales and customer success workflows."
- No named use of n8n or Zapier specifically in his background (his automation work is
  custom-coded Python/TypeScript pipelines and agent frameworks, not off-the-shelf workflow
  builders); worth being upfront that the underlying skill (wiring systems together reliably)
  transfers, but the specific tools do not have a track record yet.
- Employee-vs-contractor status and pay are both unverified (see verdict above); for a household
  budgeting on Mexico-based cost of living, this needs to be resolved early, not assumed.
- Company-risk flag: no public funding, and third-party revenue estimates (high six figures ARR as
  of late 2024) are small relative to typical VC-style hiring budgets. A ~16 to 18-person
  bootstrapped company hiring one senior engineer to report directly to the CEO is a real bet on a
  single hire; if that hire does not land, or if the founder's priorities shift, the role's scope
  could change quickly. This is worth naming as a risk, not a disqualifier, given the strong
  founder-led track record and profitability claims.

## 8. Application-question angles

- Why this company: lead with the operating-model match, not the video-marketing niche. Frame it
  as: Vidalytics is trying to do at company scale what Santiago has already done at team scale
  twice (Pragma AI's internal automations, Online Basics' internal ops platform), turn a small,
  resource-constrained team into one that runs on agents and automations instead of headcount, with
  a founder who wants to own that transformation directly rather than delegate it to a generic ops
  hire. Avoid restating video-conversion features Santiago has no real stake in; anchor on the
  "make the whole org AI native" mandate.
- Why you fit: point to the anti-hallucination framing specifically, since it is the one place the
  posting gets most concrete about what "good" looks like (grounding in company data, evals,
  observability, guardrails). Pragma Brain's deterministic no-answer and citation gating, plus the
  eval harness he built and iterated on when it over-fired, is a direct, honest answer to "how do
  you keep an AI system from being confidently wrong," not a hypothetical. Be candid that the
  vertical (direct-response marketing/martech) is new to him, and frame that as a fast learning
  curve on top of a proven pattern, not something to hide.
- Anything else: if it comes up, be straightforward that he is Mexico City based and will not
  relocate, note the timezone overlap is not actually a constraint (Mexico City is one hour behind
  Eastern), and ask directly whether the role is structured as employment or as a contractor
  engagement and what the pay range is, since neither is stated in the posting.

## Sources

- https://www.vidalytics.com/career/ai-automation-engineer (primary source, fetched directly:
  full job description, responsibilities, requirements, timezone-overlap wording, benefits
  language, reporting line to CEO, "Apply Now" liveness, sibling job listings)
- https://weworkremotely.com/remote-jobs/vidalytics-ai-automation-engineer-in-house-martech-video-saas
  (WWR mirror of this posting; blocked direct fetch with HTTP 403, so used via search-index
  snippets: "Region: Anywhere in the World," Full-Time, application deadline Aug 6 2026)
- https://weworkremotely.com/remote-jobs/vidalytics-europe-only-gtm-martech-engineer-growth-attribution-at-video-martech-saas
  and https://weworkremotely.com/remote-jobs/vidalytics-europe-only-ai-native-performance-marketing-manager-in-house-martech-video-saas
  (sibling requisitions explicitly tagged "[EUROPE ONLY]," used as corroboration that this specific
  role's lack of a country tag is a deliberate distinction, not an omission)
- https://www.linkedin.com/jobs/view/ai-automation-engineer-in-house-martech-video-saas-at-vidalytics-4436575959
  (LinkedIn mirror of the same posting: confirms active status, applicant count, CEO Patrick
  Stiles as job poster/contact)
- https://www.linkedin.com/company/vidalytics (headcount band 11-50, HQ Austin TX, founded 2016,
  privately held, industry classification)
- https://www.vidalytics.com/ (product description, core features, testimonials)
- https://www.vidalytics.com/ai-suite (AI Suite feature list, scale claims: 27,645+ marketers,
  200,000+ videos analyzed, $5.7B+ in tracked sales, $3.5B+ in tracked video revenue used for
  benchmarking)
- https://www.vidalytics.com/blog/4-2026-monthly-marketing-update (2025-2026 product release
  history: Vids AI, Vid Stats Funnel View, Experiments, Storybar, AI-Optimized Embed, Interactive
  Smart Vids)
- https://www.vidalytics.com/testimonials (named customers/testimonials: Frank Kern, Golden Tree
  Nutrition)
- https://help.vidalytics.com/en/articles/2928645-api-functions (public/advanced API description,
  used for business-model/product detail)
- https://www.starterstory.com/vidalytics-breakdown (founder story: founding year, bootstrapped
  status, personal debt during build, revenue figures as of Dec 2024, starting price point; third-
  party interview-based writeup, self-reported figures)
- https://getlatka.com/companies/vidalytics (third-party revenue/valuation estimate; flagged as
  unverified aggregator data)
- https://theorg.com/org/vidalytics/org-chart/patrick-stiles (leadership team names/titles: Patrick
  Stiles CEO, Erika Lehmann co-founder/Chief Strategic Operator, Dionis Lebedev Head of
  Engineering, Jackson Jeffries Head of Sales; team-size estimate)
- https://www.inspiredinsider.com/patrick-stiles-interview (founder background/personal story,
  public voice)
- https://himalayas.app/companies/vidalytics/tech-stack (third-party inferred tech stack; flagged
  as directional, not company-confirmed)
- https://www.glassdoor.com/Reviews/Employee-Review-Vidalytics-RVW53802209.htm and
  https://www.glassdoor.com/FAQ/Vidalytics-Question-FAQ200085-E1645156.htm (employee sentiment;
  very small sample, flagged as such)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (Santiago's location rule, comp rule, target
  role families)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience used
  for why-fit angles: Pragma AI internal automations and RAG "company brain," Online Basics
  internal operations platform, Eugenia.ai founder-led deployments)
