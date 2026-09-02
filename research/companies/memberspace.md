# MemberSpace

Draft dossier for Santiago's review. Researched 2026-08-11. Built for the "Senior React Developer"
req (local job id 17454, duplicate row id 18227, same canonical role).

## 1. Snapshot

MemberSpace is a bootstrapped, profitable SaaS that adds membership and paywall functionality to
any website (Squarespace, Wix, Webflow, WordPress, Showit, and more). Founded 2015, HQ Hoboken NJ,
100% remote team of 10 to 11 people. Took mentorship-oriented investment from Earnest Capital
(now Calm Company Fund) at some point after launch, but describes itself as bootstrapped and
profitable, not venture-scaled. [memberspace.com/jobs, weworkremotely.com/company/memberspace,
calmfund.com]

## 2. Core narrative

MemberSpace has stayed deliberately small and calm for over 10 years: no big raise, a 10 to 11
person team, a stated value of "Work Calmly," unlimited PTO, uncapped profit sharing, and a
6-week Shape Up-style cycle where every engineer owns a feature end to end and is expected to
push back on product ideas, not just implement them. The company writes this into its own job
posts ("we're a small company so there won't be as much structure and process as at larger
companies... you'll need to be a self-starter"). This is the story to lean into: a founder-minded
engineer who is comfortable owning ambiguous scope, not a specialist who wants a big platform
team around them. [memberspace.com/jobs/senior-react-developer/, weworkremotely.com/company/memberspace]

## 3. Mission & product

MemberSpace's product is a membership layer that bolts onto an existing website (rather than
requiring customers to migrate CMS). Customers are largely non-technical creators, coaches,
educators, and entrepreneurs who want to sell memberships, courses, or community access without
building their own paywall infrastructure. The company states it has helped over 10,000
businesses generate over $350 million in revenue through their membership communities (customer
revenue, not MemberSpace's own). Business model is SaaS subscription; exact pricing tiers were not
verified in this pass. [memberspace.com/about, calmfund.com/writing/why-we-invested-in-memberspace]

## 4. Culture & voice

Stated values: Act Kindly, Value Craftsmanship, Stay Curious, Work Calmly, Create Space.
Repeated language across the careers page and job posts: "low-stress and calm company," "very
few meetings," encouragement to work under 40 hours a week, mostly-asynchronous communication.
Hiring is hands-on and small-team: candidates interview directly with the CEO (Ward) and CTO
(Ryan), get a paid technical project, then a technical interview with a senior developer and the
CTO. No large PR/marketing voice was found beyond the product blog and standard social channels
(YouTube, Instagram, TikTok, LinkedIn); the public voice is calm and product-support-led rather
than irreverent or high-volume. [memberspace.com/about, weworkremotely.com/company/memberspace,
memberspace.com/jobs/senior-react-developer/]

## 5. Recent news (last ~12 months)

- 2026-02-06: Shipped "Comments & Reactions," letting members discuss and react directly on
  protected content instead of relying on third-party tools. [memberspace.com/blog/add-conversation-to-content-with-comments-and-reactions]
- 2025-10-06: Reworked the Member Menu (renamed, improved notifications, search, bookmarks) to
  make member-facing navigation and content management smoother. [memberspace.com/blog/notifications-search-bookmarks-and-more]
- 2026-08-05/06: Opened this Senior React Developer req on We Work Remotely as a paid "Boosted /
  Featured" listing, first time this specific stack (Vite, Storybook, Semaphore-CI, Render,
  CloudFlare) shows up in a MemberSpace posting, versus an older, now-closed Senior React
  Developer req on their own site that ran on Heroku/MongoDB. This reads as a refreshed front-end
  platform, not a new team or new leadership. [weworkremotely.com/remote-jobs/memberspace-senior-react-developer,
  memberspace.com/jobs/senior-react-developer/]

No funding round, leadership change, or layoff was found in this window. No traditional VC
funding round exists to report; the company self-describes as bootstrapped and profitable.

## 6. Engineering & AI direction

Current stack per the live posting: React & ES6, TypeScript, Vite, Storybook, Cypress (frontend);
Ruby on Rails, PostgreSQL, Redis (backend); AWS, Render, AWS S3, CloudFlare (infra); GitHub, Yarn
workspaces, Swagger, Semaphore-CI (tooling). Frontend and backend are separate concerns: a React/
TypeScript SPA-style frontend team integrating with a Rails API over REST, documented with
Swagger. Development process is explicitly Shape Up-inspired: 6-week cycles, a cooldown period
after each cycle for tech debt and modernization, engineers own features from technical planning
through code review and deployment. On AI: the posting says "we expect you to use AI tools
thoughtfully to ship faster... while trusting your judgment on which tools to use and when not
to," which signals AI-assisted coding is expected and normalized, not a dedicated AI product
initiative. No public engineering blog was found; product-facing blog posts are support/marketing
oriented, not technical. [weworkremotely.com/remote-jobs/memberspace-senior-react-developer,
findwork.dev/QGBPR8n/senior-react-developer-at-memberspace]

## 7. Why-fit angles for Santiago

**Lead hook:** frontend React/TypeScript is one of Santiago's two strongest positions, and this
role is almost entirely React/TypeScript ownership (UI, component architecture, state,
performance) integrating with a Rails backend over REST, which is exactly the shape of his
Eugenia.ai and Hydrel work (React front end, Node/Rails-style backend he did not own, REST
integration).

- React 18/19 + TypeScript production work across three recent builds: Plutus (Vite, Tailwind,
  11 routes, 45+ components), the Hydrel client portal (~30,000 lines of React + TypeScript,
  Radix UI design system, Vitest and Playwright test suites), and Eugenia.ai (React front end,
  Node.js backend on AWS, 10,000+ users). Matches MemberSpace's "own your front-end features
  start to finish" expectation directly.
- REST API integration with a backend he did not build (Node/Rails style) is proven at Eugenia.ai
  and Hydrel, matching the "collaborate with Rails developers to design and integrate with APIs"
  responsibility here.
- Founder background (Eugenia.ai, Online Basics, Pragma AI) maps onto MemberSpace's explicit ask
  for engineers who "think strategically about the product," push back on ideas respectfully, and
  self-direct in a small, low-structure team. This is a real overlap, not a generic claim: he ran
  full product lifecycles solo and with small teams (9 people at Online Basics).

**Honest gaps and watch-outs:**

- No hands-on Cypress or Storybook experience on the master resume (he uses Playwright and Vitest
  instead); no direct Ruby on Rails experience. Both are named as missing by the job-matcher scan.
  Reasonable to address by naming the Playwright/Vitest equivalent and REST-API collaboration
  experience rather than claiming the exact tools.
- Employment classification for a non-US hire is not stated anywhere in the posting. The listing
  explicitly scopes "Unlimited PTO" and "4% matching 401(k)" to "USA-only employees," which is a
  real signal (not proof) that a Mexico-based hire may land on a different arrangement, most
  likely a contractor agreement rather than the same employee package. Per Santiago's comp rule,
  a contractor rate must clear the equivalent employee salary, not just be tax-grossed-up from it.
  This needs a direct question early in the process, not an assumption either way.
- No compensation figure is stated on the current live posting ("competitive salary based on
  experience"). An older, now-closed Senior React Developer req on MemberSpace's own site (same
  title, older stack, presumably a prior hiring round at the same company) listed $100,000 to
  $120,000 plus uncapped profit sharing for a USA-based hire. That is a useful comp data point for
  this company and role family, but it is not a confirmed figure for the current req.
- MemberSpace's own careers page (memberspace.com/jobs/) currently lists only three closed roles
  (Customer Success Manager, Senior Designer, Senior Rails Developer) and does not list this
  Senior React Developer opening at all, even as closed. The req is live and currently the only
  active listing on We Work Remotely, shown as a paid "Boosted / Featured" post 6 days old as of
  research date, with a structured country-eligibility field that explicitly includes Mexico
  alongside Argentina, Brazil, Canada, Chile, Colombia, the United States, and Uruguay. Treat the
  posting as live based on the WWR/findwork evidence, but this discrepancy with the company's own
  site is worth a quick sanity check before or during application (e.g. confirm the req is still
  open when applying).

## 8. Location scope: verified

The live posting's own text states: "Full-time Senior React Developer who mostly overlaps with
our core working hours of 10am to 6pm ET, Monday to Friday. Based in the Western Hemisphere
(ideally USA)." This is a requirement, not a preference framed as a requirement; "ideally USA"
signals a preference within an already-broader hemisphere requirement, not a hard USA-only rule.
[weworkremotely.com/remote-jobs/memberspace-senior-react-developer, verbatim copy also on
findwork.dev/QGBPR8n/senior-react-developer-at-memberspace]

This is corroborated by a structured field, not just prose: We Work Remotely's own company page
lists this exact listing with explicit country-eligibility flags: Argentina, Brazil, Canada,
Chile, Colombia, Mexico, United States of America, Uruguay. Mexico is explicitly named as an
eligible country in WWR's structured data, independent of the free-text description.
[weworkremotely.com/company/memberspace]

Mexico City is GMT-6 (CST), one hour behind ET. Full overlap with 10am to 6pm ET is a one-hour
shift, not a real scheduling obstacle.

Posting status: live as of 2026-08-11. It is the only active MemberSpace listing on We Work
Remotely, posted/boosted 6 days prior to research date (consistent with the discover pipeline's
first-seen date of 2026-08-05/06). It is not currently listed on MemberSpace's own careers page
(see watch-outs above), which is worth a light sanity check but is not, on its own, evidence the
req has closed.

## 9. Application-question angles

- **Why this company:** lean on the "own a feature end to end in a small, low-meeting, calm
  team" narrative, tied to his founder background of shipping product solo or with a small team,
  not a generic "I love your mission" line.
- **Why you fit:** lead with concrete React/TypeScript production work (Plutus, Hydrel, Eugenia.ai)
  and REST-API collaboration with a backend he didn't own, since that is literally the day-to-day
  of this role. Keep it to the 1 to 2 strongest examples, not a tour of the whole resume.
- **Anything else:** if useful, note Mexico City remote with a one-hour ET overlap and TN-visa
  eligibility for any US travel, stated plainly and briefly, not as a selling point.

## 10. Sources

- researched: 2026-08-11
- https://weworkremotely.com/remote-jobs/memberspace-senior-react-developer (accessed via r.jina.ai text proxy; direct fetch returned 403) - full job text, verbatim location and salary language, tech stack, benefits
- https://weworkremotely.com/company/memberspace (accessed via r.jina.ai text proxy) - structured job listing card with posted date (6 days ago), Full-Time tag, "$100,000 or more USD" salary band, and explicit country-eligibility flags including Mexico; company profile (size 1-10, established 2015, 10+ years remote), values, hiring process
- https://findwork.dev/QGBPR8n/senior-react-developer-at-memberspace - mirrors the same job text verbatim, "Date listed: 5 days ago" at fetch time, employee count 1-10
- https://www.memberspace.com/jobs/senior-react-developer/ - MemberSpace's own careers page for an older, now-CLOSED Senior React Developer req (different, older stack: MongoDB/Heroku); confirms $100,000-$120,000 plus uncapped profit sharing salary range and 11-person team size for that earlier round; also confirms this exact req is not currently listed on the company's own site
- https://www.memberspace.com/jobs/ - current MemberSpace careers index, lists only 3 closed roles (Customer Success Manager, Senior Designer, Senior Rails Developer), Senior React Developer not present
- https://www.memberspace.com/about/ - mission statement, stated values, "10,000 businesses... over $350 million in revenue" claim
- https://calmfund.com/writing/why-we-invested-in-memberspace (accessed via r.jina.ai text proxy) - primary source confirming Earnest Capital / Calm Company Fund investment, "profitable on a team of nine full-time employees" at time of investment, no exact date found
- https://saasclub.io/podcast/memberspace-bootstrapping-a-profitable-saas-company/ - founder story (Ryan Bennick, Ward Sandler; met in enterprise sales; self-taught coding around 2010; agency-to-SaaS origin); used for founder context only, not for the investment date
- https://www.memberspace.com/blog/add-conversation-to-content-with-comments-and-reactions/ - dated 2026-02-06, Comments & Reactions launch
- https://www.memberspace.com/blog/notifications-search-bookmarks-and-more/ - dated 2025-10-06, Member Menu redesign
- Internal: `.venv/bin/python -m src.query job 17454` and `job 18227` - canonical job description text and posting metadata used to verify the aggregator copy against the live sources above
