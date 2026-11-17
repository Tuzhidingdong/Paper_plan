# 02 — Research Frontier (specified; not implemented in MVP)

Consumes the validated Evidence Bundle. Use a three-stage funnel: review-first terminology alignment; competitive/frontier primary studies; counter-evidence and limitations. Add backward/forward citation chaining for selected seeds. Save retrieval logs outside model context.

Access tiers:
- Metadata-only: discovery/deduplication only.
- Abstract-verified: support only claims stated in the abstract.
- Full-text-verified: support methods, conditions, figure data and body claims only when exact source text/location is available.

Prioritize 3–5 full-text competitor comparisons per route where the field and lawful access make this feasible. This is a target, not a hard gate. Otherwise mark Benchmark_Conditions_Unverified. Never infer experimental conditions from abstracts.

Use BM25/keyword prefiltering on the full local citation graph before model review. A default core context of 15–18 papers is a budget, not a limit on the disk corpus.

Research gaps must be bounded by searched systems, dates, databases and terms. Lack of a search hit is not proof no prior study exists.
