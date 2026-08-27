# Finlay (Aegypti) CAR Experiment

Generated: 2026-08-27T04:44:01.699641+00:00
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
| dense | 5639 | 4799 | 0 | 5639 | 4799 | 1.2000 | 3 | 2.1538 | 0.0456 |
| sparse | 6691 | 4061 | 0 | 0 | 0 | -- | -- | 0.0404 | 0.0238 |

## By family

| family | instances | truth_positive | aegypti_misses | dense_instances | dense_positives | max_cover_ratio | min_uncovered_on_positive | mean_aegypti_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| atlas_exhaustive_n<=7 | 1244 | 1080 | 0 | 91 | 91 | 1.0000 | 3 | 0.0376 | 0.0106 |
| er_dense | 2500 | 2500 | 0 | 2425 | 2425 | 1.2000 | 3 | 1.7897 | 0.0354 |
| er_sparse | 2486 | 1139 | 0 | 0 | 0 | -- | -- | 0.0402 | 0.0240 |
| near_turan | 400 | 400 | 0 | 400 | 400 | 1.0000 | 3 | 2.4103 | 0.0326 |
| omega3_tripartite | 400 | 400 | 0 | 400 | 400 | 1.0000 | 3 | 0.8190 | 0.0233 |
| omega4_fourpartite | 300 | 300 | 0 | 300 | 300 | 1.0000 | 4 | 0.7765 | 0.0255 |
| planted_clique | 1000 | 1000 | 0 | 987 | 987 | 1.1667 | 3 | 1.8526 | 0.0338 |
| planted_triangle | 1500 | 1500 | 0 | 0 | 0 | -- | -- | 0.0490 | 0.0272 |
| structured | 1000 | 541 | 0 | 365 | 196 | 1.0000 | 3 | 0.6466 | 0.0364 |
| tri_free_bipartite | 1500 | 0 | 0 | 671 | 0 | 1.0000 | -- | 2.4646 | 0.0760 |

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
