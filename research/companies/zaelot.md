# Zaelot

Draft dossier for Santiago's review. Researched 2026-08-11.

## 1. Snapshot

Nearshore software and AI consultancy (staff augmentation plus project-based AI builds), not a
product company. Registered HQ in Sheridan, Wyoming, with delivery offices in Montevideo
(Uruguay), Buenos Aires, San Francisco, Reykjavik, Valencia, and Gothenburg. LinkedIn lists
51-200 employees; the company's own About page claims 120 professionals across 11 countries.
Founded 2020 per LinkedIn/Crunchbase listings (the company's own About page says "nearly a
decade," a discrepancy that is unresolved). No funding rounds found; it reads as a
bootstrapped/founder-owned services firm, not VC-backed.

## 2. Core narrative

Zaelot is a "human bridge" agency: it sells senior engineering, design, and (increasingly) AI
integration talent embedded directly into client teams, alongside discrete AI-solution builds
(agentic workflows, LLM integration, data pipelines). The founding/leadership team (German
Clark, Christian Clark, Guillermo Clark, plus Gaston Esmela, Virginia Antognazza, Leandro
Folgar) and the Montevideo/Buenos Aires office footprint point to a Uruguay/Argentina-rooted
nearshore shop that later added a US-facing Wyoming registration and a "AI-first" repositioning
for 2026. This is a staffing/consulting business model, not a product company: Santiago would be
billed out to a client, not building Zaelot's own product.

## 3. Mission & product

- Two service lines: "Talent" (embed senior engineers, tech leads, full-stack developers,
  DevOps, designers, PMs, business analysts into client orgs) and "AI Solutions" (agentic
  workflows, machine learning, LLM integration, data pipelines, MLOps), per the homepage.
  [zaelot.com]
- Client-facing pitch is aimed at CTOs/VPs of Engineering; sectors named on the About/marketing
  pages include Travel & Hospitality, Real Estate, Health, and News/Media. [zaelot.com,
  cbinsights.com]
- Platform partnerships listed: AWS, Salesforce, Vercel, Snowflake. Also runs a Salesforce
  consulting practice (listed on the Salesforce AppExchange). [zaelot.com, appexchange.salesforce.com]
- Revenue model is services/staffing, not a subscription or usage-based product. No product
  Zaelot itself owns and sells was found in this research.

## 4. Culture & voice

- Stated values (About page): continuous learning, "no shortcuts, no compromises," collaborative
  spirit blending analysts/designers/engineers, a "global mindset" across time zones, and
  ownership/care. Five listed principles: cooperation over competition, AI-first mindset,
  remote-first operations, engineering-led leadership, strategic team evolution. [zaelot.com]
- Glassdoor: 4.4/5 overall (17 reviews), 85% would recommend, 4.3 culture and values, 4.5
  work-life balance, 3.9 career opportunities, 4.2 compensation and benefits. A quoted positive:
  "They are transparent and show you salary ranges, have good benefits and flexibility." Sample
  size is small (17 reviews), so treat as a signal, not a verdict. [glassdoor.com search result]
- No distinctive public brand voice, no engineering blog, no visible social presence (Twitter/X,
  YouTube) surfaced in this research. Marketing language is standard B2B-agency copy ("digital
  transformation," "scale smarter, win harder").

## 5. Recent news (last ~12 months)

No dated press releases, funding announcements, or product launches from the last 12 months
turned up in search. The company site markets an "AI-first" pivot (AI Solutions as a named
service line) but does not date when this started. This is a thin public footprint: Zaelot does
not appear to publish company news, a blog, or press coverage in any indexed, citable form.
Treat "recent news" as unverified/absent rather than inferring nothing happened.

## 6. Engineering & AI direction

- Listed tech stack (from job boards/profile aggregators): React, Angular, Vue, TypeScript,
  JavaScript, .NET, Ruby, PHP, Java, Go, Rust, Python. [search result citing remotehub.com listing]
- The specific req Santiago is targeting (getonbrd id 6938, "Senior/Lead Full-Stack Engineer")
  asks for: Next.js (App Router, Server Components, Server Actions), TypeScript, Shadcn/ui,
  Tailwind, Supabase (Postgres, Auth, Realtime, Storage, Cron, Queues), Drizzle ORM, Upstash
  Redis, better-auth, Vercel deployment, Sentry, production OpenAI/Anthropic integration
  (function calling, structured outputs, streaming, retry/fallback/eval patterns), Google Maps
  APIs, and explicit daily fluency with Claude Code/Codex, MCP, subagent workflows, and
  CLAUDE.md-style project conventions. This is a modern, AI-native full-stack req, and it reads
  as a client engagement (the stack is specific enough to be one client's actual codebase, not a
  generic Zaelot stack). [getonbrd job posting, via local job DB]
- A separate open req ("Data Engineer," getonbrd) confirms Zaelot is actively staffing AI/data
  roles beyond this one posting, consistent with the "AI Solutions" line being a real, current
  hiring push, not just marketing copy. [getonbrd.com/empleos/data-science-analytics/data-engineer-zaelot-remote]
- No engineering blog, GitHub org, or technical writing was found, so "how they build" beyond
  the job req's stack list is unverified.

## 7. Compensation signal (important, read before applying)

The getonbrd posting for this exact req (id 6938) lists salary_min 4,000 and salary_max 6,500 in
USD. getonbrd figures are consistently monthly USD (documented convention in
`config/profile.yaml`), which annualizes to roughly $48,000 to $78,000 per year. The bottom of
that range is well below Santiago's $70,000 LATAM-scope floor (`config/profile.yaml:
comp.min_usd_latam_scope`); only the top of the range ($78k) clears it, so this posting works
only if the offer lands near the very top of the band. Glassdoor reviewers do describe Zaelot as
transparent about salary bands and good on benefits, but that reputation is for direct
Zaelot employees generally, not confirmation this specific band is negotiable upward.

No posting or page found states explicitly whether this role is a contractor engagement or a
direct Zaelot employee position, or whether Zaelot hires from Mexico specifically (its confirmed
LATAM offices are Uruguay and Argentina; Mexico is not named on any page found in this
research). Both the employment-type and Mexico-eligibility questions are unverified and should
be asked directly and early, before investing more time, alongside a direct conversation about
whether the posted band can move given the seniority and stack the req asks for.

## 8. Why-fit angles for Santiago

Best hook: the req's own language, "daily working proficiency with Claude Code and/or Codex,"
"skills, MCPs, and subagent workflows," "set up project-level conventions (CLAUDE.md, custom
skills, MCP configurations)," maps almost line for line onto how Santiago actually works today:
Pragma AI's internal platform is a hosted MCP service with 15 agent definitions and 10 reusable
routines run as Claude Code tools, and Kairos ships both an in-app Claude Agent SDK integration
and a standalone MCP server built from one typed tool layer. Few candidates can point to shipped,
production MCP/agent-loop work at this level of specificity; that is the angle to lead with, not
a generic "AI consultancy fit" pitch.

Secondary hook: the stack itself (Next.js, TypeScript, Supabase/Postgres, production OpenAI and
Anthropic integration with retry/fallback/eval patterns) is close to what he already ships:
Plutus is a FastAPI/Postgres backend with a React/TypeScript frontend and an MCP control plane;
Pragma's RAG brain has deterministic no-answer and citation gating, which is the same "handling
non-deterministic outputs" concern the req names for LLM features.

Honest concerns:
- Comp is the real risk. The posted band on this exact req annualizes below his floor. This
  needs to be resolved in the first conversation, not assumed away.
- This is a staffing/consulting business, so the actual day-to-day team, tooling, and client may
  differ from what the marketing site describes; the req itself reads like one specific client's
  stack, so the interview should confirm which client and how long the engagement is expected to
  run.
- No confirmation Zaelot hires from Mexico specifically (confirmed LATAM presence is Uruguay and
  Argentina). Should be asked directly rather than assumed, since it affects whether this is
  employee or contractor and how payment/benefits work.
- Public footprint is thin (no blog, no recent press, small Glassdoor sample), so most of the
  culture read here rests on the company's own marketing copy plus a handful of reviews.

## 9. Application-question angles

Why this company: lead with the agent-loop and MCP-specific language in the req itself, that is
what makes this posting different from a generic "know React and an LLM API" listing, and it is
exactly the surface Santiago has been building on (Pragma's hosted MCP brain, Kairos's dual
Claude Agent SDK plus MCP server). Keep it to the one sentence the voice guide allows, then move
straight to concrete work.

Why you fit: do not restate the whole stack checklist. Pick the two or three req items that map
to real shipped work (MCP tool layer, production Anthropic/OpenAI integration with
retry/fallback handling, Next.js/TypeScript/Postgres experience via Plutus and the Pragma
platform) and describe what was actually built, not a capability list.

Anything else: this is the natural place to raise the comp question directly and plainly (the
posted range is monthly-equivalent to below his floor, so confirm scope, employment type, and
whether the band moves for lead-level ownership) rather than folding it into flattery. If the
form does not have room for a comp question, it belongs in the first recruiter conversation, not
buried in the cover letter.

## 10. Sources

- researched: 2026-08-11
- https://www.zaelot.com/ (services, business model, client model, values, headquarters address)
- https://zaelot.com/careers/ (six stated values, "explore open positions" pointer)
- https://www.zaelot.com/about (founding story, 120 professionals/11 countries claim, leadership
  names, five principles)
- https://www.linkedin.com/company/zaelot (company size 51-200, founded 2020, industry)
- https://www.crunchbase.com/organization/zaelot (founded 2020, no funding found; profile marked
  thin/unclaimed on cbinsights mirror)
- https://www.cbinsights.com/company/zaelot (confirms unclaimed/thin profile, no funding data)
- https://www.remotehub.com/company/zaelot (via search snippet: office locations including
  Montevideo, Buenos Aires, San Francisco, Reykjavik, Valencia, Gothenburg; tech stack list)
- https://www.glassdoor.com/Reviews/Zaelot-Reviews-E6888294.htm (rating 4.4/5, 17 reviews, 85%
  recommend, culture/comp/work-life sub-scores, quoted review on salary transparency)
- https://www.getonbrd.com/jobs/senior-lead-full-stack-engineer-zaelot-remote (the target req,
  id 6938 in local job DB: full stack/requirements list, salary_min 4000 / salary_max 6500 USD;
  page itself returned 403 on direct fetch, so this data is via the previously scraped job
  record in `data/jobs.db`, originally sourced from this URL by `src/adapters/getonbrd.py`)
- https://www.getonbrd.com/empleos/data-science-analytics/data-engineer-zaelot-remote (confirms
  a second concurrent open AI/data req, cited via search snippet; direct fetch also returned 403)
- https://appexchange.salesforce.com/appxConsultingListingDetail?listingId=933b3838-d99f-430f-8469-6257a7a6dc7b
  (Salesforce consulting practice listing)
- config/profile.yaml (Santiago's comp floor, LATAM-scope rule, getonbrd monthly-USD convention)
- resume/master_resume.yaml (Santiago's MCP, Claude Agent SDK, RAG, and full-stack evidence used
  in the why-fit section)

Notes on verification gaps: founding date is inconsistent between sources (2020 vs "nearly a
decade"), no page confirms Mexico-specific hiring or employee-vs-contractor status for this req,
and no recent (last 12 months) dated news item was found. These are flagged above rather than
guessed at.
