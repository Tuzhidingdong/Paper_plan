# Implementation status — ERA V3.3

## Current milestone

**P0/P1 evidence-mining engine plus Agent-executable research-planning workflow.**

| Capability | Status | Notes |
|---|---|---|
| PDF SHA-256 and page inventory | Implemented | PyMuPDF; original copied as read-only source |
| Embedded raster extraction | Implemented | Source/page/BBox/pixel provenance retained |
| Repeated layout-asset triage | Implemented | dHash similarity hint for repeated top/footer assets; never deletes evidence |
| Vector-figure candidate detection | Implemented heuristic | Central-page spatial grid clusters and vector primitive types; candidate review only |
| Vector-only chart cropping | Partial/manual | Explicit PDF-coordinate BBox remains necessary |
| Stable Region/Panel IDs | Implemented | Python-owned registry; repeated extraction reuses IDs |
| Result/Finding/Sample ID reservation | Implemented | Python-owned |
| Planning ID reservation | Implemented | Literature, literature claim, gap, route, claim, Data Slot, Data Unit and task |
| Capability profile | Implemented | Operator-attested exact model profile; unknown capability blocks high-risk stages |
| Caption-blind task preparation | Implemented protocol | Text withheld from task pack; same-context cognitive leakage must be declared |
| Visual inspection and retry gate | Implemented | One initial inspection and at most one targeted reinspection |
| Sample identity and Micro-Gate | Implemented | Unresolved core links trigger human confirmation |
| Evidence validation | Implemented | Provenance, IDs, source hash, quantitative permissions and sample references |
| Literature frontier | Agent-executable | Three-stage search, access-tiered records and source snippets; no autonomous crawler |
| Three research routes | Agent-executable | Persistent route bundle, provisional recommendation and Gate A state |
| Claim–Evidence/Data Slot framework | Agent-executable + validated | Planning bundle and cross-reference validator |
| Experiment/analysis/computation plan | Agent-executable + validated | Task prerequisites and BLOCKED_BY_EXPERIMENT calculation gate |
| Introduction and final research-plan PDF | Agent-executable/export script | Markdown rendered through installed Edge/Chrome and PDF text/page verification |

## Known limits that remain explicit

1. Vector candidate heuristics cannot semantically identify a chart. They prioritize likely spatially coherent plot-like drawing clusters; PDF pages still need human review. Thresholds must be checked on representative local reports before tuning.
2. Vector-only regions need explicit BBoxes. The script does not claim fully automatic vector chart extraction.
3. Perceptual similarity is used only to label repeated layout assets for Contact Sheet triage. IDs and evidence records are not merged or deleted.
4. Caption-blind packs omit report text, but a model that has already read the report in the same context cannot be cognitively blind. The workflow requires image-first ordering and honest declaration.
5. Capability profiles are operator-attested metadata, not independent model benchmarks. A profile must identify exact provider/model/version and evidence basis.
6. Literature search/reasoning depends on the host Agent's available web tools and access rights. Full-text access is never presumed.
7. Planning validation checks references, access tiers, IDs, Data Slot relationships, lineage and calculation blockers. It does not determine scientific truth, novelty or peer-review outcome.
8. A proposed experiment is not an approved local protocol. Unknown reagent amounts, equipment, sample availability and replicate counts must remain TBD for lab/supervisor confirmation.
9. A computational task is not executable until required structure/composition/model inputs are present and validated.
10. Gate A and Gate B stay pending until a human decision is recorded.

## Verification

The GitHub Actions matrix runs deterministic unit/integration tests on Python 3.10, 3.11 and 3.12. Real-report visual quality and scientific quality still require local review of the actual PDF and resulting research plan.
