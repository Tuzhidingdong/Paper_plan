# V5.1 Literature-Frontier Discovery and Synthesis Protocol

## Purpose
Build a current, defensible and bounded state-of-the-art account, identify the studies most capable of defeating a novelty claim, and explain what the project adds. A short bibliography or a few broad background papers is not a literature frontier.

## 1. Decompose the question into searchable facets
Derive query concepts from the current project, as relevant: material/system and synonyms/formulas/phases; reactants/products and transformation direction; mechanism and alternatives; medium/process and defining conditions; impurity/additive/dopant/defect classes and chemical forms; measured observables and analytical/model methods; application and significance endpoints; adjacent-discipline terminology.

Build multiple query families combining these facets. Use exact-phrase, formula-based, synonym and broader adjacent-system searches.

## 2. Use independent discovery routes and citation trails
Use scholarly search tools/databases actually available. Possible routes include multidisciplinary and field-specific indexes, publisher platforms, Crossref/DOI metadata, OpenAlex, Semantic Scholar, PubMed/PMC and institutional repositories. No single provider is mandatory if unavailable, but do not rely on one endpoint.

Record each route, access status, date, query family, filters/time span and limitations. If a search returns no results or errors:
1. retry alternate names, spelling, synonyms, formulas, phases and broader/narrower terms;
2. search known titles/DOIs/authors at publishers and bibliographic services;
3. follow backward references from closest primary papers/reviews;
4. follow forward citations to identify newer or contradictory studies;
5. search neighboring systems/processes with the same mechanism or observable;
6. if full text is inaccessible, record the limit and restrict claims to verified metadata/abstract.

A null result from one provider is retrieval failure/coverage limitation, never evidence of novelty or absence of prior art.

## 3. Identify nearest prior art, not keyword overlap
Prioritize primary studies closest in decisive dimensions: same system/transformation; same medium/process; same phase direction/mechanism in an adjacent system; same impurity/interfacial effect; same measurement/proxy relationship; or overlapping application/claim. Explain whether each paper is a direct competitor, mechanistic or methodological precedent, adjacent comparator, counter-evidence or background.

## 4. Verify sources and publication status
For each source capture title, authors, journal, year, volume/pages/article number, DOI, stable URL, publication status/date, discovery route, access date and access tier:
- METADATA_ONLY — supports only bibliographic facts;
- ABSTRACT_VERIFIED — supports only claims stated in the abstract;
- FULLTEXT_VERIFIED — relevant full-text sections/figures/tables inspected with their locations recorded.

Distinguish preprint, accepted manuscript, online-first, issue-assigned, correction/retraction and future-dated issue entry. Verify the actual first-online date; do not use a future issue date alone to infer availability or describe an unpublished item as published. Never invent citations/findings or use search snippets as substitutes for source verification.

## 5. Build a nearest-work comparison
For each closest study compare, where relevant: exact system/material/composition; reactants/products and phase direction; medium/conditions; mechanism and its evidence; impurity/structure role and chemical form; direct measurands vs proxies and validation; result actually demonstrated; stated/identified limitations; precise overlap and difference from the current project. Do not omit a decisive similarity because it weakens the proposed novelty.

## 6. Triangulate and bound gap statements
Every gap must be grounded in inspected prior work, not merely absent search hits. Classify:
- SUPPORTED_GAP — directly relevant studies were inspected and leave a bounded unresolved question;
- PROVISIONAL_GAP — relevant coverage exists but search breadth/access/direct comparison is incomplete;
- NOT_ESTABLISHED — available sources do not support a defensible gap statement.

Avoid absolute “first”, “unprecedented” or “no studies” claims unless exceptional search evidence justifies them. Prefer bounded formulations stating what is established under which conditions and what remains unresolved in the inspected literature.

## 7. Stop on coverage/saturation, not paper count
Stop when the relevant query families have been explored across independent routes, major backward/forward citation trails followed, closest prior-art candidates checked, and searches cease to reveal closer or materially contradictory work. If tools/access prevent saturation, mark the frontier provisional and name the coverage gap. There is no fixed paper-count target.

## 8. Synthesize the frontier into the argument
Explain what the field established; known mechanisms/processes/measurements; agreement/disagreement; what the closest work already achieves; the narrow unresolved question; how the current project's system/evidence/method addresses a genuinely different dimension; and what remains provisional. Reviews map fields but do not replace closest primary studies.

## 9. Link literature to scientific-mainline selection
Link each literature claim to its source and access tier. The closest-work comparison must influence the candidate-line decision in `V5_1_SCIENTIFIC_MAINLINE_DECISION.md`, not merely decorate the Introduction. Identify which prior works constrain each candidate's novelty and which supply counter-evidence.

## 10. Required output
Report search scope, routes, query families, dates, access limits, publication-status checks, closest-prior-art comparison, contradictions, bounded gaps/confidence and source locations.

## 11. Resolve supplied references and literature leads explicitly

Treat every paper, author/year clue, DOI fragment, title fragment, citation list, bibliography and "closest work" suggested by the user or found in project materials as a **search lead that must be resolved**, not as an optional hint. Do not silently omit an inconvenient or difficult-to-find lead.

For each lead, maintain a resolution record with: original clue exactly as supplied; candidate title/authors/venue/year; DOI or stable identifier; publication/version status; discovery routes and exact queries attempted; identity confidence; access tier; and final disposition. Separate bibliographic identity resolution from verification of the scientific claims attributed to the paper.

Use an escalating identity-resolution sequence as available:
1. exact quoted title and title fragments;
2. author surname(s) + year + journal/venue;
3. DOI or DOI fragment through a resolver, Crossref and publisher record;
4. alternate title wording, transliteration, abbreviations, conference/journal versions and preprint/accepted-manuscript variants;
5. an independent scholarly index or repository;
6. references/citations from a confirmed related paper.

A single zero-result response, a search endpoint error, or one failed API query is not enough to classify a supplied lead as unlocated. If multiple candidates remain, preserve the ambiguity and compare identifiers; ask the user only when identity materially changes the decision. Use explicit states such as CONFIRMED, LIKELY_MATCH, AMBIGUOUS, NOT_LOCATED_AFTER_DOCUMENTED_SEARCH, and INVALID_OR_INCONSISTENT_CITATION. Never turn an unresolved clue into a cited finding.

## 12. Stress-test each novelty claim against prior art

Do not test novelty only at the level of a broad topic or the final one-sentence contribution. Decompose it into atomic novelty dimensions that actually matter to the project's claim. Depending on the field, these may include system/material, transformation or reaction direction, operating regime, boundary conditions, mechanism, causal coupling, measured quantity, analytical method, predictive capability, performance consequence or application.

For each proposed novelty dimension:
- state the exact proposition being claimed;
- write at least one focused query family that could find a paper proving it is already known;
- compare the closest primary study or studies, including inconvenient overlaps;
- distinguish an established principle from a new system-specific application, a parameter extension, a new causal relation, a new measurement, or a genuinely new capability;
- state what observable result would make the claimed distinction real rather than merely different wording;
- classify the dimension as ALREADY_ESTABLISHED, INCREMENTAL_EXTENSION, POTENTIALLY_DISTINCT, or NOT_ASSESSABLE.

A new combination of known materials, factors or methods is not automatically a new scientific contribution. Explain what non-trivial interaction, quantitative relation, predictive consequence or previously unresolved condition the combination establishes. Do not call a result novel merely because the exact combination of keywords has not been found.

## 13. Apply a full-text priority rule to novelty-critical sources

Prioritize full-text inspection for sources that could overturn the mainline, establish the closest transformation/mechanism, or directly overlap the proposed contribution. Inspect the relevant Methods, Results, figures/tables and limitations, and record exact source locations. Abstracts can establish only claims actually stated in the abstract; metadata can establish only bibliographic facts.

If a novelty-critical source remains abstract-only or metadata-only, do not infer that it lacks a method, condition, control or result not mentioned in the available record. Keep the comparison incomplete and the gap provisional or not established. Where full text cannot be accessed, name the missing source locations/information needed to complete the comparison.

## 14. Preserve a query and citation-trail audit

The literature ledger must retain enough information for another researcher to understand how the frontier was searched. Record, at minimum: provider/database; exact query or query family; query date; field/filter/time range where available; result or retrieval status; closest candidates discovered; follow-up action; and known coverage limitations.

For citation chasing, record the seed paper, whether backward references or forward citations were followed, how candidate papers were selected, and whether each closest candidate was inspected. Deduplicate DOI/version variants without losing links between preprint, accepted manuscript and version of record.

Search breadth is demonstrated by coverage of material query facets and citation trails, not by an impressive bibliography count. Do not stop because a convenient number of papers has been collected.

## 15. Frontier closure and decision gate

Before calling the literature frontier complete, explicitly answer:
- Have all user-supplied literature leads been resolved or transparently retained as unresolved?
- Have exact-system and adjacent-mechanism queries both been attempted?
- Have the nearest primary studies and material counter-evidence been inspected at the highest accessible tier?
- Have backward and forward citation trails from the closest studies been followed?
- Has every important novelty phrase been adversarially searched?
- Are publication dates, versions, corrections/retractions and preprint status clear enough for the claims being made?
- Which comparisons remain incomplete because of access or identity limits?

If any novelty-critical lead remains unresolved, a direct competitor is represented only by metadata, or a major query facet/citation trail is unsearched, do not issue SUPPORTED_GAP. Use PROVISIONAL_GAP or NOT_ESTABLISHED and state the exact limitation. A literature frontier can still be useful before saturation, but its uncertainty must constrain the mainline recommendation and title/claim language.
