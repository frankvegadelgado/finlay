# Finlay (Aegypti) CAR Experiment

Generated: 2026-06-29T14:50:50.767905+00:00
Aegypti version imported: unknown
Seed: 20260629

This report compares three triangle-detection routines from the installed
`aegypti` package on 9986 deterministic small-graph instances, scored against an
independent exact triangle oracle.

Subjects:
1. **Aegypti** -- `find_triangle_coordinates` (hybrid, O(n^2) worst case)
2. **Chiba-Nishizeki** -- `find_triangle_chiba_nishizeki` (O(m^{3/2}))
3. **Matrix multiplication** -- `is_triangle_free_brute_force` (O(n^{2.37}))

## Headline

- Instances: 9986
- Aegypti correct: 9986/9986
- Aegypti misses (oracle says triangle, Aegypti said none): 0
- Chiba-Nishizeki correct: 9986/9986
- Matrix multiplication correct: 9986/9986
- Invalid witnesses returned: 0
- All three agree: 9986/9986

Scope: finite small-graph evidence with exact oracles; this is a reproducible
regression / integrity check, not a worst-case completeness proof for the dense
branch of Aegypti.

## By regime

| regime | instances | truth_positive | aegypti_correct | chiba_correct | matmul_correct | aegypti_misses | mean_aegypti_ms | mean_chiba_ms | mean_matmul_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 4448 | 3608 | 4448 | 4448 | 4448 | 0 | 1.4819 | 0.1585 | 0.1623 |
| sparse | 5538 | 3072 | 5538 | 5538 | 5538 | 0 | 0.0805 | 0.0602 | 0.1156 |

## By family

| family | instances | truth_positive | aegypti_correct | chiba_correct | matmul_correct | aegypti_misses | mean_aegypti_ms | mean_chiba_ms | mean_matmul_ms |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| er_dense | 2500 | 2500 | 2500 | 2500 | 2500 | 0 | 1.5059 | 0.1706 | 0.1784 |
| er_sparse | 2486 | 1139 | 2486 | 2486 | 2486 | 0 | 0.0879 | 0.0662 | 0.1211 |
| planted_clique | 1000 | 1000 | 1000 | 1000 | 1000 | 0 | 1.3678 | 0.1249 | 0.1548 |
| planted_triangle | 1500 | 1500 | 1500 | 1500 | 1500 | 0 | 0.0808 | 0.0592 | 0.1102 |
| structured | 1000 | 541 | 1000 | 1000 | 1000 | 0 | 0.2173 | 0.0729 | 0.1145 |
| tri_free_bipartite | 1500 | 0 | 1500 | 1500 | 1500 | 0 | 0.8987 | 0.1071 | 0.1202 |

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
