# Telos Labs: Company Dossier (DRAFT for Santiago's review)

Researched: 2026-07-28
Target posting: "AI Engagement Manager" (job id 11817), listed location "Mexico". Adzuna mirror:
https://www.adzuna.com.mx/land/ad/5784465925 (403 Forbidden when fetched directly; see liveness
verdict below).

## Disambiguation (important)

"Telos Labs" is an ambiguous name online. This dossier is about the Berkeley, California-founded
AI/software product studio at teloslabs.co (LinkedIn: linkedin.com/company/telos-labs), founded by
Jordan G. Trevino in 2017, whose own site describes it as living "at the intersection of business
consulting and technology" and building internal tools and AI workflows for mid-market clients
[teloslabs.co homepage; teloslabs.co/about-us], which matches the target job's own self-description
verbatim [local DB job description, job id 11817]. It is NOT: telos-labs.com (a different, separate
consultancy with an "AI Data Sphere" case study), Telos Corporation (a US federal cybersecurity
contractor in Ashburn, VA), or the "Telos Labs" gaming-guild/Web3 company that appears under a
similarly named LinkedIn jobs listing [web search results distinguishing these].

## LOCATION AND LIVENESS VERDICT: UNVERIFIED (leaning plausible, but not independently confirmed live today)

This one could not be fully verified as-is, for two separate reasons, and that should be stated
plainly rather than papered over.

**On location:** the only independently found copy of this exact posting (via a Mexican job
aggregator, trabajo.org, dated by its own listing to around June 22, 2026) tags the role as based
in "Nuevo Leon, Nuevo Leon" [web search snippet of mx.trabajo.org/oferta-5568-...], not Mexico City
or "remote, LATAM." Telos Labs' own site confirms it has a real physical presence in Mexico,
listing Mexico City and Monterrey (Monterrey is the capital of Nuevo Leon) alongside its Bay Area
HQ [teloslabs.co, company overview via web fetch]. A Nuevo Leon location is still inside Mexico, so
it does not trip the hard "outside Mexico" dealbreaker in Santiago's profile, but it is not
confirmed to be remote-from-Mexico-City-fine versus an on-site-in-Monterrey expectation; this
needs a direct question to the recruiter, not an assumption either way
[config/profile.yaml location_rule].

**On liveness:** the direct trabajo.org URL returned HTTP 410 Gone when fetched just now (a status
code that specifically means "this resource used to exist and was deliberately removed," stronger
than a generic 404) [direct fetch of mx.trabajo.org/oferta-5568-9e37f18886d672d09880eb750520addd].
Both Adzuna mirror URLs for this job (the one supplied and the one stored in jobhunt's own DB)
returned 403 Forbidden on direct fetch, which is Adzuna's normal anti-scraping behavior and not
itself evidence the posting is dead. But jobhunt's own crawler last confirmed this listing as seen
on 2026-07-21, a full week before this research date, versus first_seen 2026-07-16
[local DB, job id 11817], and Telos Labs' own current careers page states "we don't always have a
role posted" and directs candidates to a general-interest form rather than listing open roles
[teloslabs.co/join-us, fetched today]. Taken together, this specific requisition may no longer be
open. Recommend confirming directly (apply and see, or a quick email to the general contact) before
assuming it is still live.

## 1. What Telos Labs does

- Self-description (matches the job posting almost verbatim): "we design, build, and manage
  digital and AI-powered products for technology and social impact ventures... a product studio
  that lives at the intersection of business consulting and technology. Our clients are mid-market
  operating companies. The products we build for them are usually internal: tools and AI workflows
  that make their operations..." [local DB job description, job id 11817; corroborated by
  teloslabs.co homepage and services pages].
- Service lines: Strategy & Design (a "3-week Strategic Assessment" that maps client operations and
  automation opportunities), Build & Launch (MVP builds in roughly 3 to 5 weeks, fractional CTO
  work), and AI Systems (workflow automation, copilots, RAG, and "agentic flows scoped for
  utility"), explicitly positioned as "production AI wired into real systems, not slide decks"
  [teloslabs.co/services].
- Target clients: mid-market companies, with named sector focus in legal, fintech, and social
  impact; named client/partner logos across case studies include Law Insider, SimpleDocs,
  SaverLife, FiscalNote, Jericho Security, and Truss [teloslabs.co homepage and case studies].
- Founded 2017 by Jordan G. Trevino (Yale graduate, also founder/CTO of SimpleDocs, an AI-driven
  legal contract-review product) in Berkeley, California [web search: Crunchbase person profile,
  LinkedIn]. No public venture funding round for Telos Labs itself was found in this research; it
  reads as a bootstrapped, revenue-funded consultancy/studio rather than a venture-backed startup,
  though absence of a funding announcement is not proof none exists.
- January 2026: Telos Labs acquired Flourish Fi, a behavioral loyalty and financial-engagement
  platform for banks and fintechs, used by PicPay, BancoSol, Carrefour Bank, and the Pennsylvania
  Treasury among "dozens of institutions across the Americas" [flourishfi.com press release, dated
  January 28, 2026]. CEO Jordan Trevino framed it as combining "behavioral insight and real-world
  fintech execution" to help clients ship "AI-powered experiences that are effective, scalable, and
  regulator-ready" [same source]. This is the single clearest, most recent, dated news item found
  for the company.
- Team: roughly 20 people total per the "about us" page (6 named leads plus "14 additional software
  engineers and one operations associate"), explicitly described as spanning backgrounds from
  Venezuela, Mexico, Brazil, and Chile [teloslabs.co/about-us]. Named leadership: Jordan G. Trevino
  (Company Lead/CEO), Pedro Moura (Operating Partner, fintech background including Morgan Stanley,
  Chase, and Oportun), Sergio Alvarez (Engineering Lead), Claudia Galvis (Product Manager & Ops
  Lead), Arely Rivera and Alejandra Zapata (Digital Product Designers) [teloslabs.co/about-us].
  The presence of Mexico City and Monterrey as stated company locations, plus multiple named
  Mexico/LatAm team members, is a real, sourced signal that the company already operates and hires
  in Mexico, not a first-time remote-Mexico experiment [teloslabs.co, about-us page].
- Reputation signal: 5.0/5 on Clutch across 5 reviews, with a quoted client (SaverLife's Senior
  Director of Product) describing them as "collaborative and quick to work with"
  [web search: clutch.co/profile/telos-labs].

## 2. Mission & product, in the client's own words

Mission statement: "tangible enhancement of our society through clarity of thought, creativity and
technology" [teloslabs.co/about-us]. In practice this shows up as a mix of purely commercial
fintech/legal-tech client work (Simple AI, a Word-integrated legal document review platform with an
AI chat assistant and compliance "Playbooks," distributed to 1.2 million users via a Law Insider
partnership and adopted by multinational banks [teloslabs.co/projects/simple-ai/]) and explicit
social-impact clients (SaverLife, Jericho Security) sitting inside the same practice
[teloslabs.co homepage; teloslabs.co/post/dear-pms-dont-miss-out-on-the-ai-fever].

## 3. Culture & voice

- A public blog post by Claudia Galvis ("Dear PMs, Don't Miss Out on the AI Fever") is the clearest
  voice sample available: pragmatic, mentoring, and explicitly cautious about hype, framing AI
  adoption for product managers around five competencies (recognizing AI's real potential beyond
  chatbots, offense-vs-defense feature strategy, working closely with data scientists, rigorous
  evaluation of AI performance, and ethical safeguards), stating directly that "we can't turn a
  blind eye to the fact that we don't understand the technology at its fullest"
  [teloslabs.co/post/dear-pms-dont-miss-out-on-the-ai-fever]. The tone throughout is accessible and
  jargon-light, grounded in named client examples (SimpleDocs, Jericho Security) rather than
  abstract claims.
- A second post, "What We Build at Telos (and What We Don't)," sets an explicit boundary: no
  branding, no fractional-CMO work, no acting as a generic "dev shop" or feature-order-taking IT
  department, and a stated willingness to push back on a client's own MVP scope if it does not
  solve the real problem, on the belief that "the software we build should be easy to extend, easy
  to support, and hard to break" [teloslabs.co/post/what-we-build-at-telos-and-what-we-dont]. This
  reads as a studio that positions itself as a product partner willing to say no, not a vendor that
  takes every brief.
- Four stated values: Purpose, Impact, Equality, and Drive [teloslabs.co/about-us].

## 4. Recent news (last ~12 months, dated)

- January 28, 2026: acquired Flourish Fi (behavioral loyalty/engagement platform for banks and
  fintechs, clients including PicPay, BancoSol, Carrefour Bank, Pennsylvania Treasury), expanding
  Telos Labs' fintech practice and combining behavioral-engagement product with Telos' engineering
  and AI delivery capability [flourishfi.com press release].
- Ongoing through at least June 2026: actively recruiting, including the target AI Engagement
  Manager role tagged to Nuevo Leon, Mexico and dated around June 22, 2026 on a Mexican job
  aggregator [web search snippet, mx.trabajo.org listing], though see the liveness caveat above.
- No other dated news (funding, leadership changes, layoffs) was found in this research; a small,
  founder-led studio of this size typically does not generate wide press coverage, so absence of
  news is not itself informative here.

## 5. Engineering & AI direction

- Stated AI stack/approach: integrations with both OpenAI and Anthropic for LLM functionality,
  Retrieval-Augmented Generation (RAG) and recommendation engines built on vector embeddings, and a
  general emphasis on "production AI wired into real systems, not slide decks" rather than
  proof-of-concept demos [teloslabs.co/services].
- Two service-line framing for AI work specifically: "Workflow Automation with AI" (automating
  recurring operational work, meant to go live "in weeks, in the tools you already use") and "AI
  for Product & Operations" (copilots, RAG, and agentic flows "scoped for utility," embedded "where
  it improves the user's real job to be done") [teloslabs.co/services].
- Case-study evidence of delivered work: Simple AI, an enterprise legal-tech product combining an
  AI-powered Word plugin, an in-app chat assistant, automated compliance review, and configurable
  "Playbooks" for standardizing legal review protocols, adopted by multinational banks and
  distributed through a Law Insider partnership to roughly 1.2 million users
  [teloslabs.co/projects/simple-ai/].
- Team composition skews engineering-heavy for a studio of its size (14 named engineers on a team
  of about 20), with an explicit LatAm hiring footprint (Venezuela, Mexico, Brazil, Chile)
  [teloslabs.co/about-us], consistent with a studio that staffs delivery work from the same region
  it is now hiring an Engagement Manager into.
- No specific backend/cloud stack (languages, frameworks, cloud provider) was disclosed on the
  public site beyond the AI/LLM layer described above; this is a real documentation gap, not an
  omission on this dossier's part.

## 6. The target role, as far as it could be reconstructed

Because the live posting could not be directly fetched (403/410, see liveness verdict), this
section relies on the local DB's captured description and third-party search summaries, both
flagged accordingly:
- Framing: "the Engagement Manager exists so that each engagement has one accountable owner. You
  are the person the client calls, the person who knows what matters this week, and the person who
  makes sure the pod is building the right thing... you manage engagements, not people" [web search
  summary of the live posting; not independently re-verified by direct fetch].
- Desired profile: an "AI-native mindset," treating AI as core to how the person thinks, builds, and
  delivers, not an add-on, plus a stated enthusiasm for continuous learning and for projects that
  improve people's lives [web search summary of the live posting].
- Clients: per the job's own "About Us" text captured in jobhunt's database, "most of our clients
  are based in the U.S." and the products built for them are "usually internal: tools and AI
  workflows that make their operations" more efficient [local DB job description, truncated at that
  point; job id 11817].
- Compensation: not found anywhere in this research; not listed in the DB-captured description
  snippet and not surfaced in any third-party mirror.

## 7. Why-fit angles for Santiago

Best hook to lead with, if the role turns out to still be open: the job's own self-description
("mid-market operating companies," "usually internal" tools and AI workflows, "one accountable
owner" for the engagement) is close to a direct match for how Santiago already operates at Pragma
AI, a B2B AI consultancy building tailor-made conversational agents, a RAG "company brain," and
internal automations for quoting, reporting, onboarding, and collections for Mexican SMB clients,
including running client diagnostics himself [resume/master_resume.yaml]. The "Engagement
Manager... you manage engagements, not people" framing also matches his founder history: at both
Eugenia.ai and Online Basics he owned the full client/product lifecycle without a large team behind
him [resume/master_resume.yaml].

Concrete transferable evidence:
- Pragma AI's flagship "Pragma Brain" (a RAG system with scoped retrieval, citation gating, and an
  eval harness) is a direct proof point for Telos Labs' own stated AI Systems work (RAG, copilots,
  "agentic flows scoped for utility") [resume/master_resume.yaml; teloslabs.co/services].
  Eugenia.ai's on-site client deployments (onboarding HOAs and property administrators, gathering
  requirements, translating conflicting needs into working software) map onto being "the person the
  client calls" and owning delivery end to end [resume/master_resume.yaml; web search summary of
  the posting].
- Bilingual Spanish (native)/English (fluent) fits a Mexico-based role serving mostly U.S. clients
  directly [resume/master_resume.yaml; local DB job description].

Honest concerns and watch-outs:
- The single biggest open question is whether this requisition still exists. The primary sources
  found return 403/410 and Telos Labs' own current careers page says roles aren't always posted;
  this should be confirmed by directly applying or emailing rather than assumed either way.
- Location: the only independently found copy of this exact listing tags Nuevo Leon, not Mexico
  City or generic "remote." Telos Labs does have a real Monterrey presence, so this is very
  plausibly fine, but the degree of expected physical presence (fully remote vs some on-site
  expectation in Monterrey) was not found and should be asked directly.
- Compensation is undocumented anywhere found in this research; for a small, apparently
  bootstrapped studio this is a genuine unknown, not just an omission, and should be raised early.
- This is an Engagement Manager role, i.e. client-relationship ownership rather than hands-on
  engineering; Santiago's strongest resume evidence is technical build work, so the honest framing
  in an interview is that the AI/product fluency is real and resume-backed, while the pure
  client-portfolio-management scope (managing multiple concurrent "pods"/engagements at once,
  rather than one company at a time as a founder) is a real stretch versus anything explicitly
  documented in his history.

## 8. Sources

- Local jobhunt DB, job id 11817 (captured job description snippet: self-description as a product
  studio, "mid-market operating companies," "usually internal" tools/workflows, U.S.-based clients;
  posted_at 2026-07-01, first_seen 2026-07-16, last_seen 2026-07-21)
- https://www.adzuna.com.mx/land/ad/5784465925 and the DB-stored variant with utm params (both
  returned HTTP 403 Forbidden on direct fetch; used only to establish that this exact mirror could
  not be independently re-verified today)
- https://mx.trabajo.org/oferta-5568-9e37f18886d672d09880eb750520addd (returned HTTP 410 Gone on
  direct fetch; a web-search snippet of this same URL, captured separately, showed "AI Engagement
  Manager en Nuevo Leon, Nuevo Leon - Telos Labs" dated around June 22, 2026, used as the only
  location signal for the specific role; the 410 status itself is evidence the page was later
  taken down)
- https://www.teloslabs.co/ (homepage: self-description, service lines, client logos)
- https://www.teloslabs.co/about-us (mission statement, values, founding year, full leadership and
  team roster, team geographic distribution)
- https://www.teloslabs.co/services (AI Systems and Workflow Automation service descriptions, AI
  stack mentions: OpenAI, Anthropic, RAG, vector embeddings)
- https://www.teloslabs.co/projects/simple-ai/ (Simple AI legal-tech case study: product
  description, distribution/user-count claims, client sector)
- https://www.teloslabs.co/post/what-we-build-at-telos-and-what-we-dont (culture/voice: explicit
  scope boundaries, product-partner positioning)
- https://www.teloslabs.co/post/dear-pms-dont-miss-out-on-the-ai-fever (culture/voice: AI
  philosophy, written by Claudia Galvis, Product Manager & Ops Lead)
- https://www.teloslabs.co/join-us (current careers page, fetched 2026-07-28: no roles formally
  posted, general-interest application form only, used for the liveness caveat)
- https://www.flourishfi.com/new-article/telos-labs-acquires-flourish-fi-to-expand-its-ai-driven-fintech-and-engagement-platform
  (Flourish Fi acquisition announcement, dated January 28, 2026: deal rationale, named Flourish Fi
  clients, CEO quote)
- Web search results distinguishing this Telos Labs (teloslabs.co, Berkeley, Jordan Trevino, 2017)
  from telos-labs.com, Telos Corporation, and an unrelated Web3/gaming "Telos Labs" LinkedIn jobs
  listing (used for the disambiguation section)
- Web search: Crunchbase person profile for Jordan Trevino, LinkedIn profile (founder background,
  SimpleDocs connection, Yale, founding year 2017, Berkeley HQ)
- Web search summary of Clutch.co profile for Telos Labs (5.0/5 rating across 5 reviews, quoted
  client testimonial)
- Web search summaries of the live AI Engagement Manager posting via third-party job boards
  (role framing: "one accountable owner," "manage engagements, not people," AI-native mindset ask;
  could not be independently re-verified by direct fetch, flagged accordingly throughout Section 6)
- /Users/santiagocoronado/jobhunt/resume/master_resume.yaml (Santiago's verified experience: Pragma
  AI, Eugenia.ai, Online Basics, used for the why-fit section)
- /Users/santiagocoronado/jobhunt/config/profile.yaml (location_rule, used for the eligibility
  verdict)

Note for Santiago: this is a draft dossier. The company itself (Telos Labs / teloslabs.co) is
reasonably well documented through its own site and one dated acquisition announcement, but the
specific job posting is thin and its current liveness is genuinely in question (410 Gone on the
Mexican aggregator copy, 403 on both Adzuna mirrors, and a "roles aren't always posted" careers
page). Please confirm directly whether this requisition is still open, what the actual location
expectation is (Nuevo Leon on-site versus remote), and what compensation looks like, before this
feeds into a cover letter or application answers.
