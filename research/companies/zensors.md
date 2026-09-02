# Zensors (Zensors AI / Zensors Inc.)

Draft dossier for Santiago's review. Researched 2026-07-16.

## 1. Snapshot
Zensors builds "Physical AI" that turns existing security/CCTV cameras into real time spatial
intelligence (queue times, occupancy, staffing signals) for airports, transit, retail, and
commercial real estate; spun out of Carnegie Mellon's Human-Computer Interaction Institute,
Y Combinator S21, roughly 22 to 23 employees, headquartered in San Francisco, only publicly
disclosed funding is a $125K YC seed check (no later round found in public sources).

## 2. Core narrative
A ~22-person CMU spinout turned its academic computer-vision research into mission-critical
infrastructure for the TSA and some of the busiest airports in North America (Boston Logan,
Harry Reid Las Vegas, Pittsburgh, Toronto Pearson), doing it by reusing customers' existing
cameras instead of selling new hardware. That "no new hardware, real savings" pitch produced
concrete numbers (over $5M in avoided capital costs and $140K in annual savings at one airport)
and, as of June 2026, a formal role in setting the TSA's new nationwide "Real Time Wait Time"
standard. This is a small team punching well above its headcount on government-grade deployments.

## 3. Mission & product
- Mission: "AI to automate physical world processes between humans, buildings & machines,"
  aiming to make advanced spatial intelligence accessible without an in-house ML team
  ([About page](https://www.zensors.com/company/about-zensors-vision-ai)).
- Product: two AI layers, "Momenta AI" (multimodal video understanding) and "Hologram AI"
  (spatial data structuring), power two offerings: Zensors Spatial AI (a data platform) and
  Zensors Virtual Manager (operations automation) ([homepage](https://www.zensors.com/)).
- Business model: software-only SaaS that ingests existing camera feeds (a network gateway
  device plus cloud AI) rather than requiring new sensor hardware; CEO Anuraag Jain: "we are a
  software company, not in the hardware business"
  ([Forbes, Feb 28 2026](https://www.forbes.com/sites/jonathanreichental/2026/02/28/how-leaders-can-capture-a-hidden-opportunity-in-physical-ai/)).
- Customers/sectors: aviation and transit, retail, and commercial real estate. Named accounts:
  Harry Reid International Airport (Las Vegas), Toronto Pearson, Pittsburgh International,
  Sydney Airport, NJ Transit, CBRE, and now TSA/Boston Logan
  ([NVIDIA case study](https://www.nvidia.com/en-us/case-studies/zensors-ai-las-passenger-experience/);
  [TSA press release, June 4 2026](https://www.globenewswire.com/news-release/2026/06/04/3306770/0/en/zensors-physical-ai-enables-tsa-s-new-standard-for-real-time-passenger-experience.html)).
- Compliance: GDPR and SOC 2 Type II certifications are surfaced on the homepage, signaling
  enterprise/government-grade posture despite the small team ([homepage](https://www.zensors.com/)).

## 4. Culture & voice
- Founders: Anuraag Jain (CEO, Head of Product and Technology, prior data work at Terminal and
  Palantir) and Chris Harrison (Director, CMU Future Interfaces Group, Forbes 30-under-30,
  MIT Tech Review 35-under-35) ([About page](https://www.zensors.com/company/about-zensors-vision-ai)).
- Stated values: solving real-world business problems through collaboration, measurable business
  impact and customer success over abstract technology, and human-centered, design-driven
  innovation ([About page](https://www.zensors.com/company/about-zensors-vision-ai)).
- Careers page tone: describes itself as "a fast-growing tech startup searching for flexible
  go-getters" and wants "mission-driven Swiss-Army knives" willing to wear multiple hats
  ([careers.zensors.com](https://careers.zensors.com/jobs)).
- Leans hard on academic pedigree in its own narrative ("spun out of Carnegie Mellon, the
  birthplace of artificial intelligence") ([About page](https://www.zensors.com/company/about-zensors-vision-ai)).
- Industry visibility: founding member of the Airports AI Alliance alongside NVIDIA and AWS,
  convened by the Cities Today Institute to accelerate AI adoption in aviation (announced 2024,
  still listed as an active affiliation) ([PR Newswire](https://www.prnewswire.com/news-releases/leading-industry-players-join-forces-to-establish-an-alliance-to-accelerate-ai-adoption-in-aviation-302158213.html);
  [Airports AI Alliance member page](https://www.airportsalliance.ai/our-members/zensors-ai/)).

## 5. Recent news (last ~12 months)
- June 4, 2026: Zensors' "Hologram" Physical AI platform selected by the TSA to power a new
  nationwide "TSA Real Time Wait Time" standard at security checkpoints; Boston Logan is among
  the first airports live across all checkpoints, tracking bag-screening time, throughput, and
  search rates ([GlobeNewswire](https://www.globenewswire.com/news-release/2026/06/04/3306770/0/en/zensors-physical-ai-enables-tsa-s-new-standard-for-real-time-passenger-experience.html)).
- February 28, 2026: Featured in Forbes coverage of "physical AI," with CEO Anuraag Jain
  detailing the software-gateway approach and the Harry Reid International Airport (Las Vegas)
  deployment across 500+ existing cameras
  ([Forbes](https://www.forbes.com/sites/jonathanreichental/2026/02/28/how-leaders-can-capture-a-hidden-opportunity-in-physical-ai/)).
- Undated (recent, per NVIDIA's case-study page): NVIDIA published a customer story on the Harry
  Reid deployment, citing over $5M in avoided capital costs and $140K in annual operational
  savings from converting existing cameras rather than installing new sensors
  ([NVIDIA case study](https://www.nvidia.com/en-us/case-studies/zensors-ai-las-passenger-experience/)).
- Watch-out: no public funding round beyond the original $125K YC seed (Summer 2021) turned up
  in this research; treat any claim of a later raise as unverified until confirmed directly with
  the company ([YC profile](https://www.ycombinator.com/companies/zensors-inc)).

## 6. Engineering & AI direction
- Core AI bet: "Physical AI," foundation models and spatial ontologies applied to video and
  sensor streams, positioned as a replacement for traditional point-solution IoT sensors
  ([homepage](https://www.zensors.com/); [About page](https://www.zensors.com/company/about-zensors-vision-ai)).
- ML infrastructure stack (from an active AI/ML Infrastructure Engineer posting): PyTorch, CUDA,
  C/C++, TensorRT, NVIDIA DeepStream and DALI, ONNX Runtime, ML compilers (TVM, MLIR),
  quantization/pruning/distillation of Vision Transformers and CNNs, Nsight profiling, and
  SQL/graph (Neo4j) data systems
  ([YC job posting](https://www.ycombinator.com/companies/zensors-inc/jobs/O6towJf-ai-ml-infrastructure-engineer)).
- Production video pipeline (per NVIDIA case study): NVIDIA Dynamo-Triton for inference scaling,
  TensorRT, CUDA/cuDNN, NVIDIA Metropolis for video analytics, and DALI for data loading,
  processing "spiky and heterogeneous" video workloads at real-time scale
  ([NVIDIA case study](https://www.nvidia.com/en-us/case-studies/zensors-ai-las-passenger-experience/)).
- Frontend stack for this open role: React with TypeScript, CSS/SCSS (cross-browser, flexbox),
  component-driven development for reusable modules, Git; Node.js, Docker, and PostgreSQL called
  out as a plus, implying the frontend talks to a Node/Postgres-adjacent backend
  ([Freshteam posting](https://zensors.freshteam.com/jobs/Qc_VY1AEfbC5/frontend-web-developer-react-typescript-remote)).
- Open engineering roles beyond this one skew ML infra and ML/DevOps systems (San Francisco,
  onsite), suggesting the core AI/vision engineering org is concentrated in-office while frontend
  is the team's remote-friendly discipline ([careers.zensors.com](https://careers.zensors.com/jobs)).

## 7. Why-fit angles for Santiago
Best hook to lead with: Santiago has repeatedly built the exact kind of artifact Zensors sells,
a data-dense operational dashboard that turns messy real-time signals into decisions for
non-technical operators. At Online Basics he built the company's internal React front end
(pricing dashboard, inventory admin panel, alerting) that ran a $8M-revenue business day to day
for a lean 7-person team; at Eugenia.ai he shipped a React/Node platform used by 10,000+ users
across 20+ buildings; in Plutus he built an 11-route React/TypeScript app with live charting and
a real-time WebSocket/SSE layer. Zensors' Virtual Manager (turning airport/retail camera data
into staffing and queue decisions for operators) is the same problem shape, just a different
vertical. That maps directly onto his two strongest role families (frontend engineering and
internal tooling) per his profile notes.

Secondary hook: Zensors' own careers language ("flexible go-getters," "Swiss-Army knives" on a
~22-person team) matches his founder background of wearing every hat across three ventures
(product, engineering, client-facing deployment), which is a real differentiator versus a
typical frontend-only candidate.

Honest concerns / watch-outs:
- The posting is titled "Frontend Web Developer React/Typescript (Remote, Internship)" on
  Zensors' own careers page, while the WeWorkRemotely/Freshteam listing requires 3+ years of
  experience across UI/UX, responsive CSS, and React. That is an unresolved seniority/level
  mismatch worth clarifying early rather than assuming it is a senior IC role
  ([careers.zensors.com](https://careers.zensors.com/jobs);
  [Freshteam posting](https://zensors.freshteam.com/jobs/Qc_VY1AEfbC5/frontend-web-developer-react-typescript-remote)).
- No salary is published anywhere found; confirm compensation expectations early given his
  $65K USD floor.
- This specific role is pure frontend, no LLM/agent/AI-building scope, so it does not exercise
  his applied-AI experience (RAG, agents, prompt engineering); frame the application around the
  frontend/internal-tooling narrative rather than the AI-builder narrative.
- The company's only disclosed funding is a $125K YC seed from 2021 despite visible enterprise
  and government traction (TSA, major airports); this could mean lean runway on a small team, or
  simply an unannounced later round. Worth a direct question in the process, not a resume risk.

## 8. Application-question angles
- Why this company: lead with the "physical AI that reuses your existing cameras" story and the
  jump from a CMU research spinout to becoming part of the TSA's new national wait-time standard
  at Boston Logan. This is a company proving physical-world AI in the hardest possible
  environment (federal security infrastructure) with a lean team, not a hype-cycle AI product.
- Why you fit: lean on the "I have already built this exact artifact" angle, specifically the
  internal operations platform he built and ran at Online Basics (React front end over SQL and
  Python ETL, used daily to run pricing and inventory for an $8M business) as the closest analog
  to Zensors' Virtual Manager, plus the React/TypeScript depth from Eugenia.ai and Plutus.
- Anything else: mention comfort operating as a generalist on a small team (founder background
  across three companies, doing product, engineering, and client deployment at once), which
  matches how Zensors describes itself hiring for a ~22-person team.

## 9. Sources
- researched: 2026-07-16
- [Zensors homepage](https://www.zensors.com/) - product (Momenta/Hologram AI, Spatial AI,
  Virtual Manager), sectors, compliance certifications
- [About Zensors Vision AI](https://www.zensors.com/company/about-zensors-vision-ai) - mission,
  founding story, founders, stated values
- [Zensors careers](https://careers.zensors.com/jobs) - open roles list, hiring tone/culture
  language
- [Freshteam: Frontend Web Developer React/Typescript posting](https://zensors.freshteam.com/jobs/Qc_VY1AEfbC5/frontend-web-developer-react-typescript-remote) -
  full text of this role's responsibilities and requirements
- [Y Combinator: Zensors profile](https://www.ycombinator.com/companies/zensors-inc) - batch
  (S21), team size, HQ, mission statement
- [Y Combinator: AI/ML Infrastructure Engineer posting](https://www.ycombinator.com/companies/zensors-inc/jobs/O6towJf-ai-ml-infrastructure-engineer) -
  ML infra stack, salary band, visa sponsorship note
- [NVIDIA case study: Zensors AI at Harry Reid International Airport](https://www.nvidia.com/en-us/case-studies/zensors-ai-las-passenger-experience/) -
  video pipeline stack, deployment scale, savings figures
- [Forbes, Feb 28 2026: How Leaders Can Capture a Hidden Opportunity in Physical AI](https://www.forbes.com/sites/jonathanreichental/2026/02/28/how-leaders-can-capture-a-hidden-opportunity-in-physical-ai/) -
  founding story, CEO quotes, Harry Reid deployment detail
- [GlobeNewswire, June 4 2026: Zensors physical AI enables TSA's new standard for real-time
  passenger experience](https://www.globenewswire.com/news-release/2026/06/04/3306770/0/en/zensors-physical-ai-enables-tsa-s-new-standard-for-real-time-passenger-experience.html) -
  TSA partnership, Boston Logan deployment, leadership quote
- [PR Newswire: Airports AI Alliance formation](https://www.prnewswire.com/news-releases/leading-industry-players-join-forces-to-establish-an-alliance-to-accelerate-ai-adoption-in-aviation-302158213.html)
  and [Airports AI Alliance member page](https://www.airportsalliance.ai/our-members/zensors-ai/) -
  founding-member status alongside NVIDIA and AWS
- [Zensors company LinkedIn](https://www.linkedin.com/company/zensors) - headcount (22-23),
  recent post summaries (TSA, airport deployments)
- Job posting used for role context (WeWorkRemotely mirror of the same Freshteam listing):
  https://weworkremotely.com/remote-jobs/zensors-frontend-web-developer-react-typescript-remote
