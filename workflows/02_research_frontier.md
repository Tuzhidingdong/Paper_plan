# 02 — Research Frontier Review (Agent-executable)

## Input and output

Input: validated Evidence Bundle, Sample Mapping and compact evidence context.

Output: literature_bundle.json, append-only state/history/literature_search_log.jsonl, and a readable literature review. Do not begin until the key Result Units and candidate Findings are traceable.

## Search funnel

### Stage 1 — Terminology and field map
- Extract material names, synthesis/processing methods, target reactions or properties, analytical techniques and application terms from the report.
- Resolve synonyms and abbreviations against recent reviews and authoritative terminology sources.
- Separate neighboring fields that share words but not mechanisms or benchmark conditions.
- Write the exact keyword families and inclusion/exclusion logic to search_scope before broad searching.

### Stage 2 — Competitors and frontier primary studies
- Search recent primary studies first, then high-relevance foundational studies.
- Search by material/system, transformation route, performance metric, mechanism and characterization method.
- Use DOI/Crossref metadata and publisher pages to verify title, authors, journal, year and DOI.
- Follow backward and forward citations for the most relevant seed papers.
- Build a full local candidate corpus, then use keyword/BM25 prefiltering to choose a compact 15–18 paper reasoning set. The context budget is not a limit on the disk corpus.
- For each selected competing study, compare conditions only when those conditions were actually verified from abstract or full text.

### Stage 3 — Counter-evidence and limitations
- Search for null/negative results, contrary mechanisms, scale-up or reproducibility limitations, known artifacts and studies reporting different trends.
- Test each proposed gap against the strongest competing studies.
- Record why a reported limitation leaves a scientific question open; do not turn a missing search hit into a gap.

## Access levels

Each literature record must be exactly one of:
- METADATA_ONLY: title/DOI/abstract metadata only. Useful for discovery and bibliography, not claim support.
- ABSTRACT_VERIFIED: abstract was actually inspected. Support only statements explicitly present in the abstract.
- FULLTEXT_VERIFIED: relevant full-text methods/results/discussion were actually inspected. Store short exact evidence snippets and section/page/figure/table location.

If full text is inaccessible, retain the record with its true access level and set the relevant benchmark conditions to Benchmark_Conditions_Unverified. Never infer details from a title, graphical abstract, citation or abstract.

## Required records

search_scope records:
- search date (ISO date), databases/search systems actually queried;
- date range and language scope;
- exact query strings and target material/system terms;
- inclusion and exclusion criteria;
- known access limitations and searches not possible.

Each literature_record contains Python-issued LIT ID, title, DOI when available, year, journal, URL, source systems, access level, inspected abstract where available, short evidence snippets and exact source locations.

Each literature_claim has a Python-issued LC ID, a narrowly worded claim, citation_refs with LIT ID + snippet ID, claim scope, and verification notes. No naked bibliography citation may support a technical assertion without a traceable snippet.

Each research_gap has a Python-issued GAP ID, bounded target system, date/database/query bounds, supporting and counter-evidence literature claims, residual unknown, and confidence (LOW/MEDIUM/HIGH).

## Quality rules

- Prefer primary literature for novelty and benchmark claims; use reviews for vocabulary and field mapping.
- Compare like-for-like conditions. Do not rank performance where units, sample basis, pH, temperature, loading, conversion definition, normalization or test protocol differ.
- Separate absence of evidence from evidence of absence.
- Avoid generic gaps such as “the mechanism is unclear” unless specific competing explanations and missing discriminating evidence are identified.
- Verify bibliographic metadata and links before final export. Remove duplicates and retracted/unreliable sources or flag them.
- Cite all external factual statements in the readable review. Store source URLs/DOIs in the bundle.
- Do not create invented author/title/DOI combinations. DOI mismatch is an error to resolve, not a formatting issue.

## Completion check

Before route synthesis, report how many candidates are metadata-only, abstract-verified and full-text-verified; list unverified comparison conditions; run the planning validator after initializing the other bundles. If literature access is too weak, continue with exploratory routes and explicitly downgrade novelty confidence.
