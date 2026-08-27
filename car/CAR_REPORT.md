# Finlay (Aegypti) CAR Experiment

Generated: 2026-08-27T07:01:39.879303+00:00
Aegypti version: unknown   Hvala diagnostics: True
Seed: 20260629

Three subjects on 12330 instances, scored against an independent exact oracle:
**Aegypti**, **Chiba-Nishizeki**, and **matrix multiplication**. The benchmark adds
dense small-clique families (complete tri-/four-partite, balanced bipartite + one
edge) and an exhaustive sweep of all graphs with n <= 7 (Graph Atlas), to
stress the dense branch.

## Headline

- Instances: 12330  (with a triangle: 8860)
- Aegypti correct: 12330/12330  (misses: 0)
- Chiba-Nishizeki correct: 12330/12330
- Matrix multiplication correct: 12330/12330
- Invalid witnesses: 0    All three agree: 12330/12330

### Dense-branch diagnostics

- Dense-regime instances: 5639  (triangle-containing: 4799)
- Dense-branch misses on positives: 0
- Max |C| / OPT_VC(complement) observed: 1.2000
- Min |V\C| over triangle-containing dense instances: 3

## By regime

| regime | instances | truth_positive | aegypti_misses | dense_instances | dense_positives | max_cover_ratio | min_uncovered_on_positive | mean_aegypti_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 5639 | 4799 | 0 | 5639 | 4799 | 1.2000 | 3 | 1.8575 | 0.0497 |
| sparse | 6691 | 4061 | 0 | 0 | 0 | -- | -- | 0.0434 | 0.0256 |

## By family

| family | instances | truth_positive | aegypti_misses | dense_instances | dense_positives | max_cover_ratio | min_uncovered_on_positive | mean_aegypti_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| atlas_exhaustive_n<=7 | 1244 | 1080 | 0 | 91 | 91 | 1.0000 | 3 | 0.0290 | 0.0095 |
| er_dense | 2500 | 2500 | 0 | 2425 | 2425 | 1.2000 | 3 | 1.7396 | 0.0347 |
| er_sparse | 2486 | 1139 | 0 | 0 | 0 | -- | -- | 0.0397 | 0.0236 |
| near_turan | 400 | 400 | 0 | 400 | 400 | 1.0000 | 3 | 2.1459 | 0.0294 |
| omega3_tripartite | 400 | 400 | 0 | 400 | 400 | 1.0000 | 3 | 0.8406 | 0.0231 |
| omega4_fourpartite | 300 | 300 | 0 | 300 | 300 | 1.0000 | 4 | 0.8645 | 0.0284 |
| planted_clique | 1000 | 1000 | 0 | 987 | 987 | 1.1667 | 3 | 1.9025 | 0.0340 |
| planted_triangle | 1500 | 1500 | 0 | 0 | 0 | -- | -- | 0.0575 | 0.0322 |
| structured | 1000 | 541 | 0 | 365 | 196 | 1.0000 | 3 | 0.3262 | 0.0362 |
| tri_free_bipartite | 1500 | 0 | 0 | 671 | 0 | 1.0000 | -- | 1.6748 | 0.0972 |

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
