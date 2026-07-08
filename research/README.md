# research/

Reusable, cited company dossiers for the job hunt.

- `companies/<company-slug>.md` - one dossier per company, written by the `company-researcher`
  agent via the `/research <company | job_id>` command. Slug is derived by `src/research.py`
  (`company_slug`), so every role at the same company shares one dossier (e.g. Backblaze).
- Each dossier researches four areas (mission & product, culture & voice, recent news,
  engineering & AI) with sources. `/tailor` reads the dossier when present and weaves the most
  resonant, company-specific hook into the cover letter.

Dossiers are committed (durable, reusable knowledge that also syncs across machines), unlike the
gitignored `data/` and `applications/*/` generated artifacts. House rules apply: cite every fact,
never fabricate, zero em-dashes.
