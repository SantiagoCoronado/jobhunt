# Grupo Financiero Banorte

Draft dossier for Santiago's review. Researched for job id 19548, "Cientifico de Datos,
Subdirector de Generative AI Engineering" (Adzuna MX, Mexico City, posted 2026-08-15).

## 1. Snapshot

Grupo Financiero Banorte is one of Mexico's four largest commercial banking groups by assets
and loans, publicly listed (BMV: GFNORTE, Madrid: XNOR), headquartered across Monterrey and
Mexico City, with roughly 1,269 branches and 7,297 ATMs and about 27,000 employees as of 2021
(most recent public headcount found). It is the only major Mexican bank not foreign-owned. Q2
2026 results: net income of MXN 15.55 billion (up 6 percent year over year), total revenue of
MXN 43.15 billion (up 12 percent), loan book of MXN 1.27 trillion (up 8 percent), ROE of 25.7
percent. (Sources: Wikipedia, Q2 2026 press coverage.)

## 2. Core narrative

Banorte has spent the last two years pushing generative AI from a single flagship product
(its Maya virtual assistant, live since 2018) into an org-wide engineering capability: in May
2024 it became the first bank in Mexico authorized by the CNBV to run AI models in the cloud,
and in May 2026 Red Hat gave Banorte a Latin America Honorable Mention for standing up Red Hat
OpenShift AI as a central platform for building and scaling internal AI tools (incident
diagnosis assistants, IT requirement generation, and more), explicitly to "democratize" AI
access across the bank. This "Subdirector de Generative AI Engineering" role reads as the next
step in that arc: converting a proven consumer-facing assistant and a newly authorized cloud/AI
platform into scaled, production GenAI engineering across the organization.

## 3. Mission & product

Banorte is a full-service financial group: commercial banking, pensions (it runs Mexico's
largest AFORE retirement-fund administrator), insurance, brokerage, leasing, and factoring,
operating under the Banorte and (formerly) Ixe brands. Its stated mission language, echoed
verbatim in the job posting, frames the company as wanting to be "a great ally to grow strong
with Mexico," built on solidarity, innovation, respect, loyalty, and responsibility. Its
best-known AI product is Maya, a virtual assistant embedded in Banorte Movil and web banking
since 2018, reachable via chat, voice, Google Assistant/Home, and Amazon Alexa. As of the most
recent reporting found, Maya handles roughly 2.5 million messages a month with over 90 percent
first-contact resolution, and can execute around 17 to 18 monetary operations (transfers, bill
pay, card blocking, balance/statement lookups) plus several hundred distinct query types.
(Sources: Wikipedia, Banorte.com press release on Maya, Publimetro, Carlos Hank Gonzalez site,
ITMastersMag.)

## 4. Culture & voice

Public-facing culture language (used in Banorte's own careers copy and repeated in this job
posting) centers on "talento unico, fuerte y extraordinario" and five values: solidaridad,
innovacion, respeto, lealtad, responsabilidad. Banorte frames itself explicitly as a national
champion, the only major Mexican-owned bank among the big four, and ties its brand to the
country (2026 FIFA World Cup tie-in: it acquired the naming rights to Estadio Azteca, now
Estadio Banorte, in March 2025). Its AI leadership speaks publicly about a "human-digital"
model, positioning AI as augmenting rather than replacing relationship banking (Olga Ceja,
Executive Director of AI and Innovation, quoted on this framing). (Sources: Wikipedia,
Banorte careers page language embedded in job posting, ITMastersMag.)

## 5. Recent news (last ~12 months)

- 2026-08-15: Posted this "Subdirector de Generative AI Engineering" role in Mexico City,
  tasked with leading the design, implementation, and scaling of generative AI (posting text
  truncated beyond this line; full scope not independently confirmed). (Source: Adzuna listing,
  job id 19548.)
- 2026-07-21/22: Q2 2026 results reported: net income MXN 15.55 billion (+6% YoY), total
  revenue MXN 43.15 billion (+12% YoY), loan portfolio MXN 1.27 trillion (+8% YoY), ROE 25.7
  percent, ROA 2.3 percent. (Sources: El Universal, MVS Noticias, Uniradio Informa.)
- 2026-05-14: Red Hat named Banorte (alongside IMSS) a 2026 Latin America Honorable Mention for
  digital transformation, citing Banorte's use of Red Hat OpenShift AI as its central platform
  for advanced AI model development and internal-data-processing architectures, and for shipping
  intelligent assistants that cut incident diagnosis and IT requirement-gathering work from
  months to weeks. (Source: infochannel.info.)
- 2024-05 (just outside the 12-month window but foundational context): the CNBV authorized
  Banorte to run AI models in the cloud, making it the first bank in Mexico with that
  authorization; Banorte's AI and Innovation Executive Director Olga Ceja said the move would
  improve language comprehension, speed up model training, and enable faster, more personalized
  feature rollout for tools like Maya. (Source: ITMastersMag.)
- 2025-03: Banorte acquired the naming rights to Estadio Azteca (now Estadio Banorte) ahead of
  the 2026 FIFA World Cup, a large public brand investment, not AI-related but relevant as a
  signal of Banorte's national-champion positioning and marketing scale. (Source: Wikipedia.)

## 6. Engineering & AI direction

- Cloud-hosted AI models: Banorte moved from fully on-premise AI infrastructure to CNBV-
  authorized cloud hosting for its models starting 2024, specifically to unlock real-time
  inference and larger compute for language understanding and faster training/iteration cycles.
  (Source: ITMastersMag; cloud vendor not specified in any source found, do not assume a
  specific provider.)
- Internal AI platform: Red Hat OpenShift AI is the named central platform for developing and
  scaling Banorte's AI models and specialized data-processing architectures, per Red Hat's own
  2026 recognition. (Source: infochannel.info.)
- Internal-tooling GenAI: Banorte has already shipped internal assistants for incident diagnosis
  and for generating IT project requirements, explicitly framed as cutting multi-month workflows
  to weeks, and states a goal of democratizing AI tooling access org-wide in a secure, scalable
  way. (Source: infochannel.info.)
- Customer-facing GenAI: Maya remains the flagship product surface, in continuous iteration
  since 2018, now handling millions of monthly conversational interactions and dozens of
  transaction types; Banorte's AI leadership (Alejandro D'Leon, senior AI specialist; Olga Ceja,
  Executive Director of AI and Innovation) publicly frames the next phase as deeper
  personalization using customer data, plus AI/ML for fraud and anti-money-laundering
  monitoring. (Sources: Forbes Mexico, ITMastersMag.)
- No engineering blog, public GitHub, or detailed stack disclosure (languages, model vendors,
  vector/RAG infrastructure) was found in public sources; treat Banorte's GenAI engineering
  stack as unverified beyond "cloud-hosted, Red Hat OpenShift AI as a platform layer."

## 7. Why-fit angles for Santiago

Strongest hook: Santiago has already built and shipped the exact category of system this role
sounds like it owns at enterprise scale. Pragma AI's "Pragma Brain" is a production RAG
"company brain" with scoped retrieval, deterministic no-answer/citation gating, and an
automated eval harness, and Online Basics ran a $8M-revenue operation on his own LLM workflows
(Anthropic/OpenAI APIs, prompt engineering, multi-stage validation) plus internal data
pipelines. That is a real, defensible answer to "have you designed and scaled generative AI
systems," just at founder scale rather than at 27,000-employee-bank scale.

Second hook: Banorte's own framing (turning point-solution GenAI, Maya, into org-wide
platform-level AI engineering via OpenShift AI) mirrors Santiago's Pragma AI arc of turning a
single client RAG tool into a reusable internal MCP platform (per-operator tokens, 15 agent
definitions, 10 reusable routines) used across the firm. That is the more literal analogy to
"scaling GenAI engineering" than a chatbot comparison.

Honest concerns and watch-outs:
- Scale gap: Santiago's largest team was 9 people; this is a Subdirector (director-level) role
  at a bank with roughly 27,000 employees and heavy regulatory/compliance overhead (CNBV
  oversight, banking-grade security). He has no direct experience in regulated financial
  services or with a CNBV-style compliance environment; this should be acknowledged, not
  glossed over, if asked about gaps.
- The job posting text pulled via Adzuna is truncated after "Objetivo del puesto: Liderar el
  diseno, implementacion y escalamiento..."; the full scope, team size, and reporting line for
  this specific role were not independently found in public sources. Treat detailed
  responsibilities as unconfirmed until the full JD or an interview clarifies them.
- No confirmed detail on Banorte's specific model vendors, cloud provider for AI workloads, or
  whether the role is IC-heavy or purely managerial; Santiago's strongest asset (hands-on
  building) should be framed carefully until that is clarified.

## 8. Application-question angles

- Why this company: lean on Banorte's public pivot from a single AI product (Maya) to org-wide
  GenAI platform engineering (CNBV cloud authorization, Red Hat OpenShift AI, internal
  assistants cutting months of IT work to weeks). Frame interest around joining at the exact
  moment a large, Mexican-owned institution is trying to scale GenAI past one product into a
  platform, which is the same transition Santiago has driven at much smaller scale.
- Why you fit: lead with the concrete RAG/GenAI systems he has actually shipped and operated
  (Pragma Brain's retrieval and eval harness, Online Basics' LLM content pipeline at $8M scale)
  rather than a generic AI-enthusiasm pitch. Be candid that his scale reference point is
  founder-team-sized, not bank-sized, and pitch that as fast, hands-on execution experience
  translating well to standing up new GenAI capability quickly.
- Anything else: worth naming, if relevant, that he is Mexico City based and bilingual ES/EN,
  which matters for a role explicitly framed around Mexico ("un gran aliado para crecer fuerte
  con Mexico"), without overplaying a generic patriotism angle he cannot substantiate.

## Sources

- researched: 2026-08-17
- [Adzuna job posting (job id 19548, internal DB)](https://www.adzuna.com.mx/land/ad/5843062730): posting title, location, truncated JD text, posted date 2026-08-15
- [Banorte, Wikipedia](https://en.wikipedia.org/wiki/Banorte): HQ, founding, size (assets/employees/branches/ATMs), stock listings, business lines, Estadio Azteca naming rights
- [Banorte ya puede usar la nube para sus modelos de AI, ITMastersMag](https://www.itmastersmag.com/inteligencia-artificial/banorte-ya-puede-usar-la-nube-para-sus-modelos-de-ai-es-el-primer-banco-en-mexico-con-autorizacion/): CNBV cloud AI authorization (May 2024), Maya usage stats, Olga Ceja quotes
- [IMSS y Banorte destacan por sus proyectos de IA, infochannel.info](https://infochannel.info/imss-y-banorte-destacan-por-sus-proyectos-de-ia-y-modernizacion-tecnologica/): Red Hat OpenShift AI platform, 2026 Red Hat Honorable Mention, internal AI assistants (incident diagnosis, IT requirements), published 2026-05-14
- [Banorte presenta a Maya, banorte.com](https://www.banorte.com/wps/portal/gfb/Home/noticias-banorte/2022/banorte-presenta-a-maya): Maya launch and product description (company primary source)
- [Banorte's virtual assistant Maya named one of the world's best banking AI innovations](https://carloshankgonzalez.com/banortes-virtual-assistant-maya-named-one-of-the-worlds-best-banking-ai-innovations/): Maya recognition and capability detail
- [Inteligencia artificial es clave para agilizar y mejorar servicios: Banorte, Forbes Mexico](https://forbes.com.mx/inteligencia-artificial-es-clave-para-agilizar-y-mejorar-servicios-banorte/): Alejandro D'Leon (AI specialist) commentary on Maya evolution, personalization, fraud/AML AI use
- [Crece utilidad de Banorte en segundo trimestre de 2026, El Universal](https://www.eluniversal.com.mx/mundo/crece-utilidad-de-banorte-en-segundo-trimestre-de-2026-el-banco-reporta-15-mil-550-millones-de-pesos/): Q2 2026 net income figure
- [Eleva Banorte 6% su utilidad en el segundo trimestre de 2026, MVS Noticias](https://mvsnoticias.com/economia/2026/7/22/eleva-banorte-6-su-utilidad-en-el-segundo-trimestre-de-2026-739209.html): Q2 2026 revenue, loan book, ROE/ROA figures
- [Crece utilidad de Banorte en segundo trimestre de 2026, Uniradio Informa](https://www.uniradioinforma.com/negocios/crece-utilidad-banorte-segundo-trimestre-2026-n895604): corroborating Q2 2026 results
