# Bland (Bland AI)

## 1. Snapshot
Bland builds proprietary, self-hosted AI voice agents that handle real, high-stakes phone calls (inbound and outbound) for regulated enterprises in healthcare, insurance, and financial services. Series C stage, over $100M raised total, roughly 40 people, HQ in San Francisco (Jackson Square). The Forward Deployed Engineer role is on-site in SF, with travel to customer sites [1][2][6][10].

## 2. Core narrative
Co-founders Isaiah Granet and Sobhan Nejad started Bland in 2023 after Nejad's aunt could not reach her insurer by phone and was denied medical treatment. About 180 investors passed, several telling them phone calls "won't exist a year from now." The founders bet everything, plus an extra $600,000, on owning the entire voice stack (proprietary LLM, text-to-speech, speech-to-text, and their own GPU cluster) instead of wrapping OpenAI or Anthropic APIs, chasing sub-400ms latency good enough for real conversation. That "own the whole stack, prove the skeptics wrong" bet is now handling 30 to 45 minute high-stakes calls (insurance claims, healthcare triage) for 250+ enterprise customers [2][6].

## 3. Mission & product
- **Product**: Bland Voice, an enterprise voice AI platform for building, deploying, and monitoring phone agents across voice, SMS, iMessage, and web chat with shared agent memory. In March 2026 they launched Norm, an AI assistant that builds production-ready voice agents from a single prompt, which Bland frames as giving customers "the equivalent of their own personal FDE" [1][3][8][9].
- **Business model**: enterprise SaaS/usage-based platform sold to security-conscious enterprises; typical deployment to production within 30 days [1].
- **Customers named in company and press materials**: Samsara, Kin Insurance, Mutual of Omaha, CNO Financial Group, Gallup, TripAdvisor, Snapchat, Signant Health, Better.com, Cleveland Cavaliers, EvenUp [1][2][6][10].
- **Scale claims (company-stated)**: 547M+ calls resolved to date (site claim), 3.5M+ calls per week, 175M+ AI phone calls in the past year [1][6].
- **Compliance**: SOC 2 Type II (annual audit), HIPAA with BAAs, PCI DSS v4.0, GDPR/CCPA [1][3].

## 4. Culture & voice
- Hiring philosophy is explicitly "obsession, not pedigree": the team mixes Stanford PhDs and ex-DeepMind researchers with self-taught engineers who trained their own models independently [4].
- Founder story is part of the brand: Granet reportedly slept on a closet floor in SF while the team put its capital, plus an extra $600K, into GPUs rather than office comforts [2][4].
- Job postings describe "relentlessness" as the single most important trait they screen for, and ask FDEs to bring "unreasonable hospitality" to customers, including traveling on-site and hosting trainings/dinners to build real relationships [7][10].
- CEO framing leans hard into automation-over-headcount: "Humans simply can't work 24/7, handle millions of phone calls simultaneously, or be trained to a company's exact liking down to its voice and behavior. AI can, at a fraction of the cost." [4]

## 5. Recent news (last ~12 months)
- **2026-06-16**: Closed a $50M Series C led by Dell Technologies Capital (HubSpot Ventures, Archerman Capital, Tribeca Venture Partners, plus existing investors Emergence, Upfront, Scale Venture Partners, Y Combinator, Max Levchin, Jeff Lawson), pushing total funding past $100M. Funds earmarked for research, engineering headcount, and expansion into more regulated industries [2][5][6].
- **2026-03-26**: Launched Norm, described as the first AI assistant that builds production-ready voice agents from a single prompt, including automated diff review, pathway validation, prompt-based unit tests, and simulated customer calls before go-live [8][9].
- *(For context, outside the strict 12-month window)* **2025-02-03**: Closed a $40M Series B led by Emergence Capital, bringing funding to $65M at that point; investors included Scale Venture Partners, Y Combinator, and angels Max Levchin and Jeff Lawson [3].

## 6. Engineering & AI direction
- **Full in-house stack**: proprietary LLM, TTS, and STT models, refuses to integrate third-party model providers (OpenAI, Anthropic) into the core voice pipeline, runs on Bland's own GPU cluster rather than third-party inference APIs [2][6].
- **Latency and cost target**: sub-200 to sub-400ms end-to-end response latency (company claims ~400ms vs. an industry average they cite around 1,240ms), with cost engineering down toward fractions of a cent per minute for call handling [1][6].
- **Architecture**: a real-time transport/orchestration layer (industry reporting points to LiveKit-style transport) coordinating three model layers (STT, inference, TTS) plus telephony handling; "branching logic with guardrails" for regulated workflows rather than pure prompt-based flows, so disclosures/verifications are deterministic [1][6].
- **TTS research**: an LLM-based TTS engine that predicts audio tokens directly from text (via a SNAC tokenizer) instead of a traditional phonetics-then-waveform pipeline, with few-shot (3 to 6 sample) in-context style/voice transfer and explicit style tokens like `<excited>` or `<calm>`. The engineering post is candid about open problems (token repetition, audio-quality sensitivity, gender performance gaps) [11].
- **Integration surface**: REST, JavaScript, CLI, and MCP (Model Context Protocol) interfaces; telephony compatibility with SIP, Twilio, Genesys, NICE; "bring your own number/carrier/SIP trunk" [1].
- **Product-as-productized-expertise**: Norm is explicitly positioned as codifying what a Forward Deployed Engineer does (translate a customer's needs into a working agent) into a self-serve AI assistant, an interesting signal about how Bland thinks about the FDE function's long-term leverage [9].

## 7. Why-fit angles for Santiago
**Best hook to lead with**: Santiago already did this job, on-site, at a startup. At Eugenia.ai he owned the full product lifecycle and led on-site client deployments (onboarding HOAs/property administrators, gathering requirements, translating conflicting stakeholder needs into working mobile/web software) for a 0-to-1 B2B SaaS product that scaled to 20+ buildings and 10,000+ users before acquisition. That is the Forward Deployed Engineer motion Bland describes (own delivery end to end, embed with the customer, translate messy real-world workflows into a functional agent) [10], just applied to voice instead of property management.

Supporting angles:
- **Founder ownership DNA is an explicit nice-to-have in the posting** ("startup or founder background"), and Santiago is a 3x founder: bootstrapped Eugenia.ai to acquisition without external capital, scaled Online Basics to $8M in revenue on a 7-person team, now co-founding Pragma AI [master resume]. Bland's whole hiring pitch is "obsession, not pedigree" over credentialed paths, which maps to a self-taught, founder-built career.
- **Hands-on AI/agent shipping matches the posting's actual bar** (Python or JavaScript, REST/JSON, Git, hands-on LLM/automation integration, LLM deployment experience as a plus). Santiago ships production LLM workflows and agent systems daily (Anthropic/OpenAI APIs, RAG, tool-use/function-calling agents, Claude Agent SDK, MCP), including a live consultancy (Pragma AI) building conversational agents and a RAG "company brain" for SMB clients, which is forward-deployed AI delivery work in miniature.
- **Comfort in ambiguous, fast-moving environments**: leading a 7-person team through incident response, agile delivery, and raising $500K+ from private investors shows he can operate without a big-company approval chain, which fits a 40-person startup that explicitly screens for relentlessness over process.

**Honest concerns / watch-outs**:
- **Location conflicts with his stated dealbreaker.** This role is on-site in San Francisco (full-time in-office the first month, then mostly in-person or on customer sites) [10]. Santiago's own profile lists "on-site or hybrid outside Mexico City" as a dealbreaker and states he is "not open to relocating for on-site" [config/profile.yaml]. He is TN-visa eligible for US employment, so the role is legally workable, but taking it means overriding his stated location preference, not just clearing a visa hurdle. This should be a deliberate, named choice, not glossed over.
- **Voice/telephony is a new technical domain.** His agent and RAG experience is real, but nothing in the master resume touches real-time audio, SIP/telephony integration, or low-latency voice pipelines specifically. The job explicitly welcomes "exceptional new grads" and fast learners without an exact experience match, and lists LLM deployment experience only as a plus, so this is a real but survivable gap worth naming rather than papering over.
- **Regulated-industry depth is thin.** Bland's flagship use cases are healthcare and insurance calls with compliance stakes (HIPAA, PCI). Santiago's closest analog is PropTech/HOA operations at Eugenia.ai, not healthcare or financial services, so this is a domain to acknowledge and express eagerness to learn rather than claim direct experience in.

## 8. Application-question angles
- **Why this company**: Lean into the founder-bet narrative, an unproven, rejected-by-180-investors thesis that they backed by putting all their own capital (plus $600K more) into owning the full stack rather than the easy path of wrapping someone else's model. Santiago has made comparable bets: bootstrapping Eugenia.ai to an acquisition with no outside capital, and scaling Online Basics to $8M on lean, self-built infrastructure. The resonance is "conviction plus building the unglamorous infrastructure yourself," not a generic "I love AI" pitch.
- **Why you fit**: Lead with Eugenia.ai's on-site B2B deployment work (owning delivery end to end, embedding with customers, translating messy requirements into shipped software) as a near-literal preview of the FDE role, then back it with daily hands-on LLM/agent shipping (Claude Code, RAG, tool-use agents) that matches Bland's own AI-native build culture. Do not also reach for the Nextia.mx or Online Basics ops angles in the same breath; one tight thread beats a checklist.
- **Anything else**: A good place to be candid about the voice/telephony gap and the SF relocation, framed as a deliberate choice, not an oversight: he is picking this because the delivery-to-customer motion and founder-obsession culture are the closer fit than the specific medium (voice) or geography (SF over Mexico City), and he has a track record (mobile Swift/Java as a self-taught add, PropTech, e-commerce data pipelines) of picking up an unfamiliar technical domain fast when the underlying problem (translate a real workflow into working software, ship it, own it) is the same.

## 9. Sources
1. https://www.bland.ai/: product overview, scale claims (547M+ calls), latency claim, compliance certs, customer examples.
2. https://fortune.com/2026/06/16/voice-ai-bland-50-million-after-being-rejected-by-180-investors/: Series C story, founder background, "one of one" quote, growth metrics (3.5M calls/week, 175M calls/year, 250+ customers), 30-45 min call detail.
3. https://www.bland.ai/blog/bland-raises-a-40m-series-b: Series B announcement, dated 2025-02-03, funding total at the time ($65M), investor list, customer names (Cleveland Cavaliers, Better.com).
4. https://www.bland.ai/about: mission framing, founding story (closet floor, $600K into GPUs), hiring philosophy ("obsession, not pedigree"), CEO quote on automation vs. human labor.
5. https://www.prnewswire.com/news-releases/bland-surpasses-100m-funding-with-new-series-c-to-advance-voice-ai-for-complex-high-stakes-conversations-302801583.html: official Series C release, investor list, use of funds, Dell Technologies Capital quote.
6. (Corroborating Series C coverage) https://siliconangle.com/2026/06/16/bland-raises-50m-automate-complex-high-stakes-phone-calls/: self-hosted-everything thesis, GPU spend detail, per-minute cost figures, in-house model philosophy.
7. https://talent.emcap.com/companies/bland-ai-2/jobs/68954639-forward-deployed-engineer: full Forward Deployed Engineer job description (mirror of the Ashby posting): responsibilities, required/nice-to-have qualifications, "relentlessness," "unreasonable hospitality," compensation ($120k-180k), on-site requirement, 0-10 years experience range.
8. https://www.bland.ai/blog/norm-build-voice-agents-from-prompt: Norm launch details, "personal FDE" framing, feature set (diffs, unit tests, simulated calls).
9. https://siliconangle.com/2026/03/26/bland-launches-norm-help-teams-build-production-ready-voice-agents-minutes/: corroborates Norm launch date (2026-03-26) and positioning.
10. Job posting content for the Forward Deployed Engineer role (San Francisco), as provided in the task context (Ashby URL: https://jobs.ashbyhq.com/bland/824f7ebb-6d71-4484) and cross-verified via the Emergence Capital mirror [7]: team size (~40 people), named enterprise customers (Samsara, Gallup, TripAdvisor, Snapchat, Signant Health, Better.com), on-site/Jackson Square detail, "first month full-time in office, then mostly in-person or on customer sites."
11. https://www.bland.ai/blogs/new-tts-announcement: engineering blog on Bland's in-house LLM-based TTS approach (audio-token prediction, SNAC tokenizer, few-shot style transfer, stated open problems).

Config sources: `config/profile.yaml` and `resume/master_resume.yaml` (Santiago's location dealbreakers, TN-visa eligibility, founder history, skills) were read directly, not fetched from the web.

researched: 2026-07-13

---
Draft dossier for Santiago to review. All facts above trace to the numbered sources; anything not sourced was intentionally omitted rather than guessed (e.g. Bland's current valuation and exact headcount are not stated in any source found and are left out).
