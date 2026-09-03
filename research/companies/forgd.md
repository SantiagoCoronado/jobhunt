# forgd (forgd, inc.): Company Dossier

*Draft for Santiago to review. Facts below trace to the Sources list; anything not sourced is marked unverified.*

## Core narrative

forgd is a pure-play consultancy with an exclusive partnership with Anthropic: it does not sell generic AI transformation, it sells Claude-native engineering transformation (Adzuna JD, job id 42697). Its bet is that engineers, not traditional management consultants, are the right people to lead enterprises into AI-native software delivery, and it proves that bet by embedding its own engineers with client teams for short, intensive capability-transfer sprints rather than long advisory engagements (PR Newswire, 2026-07-08). The Solifi case study, a 70 percent cut in database calls achieved in three weeks with client engineers working independently by week three, is the clearest public evidence of that model actually landing (PR Newswire, 2026-07-08).

## Mission & product

- forgd describes itself in its own job postings as "the consultancy partnering exclusively with Anthropic to help enterprises build AI-native businesses," starting with engineering (moving client teams from individual Claude Code users to entire teams shipping with AI-native workflows) and expanding into agentic solution delivery and broader business transformation (Adzuna JD text for job id 42697, sourced from forgd's own posting).
- Independently, forgd calls itself "a pure-play Anthropic, applied AI consultancy that helps companies build AI-native engineering capabilities with Claude" (PR Newswire, 2026-07-08), which matches the JD's framing and cross-confirms the exclusivity claim.
- Working model: forgd's architects/engineers embed directly with client engineering teams, working alongside developers in short (roughly one-week) sprints, transferring working knowledge of AI tools, prompt design, and development workflows so client teams can operate independently after the engagement (PR Newswire, 2026-07-08).
- Customers include enterprise software engineering organizations; the one named, sourced case is Solifi (a fintech software vendor), where forgd's embedded team closed long-standing test-coverage gaps and cut database calls by 70 percent in three weeks (PR Newswire, 2026-07-08).
- forgd runs multiple open roles built around this delivery model: Forward Deployed Engineer, Applied AI Architect, and AI Engagement Lead, all client-embedded, delivery-facing titles rather than internal-product titles (Ashby careers board, jobs.ashbyhq.com/forgd-ai; Indeed listing for Applied AI Architect; RemoteRocketship listing for AI Engagement Lead).

## Recent news (2026)

- 2026-07-08: forgd and Solifi jointly published findings on an embedded AI-adoption engagement: 70 percent reduction in database calls achieved in three weeks, closed test-coverage gaps, and a stated principle from Morten Bagai (SVP of AI Engineering at forgd): "Durable AI adoption happens when building with AI becomes the default for an entire engineering team." (PR Newswire, 2026-07-08)
- 2026-09-02 (date this JD was pulled): forgd has an open Forward Deployed Engineer, North America req live, remote with roughly 20 percent travel, posted comp of 171,730 USD (Adzuna listing for job id 42697, https://www.adzuna.com/details/5866872110).
- forgd is simultaneously hiring Applied AI Architect (North America) and AI Engagement Lead (Remote USA and UK) as of this research date, indicating active, multi-role hiring push rather than a single opportunistic req (Ashby careers board; Indeed listing jk=c3c16e26c16da19d; RemoteRocketship UK listing).
- Could not independently verify company stage, headcount, HQ, or funding: forgd's own marketing site (forgd.com) did not return readable content through available tooling in this research pass, so those facts are left unverified rather than guessed.

## Culture & hiring signals

- Voice: direct, delivery-metric-driven. The one sourced leadership quote (Morten Bagai, SVP of AI Engineering) frames success as an engineering-team-wide adoption outcome, not a tooling rollout to early adopters (PR Newswire, 2026-07-08).
- Delivery ethos: short, embedded sprints (about one week) aimed at making client engineers self-sufficient by week three, rather than a long-term staff-augmentation model (PR Newswire, 2026-07-08).
- Hiring geography: forgd posts roles as "North America" (Forward Deployed Engineer, Applied AI Architect) and also has posted at least one explicitly "United Kingdom Remote" role (AI Engagement Lead), which shows forgd does hire remote staff outside the United States in at least one instance (RemoteRocketship listing, gb/company/forgd-ai-ai). Whether forgd hires remote workers based in Mexico, or engages contractors there, is unverified: no source found confirms or rules this out. This should be treated as an open question to raise directly with the recruiter, not assumed either way.
- forgd runs its hiring through Ashby (jobs.ashbyhq.com/forgd-ai), a standard modern ATS choice consistent with an AI-native, tooling-forward company, though the Ashby page itself is JS-rendered and did not yield readable listing content through available fetch tooling in this pass.

## Target role

- Title: Forward Deployed Engineer (FDE), North America. Job id 42697 in the local pipeline, source Adzuna, external id 5866872110, URL https://www.adzuna.com/details/5866872110 (job record, src.query job 42697).
- Posted comp: 171,730 USD (single figure, likely a stated base; period/structure beyond that not specified in the listing) (job record).
- Stated work arrangement in the JD header: "Remote / 20% Travel." The structured location field pulled from the source lists "Denver, Colorado," which conflicts with the "Remote" header; this is worth clarifying with forgd directly before assuming true full-remote eligibility, especially given the profile's Mexico-remote requirement (job record; Adzuna listing).
- JD framing of the role (forgd's own words, from the posting): FDEs help enterprises move "from individual developers using Claude Code to entire teams shipping together with AI-native workflows," expanding into "agentic solution delivery and broader business transformation," under the conviction that "engineers are uniquely positioned to lead this transformation" (job record, Adzuna JD text for job id 42697).
- Local pipeline status: shortlisted, match_score 87, matcher noted this as a strong fit for the "AI deployment / enablement" family and flagged the North America/remote scope as the main thing to confirm in practice (job record, match_verdict field).
- Canonical careers/apply channel: forgd hires through Ashby (jobs.ashbyhq.com/forgd-ai and per-role Ashby URLs, e.g. https://jobs.ashbyhq.com/forgd-ai/8bf4f921-64f6-435f-af94-581c31f62304 for the Applied AI Architect req). The exact Ashby URL for this specific Forward Deployed Engineer req was not directly recovered in this research pass; apply via the Adzuna listing link or by searching the Ashby board (jobs.ashbyhq.com/forgd-ai) for "Forward Deployed Engineer."

## Sources

- Adzuna job listing / local job record for job id 42697, "Forward Deployed Engineer (FDE): North America": https://www.adzuna.com/details/5866872110 (used for JD text, posted comp, location field, remote/travel header, match_score/verdict; pulled via `.venv/bin/python -m src.query job 42697`)
- PR Newswire, "Solifi and forgd Release Findings on AI Adoption in Enterprise Software Engineering," 2026-07-08: https://www.prnewswire.com/news-releases/solifi-and-forgd-release-findings-on-ai-adoption-in-enterprise-software-engineering-302819776.html (used for company description, delivery model, Solifi case metrics, Morten Bagai quote)
- forgd careers board (Ashby): https://jobs.ashbyhq.com/forgd-ai (used to confirm forgd's ATS and that multiple roles, including Applied AI Architect and Forward Deployed Engineer, are posted there; page content itself was not fully readable via available fetch tooling)
- Applied AI Architect posting on Ashby: https://jobs.ashbyhq.com/forgd-ai/8bf4f921-64f6-435f-af94-581c31f62304 (used to confirm role naming pattern and "North America" scoping used across forgd's open roles)
- Indeed listing for Applied AI Architect, Denver, CO: https://www.indeed.com/viewjob?jk=c3c16e26c16da19d (used to corroborate the North America/Denver location pattern seen across forgd postings)
- RemoteRocketship listing, "AI Engagement Lead at forgd.ai, United Kingdom Remote": https://www.remoterocketship.com/gb/company/forgd-ai-ai/jobs/ai-engagement-lead-united-kingdom-remote/ (used as the only found evidence that forgd hires remote roles outside the United States)

researched: 2026-09-02

Note: forgd's own marketing site (forgd.com) and the full Ashby job board did not return readable content through the fetch tooling available in this research pass (likely JS-rendered pages). Company stage, headcount, HQ, funding, and any explicit statement on hiring from Mexico remain unverified. Treat this dossier as a draft; verify the location/remote terms for this specific role directly with forgd before leaning on them in application materials.
