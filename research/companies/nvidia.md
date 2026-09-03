# NVIDIA: Company Dossier

## Core narrative
NVIDIA has pivoted from GPU maker to the platform company for agentic AI at enterprise scale. FY2026 full-year revenue hit a record $215.9 billion (Axios, Feb 25 2026), and 2026 has been dominated by a full-stack push, Nemotron open models, NIM microservices, NeMo Agent Toolkit, OpenShell secure agent runtimes, to move enterprise ISVs and partners from LLM demo to production agents. The Senior Solutions Architect, Agentic AI role sits exactly at that seam: taking partner multi-agent systems from proof of concept to scaled, production deployment.

## Mission & product
- Core stack: GPUs plus a full AI software layer, CUDA, NIM microservices, NeMo Framework/Retriever/Guardrails/Agent Toolkit, Nemotron open models, Dynamo, TensorRT-LLM, and Triton, covering training, fine-tuning, retrieval, and now agent orchestration.
- 2026 platform bet is agentic AI specifically. Nemotron 3 Ultra (a 550B mixture-of-experts model) plus NemoClaw, an open-source stack for building and running enterprise agents, launched June 4 2026, available as NIM microservices on Hugging Face and build.nvidia.com (enterprisedna.co).
- LangChain partnership (announced March 2026) merges LangSmith with NVIDIA's Agent Toolkit, Nemotron, NIM, and Dynamo (langchain.com).
- Enterprise software leaders are building AI agents on NVIDIA's stack per NVIDIA's own newsroom framing (nvidianews.nvidia.com), and NVIDIA is extending the same agent pattern into science via BioNeMo Agent Toolkit (nvidianews.nvidia.com).
- Business model: sell compute (GPU/DGX) plus software and microservices (NIM) to enterprises and ISV partners, who embed NVIDIA's stack into their own products. That is the direct reason a partner-facing "Solutions Architect" role exists: NVIDIA needs technical staff who can co-build with those partners, not just sell to them.

## Recent news (2026, dated)
- Feb 25, 2026: Q4 FY26 earnings, $68B quarterly revenue, record full-year revenue of $215.9B; Jensen Huang describes AI demand as an "inflection point" (Axios; Fortune).
- Mar 2026: LangChain announces an enterprise agentic AI platform built with NVIDIA, combining LangSmith with NeMo Agent Toolkit, Nemotron, NIM, and Dynamo (langchain.com).
- Apr 29, 2026: Nemotron 3 Nano Omni model launched, unifying vision, audio, and language for agents (HPCwire).
- May 12, 2026: Jensen Huang's total pay package fell 27% to $36.3M on smaller stock awards (Bloomberg).
- May 20, 2026: Q1 FY27 revenue reported at $81.6B, up 85% year on year (StartupHub.ai).
- Jun 1, 2026: NVIDIA partners with software leaders to build secure, autonomous AI agents (HPCwire).
- Jun 4, 2026: NemoClaw and Nemotron 3 Ultra released as an open stack for enterprise agents (EnterpriseDNA).
- 2026 (undated in source): NVIDIA Agent Toolkit expanded with PhysicsNeMo and CUDA-X libraries (nvidianews.nvidia.com); BioNeMo Agent Toolkit launched for agentic scientific discovery (nvidianews.nvidia.com).

## Culture & hiring signals
- Roughly 42,000+ employees across 38 countries (Makerstations.io; Yahoo Finance).
- Revenue per employee cited around $5.1 million, described as roughly double Apple's and nearly triple Microsoft's, a signal the org runs lean relative to its output (Yahoo Finance/Makerstations.io).
- Jensen Huang's management style is described as direct and immediately critical ("criticizes everything his employees show him"), a habit he attributes to his Taiwanese parents' style of feedback; the same piece notes employees tend to stay for years despite the intensity (Fortune, May 26 2026).
- The target posting itself signals the team's working style: it explicitly wants someone hands-on who spends time "architecting and writing code" (per an earlier NVIDIA job-search summary of a related Solutions Architect, Agentic AI posting) rather than a pure advisory architect, and it rewards a field-facing profile (workshops, architecture reviews, technical presence) as a way to stand out.
- Visa posture: NVIDIA has filed thousands of H-1B labor condition applications (one tracker cites 7,308 LCAs covering 147,823 positions, median sponsored salary about $170,914) and Jensen Huang has publicly committed to continuing H-1B sponsorship and covering the higher visa fees (Ellis.com; Business Insider, via Yahoo Finance/Investing.com/Seeking Alpha).

## Target role
Senior Solutions Architect, Agentic AI, requisition JR2021199, Santa Clara CA ("2 Locations" per the Workday listing). Base salary range as posted: $184,000 to $287,500 USD, plus equity and benefits eligibility. Source: NVIDIA's Workday posting (see Sources).

The local DB row for job id 41573 had an empty `description` field; the text below was fetched fresh from the live Workday posting and is bullet-verbatim from that source. `python -m src.query job 41573` shows no Curated/sheet block for this row (it came in through the Workday adapter, not the hand-curated dream sheet).

**What you'll be doing** (verbatim):
- "Lead technical delivery for strategic Agentic AI partner engagements from discovery and architecture through PoC, production readiness, rollout, and scale."
- "Design and build enterprise-grade agentic systems, including multi-agent workflows, tool-using agents, RAG-integrated applications, planning, memory, evaluation, and guardrail patterns."
- "Lead deep architecture reviews with partner engineering teams, driving tradeoffs across model quality, latency, efficiency, cost, retrieval quality, reliability, safety, security, and observability."
- "Build hands-on PoCs, benchmarks, reference architectures, and reusable blueprints that help Enterprise ISVs and NVIDIA field teams move from exploration to production."
- "Guide partners on model customization and post-training workflows, including supervised fine-tuning, reinforcement learning methods, human or AI feedback, direct preference optimization, PEFT/LoRA, synthetic data generation, evaluation, and regression analysis."
- "Work with agent harnesses and execution environments such as OpenShell, OpenAI Agents SDK, LangGraph, LlamaIndex, LangChain, CrewAI, Semantic Kernel, or similar frameworks."
- "Translate partner deployment findings into actionable feedback for NVIDIA Product and Engineering, so we can improve our platforms, tools, and field guidance."

**What we need to see** (required, verbatim where quoted):
- BS/MS/PhD in Computer Science, Electrical Engineering, AI/ML, or equivalent experience
- "8+ years of engineering, solutions architecture, applied ML, or technical deployment experience"
- Track record leading complex AI/ML deployments from prototype to production
- "Hands-on experience building LLM, generative AI, RAG, or agentic AI applications in production"
- Strong Python and Linux programming skills with deep learning framework experience
- "Deep understanding of agentic AI architectures, including tool use, orchestration, memory, retrieval, planning, evaluation, guardrails, and failure handling"
- Experience with model customization techniques including SFT, RL/RLHF/RLAIF, DPO, LoRA/PEFT, and quantization
- Leadership ability with ambiguous engagements and clear communication across audiences

**Ways to stand out from the crowd** (preferred, verbatim where quoted):
- "Hands-on experience with NVIDIA AI software such as NIM, NeMo Framework, NeMo Retriever, NeMo Guardrails, NeMo Agent Toolkit, Dynamo, Nemotron, Triton, TensorRT-LLM, or NIM Operator"
- Experience building post-training pipelines for reasoning, tool use, and domain adaptation
- "Experience with agent harnesses, sandboxed execution, policy enforcement, OpenShell-like environments, or secure enterprise agent runtime build"
- Recognized expertise demonstrated through workshops, architecture reviews, technical presence, or whitepapers

## Visa / relocation notes
- The DB's own match verdict for this row already flags `location_ok: false` and a `visa_path` note of "TN, confirm NVIDIA files it; on-site Santa Clara" (python -m src.query job 41573). config/profile.yaml lists NVIDIA in `dream_companies`, which waives the location rule under `dream_rule`: Santiago is open to relocating to the US for NVIDIA specifically, on a TN visa the employer files.
- Could not verify a citable NVIDIA-specific TN precedent in this pass. Search results confirm NVIDIA actively sponsors H-1B (thousands of LCAs filed, and Jensen Huang has publicly said the company will keep sponsoring H-1B and cover the higher fees) and also sponsors E-3 and Green Card paths, but no source turned up a specific statement about NVIDIA and TN visas (Ellis.com; Business Insider report via Yahoo Finance/Investing.com/Seeking Alpha). Treat "NVIDIA files TN" as unverified: raise it directly with the recruiter rather than asserting it as fact in application text.
- The posting requires Santa Clara presence ("2 Locations", no remote option stated in the fetched description). Per profile.yaml's `relocation_line`, application text can state: "I am based in Mexico City and open to relocating to the US for this role on a TN visa, which the employer files."

## Sources
- researched: 2026-09-02
- NVIDIA Workday posting, verbatim job description, bullets, salary range, req ID, location: https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Solutions-Architect--Agentic-AI_JR2021199 (human-facing page: https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite/job/US-CA-Santa-Clara/Senior-Solutions-Architect--Agentic-AI_JR2021199)
- NVIDIA newsroom, enterprise software leaders building AI agents with NVIDIA: https://nvidianews.nvidia.com/news/enterprise-software-leaders-build-ai-agents-with-nvidia
- NVIDIA newsroom, Agent Toolkit expanded with PhysicsNeMo and CUDA-X libraries: https://nvidianews.nvidia.com/news/nvidia-expands-nvidia-agent-toolkit-with-nvidia-physicsnemo-and-cuda-x-libraries-to-transform-how-the-world-engineers-designs-and-builds
- NVIDIA newsroom, BioNeMo Agent Toolkit launch: https://nvidianews.nvidia.com/news/nvidia-launches-bionemo-agent-toolkit-giving-ai-agents-the-tools-to-accelerate-scientific-discovery
- NVIDIA newsroom, Nemotron 3 family debut: https://nvidianews.nvidia.com/news/nvidia-debuts-nemotron-3-family-of-open-models
- LangChain blog, NVIDIA enterprise agentic AI integration (Mar 2026): https://www.langchain.com/blog/nvidia-enterprise
- HPCwire, Nemotron 3 Nano Omni model launch (Apr 29 2026): https://www.hpcwire.com/aiwire/2026/04/29/nvidia-launches-nemotron-3-nano-omni-model-unifying-vision-audio-and-language-for-ai-agents/
- HPCwire, NVIDIA partners with software leaders on secure autonomous agents (Jun 1 2026): https://www.hpcwire.com/aiwire/2026/06/01/nvidia-partners-with-software-leaders-to-build-secure-autonomous-ai-agents/
- EnterpriseDNA, NemoClaw / Nemotron 3 Ultra launch (Jun 2026): https://enterprisedna.co/resources/news/nvidia-nemoclaw-nemotron-3-ultra-enterprise-agents-2026/
- Axios, Nvidia Q4 earnings record, "AI inflection point" (Feb 25 2026): https://www.axios.com/2026/02/25/nvda-earnings-nvidia-jensen-huang
- Fortune, Nvidia Q4 FY26 results, $68B quarterly revenue (Feb 25 2026): https://fortune.com/2026/02/25/nvidia-nvda-earnings-q4-results-jensen-huang/
- StartupHub.ai, Q1 FY27 revenue $81.6B (reported May 20 2026, published Jul 17 2026): https://www.startuphub.ai/ai-news/ai-figures/2026/figure-jensen-huang-company-financial-breakdown-2026-07-17
- Bloomberg, Jensen Huang CEO pay package shrinks 27% (May 12 2026): https://www.bloomberg.com/news/articles/2026-05-12/nvidia-ceo-pay-package-shrinks-27-on-smaller-stock-awards
- Fortune, Jensen Huang on giving critical feedback and NVIDIA's culture (May 26 2026): https://fortune.com/2026/05/26/nvidia-ceo-jensen-huang-embrace-criticism-leadership-strategy-learned-from-taiwanese-parents-five-trillion-dollar-tech-firm/
- Makerstations.io, NVIDIA employee statistics 2026 (headcount, revenue per employee): https://www.makerstations.io/nvidia-employee-statistics/
- Yahoo Finance, NVIDIA employee count and revenue per employee: https://finance.yahoo.com/markets/stocks/articles/many-employees-does-nvidia-r-145900596.html
- Ellis.com, NVIDIA visa sponsorship record (H-1B LCA counts, median sponsored salary): https://www.ellis.com/visa-sponsors/nvidia-corporation
- Internal: config/profile.yaml, dream_companies / dream_rule / relocation_line entries for NVIDIA
- Internal: `python -m src.query job 41573`, DB row and match_verdict for this posting (location_ok:false, visa_path note, no Curated sheet block)

This dossier is a draft for Santiago to review. The TN visa item above is explicitly unverified and should be confirmed with NVIDIA before being stated as fact in application text.
