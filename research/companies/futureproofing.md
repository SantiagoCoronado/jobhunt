# FutureProofing

*Draft dossier for Santiago's review. Researched: 2026-07-03. A note on ambiguity: "FutureProofing"
is a generic-sounding name shared by several unrelated companies (an insurtech "FutureProof
Technologies," a marketing-AI "Futureproof" owned by Blend, etc). This dossier is specifically
about the talent-placement startup at futureproofing.dev, the company behind the Get on Board
posting for "Applied AI Full-Stack Engineer."

## 1. Snapshot

FutureProofing is a very early-stage (2-10 employees, LinkedIn lists 4) talent platform that
vets senior AI engineers, mostly LATAM-based, and embeds them into US startups (fintech,
biotech, healthtech, insurtech, legal tech) for production AI work. Fully remote, no confirmed
HQ address. No public funding round found; appears to be self-funded or backed informally
through co-founder Jess Mah's venture studio Mahway rather than institutionally financed.

## 2. Core narrative

FutureProofing's pitch is selectivity over volume, applied to AI engineering staffing: 12 of
about 2,000 engineers screened monthly pass their five-stage "HackerEval" gate, and the ones who
do get embedded with client startups within about 3 weeks. The founders (serial operators Jess
Mah and Andrea Barrica, who scaled inDinero together from age 19/20) frame this as "the
selectivity lens we built at Mahway, applied to engineer vetting." Their proof point is a public
case study of one of their engineers shipping a citation-backed, production RAG pipeline over
4,000 clinical guidelines in 11 days using Claude Code, exercising judgment to reject several
AI-generated suggestions along the way. That is the story worth leaning into: this is a company
that markets itself on engineers who ship fast in production with AI tools while keeping their
own judgment in the loop, not engineers who defer to the model.

## 3. Mission & product

- Business model: staffing/placement, not a SaaS product. FutureProofing sources, vets, and
  embeds senior AI engineers (mostly LATAM) with US client companies, positioned as cheaper and
  faster than a US in-house senior hire (they cite roughly $13.5K/month all-in for an embedded
  engineer vs $24K+ for a US in-house hire) and without equity or recruiter fees.
  (https://www.futureproofing.dev/)
- Customers: Series A-B startups, some seed-stage and PE-backed firms, spanning fintech,
  biotech/healthtech, insurtech, legal tech, dev-tools, and "next-gen infrastructure."
  (https://www.futureproofing.dev/, https://www.futureproofing.dev/engineers)
- Vetting process ("HackerEval"): initial screen, technical assessment, EQ/behavioral round,
  paired AI challenge, and a final interview; marketed as a roughly 1-in-166 acceptance rate
  (12 of ~2,000 screened monthly). (https://www.futureproofing.dev/)
- The job itself (Applied AI Full-Stack Engineer, posted via Get on Board): build and ship MVPs
  from concept to production, work hands-on with LLMs, APIs, and AI-assisted workflows, use tools
  like Copilot, Cursor, GPT, and Claude daily, deliver AI features for client startups in fintech,
  biotech, and infrastructure. Requirements: 5+ years shipping production products, JavaScript
  (React/Node) and/or Python, full-stack comfort, active AI product experimentation, an
  autonomous/detail-oriented builder mindset. Listed as senior level, fully remote (work from
  anywhere), with US time-zone overlap expected; explicitly described as part-time/project-based
  engagement rather than confirmed full-time W2 employment. No salary listed. Posted March 16,
  2026; 313 applications at time of research.
  (https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote)

## 4. Culture & voice

- Founders: Jess Mah (co-founder, previously founded inDinero at 19, UC Berkeley CS, Forbes 30
  Under 30, and founded venture studio Mahway in 2023) and Andrea Barrica (co-founded inDinero at
  20, Y Combinator 2010 alum, former Venture Partner/EIR at 500 Startups, founder of O.school).
  Gabe Murillo (co-founder) has a 15+ year talent-acquisition background, including building
  sourcing at Shopify Logistics. (https://www.futureproofing.dev/)
- Voice: confident, operator-to-operator, selectivity as a badge ("we've made the mistakes so
  you don't have to," "invitation-only," positioning against Toptal/Turing/Andela as more
  selective and production-focused). Blog content is almost entirely about hiring philosophy,
  vetting rigor, and LATAM AI-talent economics rather than product marketing.
  (https://www.futureproofing.dev/blog,
  https://www.futureproofing.dev/blog/mahway-playbook-engineering-hiring)
- Because the actual day-to-day work happens embedded inside a client startup, the lived culture
  for an engineer in this role will largely be set by whichever client team they land with, not
  by FutureProofing itself. FutureProofing describes its own contribution as "The FutureProofing
  Way," a remote operating system for communication cadence and delivery standards, but this is
  thin on public specifics. (LinkedIn company page,
  https://www.linkedin.com/company/futureproofing-dev)

## 5. Recent news (last ~12 months, dated)

- Apr 30, 2026: Published a case study, "Claude Code Case Study: Production RAG in 11 Days,"
  detailing an embedded engineer shipping a citation-backed RAG system over 4,000 clinical
  guideline documents for a healthcare AI client using Claude Code (20x/Max tier), hitting 87%
  on an internal eval suite against an 80% target.
  (https://www.futureproofing.dev/blog/claude-code-production-rag-case-study)
- Apr 29, 2026: Published "FutureProofing AI Talent Index, Q2 2026," a report on US AI engineer
  rates by stack and seniority. (https://www.futureproofing.dev/blog)
- Apr 30, 2026: Published "Embedded AI Engineer vs FTE: The 12-Month Total Cost of Ownership,"
  a pricing/positioning post comparing embedded-engineer cost to a full-time US hire.
  (https://www.futureproofing.dev/blog)
- May 6, 2026: Published two posts tying the "Mahway playbook" (co-founder Jess Mah's venture
  studio selectivity model) explicitly to FutureProofing's engineer-vetting approach.
  (https://www.futureproofing.dev/blog/mahway-playbook-engineering-hiring,
  https://www.futureproofing.dev/blog/jess-mah-latam-ai-talent-thesis)
- March 16, 2026: The "Applied AI Full-Stack Engineer" role itself was posted on Get on Board.
  (https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote)
- No funding announcement, launch/press coverage, or leadership-change news was found for
  FutureProofing itself in the last 12 months; could not confirm founding date or HQ.

## 6. Engineering & AI direction

- Stack signals (from the job posting and the one detailed case study): JavaScript/React/Node
  and/or Python on the engineer side; the case study client stack was Next.js, LangChain,
  Pinecone (vector DB), and OpenAI embeddings, with a custom citation-tracking layer built by
  hand rather than using LangChain's built-in citation chain.
  (https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote,
  https://www.futureproofing.dev/blog/claude-code-production-rag-case-study)
- Explicit AI-tooling stance: engineers are expected to use Copilot, Cursor, GPT, and Claude
  (Claude Code specifically documented) daily as part of the job, not as an experiment.
  (https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote,
  https://www.futureproofing.dev/blog/claude-code-production-rag-case-study)
- Documented engineering philosophy from the case study: build the evaluation harness before
  the pipeline; use AI tools for mechanical work (test fixtures, debugging, docs) but keep
  architectural judgment human, evidenced by the engineer rejecting AI-suggested approaches
  (fixed-size chunking, a built-in citation chain, an aggressive rollout plan) in favor of more
  conservative, hand-built alternatives. Claude Code reportedly wrote about 68% of keystrokes on
  that project but the engineer's judgment drove roughly 95% of architectural decisions.
  (https://www.futureproofing.dev/blog/claude-code-production-rag-case-study)
- No public engineering blog beyond the hiring/vetting/case-study content described above; no
  evidence of an open-source presence, public GitHub org, or technical conference talks.

## 7. Why-fit angles for Santiago

Best hook to lead with: the Claude Code production RAG case study is close to a direct mirror of
Santiago's own daily practice. He is a full-stack founder-engineer who ships production LLM/RAG
systems (Pragma AI's "Pragma Brain" RAG company-brain product, Plutus's LLM research agent) using
Claude Code as his primary tool, and the resume shows the same "AI does the mechanical work, I own
the architecture" posture the case study describes.

- Full-stack production shipping, 5+ years bar: Santiago has 7+ years shipping products end to
  end (Eugenia.ai: React/Node full-stack SaaS taken from concept to acquisition in 18 months;
  Online Basics: Python microservices on AWS/Heroku scaled to $8M revenue), directly matching the
  "5+ years shipping production products" and "full-stack comfort" requirements.
- Applied LLM/agent work, not just experimentation: Pragma AI's RAG "company brain," an LLM
  workflow with multi-stage validation on the Anthropic/OpenAI APIs, an autonomous personal-finance
  agent with tool-use/function calling, and an MCP-based research agent in Plutus. This matches
  the posting's ask for "active AI product development or experimentation" and the case study's
  emphasis on shipping real production AI, not demos.
- Founder autonomy: 3x founder background (raised capital, led a 7-person team, owned client
  relationships end to end) maps well onto an "embedded, autonomous, detail-oriented builder"
  engagement model where an engineer effectively parachutes into a client team and needs to move
  without hand-holding.
- Remote and LATAM-based: Santiago is Mexico City-based and remote by default, which fits both
  the fully-remote posting and FutureProofing's LATAM-engineer sourcing thesis, though he should
  be ready to speak to US time-zone overlap since the posting calls that out.

Honest concerns / watch-outs:
- Engagement model: the posting itself describes the role as part-time/project-based ("flexible
  part-time/project-based engagement"), not confirmed full-time employment, and lists no salary.
  That is a real gap against the profile's baseline expectations and needs to be clarified before
  or during the application, since it could affect income stability and whether the $65k minimum
  is even a relevant frame here.
  (https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote)
- Company stage and durability: FutureProofing is tiny (LinkedIn lists 4 employees, 2-10 band),
  has no public funding, and its own public content is almost entirely hiring/marketing copy
  rather than product or customer proof beyond the one named case study. This is a thin,
  early-stage layer to build a career on; the actual day-to-day culture and stability will depend
  heavily on which client startup Santiago is embedded with, which is not knowable in advance.
- Founder litigation: co-founder Jess Mah is currently in active, unresolved litigation (a suit
  she filed in May 2025 against a venture capitalist, met with counter-suits from two former
  executives at her venture studio Mahway and from the VC's firm, alleging among other things
  misuse of company funds; reported as in early stages as of June 2025).
  (https://lawadvocategroup.com/jessica-mah-and-justin-caldbeck-in-legal-crossfire-over-startup-fallout/)
  This litigation involves Mahway and inDinero, not FutureProofing directly, but Jess Mah is a
  visible co-founder and the public face of FutureProofing's vetting philosophy, so it is worth
  being aware of as a reputational and stability consideration, not something to raise unprompted
  in an application.

## 8. Application-question angles

- Why this company: lead with the Claude Code production RAG case study as evidence
  FutureProofing hires and markets engineers who ship real production AI fast while keeping
  human judgment over the model, which is exactly how Santiago already works day to day (Pragma
  Brain, Plutus). Frame it as recognizing a philosophy he already practices, not as attraction to
  the staffing model itself.
- Why you fit: anchor on the combination of full-stack production ownership (Eugenia.ai concept
  to acquisition, Online Basics to $8M) plus hands-on applied LLM/agent shipping (RAG, tool-use
  agents, MCP), which together map onto "5+ years shipping production" and "active AI product
  development" without needing to touch culture or news angles.
- Anything else: worth naming that he is Mexico City-based, remote-first, and comfortable with
  US time-zone overlap, since that speaks directly to the posting's LATAM-embedded model; avoid
  raising the part-time/compensation ambiguity here and instead clarify it directly with
  FutureProofing before or early in the process.

## 9. Sources

- https://www.getonbrd.com/jobs/applied-ai-fullstack-engineer-remote-futureproofing-remote
  Primary source for the role itself: responsibilities, requirements, remote/part-time framing,
  posted date, application count, no salary listed.
- https://www.futureproofing.dev/
  Company homepage: business model, pricing framing, target customers, vetting process, founders,
  scale stats.
- https://www.futureproofing.dev/engineers
  Engineer-facing page: placement sectors, vetting funnel detail, positioning language.
- https://www.futureproofing.dev/blog
  Blog index: post titles, themes, and dates used for the recent-news section.
- https://www.futureproofing.dev/blog/claude-code-production-rag-case-study
  Case study on an embedded engineer shipping a production RAG pipeline with Claude Code; core
  source for the core narrative and engineering-direction sections.
- https://www.futureproofing.dev/blog/mahway-playbook-engineering-hiring
  Detail on the founders' relationship (Mah/Barrica, inDinero, Mahway) and the selectivity
  philosophy applied to hiring.
- https://www.linkedin.com/company/futureproofing-dev
  Company size (2-10 employees, 4 listed), industry classification (staffing and recruiting).
- https://lawadvocategroup.com/jessica-mah-and-justin-caldbeck-in-legal-crossfire-over-startup-fallout/
  Dated June 16, 2025. Source for the co-founder litigation watch-out.
- No dedicated Crunchbase, PitchBook, or press coverage of FutureProofing (the AI-staffing
  company) itself was found; funding status, founding date, and HQ location remain unconfirmed.

researched: 2026-07-03
