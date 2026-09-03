# MongoDB, company dossier

Draft for Santiago's review. Researched: 2026-09-02.

## Snapshot

MongoDB (NASDAQ: MDB) is a publicly traded developer data platform company, founded 2007, headquartered in New York City, with 5,000+ employees and an office in Mexico City. FY2026 (year ended January 31, 2026) revenue was $2.46 billion, up 23% year over year; the most recent quarter (reported September 1, 2026) grew revenue 30% year over year to $771.8 million, its fastest quarterly growth since fiscal 2024. Over 70,600 customers as of July 31, 2026.

## Core narrative

MongoDB has repositioned from "modern document database" to "the database built for the AI era." Its centerpiece move was the February 2026 acquisition of Voyage AI, an embedding and reranking model company, which MongoDB is folding directly into Atlas so AI applications can retrieve grounded, hallucination-resistant context from live operational data instead of bolting on a separate vector store and embedding pipeline. That AI-platform bet is showing up in the numbers: the quarter reported September 1, 2026 was MongoDB's fastest revenue growth since fiscal 2024, with Atlas up about 29% year over year and a record 2,900 new customer additions. The pre-sales Solutions Architect is the person who turns that "unified AI-ready platform" pitch into a proof of value in front of a specific customer's engineers, which is exactly the seat open in Mexico City.

## Mission & product

MongoDB's stated mission is to "empower innovators to create, transform, and disrupt industries by unleashing the power of software and data" (mongodb.com/company). The core product is MongoDB Atlas, a fully managed, multi-cloud document database available on AWS, Google Cloud, and Azure, bundling Atlas Search, Atlas Vector Search, Atlas Stream Processing, Atlas Data Lake, Charts, and a Relational Migrator; MongoDB Enterprise Advanced is the self-managed alternative for on-prem or regulated customers (JD, mongodb.com/company). Atlas is now the majority of revenue: 75% of total revenue in the most recent reported quarter (JD text; corroborated by the mongodb.com/company product framing). The business model is subscription/consumption based, sold to more than 67,000 customers in over 100 countries, including 75% of the Fortune 100, spanning AI-native startups to large enterprise IT organizations (JD).

The February 2026 Voyage AI acquisition is the current product center of gravity: MongoDB is integrating it in phases, starting with automated Voyage AI embeddings for Atlas Vector Search and an Embedding and Reranking API (including voyage-code-4), then native reranking, then advanced multi-modal retrieval. It has also added vector search inside Atlas Stream Processing so AI applications can pull real-time context from live operational data, not just static stores. The pre-sales Solutions Architect motion sits directly on top of this stack: SAs pair with sales executives on technical discovery, demos, proof-of-value engagements, sizing, and documentation that turn the Atlas and AI pitch into a signed deal. In LATAM specifically, MongoDB is hiring this motion locally out of a Mexico City hybrid hub rather than covering the region from the US.

## Recent news (2026)

- February 2026: MongoDB announced the acquisition of Voyage AI, an embedding and reranking model company, to reduce hallucinations in AI applications by giving them better grounded retrieval.
- 2026 (MongoDB.local San Francisco): MongoDB detailed a three-phase Voyage AI integration into Atlas: broad availability of Voyage's models, then automated embeddings plus native reranking inside Atlas Vector Search, then advanced multi-modal retrieval, framed as making AI systems hold up on live data and real workloads.
- Company also announced automated Voyage AI embeddings in Atlas Vector Search, an Atlas Embedding and Reranking API, the voyage-code-4 model, and vector search added to Atlas Stream Processing.
- September 1, 2026: MongoDB reported quarterly revenue of $771.8 million, up 30% year over year (its fastest quarterly growth since fiscal 2024), non-GAAP operating margin expanding to 24% from 15% a year earlier, Atlas growth of about 29% year over year, a record 2,900 new customer additions, and net revenue retention of 122%. Shares fell despite the beat.
- Full fiscal year 2026 (ended January 31, 2026): total revenue of $2.46 billion, up 23% year over year, with subscriptions at 97% of revenue.
- As of July 31, 2026: over 70,600 customers, up from over 59,900 a year earlier.

## Culture & hiring signals

MongoDB frames its "Leadership Commitment" as the company's compass, guiding employees to "deliver the right outcomes for customers, live MongoDB's values in everything they do, and engage with each other as leaders" (JD, mongodb.com/company). The company was named to Built In's 2026 Best Places to Work list and was recognized on Glassdoor's 2025 list. Stated employee benefits include affinity groups, fertility assistance, and a generous parental leave policy (JD, linking to mongodb.com's culture blog).

Mexico City is a real hybrid hub rather than a token satellite: MongoDB runs an office in the Molino del Rey area of Mexico City (IOS Offices Virreyes, Pedregal 24) and has multiple concurrent hybrid Mexico City postings beyond this role (for example an Account Development Representative and a Senior Specialist, Industry Solutions), consistent with active local team-building rather than a single one-off req.

For the pre-sales Solutions Architect track specifically, public candidate reports (Glassdoor) describe a long, multi-stage loop: recruiter screen, hiring manager conversation, a technical interview, a director/VP or sales-leadership interview, and a take-home "challenge" presentation. Pre-sales SA roles are cited by candidates as one of MongoDB's slower hiring processes, commonly around 180 days. Technical questions reported are broad (REST, ORM, JSON/XML conversion, ACID) and candidates note that familiarity with a sales methodology (MEDDPICC or similar) helps; one summary describes the ideal profile as "a salesperson with technical skills" rather than a pure architect. Unverified beyond individual candidate self-reports; treat as directional, not official policy.

## Target role

Solutions Architect / Sr. Solutions Architect (Pre-Sales), Mexico City, hybrid. Req ID 426369, Greenhouse job 8109873. Source: job posting text pulled via `src.query job 24703` (mongodb.com/careers/job/?gh_jid=8109873).

Responsibilities as stated in the posting:
- Design and architect scalable, performant applications, systems, and infrastructure for large software projects on MongoDB.
- Advise customers on architecture patterns and optimization strategies, and articulate MongoDB's business value to technical and business stakeholders.
- Partner with sales on account planning, opportunity qualification, and pipeline generation, owning the technical side of the deal cycle: discovery, demos, proof of value, presentations, sizing, and documentation.
- Generate demand proactively through self-driven technical initiatives, trade shows, and account-based marketing events.
- Build customer champions and drive customer success and satisfaction.
- Feed field feedback back to the product team and mentor other Solutions Consulting team members.
- Engage in ongoing training to stay current on the MongoDB product suite and industry trends.

Requirements as stated in the posting:
- 5 to 8 years of related industry experience, ideally including 2 years in a customer-facing role.
- Minimum 2 years with modern scripting languages (Python, Node.js, SQL) or popular programming languages (C/C++, Java, C#) in a professional capacity.
- Experience implementing scalable, highly available distributed systems in the cloud and on-prem.
- Demonstrated ability to review complex existing application architecture and advise improvements.
- Strong presentation, communication, and interpersonal skills for both technical and business audiences.
- Ability to work with a cross-functional sales team to run an end-to-end deal cycle.
- Ability to travel up to 25%.
- Bachelor's degree or equivalent work experience.

"May also have" (posting's own phrasing): experience deploying or supporting applications on a major cloud provider, prior technical pre-sales experience, database programming and data-model experience, data engineering or AI/ML project experience, familiarity with a sales methodology such as MEDDPICC or Command of the Message, a MongoDB certification, or a cloud provider certification.

## Why-fit angles for Santiago

Best hook to lead with: Santiago has personally run both halves of this job, technical delivery and the commercial motion around it, as a founder rather than as a hired specialist. At Online Basics he built the technical architecture himself (Python microservices on Heroku and AWS, orchestrating 10+ third-party APIs) and also owned the commercial side (raised $500K+ from private investors and banking partners, ran the P&L to $8M revenue). At Pragma AI, "Pragma Brain" is a hands-on RAG system (scoped retrieval, citation gating, multilingual ES/EN embeddings, an eval harness), which is a direct technical analog to what MongoDB now sells as Atlas Vector Search plus Voyage AI embeddings, giving him a real technical story for the AI-platform pitch rather than borrowed enthusiasm.

Second hook: the founder-led, cross-functional client work (Eugenia.ai on-site deployments translating conflicting stakeholder needs into product; Pragma AI client diagnostics and quoting automation) maps onto the SA's "trusted advisor, discovery, and demo" motion, even though it was never done under a formal pre-sales title.

Honest concerns and watch-outs:
- The matcher itself flags the two real gaps: enterprise pre-sales experience and distributed-systems-at-scale depth. Santiago has built and operated real systems, but not MongoDB's typical Fortune 100 or high-availability distributed-database scale, and his customer-facing history is founder-led rather than a formal quota-carrying SA role.
- Candidate reports describe a long (roughly 180-day), multi-stage, sales-methodology-heavy loop (MEDDPICC or similar); this is unfamiliar territory worth deliberate prep rather than assuming the technical story alone carries the process.
- The role explicitly wants "ideally 2 years in a customer-facing role" and rewards prior technical pre-sales; Santiago's version of that is founder sales and delivery, a genuine but different shape of experience that should be named and reframed, not hidden.

## Application-question angles

Why this company: lead with the Voyage AI and Atlas AI-platform narrative rather than generic "MongoDB is the leading NoSQL database" language. MongoDB just spent 2026 folding embeddings and reranking directly into its core database so AI applications get grounded answers from live operational data; that is the exact problem Santiago built Pragma Brain to solve on a smaller scale (RAG with citation gating over a company's own data).

Why you fit: lead with the founder-who-has-done-both-sides throughline, someone who has sold technical value and also built the system that proved it, citing Online Basics (raised capital, owned the architecture, ran the P&L) paired with Pragma Brain's hands-on RAG and embeddings work. Do not checklist Atlas plus culture plus news plus the Mexico office; pick this one combination and go deep.

Anything else: the Mexico City hybrid fit is real, not a remote-only stretch, since MongoDB runs an active local office and multiple concurrent Mexico City hires. Worth noting bilingual ES/EN for LATAM accounts, and that the role's own "up to 25% travel" already assumes occasional US or customer travel, which lines up with Santiago's TN-visa eligibility if that ever comes up.

## Sources

- https://www.mongodb.com/careers/job/?gh_jid=8109873 (via `src.query job 24703`): full job posting text, responsibilities, requirements, customer count, Fortune 100 stat, Leadership Commitment framing, benefits mention.
- https://www.mongodb.com/company: mission statement, founding year and founders, employee count, awards (Built In 2026, Glassdoor 2025), product overview.
- https://www.mongodb.com/company/blog/news/redefining-database-ai-why-mongodb-acquired-voyage-ai: rationale and phased integration plan for the Voyage AI acquisition.
- https://investors.mongodb.com/news-releases/news-release-details/mongodb-announces-acquisition-voyage-ai-enable-organizations: February 2026 Voyage AI acquisition announcement.
- https://www.investing.com/news/transcripts/earnings-call-transcript-mongodb-tops-q2-2026-estimates-but-shares-sink-93CH-4884698: quarter reported September 1, 2026, revenue, growth rate, Atlas growth, margin, net revenue retention, new customer count.
- https://www.sec.gov/Archives/edgar/data/1441816/000162828026016799/mdb-20260131.htm: Form 10-K, fiscal year 2026 (ended January 31, 2026) full-year revenue.
- https://www.sec.gov/Archives/edgar/data/0001441816/000162828026059830/mdb-20260731.htm: Form 10-Q, customer count as of July 31, 2026.
- https://builtin.com/company/mongodb/offices: Mexico City office location and hybrid work model description.
- https://builtin.com/job/senior-specialist-industry-solutions/7060544: evidence of concurrent hybrid Mexico City hiring.
- https://www.glassdoor.com/Interview/MongoDB-Interview-Questions-E433703.htm?filter.jobTitleExact=Pre-Sales+Solutions+Architect: candidate-reported interview loop and content for the Pre-Sales Solutions Architect track.

researched: 2026-09-02
