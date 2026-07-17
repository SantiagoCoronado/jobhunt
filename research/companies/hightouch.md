# Hightouch

Draft dossier for Santiago Coronado, prepared for job id 1947 (Software Engineer, AI Agents,
remote North America). Review before use, this is a first pass, not a final source of truth.

## 1. Snapshot

Hightouch is a San Francisco based Composable CDP and Agentic Marketing Platform: it activates
customer data directly from the warehouse (Snowflake, BigQuery, Redshift, Databricks) instead of
copying it into a walled garden, and now layers AI agents on top to research, decide, and execute
marketing campaigns. Founded in 2019 (YC S19) by ex-Segment engineers Tejas Manohar, Josh Curl,
and Kashish Gupta. Series D, raised $150M in April 2026 led by Goldman Sachs Alternatives and Bain
Capital Ventures at a $2.75B valuation, $322M total raised across six rounds. Crossed $100M ARR in
2025 with over 100% revenue growth in each of the past two years. Roughly 400 to 580 employees as
of mid-2026 depending on the tracker, remote-friendly with 5+ offices (San Francisco, NYC, London
and more). Named a Leader in the Gartner Magic Quadrant for Customer Data Platforms (first-time
inclusion, announced January 2026).
[Adweek funding recap](https://www.adweek.com/dealroom/hightouch-raised-322-million-across-six-rounds-heres-how-the-company-skyrocketed-to-a-275-billion-valuation/),
[PYMNTS Series D](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/),
[YC company page](https://www.ycombinator.com/companies/hightouch),
[Hightouch Gartner page](https://hightouch.com/gartner),
[Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).

## 2. Core narrative

Three Segment engineers who watched companies abandon their SaaS-siloed customer data for
Snowflake/BigQuery/Redshift built the tool to activate that centralized warehouse data instead of
re-copying it. That single architectural bet (warehouse-native, no data replication) took the
company through three re-brandings in six years: reverse ETL (2020) to Composable CDP (2022) to
Agentic Marketing Platform (2025) to "Agentic CDP" (June 2026), each time keeping the same
underlying insight (query the warehouse, act on the result) while pushing further up the stack
from moving data to deciding and acting on it with AI agents. The company's own framing: "the CDP
executes ideas, but it has never had one of its own."
[Contrary/Unusual product-market-fit history](https://www.unusual.vc/hightouchs-product-market-fit-journey/),
[Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp).

## 3. Mission & product

- Product suite: Composable CDP (warehouse-native identity resolution and audience building),
  Reverse ETL (sync warehouse data to 200+ SaaS destinations), AI Decisioning (reinforcement
  learning/contextual bandits that pick the best message, channel, timing, and frequency per
  customer, including whether to send at all), Hightouch Agents (AI agents that research
  opportunities, answer analytics questions, and draft/execute campaigns), plus Ad Studio,
  Lifecycle Studio, Content Assembly, Customer Studio, and Intelligence modules under the
  "Agentic Marketing Platform" (AMP) umbrella.
  [Hightouch homepage](https://hightouch.com/),
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning).
- Business model: enterprise SaaS, warehouse-native (customer's own Snowflake/BigQuery/Databricks
  stays the source of truth, no forced data copy), sold to marketing and data teams jointly.
  [Hightouch Gartner page](https://hightouch.com/gartner).
- Customers: enterprise brands including Domino's, Spotify, Aritzia, Cars.com, Ramp, PetSmart,
  Warner Music Group, Grammarly, DoorDash, DraftKings, WHOOP, Fundrise, and Accor Hotels, per the
  company's own materials and job posting. 1,000+ companies use the platform per Hightouch's site.
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004),
  [Hightouch homepage](https://hightouch.com/),
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning).
- Documented results: WHOOP +22% loyalty offer activation, PetSmart +10% cross-sell conversion and
  +52% new customer acquisition, Fundrise 4x increase in investments, Otrium -70% campaign launch
  time, Warner Music Group 1,000+ audiences managed and +200% engagement.
  [AI Decisioning product page](https://hightouch.com/platform/ai-decisioning),
  [Hightouch homepage](https://hightouch.com/).

## 4. Culture & voice

- Seven stated values: Forever Hungry (ambitious, celebrate wins but keep pushing), Kindness
  ("people who aren't kind aren't tolerated"), Efficient Execution (bias to speed, "most decisions
  are two-way doors"), Compassion, Impact Driven, Raising the Bar (talent and "slope over
  y-intercept" over credentials), Humility.
  [Hightouch careers page](https://hightouch.com/careers).
- Remote-friendly with 5+ physical offices (San Francisco, NYC, London and more); office perks
  include free weekday lunches and a $150/month commuter benefit; benefits include 100%
  employee/80% dependent health premiums, $100/month wellness stipend, flexible PTO, and 16/12
  weeks parental leave.
  [Hightouch careers page](https://hightouch.com/careers).
- Design/product philosophy leans on "craft over shortcuts": a 2025 product redesign write-up
  emphasizes sweating details, "hundreds of design explorations," and building products people
  "actually love to use," plus an explicit shift toward serving marketer (non-technical) users as
  the fastest-growing segment, not just data engineers.
  [Hightouch redesign 2025 blog post](https://hightouch.com/blog/hightouch-redesign-2025).
- No programming interview: the company states directly it does not run coding interviews because
  it considers them "low signal to noise," instead weighting product sense, system design, and
  values fit. Notable and worth internalizing before interviews.
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).

## 5. Recent news (last ~12 months)

- **June 10, 2025**: Hightouch named 2025 Databricks Retail and Consumer Goods ISV Partner of the
  Year at the Data + AI Summit.
  [Businesswire](https://www.businesswire.com/news/home/20250610695735/en/Hightouch-Awarded-2025-Databricks-Retail-and-Consumer-Goods-ISV-Partner-of-the-Year-at-Data-AI-Summit).
- **October 8, 2025**: Launched Smart Suppression inside AI Decisioning, predicting per-message
  incremental lift so marketers can suppress low-value or relationship-damaging sends instead of
  relying on static frequency caps.
  [Businesswire](https://www.businesswire.com/news/home/20251008017466/en/Hightouch-Launches-Smart-Suppression-to-Protect-Brand-Relationships-Without-Sacrificing-Conversions).
- **January 26/29, 2026**: Named a Leader (first-time inclusion) in the Gartner Magic Quadrant for
  Customer Data Platforms, credited to early leadership in warehouse-native/composable
  architecture.
  [Hightouch Gartner page](https://hightouch.com/gartner),
  [Businesswire](https://www.businesswire.com/news/home/20260129112125/en/Hightouch-Named-a-Leader-in-the-2025-Gartner-Magic-Quadrant-for-Customer-Data-Platforms).
- **April 27-29, 2026**: Raised $150M Series D led by Goldman Sachs Alternatives and Bain Capital
  Ventures at a $2.75B valuation (Iconiq, Sapphire, Amplify, YC, and The Trade Desk's TD7 also
  participated); over 100% revenue growth each of the past two years.
  [Businesswire](https://www.businesswire.com/news/home/20260427054567/en/Hightouch-Raises-$150-Million-to-Reinvent-How-Marketing-Works-Using-AI),
  [PYMNTS](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/).
- **Around the Series D**: launched "Hightouch Agents," pre-trained AI agents that answer
  marketing/analytics questions directly from warehouse data, surface audience/opportunity
  insights, and can execute actions like A/B tests and budget changes, explicitly compared by CMO
  Brian Kotlyar to how coding agents changed software engineering.
  [CMS Critic](https://cmscritic.com/hightouch-launches-high-performance-agents-to-help-marketers-move-10x-faster).
- **June 15, 2026**: Published "The Agentic CDP," repositioning the platform around three pillars:
  a long-running agent harness that investigates opportunities over hours without context loss, a
  composable context layer that reads data in place (warehouses, DAMs, Figma, Looker) via open
  standards including MCP rather than centralizing copies, and forward-deployed teams embedded
  with customers to build agent skills and guardrails. Landed the same week as competing "agentic
  CDP" moves from Databricks and a BlueConic acquisition, an active category fight right now.
  [Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp).

## 6. Engineering & AI direction

- Core stack (from current and recent Hightouch job postings, primary source): TypeScript across
  frontend and backend, React on the frontend, some Go in backend services, queueing/streaming
  infra referencing Kafka and Kinesis for distributed data-sync workloads.
  [Full Stack Product Engineer posting](https://job-boards.greenhouse.io/hightouch/jobs/4620430004).
- AI Decisioning's technical core is a documented, four-part public series: reinforcement learning
  as the foundation, multi-armed bandits for the explore/exploit tradeoff, and contextual bandits
  to personalize the decision using each customer's live and historical data, all connected back
  to the warehouse rather than a duplicated data store. Strong prep material before interviews.
  [Under the hood of AI Decisioning, part one](https://hightouch.com/blog/the-personalization-gap),
  [part two: reinforcement learning](https://hightouch.com/blog/rl-for-marketers),
  [part three: multi-armed bandits](https://hightouch.com/blog/mabs-for-marketers),
  [part four: contextual bandits](https://hightouch.com/blog/contextual-bandits-for-marketers).
- Org signal: Hightouch is actively hiring a cluster of AI-agent-adjacent roles alongside this one,
  including Engineering Manager for an "Agents" team, Forward Deployed AI Engineer, Forward
  Deployed Marketing Data Scientist, and AI Implementation Manager/Strategy Consultant roles that
  sit between the AI Decisioning/Agents product and individual enterprise customers. This is a
  company actively building both the agent product and the forward-deployed motion to make it
  work for real customers, not just a research team.
  [Job search aggregation, multiple postings confirmed live](https://www.ycombinator.com/companies/hightouch/jobs/kIoY0yH-machine-learning-engineer-ai-decisioning).
- This role's own scope (primary source, JD): rapid POCs on integrating AI into data/marketing
  workflows, architecting production LLM pipelines, choosing AI architecture/frameworks, and
  building production "data agents" that answer analytics/data-science questions against a
  customer's actual warehouse data. Explicitly senior-scoped by impact/potential rather than years
  of experience, salary band $180,000 to $400,000 USD, location-independent (remote-first).
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).
- Interview process is notably non-standard: no coding interview. Recruiter screen, a System
  Design Screen (design a data processing feature end to end), a Hiring Manager interview on
  values/operating fit, and a 75-minute Agent Building Systems interview to architect an agentic
  system at a conceptual level against product and customer requirements.
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).

## 7. Why-fit angles for Santiago

Lead hook: **he has already run the "forward-deployed AI builder on top of a client's own data"
motion Hightouch is scaling into an org chart.** Pragma AI's flagship product, "Pragma Brain," is a
RAG system that ingests a company's internal data to answer questions and auto-generate business
reports for SMB clients, essentially AI Decisioning's job (turn a customer's own data into
answers and actions) done manually, one client at a time, which is exactly the gap Hightouch is
now hiring Forward Deployed AI Engineers and AI Implementation roles to fill at enterprise scale.
He can speak concretely to what breaks when you try to make an LLM/agent reliably reason over a
specific company's messy real data, because he has done it repeatedly as both the engineer and the
client-facing owner.

Second hook: **production LLM pipelines shipped end to end, not demos.** At Online Basics he
designed and ran an LLM workflow on the Anthropic and OpenAI APIs with custom prompt engineering
and a multi-stage validation pipeline generating 100+ product listings a month in production,
which maps directly onto this role's "architect production LLM pipelines" and "rapidly prototype
then productionize" mandate. His current build, Plutus, pairs an LLM research agent (drafts memos,
converts natural language into backtestable rules) with an MCP control plane, the same protocol
Hightouch names as part of its new composable context layer, so he can speak the same technical
language the team is using in its own recent blog post.

Third hook (secondary, use if data-pipeline depth comes up): Online Basics also involved building
a cloud microservices architecture orchestrating 10+ third-party APIs to process 100K+ daily data
points with hourly sync, real ETL-adjacent, warehouse-thinking work that is close in kind (not
scale) to what Hightouch's core product does.

Honest gaps and watch-outs:
- No marketing/martech domain experience specifically (email/SMS lifecycle marketing, ad
  platforms, CDP category). His data-pipeline and AI-agent experience is real, but the vertical is
  new; be ready to say that plainly and pivot to transferable pattern-recognition rather than
  claiming martech background he doesn't have.
- No hands-on reinforcement learning or bandit-algorithm experience; his LLM/agent work is
  prompt-engineering, RAG, and tool-use/function-calling, not RL. AI Decisioning's core (bandits,
  RL) is a different ML discipline from the LLM-agent work the JD itself emphasizes (data agents,
  LLM pipelines), so this is likely a smaller gap than it first looks, but worth acknowledging
  directly rather than glossing over given how central RL is to Hightouch's other flagship product.
- Scale mismatch: Hightouch runs at enterprise/$100M-ARR/400-580-employee scale with named Fortune
  500-adjacent customers (Spotify, Domino's, Ramp), versus his own founder-scale companies (lean
  9-person team, $8M revenue; 20+ B2B buildings). Frame as "built and owned things end to end at a
  smaller scale" rather than overclaiming enterprise-scale systems experience.
- No stated visa sponsorship in the posting; role is explicitly remote-first and
  "location-independent" in pay, and Santiago is TN-visa eligible (not a US citizen), so this
  should be a non-issue for a remote-from-Mexico arrangement, but confirm during the recruiter
  screen that "remote North America" genuinely includes Mexico and does not require US work
  authorization or E-Verify (the posting's E-Verify clause applies post-hire to actual US
  employees, not universally, but worth a direct question).
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).
- Only one Hightouch application allowed; the posting states candidates who apply to multiple
  Hightouch roles are auto-rejected, so this needs to be the single best-fit role, not a hedge.
  [Job posting](https://job-boards.greenhouse.io/hightouch/jobs/5542602004).

## 8. Application-question angles

- **Why this company**: do not lead with "CDP" or "reverse ETL," those are means, not the story.
  Lead with the founder narrative: three Segment engineers who watched the industry move its
  source of truth to the warehouse, built the tool to activate it there instead of copying it
  again, and have re-invented that same bet three times (reverse ETL, Composable CDP, AI
  Decisioning, Agentic CDP) as the ceiling of "warehouse-native" kept rising. Naming the June 2026
  Agentic CDP repositioning and its forward-deployed-teams pillar shows he is tracking the company
  in real time, not reciting an "About" page.
- **Why you fit**: anchor on the Pragma Brain/RAG-for-client-data pattern being the same job
  Hightouch's AI Decisioning and forward-deployed roles do at enterprise scale: turn one company's
  specific, messy data into reliable answers and actions for a non-technical end user (an SMB
  client vs. a lifecycle marketer). Pair it with the Online Basics production LLM pipeline as proof
  he can take a prototype to something running unattended in production, directly answering the
  role's "rapidly prototype AND architect production LLM pipelines" framing.
- **Anything else**: be upfront that he is new to martech/lifecycle-marketing as a vertical and to
  RL/bandit algorithms specifically, and reframe both as fast-learning surface area rather than
  hiding them, given the interview process itself explicitly says it weighs product sense and
  growth potential over credentialed years of experience. Worth also naming, briefly, that this is
  his one Hightouch application given their one-application policy, so it should read as a
  considered, specific choice.

## 9. Sources

- [Job posting: Software Engineer, AI Agents](https://job-boards.greenhouse.io/hightouch/jobs/5542602004), full JD text, interview process, comp band, company description.
- Internal: `.venv/bin/python -m src.query job 1947` (jobhunt DB), canonical stored JD and metadata.
- [Adweek: Hightouch funding history](https://www.adweek.com/dealroom/hightouch-raised-322-million-across-six-rounds-heres-how-the-company-skyrocketed-to-a-275-billion-valuation/), round-by-round funding and valuation table (used for round data only, its founding-year/origin claims were superseded by YC/founder sources below).
- [PYMNTS: Hightouch valued at $2.75B](https://www.pymnts.com/news/investment-tracker/2026/hightouch-valued-at-2-75-billion-as-ai-agents-transform-enterprise-marketing/), Series D date, amount, valuation, growth rate, founder/investor quotes.
- [Businesswire: Hightouch Raises $150M Series D](https://www.businesswire.com/news/home/20260427054567/en/Hightouch-Raises-$150-Million-to-Reinvent-How-Marketing-Works-Using-AI), Series D announcement.
- [Businesswire: Smart Suppression launch](https://www.businesswire.com/news/home/20251008017466/en/Hightouch-Launches-Smart-Suppression-to-Protect-Brand-Relationships-Without-Sacrificing-Conversions), Oct 2025 product launch detail.
- [Businesswire: Gartner Leader announcement](https://www.businesswire.com/news/home/20260129112125/en/Hightouch-Named-a-Leader-in-the-2025-Gartner-Magic-Quadrant-for-Customer-Data-Platforms), Gartner recognition date/detail.
- [Businesswire: Databricks ISV Partner of the Year](https://www.businesswire.com/news/home/20250610695735/en/Hightouch-Awarded-2025-Databricks-Retail-and-Consumer-Goods-ISV-Partner-of-the-Year-at-Data-AI-Summit), June 2025 partner award.
- [CMS Critic: Hightouch Agents launch](https://cmscritic.com/hightouch-launches-high-performance-agents-to-help-marketers-move-10x-faster), Hightouch Agents product detail and CMO quote.
- [Hightouch: The next chapter, Agentic CDP](https://hightouch.com/blog/the-agentic-cdp), June 15 2026 repositioning, three architecture pillars, founder quote.
- [Hightouch homepage](https://hightouch.com/), product suite, customer logos, headline metrics.
- [Hightouch: AI Decisioning product page](https://hightouch.com/platform/ai-decisioning), product mechanics and customer results.
- [Hightouch: Gartner recognition page](https://hightouch.com/gartner), Leader status, date, rationale.
- [Hightouch: careers page](https://hightouch.com/careers), seven values, remote/office policy, benefits.
- [Hightouch: 2025 redesign blog post](https://hightouch.com/blog/hightouch-redesign-2025), product/design culture and philosophy.
- [Hightouch: Under the hood of AI Decisioning series](https://hightouch.com/blog/the-personalization-gap) (parts two through four linked inline), RL/bandit technical detail for interview prep.
- [YC company page: Hightouch](https://www.ycombinator.com/companies/hightouch), founding year, batch (S19), founders, one-line description.
- [Y Combinator jobs: ML Engineer, AI Decisioning](https://www.ycombinator.com/companies/hightouch/jobs/kIoY0yH-machine-learning-engineer-ai-decisioning), confirms parallel AI-team hiring (used as evidence of org build-out, not quoted directly).
- [Full Stack Product Engineer posting](https://job-boards.greenhouse.io/hightouch/jobs/4620430004), tech stack (TypeScript, React, Go, Kafka/Kinesis) and separate interview loop for comparison.
- [Unusual VC: Hightouch's product-market-fit journey](https://www.unusual.vc/hightouchs-product-market-fit-journey/), founding story, original pivot from customer-dashboard idea to reverse ETL.

researched: 2026-07-14

---
Draft prepared for Santiago's review; verify anything time-sensitive (funding stage, headcount,
open-role list, exact Gartner report year label) before relying on it in an interview.
