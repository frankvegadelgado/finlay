# Finlay (Aegypti) CAR Experiment

Generated: 2026-06-29T15:56:13.562322+00:00
Aegypti version imported: unknown
`fallback` parameter available: True
Seed: 20260629

This report compares four triangle-detection routines on 9986 deterministic
small-graph instances, scored against an independent exact triangle oracle.

Subjects:
1. **Aegypti-safe** -- `find_triangle_coordinates(G, fallback=True)` (unconditionally complete, O(m^{3/2}) worst case)
2. **Aegypti-fast** -- `find_triangle_coordinates(G, fallback=False)` (uniform O(n^2); dense branch may miss)
3. **Chiba-Nishizeki** -- `find_triangle_chiba_nishizeki(G)` (O(m^{3/2}))
4. **Matrix multiplication** -- `is_triangle_free_brute_force(A)` (O(n^{2.37}))

## Headline

- Instances: 9986  (with a triangle: 6680)
- Aegypti-safe correct: 9986/9986  (misses: 0)
- Aegypti-fast correct: 9986/9986  (dense-branch misses: 0)
- Chiba-Nishizeki correct: 9986/9986
- Matrix multiplication correct: 9986/9986
- Invalid witnesses returned: 0
- All four agree: 9986/9986

`aegypti_fast_misses` is the empirical content of Hypothesis 1: the number of
triangle-containing inputs on which the fast dense branch left fewer than three
vertices uncovered. Aegypti-safe converts any such case into a correct answer
via its Chiba-Nishizeki fallback.

Scope: finite small-graph evidence with exact oracles; a reproducible
regression / integrity check, not a worst-case completeness proof for the fast
dense branch.

## By regime

| regime | instances | truth_positive | aegypti_safe_correct | aegypti_fast_correct | aegypti_fast_misses | chiba_correct | matmul_correct | mean_aegypti_safe_ms | mean_aegypti_fast_ms | mean_chiba_ms | mean_matmul_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 4448 | 3608 | 4448 | 4448 | 0 | 4448 | 4448 | 1.4823 | 1.4541 | 0.1564 | 0.1614 |
| sparse | 5538 | 3072 | 5538 | 5538 | 0 | 5538 | 5538 | 0.0841 | 0.0725 | 0.0571 | 0.1142 |

## By family

| family | instances | truth_positive | aegypti_safe_correct | aegypti_fast_correct | aegypti_fast_misses | chiba_correct | matmul_correct | mean_aegypti_safe_ms | mean_aegypti_fast_ms | mean_chiba_ms | mean_matmul_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| er_dense | 2500 | 2500 | 2500 | 2500 | 0 | 2500 | 2500 | 1.4391 | 1.4444 | 0.1668 | 0.1743 |
| er_sparse | 2486 | 1139 | 2486 | 2486 | 0 | 2486 | 2486 | 0.0889 | 0.0795 | 0.0628 | 0.1166 |
| planted_clique | 1000 | 1000 | 1000 | 1000 | 0 | 1000 | 1000 | 1.4114 | 1.3818 | 0.1267 | 0.1579 |
| planted_triangle | 1500 | 1500 | 1500 | 1500 | 0 | 1500 | 1500 | 0.0814 | 0.0730 | 0.0562 | 0.1116 |
| structured | 1000 | 541 | 1000 | 1000 | 0 | 1000 | 1000 | 0.2633 | 0.2169 | 0.0720 | 0.1174 |
| tri_free_bipartite | 1500 | 0 | 1500 | 1500 | 0 | 1500 | 1500 | 0.9622 | 0.9018 | 0.1037 | 0.1213 |

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
