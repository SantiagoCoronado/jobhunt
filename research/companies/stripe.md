# Stripe

Draft dossier for Santiago to review. Focused on local job id 15053, "Forward Deployed AI
Accelerator, Marketing" (findwork external id nKJwqdX). Do not confuse with the separate
Stripe "Fullstack Engineer, Privy" row in his pipeline, which is a different req and was marked
dead in a liveness check on 2026-08-11.

## 0. Req viability verdict (read this first)

**Not viable from Mexico as currently posted.** The live Stripe careers listing that matches
this exact title and description (job id 8055930, https://stripe.com/careers/listing/forward-deployed-ai-accelerator-marketing/8055930)
states, verbatim:

> "This role is available either in an office or a remote location (35+ miles or 56+ km from a
> Stripe office)."

Its office locations are Toronto and Chicago, and its remote options are listed explicitly as
"Remote in Canada, Remote in United States." Mexico and LATAM are not named anywhere on the
listing. The page also states an in-office expectation for office-assigned staff of "at least
50% of the time in a given month," and confirms the posting is currently open ("Apply now,"
application window open for 100 days from posting).

Stripe has run this same req title in at least three region-locked variants: this open one
(Toronto/Chicago, Remote in Canada or US, job id 8055930), a New York, NY variant (job id
7747636 per search index, page now returns "no longer accepting applications" per the Base10
job-board mirror), and a Singapore/Sydney variant (job id 7747638 per search index, also closed
per the Atomico job-board mirror). All three are hub-based (North America or APAC); none
mentions Mexico. The findwork aggregator page Santiago found lists the location simply as
"Remote" with no country called out, which is aggregator shorthand, not the actual posting
scope; the underlying Stripe page is US/Canada only.

**What to ask if he still wants to pursue this**: does Stripe's Marketing FDA program have (or
plan) a LATAM-scoped or Mexico-hireable cohort, given Stripe's existing Mexico City delivery
center. If applying anyway, treat this as a location-mismatch application (the profile's hard
rule caps roles like this) and confirm work authorization/remote-from-Mexico eligibility with a
recruiter before investing more time.

Sources for this section: stripe.com careers listing 8055930 (fetched 2026-08-11); Base10 and
Atomico job-board mirrors of the closed NY and Singapore/Sydney variants; findwork.dev listing
page for job 15053.

## 1. Snapshot

Stripe is a private financial infrastructure company (payments, billing, Connect marketplaces,
Radar fraud detection, Issuing, and a growing agentic-commerce product line), founded 2010 by
Patrick and John Collison. Dual headquarters: South San Francisco, California and, since October
2025, Dublin, Ireland. Processed USD 1.9 trillion in total payment volume in 2025 (up 34 percent
year over year) and was valued at USD 159 billion in a February 2026 employee tender offer; no
near-term IPO plans stated by leadership. Has an office in Mexico City (opened around its 2019
Mexico launch) that today runs as a "Stripe Delivery Center" for operations and support roles.

## 2. Core narrative

Stripe is applying its own "forward deployed" playbook, borrowed explicitly from Palantir's
external client-embedding model, but pointed inward: this req exists to embed AI builders
directly inside functional teams (starting with Marketing) so that building agents and
automations becomes every employee's default way of working, not a side skill. It is happening
in parallel with Stripe's public bet that AI agents, not just humans, will be the next class of
payer, reflected in the Agentic Commerce Suite and Machine Payments Protocol launched at
Sessions 2026.

## 3. Mission & product

Stripe builds financial infrastructure for businesses: payment acceptance (including local
methods like OXXO in Mexico), Billing for subscriptions, Connect for multi-sided marketplaces,
Radar for fraud detection, Sigma for analytics, and Issuing for card programs. Business model is
usage- and transaction-based fees. Stripe states it serves roughly half of the Fortune 100 and
operates across 160+ countries. Its 2026 product push (Sessions 2026, April 29) centers on
"agentic commerce": letting AI agents transact on a merchant's behalf via a new Agentic Commerce
Suite, a co-authored Machine Payments Protocol (with Tempo), an agent-enabled Link wallet, and
agent identity/guardrail controls, positioned as infrastructure built for machine payers, not
just human ones.

## 4. Culture & voice

Stripe's public voice is engineering- and infrastructure-forward: product launches are framed as
technical announcements (288 launches unveiled at Sessions 2026) rather than marketing copy, and
its "GDP of the internet" framing recurs across careers and newsroom pages. The company
explicitly measures internal AI adoption operationally: the FDA req states success is judged by
"the number of workflows you've permanently transformed" and "the extent to which those in your
group start any task with an AI tool," a metrics-first, systems-thinking tone consistent with
its broader engineering culture. Office-assigned staff are expected in-office roughly half the
month; Stripe Delivery Center roles (its Mexico City office) are 100 percent in-office, a
different arrangement from the mostly-remote-eligible tech and marketing organization.

## 5. Recent news (last ~12 months)

- **February 2026**: Stripe reached a USD 159 billion valuation in an employee/investor tender
  offer (Thrive Capital, Coatue, a16z among participants), up from USD 106.7 billion the prior
  year; total payment volume hit USD 1.9 trillion for 2025, up 34 percent year over year.
  (Bloomberg, CNBC, Stripe's own 2025 annual letter/tender announcement.)
- **April 29, 2026**: Stripe Sessions 2026 conference; company announced 288 product launches
  built around agentic commerce, including the Agentic Commerce Suite, Machine Payments Protocol,
  agent-enabled Link wallet, Issuing for Agents (preview), Stripe Console (an agentic execution
  environment in the Dashboard), Custom Radar Models, and Stripe MCP for exposing subscription
  metrics to AI agents. Partnerships with Meta and Google on agentic commerce were also announced.
- **October 2025**: Stripe opened a permanent European headquarters, One Wilton Park in Dublin.
- **Mid-2026** (exact date not confirmed by a primary Stripe source; press coverage dated around
  early August 2026): Stripe posted the "Forward Deployed AI Accelerator, Marketing" role family
  across multiple hub locations (Toronto/Chicago, New York, Singapore/Sydney), covered by
  business press as a new, Palantir-inspired internal AI-enablement job title.

## 6. Engineering & AI direction

Stripe's 2026 engineering narrative is building payment rails for AI agents as first-class
payers, not just humans: agent identity, scoped spending guardrails, approval flows, and
programmatic card issuance for agents are shipping as core platform features (Sessions 2026).
Internally, Stripe is also standing up AI-native tooling for its own dashboard and workflows
(Stripe Console, Dashboard Assistant, Custom Radar Models, Stripe Workflows GA) and exposing an
MCP (Model Context Protocol) surface for agents to query live business data. The FDA program
itself is an engineering-adjacent enablement function: FDAs are expected to build "custom tools,
agents, automations, and skills" for the marketers they support, using tools named in the
posting like Claude, Claude Code, Codex, and custom agent frameworks, but the reporting line and
success metrics sit inside Marketing, not an engineering org.

## 7. Why-fit angles for Santiago

**Best hook to lead with**: this req rewards someone who has already run the exact loop it
describes, building an internal AI tool for a specific team, watching them adopt it, and
generalizing the pattern to others, rather than someone learning AI enablement on the job. Two
real, verifiable examples: Pragma AI's "Pragma Brain" RAG system plus 15 agent definitions and
10 reusable routines that Pragma's own operators run day to day, and Online Basics' internal
operations platform (pricing dashboard, inventory tooling, alerting) used daily by a 4-person
operator team while scaling the business to USD 8M in revenue. Both are "embed with a small
group, build the tool, make it their default workflow" stories, which is precisely this role's
job description.

Secondary angle: Santiago is a former founder who has done client-facing and stakeholder-facing
technical work (Eugenia.ai on-site HOA/property-manager deployments, Pragma client diagnostics),
which maps to the req's coaching and cross-functional-communication requirements, not just the
building requirements.

**Honest concerns / watch-outs**:
- **Location is the real blocker.** The live req is scoped to Remote in Canada or Remote in the
  United States (office Toronto or Chicago); it does not list Mexico. Per the profile's hard
  location rule, a role that requires a US/Canada work location is a dealbreaker regardless of
  fit quality. This should be flagged to Santiago before any application effort goes further.
- No marketing-function experience on the resume (the req lists marketing background as
  "preferred," not required, but it is a real gap worth naming honestly).
- The role sits inside Marketing, reporting and success metrics included, not inside an
  engineering org; if Santiago wants to keep building toward engineering-titled roles, this one
  reads as pure Family B (enablement), not Family A or C/D.

## 8. Application-question angles

These lean on the Core narrative (Stripe pointing its own "forward deployed" playbook inward)
and should NOT be used until the location question above is resolved.

- **Why this company**: do not open by restating Stripe's mission back to them. If anything, one
  line on the specific mechanic Stripe is testing: applying a client-embedding model to an
  internal team and measuring success by workflows actually transformed, not tools trialed. That
  is a bet Santiago has already tested at Pragma AI at smaller scale.
- **Why you fit**: lead with the Pragma Brain and Online Basics tooling examples above, both are
  "small embedded group adopts a tool because it solved their actual problem" stories with real
  numbers attached (147 files and 1,429 passages for Pragma Brain's dogfood test, 4 operators
  running the Online Basics platform daily). Keep it concrete; do not summarize the req back to
  them.
- **Anything else**: this is the natural place to raise the location question directly rather
  than skip past it, since the posted req is US/Canada-scoped and he works from Mexico City. If
  he wants to keep the conversation open, name that constraint plainly and ask whether a
  Mexico-eligible cohort exists or is planned, rather than let a location mismatch surface later
  in the process.

## Sources

- researched: 2026-08-11
- https://stripe.com/careers/listing/forward-deployed-ai-accelerator-marketing/8055930 (the live, matching req: exact location text, office cities, remote-country scope, comp band, open/apply status)
- https://findwork.dev/nKJwqdX/forward-deployed-ai-accelerator-marketing-at-stripe (aggregator listing Santiago sourced job 15053 from; generic "Remote" location, links onward to WeWorkRemotely)
- https://careers.base10.vc/companies/stripe/jobs/72086621-forward-deployed-ai-accelerator-marketing (mirror of the closed New York, NY variant of this req; comp band USD 145,200-217,800; "no longer accepting applications")
- https://careers.atomico.com/companies/stripe/jobs/74658393-forward-deployed-ai-accelerator-marketing (mirror of the closed Singapore/Sydney variant of this req; comp band SGD 166,200-249,200; "no longer accepting applications")
- https://www.inc.com/kaylawebster/stripe-just-created-a-new-198000-marketing-job-and-its-borrowed-from-palantirs-playbook/91341489 and related press (Forbes/Moneywise/AOL/BizTech Weekly coverage found via search) for the Palantir-inspired framing and role context
- https://stripe.com/jobs/listing/operations-associate-new-grad-mexico/7544547 and https://stripe.com/jobs/listing/operations-associate-product-support-operations-cdmx/7813141 (Stripe Delivery Center Mexico City roles; 100 percent in-office, operations/support function, not engineering)
- https://stripe.com/newsroom/news/stripe-launches-mexico (Stripe's 2019 Mexico launch, Mexico City office origin, product suite made available to Mexican businesses)
- https://stripe.com/newsroom/news/stripe-2025-update and Bloomberg (https://www.bloomberg.com/news/articles/2026-02-24/stripe-hits-159-billion-valuation-as-payment-volume-soars) and CNBC (https://www.cnbc.com/2026/02/24/stripe-value-stock-sale-tender-offer.html) for February 2026 USD 159 billion tender-offer valuation and 2025 total payment volume
- https://stripe.com/newsroom/news/sessions-2026 and https://stripe.com/blog/everything-we-announced-at-sessions-2026 (Sessions 2026, April 29 2026, 288 launches, Agentic Commerce Suite, Machine Payments Protocol, Stripe Console, Stripe MCP, agent guardrails)
- Irish Post, https://www.irishpost.com/business/proudly-irish-financial-services-company-stripe-unveils-new-dublin-headquarters-299091 (October 2025 Dublin European headquarters opening)
- https://stripe.com/about (mission framing, product suite, company-scale figures)
