# Finlay (Aegypti) CAR Experiment

Generated: 2026-08-25T23:34:57.192821+00:00
Aegypti version: unknown   `fallback` param: True   Hvala diagnostics: True
Seed: 20260629

Four subjects on 12330 instances, scored against an independent exact oracle:
**Aegypti-safe** `(fallback=True)`, **Aegypti-fast** `(fallback=False)`,
**Chiba-Nishizeki**, and **matrix multiplication**. The benchmark adds dense
small-clique families (complete tri-/four-partite, balanced bipartite + one
edge) and an exhaustive sweep of all graphs with n <= 7 (Graph Atlas), to
stress the fast dense branch.

## Headline

- Instances: 12330  (with a triangle: 8860)
- Aegypti-safe correct: 12330/12330  (misses: 0)
- Aegypti-fast correct: 12330/12330  (dense-branch misses: 0)
- Chiba-Nishizeki correct: 12330/12330
- Matrix multiplication correct: 12330/12330
- Invalid witnesses: 0    All four agree: 12330/12330

### Dense-branch diagnostics (Hypothesis 1)

- Dense-regime instances: 5639  (triangle-containing: 4799)
- Fast dense-branch misses on positives: 0
- Safe fallback triggered: 840
- Max |C| / OPT_VC(complement) observed: 1.2000
- Min |V\C| over triangle-containing dense instances: 3

`fast_dense_misses` is the empirical content of Hypothesis 1: triangle-containing
dense inputs on which the fast branch left fewer than three vertices uncovered.
Aegypti-safe converts each into a correct answer via its fallback.

## By regime

| regime | instances | truth_positive | aegypti_fast_misses | dense_instances | dense_positives | fallback_triggered | max_cover_ratio | min_uncovered_on_positive | mean_aegypti_fast_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 5639 | 4799 | 0 | 5639 | 4799 | 840 | 1.2000 | 3 | 1.5003 | 0.0377 |
| sparse | 6691 | 4061 | 0 | 0 | 0 | 0 | -- | -- | 0.0339 | 0.0214 |

## By family

| family | instances | truth_positive | aegypti_fast_misses | dense_instances | dense_positives | fallback_triggered | max_cover_ratio | min_uncovered_on_positive | mean_aegypti_fast_ms | mean_chiba_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| atlas_exhaustive_n<=7 | 1244 | 1080 | 0 | 91 | 91 | 0 | 1.0000 | 3 | 0.0359 | 0.0078 |
| er_dense | 2500 | 2500 | 0 | 2425 | 2425 | 0 | 1.2000 | 3 | 1.5260 | 0.0302 |
| er_sparse | 2486 | 1139 | 0 | 0 | 0 | 0 | -- | -- | 0.0408 | 0.0259 |
| near_turan | 400 | 400 | 0 | 400 | 400 | 0 | 1.0000 | 3 | 1.8065 | 0.0245 |
| omega3_tripartite | 400 | 400 | 0 | 400 | 400 | 0 | 1.0000 | 3 | 0.7021 | 0.0185 |
| omega4_fourpartite | 300 | 300 | 0 | 300 | 300 | 0 | 1.0000 | 4 | 0.6654 | 0.0223 |
| planted_clique | 1000 | 1000 | 0 | 987 | 987 | 0 | 1.1667 | 3 | 1.5255 | 0.0273 |
| planted_triangle | 1500 | 1500 | 0 | 0 | 0 | 0 | -- | -- | 0.0379 | 0.0221 |
| structured | 1000 | 541 | 0 | 365 | 196 | 169 | 1.0000 | 3 | 0.2451 | 0.0290 |
| tri_free_bipartite | 1500 | 0 | 0 | 671 | 0 | 671 | 1.0000 | -- | 1.1300 | 0.0616 |

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
