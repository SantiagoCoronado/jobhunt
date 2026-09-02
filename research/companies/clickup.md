# ClickUp, company dossier

> Draft for Santiago to review. Every claim is sourced in the Sources section. Facts over prose.
> Role context: Senior Software Engineer, Internally Deployed Products (internal AI tooling: MCP
> servers, agent orchestration, TypeScript/Node/React/Python, AWS Bedrock, LLMs). The full JD was
> not retrievable, so this dossier is company-level and reusable.

## 1. Snapshot
All-in-one work-management SaaS, repositioned as the self-described "world's first Converged AI Workspace" (tasks, docs, chat, whiteboards, goals, time tracking, plus AI agents in one platform). Founded 2017 by Zeb Evans (CEO) and Alex Yurkowski (CTO). HQ San Diego, California; remote-friendly with offices in the US, Canada, Ireland, the UK, and Australia. Roughly 1,000 employees as of May 2026 (down from about 1,500 after a 22% cut). About $300M ARR (flat 2025 to 2026), 20M+ users, roughly 100K paying customers. Raised $537.5M across 5 rounds; last valuation $4B at the October 2021 Series C.

## 2. Core narrative
ClickUp is making an aggressive, all-in bet that in the AI era the moat is not the model but the context: it owns a graph of 20M+ users' tasks, docs, decisions, and conversations, and it is rebuilding the whole company around turning that data into work done by humans and AI agents together. It has reorganized itself to prove the thesis: shipped ClickUp 4.0 as a "converged" workspace (Dec 2025), acquired coding-agent startup Codegen (Dec 2025), cut 22% of staff to go "AI-first" (May 2026), and launched Brain2, "your company's AI," that routes across Claude, GPT, and Gemini (June 2026). Zeb Evans frames it bluntly: "The model isn't the moat. What you can do with full context is."

## 3. Mission & product
- **Mission**: "Maximize human productivity." Company motto: "Save one day, Every week."
- **Original positioning**: "one app to replace them all," born from the founders' frustration juggling roughly 15 tools at their marketing agency.
- **Current positioning**: "Converged AI Workspace," a single place where humans and AI agents work together with full context across apps, data, and workflows.
- **Product surface**: tasks, docs, chat, whiteboards, goals, dashboards, time tracking, plus the AI layer: Brain2, Super Agents (AI teammates you @mention or assign), and Autopilot Agents (trigger-and-condition based).
- **Business model**: SaaS subscription, freemium plus paid tiers, with an "Everything AI" add-on gating higher AI usage limits.
- **Customers**: 20M+ users and roughly 100K paying customers; named logos include Netflix and Spotify. Enterprise trust posture: SOC 2, ISO 42001, HIPAA, and GDPR compliant.

## 4. Culture & voice
- **Intense, high-ownership, direct.** Hires against three pillars: Growth ("outdo yesterday's version of yourself"), Passion ("bold ideas"), and Hard Work ("take ownership of tough problems"). Value hashtags include #GREATNESS, #RESILIENCY, #URGENCY, #GROWTHMINDSET, #FUN, #DETAILSMATTER, #HARDWORK, #BESTCX, #BEDIRECT, #SCRAPPY.
- **Bold, irreverent marketing voice.** Company copy leans on the idea that normal, fragmented approaches to work do not cut it; the brand is high-energy and opinionated.
- **AI-first is now a cultural mandate, not just a product line.** Evans divides the future workforce into "Builders," system managers, and front-liners, and has said people who automate jobs with AI will always have a job. To retain top performers through the transition, ClickUp introduced salary bands up to $1M for outsized AI-driven impact "regardless of department or role."
- **Watch-out on tone**: the high-intensity culture plus a 22% layoff signals a demanding, fast-moving environment. Evans says the cut was not cost-driven and that most savings flow "back into the people who stay."

## 5. Recent news (last ~12 months, each dated)
- **Dec 2025**: ClickUp 4.0 shipped as a complete platform overhaul, replacing 3.0 navigation with the converged workspace.
- **Dec 23, 2025**: Acquired Codegen (a Cursor competitor for AI-powered code generation and agentic AI). Codegen founder/CEO Jay Hack became ClickUp's Head of AI. Stated purpose: power "Super Agents" that build software and take action with 500+ work skills.
- **May 22, 2026**: Announced a 22% workforce reduction to move to an "AI-first" operating model; introduced salary bands up to $1M for high-AI-impact employees. Evans: "If you create outsized impact using AI, you'll be paid outside of traditional bands."
- **June 2026 (announced June 17, detailed June 23)**: Launched Brain2, "your company's AI," rebuilt to have "full awareness of all of your company's knowledge." Routes queries across Claude, GPT, and Gemini (or user-selected model), adds shared "multiplayer" memory, and ships a Brain MAX app across web, desktop, and mobile. ClickUp claims 100% preference over standalone ChatGPT and Claude in blind evaluations for real work tasks (company-reported, unverified externally).

## 6. Engineering & AI direction
- **The thesis**: context (the workspace data graph) is the moat; the platform is model-agnostic. Brain2 is effectively an LLM gateway routing across Claude, GPT, and Gemini per task. Jay Hack (Head of AI): "The bottleneck to agents transforming how work is done is no longer AI capabilities, it's context."
- **MCP is a first-class surface.** ClickUp runs an official MCP server (public beta) at `https://mcp.clickup.com/mcp`, exposing tasks, lists, folders, spaces, docs, comments, and chat to AI agents. Auth is OAuth 2.1 with PKCE; custom clients speak JSON-RPC 2.0 over HTTP per the MCP spec. It connects to Claude Desktop, Claude Code, ChatGPT, Cursor, VS Code, and others, with an allowlist of vetted client redirect URIs for security.
- **Internally deployed products are a real, staffed practice (directly relevant to this role).** ClickUp built 6+ custom internal AI tools serving Sales, Support, Product, and RevOps: an Inbound SDR Agent (qualify/route inquiries), a support triage/dedup/escalation workflow (Zendesk-integrated), a Digital Adoption context tool, a product-feedback research agent named "Nexus" (ingests Zendesk, sales calls, G2, Reddit for a 40-person product team), and an Order Form Reviewer agent (extracts PDF data, cross-references Salesforce). These use OpenAI and Gemini models, connect Salesforce, data warehouses, and Zendesk, and keep human-in-the-loop review. Result claimed: hundreds of hours automated weekly and $200K+ in vendor savings. Borys Aptekar, PM of GTM AI: "Retool bridges the gap between our processes and AI... put an elegant interface over it all." (These particular tools were built on Retool; the JD's TypeScript/Node/React/Python/AWS Bedrock stack points to a broader internal-platform build.)
- **Agentic roadmap**: Codegen's agentic coding tech now feeds "Super Agents" (autonomous, multi-step, cross-function) and "Autopilot Agents" (trigger-based). This is the same problem space as the target role: orchestrating agents that act on company data with human oversight.
- **Stack (per role context, not independently confirmed for ClickUp core)**: TypeScript, Node, React, Python, AWS with Bedrock, LLMs, MCP, agent orchestration. Treat as the role's stack, not a verified description of ClickUp's whole codebase.

## 7. Why-fit angles for Santiago
**Single best hook to lead with**: Santiago has already built, end to end, the exact thing this team builds. In Kairos he shipped one typed tool-definition layer that powers BOTH an in-app agent (Claude Agent SDK) AND a standalone MCP server exposing the same 18 tools, so both an app and Claude Code operate on live user data. In Plutus he exposed an autonomous discovery and research engine through an MCP control plane. And at Pragma AI he built "Pragma Brain," a RAG "company brain" that ingests a company's internal data to answer questions and auto-generate reports. That is a 1:1 map to ClickUp's world: internally deployed AI tools, MCP servers, agent orchestration, and a context-is-the-moat, company-brain thesis.

Supporting angles:
- **Stack match is clean**: TypeScript, Node, React, and Python are all first-class in his master resume; he has AWS (EC2, RDS) experience, plus RAG, embeddings, vector DBs, function calling/tool-use, and prompt engineering. Frame the internal-tools work (LLM workflow with multi-stage validation, 10+ API orchestration, real-time ETL) as production internal-platform engineering.
- **LLM-agnostic by habit**: he has built on both the Anthropic and OpenAI APIs; Brain2's multi-model routing rewards that provider-neutral instinct.
- **Founder velocity fits the culture**: scrappy, high-ownership, "do hard things," ships 0-to-1. He scaled Online Basics to $8M with a 7-person team and led git-based, code-reviewed agile delivery, which maps to ClickUp's #SCRAPPY / #HARDWORK / #URGENCY values and its "Builders" framing.
- **Human-in-the-loop and stakeholder sense**: ClickUp's internal tools keep humans in review and serve GTM/Support/Product partners. Santiago's client-facing consulting, diagnostics, and stakeholder management are a direct asset for an internally deployed team that has non-engineer users.

**Honest concerns / watch-outs**:
- **Work authorization and location**: the role reads as US-based. Santiago is in Mexico City, TN-visa eligible (not a US citizen), and open to fully remote worldwide or hybrid in Mexico City only. Confirm the role is remote-eligible for LATAM or that ClickUp will support TN; do not assume.
- **Company stability signal**: 22% layoffs (May 2026) and flat revenue at about $300M ARR mean a high-pressure, actively restructuring environment. The upside (AI-first, $1M impact bands) is real, but so is the intensity; worth probing team stability and scope.
- **Scale gap**: his background is founder / SMB / 0-to-1, not big-SaaS platform scale. The role sits inside a ~1,000-person company; be ready to show he can operate in an established codebase and org, not only greenfield.
- **AWS Bedrock specifically**: he has used the Anthropic and OpenAI APIs directly and AWS EC2/RDS, but Bedrock is not explicitly on his resume. Frame it as a short hop from what he has shipped, not as prior direct experience.

## 8. Application-question angles (narrative-led, not canned answers)
- **"Why ClickUp / why this company"**: Lean on the Core narrative. ClickUp's bet that context, not the model, is the moat is the same bet Santiago made building Pragma Brain (a RAG company brain over a client's own data) and Kairos (agents acting on live user data through one shared tool layer). He is not applying to "an AI company," he is applying to the one company productizing the exact pattern he already builds: agents grounded in a company's full context, with humans in the loop.
- **"Why you fit"**: One line of proof, not a checklist. He has shipped an MCP server plus an in-app agent from a single typed tool-definition layer, and a company-brain RAG system, which is precisely internally deployed AI products, MCP, and agent orchestration. Then connect the stack (TypeScript/Node/React/Python/AWS) and the founder-grade ownership and velocity.
- **"Anything else"**: Founder ownership and range. He builds 0-to-1 under real constraints (scaled a business to $8M with 9 people), is provider-agnostic across Claude and GPT, and brings bilingual ES/EN plus LATAM reach, useful for a globally distributed, AI-first team. Do not enumerate all four research areas; pick the context-and-agents thread and stay on it.

## 9. Sources
researched: 2026-07-06

- https://clickup.com/about , mission ("Maximize human productivity"), motto ("Save one day, Every week"), value hashtags, HQ and office footprint, founding-frustration story.
- https://en.wikipedia.org/wiki/ClickUp , founding year (2017), founders (Zeb Evans, Alex Yurkowski), HQ San Diego, funding rounds (Series A $35M Jun 2020, Series B $100M Dec 2020, Series C $400M at $4B Oct 2021), 2023 and 2026 layoffs, Dec 2025 Codegen acquisition with Jay Hack as Head of AI. (Wikipedia flags promotional tone; cross-checked with sources below.)
- https://getlatka.com/companies/clickup , ~$300M ARR (flat 2025 to 2026), $4B valuation, $537.5M total funding across 5 rounds, ~100K customers, headcount ~1,000 post-layoff (down from ~1,500).
- https://clickup.com/brain , Brain2 positioning as "your company's AI" / converged AI workspace.
- https://www.businesswire.com/news/home/20260617198270/en/ClickUp-Launches-Brain2-Your-Companys-AI and https://markets.financialcontent.com/wral/article/bizwire-2026-6-23-clickup-launches-brain2-your-companys-ai , Brain2 launch (June 2026), multi-model routing across Claude/GPT/Gemini, 20M+ users, Brain MAX app, SOC 2 / ISO 42001 / HIPAA / GDPR, Zeb Evans quote "The model isn't the moat. What you can do with full context is."
- https://americanbazaaronline.com/2026/05/22/clickup-cuts-22-workforce-as-ceo-zeb-evans-pushes-ai-first-strategy-481410/ and https://www.businesstoday.in/technology/news/story/people-who-automate-jobs-with-ai-will-always-have-a-job-productivity-startup-clickup-cuts-22-of-workforce-532801-2026-05-22 , May 22 2026 22% layoffs, AI-first operating model, $1M salary bands, Evans quotes, Builders / system managers / front-liners framing.
- https://clickup.com/blog/clickup-codegen-acquisition/ and https://www.businesswire.com/news/home/20251223327889/en/ClickUp-Acquires-Cursor-Competitor-Codegen-to-Supercharge-AI-Super-Agents , Dec 23 2025 Codegen acquisition, Jay Hack becomes Head of AI, Super Agents with 500+ work skills, Hack quote on context being the bottleneck.
- https://developer.clickup.com/docs/connect-an-ai-assistant-to-clickups-mcp-server , official MCP server (public beta) at mcp.clickup.com/mcp, exposes tasks/docs/etc., OAuth 2.1 + PKCE, JSON-RPC 2.0 over HTTP, connects Claude Desktop/Code, ChatGPT, Cursor, VS Code.
- https://help.clickup.com/hc/en-us/articles/33335772678423-What-is-ClickUp-MCP , ClickUp MCP overview and status.
- https://retool.com/customers/clickup , 6+ internally deployed AI tools across Sales/Support/Product/RevOps (Inbound SDR Agent, support triage, Digital Adoption tool, "Nexus" feedback research agent, Order Form Reviewer), human-in-the-loop, OpenAI + Gemini, Salesforce/Zendesk/warehouse integration, $200K+ vendor savings, Borys Aptekar (PM, GTM AI) quote.
- https://clickup.com/careers/tooling-engineer , hiring pillars (Growth, Passion, Hard Work), values (#SCRAPPY, #GREATNESS, #GROWTHMINDSET), remote and benefits posture.
- https://diginomica.com/one-app-replace-them-all-clickups-ceo-future-productivity-and-how-clickup-addresses-proliferation , "one app to replace them all" origin and CEO framing.
- https://sacra.com/c/clickup/ , cross-check on revenue, valuation, and funding.

Unverified / to treat with caution: a review-blog estimate puts ClickUp's 2026 valuation near $6B; the last confirmed valuation is $4B (Series C, Oct 2021). ClickUp's "100% preference over ChatGPT and Claude in blind evaluations" is company-reported. The role's specific stack (AWS Bedrock, TypeScript/Node/React/Python) comes from the JD context provided, not from an independently verified description of ClickUp's core codebase.
