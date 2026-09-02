# PostHog

Draft dossier for Santiago's review. Not a final cover letter or answer set.

## 1. Snapshot

Open-source product analytics platform (now "the operating system for people who build
products": analytics, session replay, feature flags, a data warehouse, PostHog AI, PostHog
Code/Desktop) that has shipped into a broader product-development suite. Y Combinator W20.
Series E closed October 2025 ($75M, $1.4B post-money, led by Peak XV Partners), on top of a
June 2025 Series D ($70M at a $920M valuation, led by Stripe). Roughly $194M total raised.
Natively remote, distributed team of about 210-215 people across roughly 23 countries. HQ
registration in San Francisco but the company operates as fully distributed.
[posthog.com/careers](https://posthog.com/careers),
[technews180.com Series E](https://technews180.com/funding-news/posthog-raises-75m-series-e-reaches-unicorn-status/),
[posthog.com/blog/series-d](https://posthog.com/blog/series-d)

## 2. Core narrative

PostHog runs on radical, published transparency (a public handbook that includes how they pay
and let people go, open roadmap, GitHub-first communication) paired with a small-teams,
own-it-end-to-end operating model where engineers make product decisions with no PM layer.
That structure is why they deliberately recruit ex-founders: PostHog is explicitly built to let
someone who has run their own company keep doing that, on someone else's balance sheet, inside
a "startup within the startup." The current product bet, PostHog AI and PostHog
Code/Desktop, is an attempt to make the whole platform agent-operable: not just an
analytics tool a human reads, but infrastructure an AI agent can act on directly.
[posthog.com/handbook/company/culture](https://posthog.com/handbook/company/culture),
[Ashby posting: Technical Ex-Founder](https://jobs.ashbyhq.com/posthog/3a7e914b-a993-46e6-9029-6a0f54652497),
[posthog.com/blog/self-driving-product](https://posthog.com/blog/self-driving-product)

## 3. Mission & product

Started as open-source product analytics; has since shipped more than a dozen products onto one
platform: session replay, feature flags/experiments, a built-in data warehouse (query product
and customer data together with SQL), a customer data platform, error tracking, and PostHog AI
(an AI analyst that answers product questions, surfaces session recordings, writes SQL). The
newest bet is PostHog Code, since renamed PostHog Desktop: a desktop app running coding agents
that operate on a company's actual product data, not just its codebase, entering beta May 2026.
More than 450,000 organizations have installed PostHog, largely via word of mouth (up from the
"100,000+" figure quoted in the Technical Ex-Founder posting, which is likely the older number).
Roadmap next up: CRM, workflow, revenue analytics, and support products, i.e. becoming the
default "customer infrastructure" stack, not just an analytics tool.
[posthog.com/products](https://posthog.com/products) (referenced from job postings),
[posthog.com/blog/self-driving-product](https://posthog.com/blog/self-driving-product),
[Ashby: Product Engineer posting](https://jobs.ashbyhq.com/posthog/20ab9628-20ff-4ae3-bd6a-46ae7e9dc6b8)

## 4. Culture & voice

The handbook is the culture. Direct quotes:
- "Most of our communication happens publicly on GitHub, our roadmap is open for anyone to see,
  and our open-source handbook explains everything."
- "If given a choice, go live. If you can't go live, reduce the task size so you can."
- "Default to not asking for permission to do something if you are acting in the best interests
  of PostHog."
- "Everyone should help everyone else raise their game... We are direct about the quality of
  work."
- "We judge performance based on real outcomes, not hours spent in an office."

Job postings add the self-description: "product-led," "default alive" (revenue growing, raising
to accelerate not to survive), "as weird as possible" (their own examples: redesigning the
website a fifth time, shipping an "objectively unnecessary developer toy"). Tuesdays and
Thursdays are meeting-free, async is the default (PRs over Issues over Slack), and engineers
lead product teams with no separate PM function. Internally they share revenue, board notes, and
fundraising plans with the whole company.
[posthog.com/handbook/company/culture](https://posthog.com/handbook/company/culture),
[Ashby: Technical Ex-Founder posting](https://jobs.ashbyhq.com/posthog/3a7e914b-a993-46e6-9029-6a0f54652497)

## 5. Recent news (last ~12 months)

- **October 2025**: Series E, $75M at a $1.4B post-money valuation, led by Peak XV Partners.
  Unicorn status. [technews180.com](https://technews180.com/funding-news/posthog-raises-75m-series-e-reaches-unicorn-status/)
- **June 2025**: Series D, $70M at a $920M ("unicorn-adjacent") valuation, led by Stripe with YC,
  GV, and Formus Capital participating. Explicitly earmarked to fund expansion into support,
  sales, and marketing products. [posthog.com/blog/series-d](https://posthog.com/blog/series-d)
- **May 5, 2026**: PostHog Code enters beta (desktop app running coding agents against a
  company's live product data), later rebranded PostHog Desktop with a broader scope than code
  generation. [posthog.com/blog/self-driving-product](https://posthog.com/blog/self-driving-product)
- **2026 (year to date)**: publishing regularly on applied AI agent engineering, e.g. "8 learnings
  from 1 year of agents, PostHog AI"; headcount reported around 210-215.
  [posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai](https://posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai)

## 6. Engineering & AI direction

PostHog's current AI thesis is "self-driving product": the platform should be operable by
agents, not just observed by humans. Their May 2026 write-up lays out five building blocks they
engineer around: tools (atomic actions an agent can call, e.g. create an insight, read an event
taxonomy), skills (tool plus docs plus rules bundled into a playbook), signals (real product
metrics that trigger agent work), memory (context that stops an agent repeating itself), and
evaluation (checking a change actually moved the metric it targeted). PostHog AI itself is
described as an agent "built into PostHog that can access your data and setup via dozens of
tools and works in a loop until it achieves the task you give it": multi-step analyses, SQL
generation, feature-flag and experiment setup, error triage. The open requirement language in
the Product Engineer posting is explicit that this is now a baseline expectation, not a bonus:
"you've built things agents actually use... an API an agent can drive, an MCP server, evals,
docs written for a machine." Stack signals from postings: Python/Django on the backend,
TypeScript/React on the frontend, ClickHouse for the analytics core (a dedicated ClickHouse SRE
req exists), ship-fast small teams that own a product end to end including support and on-call.
[posthog.com/blog/self-driving-product](https://posthog.com/blog/self-driving-product),
[Ashby: Product Engineer posting](https://jobs.ashbyhq.com/posthog/20ab9628-20ff-4ae3-bd6a-46ae7e9dc6b8),
[posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai](https://posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai)

## 7. The two reqs: what each actually is, and location/comp verification

### Technical Ex-Founder (job id 4718)
The posting is explicit that this is not a fixed role: "This isn't a fixed role, by the way.
We'll work out the right team once we talk, and most technical ex-founders join us as Product
Engineers." The pitch is autonomy and ownership: "There are a ton of ex-founders who love
working at PostHog because they get to work autonomously and own a large set of problems. We're
still super early stage, and with each small team, it's a startup within itself, which means
defining a problem, talking to users, building a solution, and iterating on that." In practice
this reads as a sourcing funnel, not a distinct job: PostHog is fishing for people with founder
instincts and slotting the strongest ones into a Product Engineer seat on whichever small team
fits, rather than running a separate "ex-founder track" with its own career ladder. It suits
someone who wants to keep building hands-on (the posting explicitly frames it as staying
technical, not moving into a pure leadership or advisory seat).
[Ashby: Technical Ex-Founder](https://jobs.ashbyhq.com/posthog/3a7e914b-a993-46e6-9029-6a0f54652497)

### Product Engineer (job id 4717)
A concretely-scoped, full-stack, product-ownership role: own a feature end to end (idea, talking
to users, MVP in production, iteration, pricing), collaborate with design but ship UX yourself,
rotate through a weekly "Support hero" duty plus some on-call, and write your own docs. The
requirements section is the clearest signal in either posting: "You've built things agents
actually use... Side projects count," alongside "Experience taking a project from 0 to 1. You
might have led a project, been a founder previously, or built an impressive side project," and
"Full-stack experience... Python or similar, React or similar, something to do with big data is
a bonus." This is a substantive, well-defined req, not a funnel.
[Ashby: Product Engineer](https://jobs.ashbyhq.com/posthog/20ab9628-20ff-4ae3-bd6a-46ae7e9dc6b8)

### How they differ, and which to target
Both feed the same outcome for someone in Santiago's position: a former founder ends up as a
Product Engineer on a small team. Technical Ex-Founder is the door PostHog built specifically
for people like him (ran his own company, wants to keep shipping hands-on) and it is the more
distinctive, more on-narrative req to lead an application with. Product Engineer is the more
concretely scoped req and the safer one to point a resume/cover letter at, since its
requirements section maps almost line for line to his background (0-to-1 ownership, full-stack
Python/React, has actually built things for AI agents to use: an MCP server, an agent-driven
Claude Code toolset, evals, in Kairos and Pragma AI). Given they route to the same outcome,
applying to Product Engineer while foregrounding the ex-founder story in the cover letter
narrative captures the best of both; if PostHog's application system allows only one, Product
Engineer is the more defensible one to submit.

### Are the postings still live?
As of 2026-08-11, neither req appears in PostHog's live Ashby job-board API, which currently
lists 11 open roles (Technical Account Executive, two Backend Engineer reqs, Technical Account
Manager EMEA, AI Research Engineer, two Site Reliability Engineer reqs plus a ClickHouse SRE
req, BizOps Manager, Technical Customer Success Manager Americas, Business Development Lead
Americas), none of them "Technical Ex-Founder" or "Product Engineer."
[api.ashbyhq.com/posting-api/job-board/posthog](https://api.ashbyhq.com/posting-api/job-board/posthog)
(queried directly, 2026-08-11). The direct Ashby links for both reqs still resolve (HTTP 200)
but load as a generic client-rendered shell with no job-specific title in the page metadata,
which is consistent with a delisted or evergreen-but-currently-paused posting rather than an
actively promoted one. PostHog does maintain standing landing pages for both role archetypes at
posthog.com/careers/technical-ex-founder and posthog.com/careers/product-engineer (both return
HTTP 200), and the company has a track record of running "Technical Ex-Founder" as a rolling,
always-open req rather than a single hiring cycle, so this may simply mean the specific listing
snapshot changed, not that PostHog stopped wanting ex-founders. Bottom line: verify live status
by opening both links directly (and the two static careers pages) immediately before applying;
do not assume either is currently accepting applications off this dossier alone.

### Does PostHog hire from Mexico?
Location rule, quoted directly from both postings: "We are full-remote and globally distributed!
Our current team is distributed between GMT-8 and GMT+2 so we currently only hire in these
timezones." The handbook's hiring-process page is more specific: hiring is restricted to people
"physically based in GMT+2 through GMT-8" (with a documented exception for Bulgaria/Greece
during daylight savings), and by country, the only hard exclusions are US-sanctioned Cuba, Iran,
North Korea, and Syria. Mexico City sits at GMT-6, inside the GMT-8-to-GMT+2 band, so the
timezone rule does not exclude Santiago. Mexico is not named on either the hiring-process page or
the compensation page as a country PostHog has hired in before (their listed prior-hire examples
are Belgium, the US East and West coasts, Canada, Germany, the UK, Finland, Poland, and
Colombia), and it is not on the "no EOR" exceptions list (France, Italy, Sweden, Switzerland,
Iceland, Belgium, Luxembourg, Uruguay, Bolivia, Denmark, Brazil) either. That means Mexico's
employment mechanism (EOR vs local entity vs contractor) is genuinely unconfirmed from the public
handbook: it is not on any documented exclusion list, and the timezone rule clears it, but there
is no direct precedent quoted. This is worth a direct question early in the process rather than
an assumption either way.
[posthog.com/handbook/people/hiring-process](https://posthog.com/handbook/people/hiring-process)
(hard sanctions list, timezone rule, EOR exceptions, "23 countries" line, quoted directly)

### What would a Mexico-based hire be benchmarked at?
PostHog's compensation handbook publishes the actual formula: **Benchmark (role and level, US
San Francisco reference) x Level Modifier x Step Modifier**, then a location factor is applied.
The location factor methodology "based on GitLab's location factors," which are "based on cost
of market, not cost of living," pulling from ERI, Numbeo, Comptryx, Radford, Robert Half, and
Dice data. The floor is explicit: "We set a floor of 0.8 in the US, and 0.6 everywhere else, to
avoid creating huge disparities in pay if someone happens to live in an exceptionally low cost of
living country/state." Mexico is not given its own named factor in the public handbook text (no
number quoted for Mexico specifically), so the honest read is: pay is location-adjusted downward
from the US benchmark, with 0.6x as the published worldwide floor, and always paid in local
currency unless there is a specific reason not to. PostHog also states they "aim to review
compensation during the hiring process" if salary is the only blocker, and that for the
Technical Ex-Founder/Product Engineer level of role the company explicitly invites candidates to
run their own number via the public compensation calculator linked from both postings before
applying, since a Mexico factor was not extractable from the static handbook page. Given the
floor of 0.6x and a US benchmark for a mid-level product engineer role at a company of this
caliber plausibly in the low-to-mid six figures, a 0.6x floor on even a conservative US benchmark
clears his 70,000 USD/year floor by a wide margin, but this is an estimate from the published
formula, not a quoted figure, and should be confirmed with the actual calculator output before
treating it as fact.
[posthog.com/handbook/people/compensation](https://posthog.com/handbook/people/compensation)
(formula, floor, methodology, all quoted directly)

## 8. Why-fit angles for Santiago

Best hook to lead with: PostHog built the Technical Ex-Founder pipeline specifically for people
who ran their own company and want to keep shipping hands-on rather than move into pure
management, which is exactly Santiago's situation coming out of Online Basics and Eugenia.ai
(founded, built, and in Eugenia's case sold a product) and now Pragma AI (still building). The
Product Engineer requirements read almost like a checklist of his recent work: "you've built
things agents actually use, an API an agent can drive, an MCP server, evals, docs written for a
machine" maps directly to Kairos (an MCP server exposing 46 tools to both an in-app agent and
Claude Code) and Pragma AI's internal MCP brain service (per-operator tokens, 15 agent
definitions, an eval harness for the RAG pipeline). "Experience taking a project from 0 to 1...
led a project, been a founder previously" is close to a direct restatement of his resume summary.
Full-stack Python and React across Online Basics, Eugenia.ai, and Plutus covers their stated
stack.

Honest concerns and watch-outs:
- Mexico is not a country PostHog has publicly confirmed hiring in before; the hard exclusions
  and timezone rule clear him, but the employment mechanism there is unconfirmed and should be
  raised directly rather than assumed.
- Neither req currently appears on PostHog's live 11-job Ashby board as of 2026-08-11; both need
  a live-status check immediately before applying, since this dossier cannot confirm they are
  still accepting applications.
- The Product Engineer posting lists Django and TypeScript-React as "nice to have" and the
  matcher flagged Django as a missing skill; his production experience is Python/FastAPI and
  React/Node, not Django specifically, which is worth acknowledging rather than overclaiming.
- PostHog's bar and interview process are widely described (including by PostHog itself) as
  demanding; this is a high-signal, high-effort application, not a volume one.

## 9. Application-question angles

**Why this company**: Lead with the ex-founder-to-product-engineer pipeline, not the product
pitch. PostHog built a specific path for people who started a company and want to keep building
instead of managing, and that is the actual reason to apply here over a generic "great product
analytics company" answer. One sentence on the product (self-driving, agent-operable platform)
is enough context, not the opener.

**Why you fit**: Anchor on concrete, agent-facing build work, not a skills list. Kairos's MCP
server (46 tools shared by an in-app agent and Claude Code) and Pragma AI's MCP brain service
with an eval harness are direct answers to PostHog's own stated bar ("an API an agent can
drive... evals, docs written for a machine"). Pair with founding and running Online Basics or
Eugenia.ai for the 0-to-1 ownership piece PostHog explicitly screens for. Do not restate all four
research areas; two concrete build examples plus the founder background carry the answer.

**Anything else**: Good place to raise the Mexico employment question directly and plainly
(timezone clears him, country precedent does not) rather than let it surface later in the
process. Keep it factual: state he is Mexico City based, confirm the GMT-8 to GMT+2 window
covers Mexico City's GMT-6, and ask how PostHog structures pay and employment for a Mexico-based
hire, since the public handbook does not name Mexico either way.

## Sources

researched: 2026-08-11

- [posthog.com/careers](https://posthog.com/careers): current open-role list, headcount context, "startup within a startup" framing.
- [Ashby: Technical Ex-Founder posting](https://jobs.ashbyhq.com/posthog/3a7e914b-a993-46e6-9029-6a0f54652497): full job text (also pulled via `src.query job 4718`), role description, "not a fixed role" language, funding and product claims.
- [Ashby: Product Engineer posting](https://jobs.ashbyhq.com/posthog/20ab9628-20ff-4ae3-bd6a-46ae7e9dc6b8): full job text (also pulled via `src.query job 4717`), requirements, what-you'll-be-doing detail.
- [api.ashbyhq.com/posting-api/job-board/posthog](https://api.ashbyhq.com/posting-api/job-board/posthog): live job-board API, queried directly 2026-08-11, confirms current 11 listed roles and that neither target req is among them.
- [posthog.com/handbook/people/hiring-process](https://posthog.com/handbook/people/hiring-process): timezone rule (GMT+2 to GMT-8), sanctioned-country exclusions, no-EOR country list, prior-hire country examples, "23 countries" figure.
- [posthog.com/handbook/people/compensation](https://posthog.com/handbook/people/compensation): compensation formula (Benchmark x Level Modifier x Step Modifier), location-factor methodology (GitLab-style, cost of market), US floor 0.8 / worldwide floor 0.6, local-currency policy.
- [posthog.com/handbook/company/culture](https://posthog.com/handbook/company/culture): direct culture quotes (transparency, "go live," autonomy, direct feedback, outcomes over hours).
- [posthog.com/blog/self-driving-product](https://posthog.com/blog/self-driving-product): PostHog Code/Desktop beta (May 5, 2026), the five-part agent architecture (tools, skills, signals, memory, evaluation).
- [posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai](https://posthog.com/blog/8-learnings-from-1-year-of-agents-posthog-ai): PostHog AI agent description and engineering-blog AI theme.
- [posthog.com/blog/series-d](https://posthog.com/blog/series-d): Series D detail (June 2025, $70M, $920M valuation, led by Stripe) and Series C context.
- [technews180.com Series E writeup](https://technews180.com/funding-news/posthog-raises-75m-series-e-reaches-unicorn-status/): Series E detail (October 2025, $75M, $1.4B post-money, Peak XV Partners), unicorn status.
- Headcount (approx. 210-215 people, about 23 countries): cross-referenced from the hiring-process handbook page and general company-profile search results; treat the exact figure as approximate.
