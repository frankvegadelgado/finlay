# `car/` — Triangle-Detection Comparison Experiment

`car_experiment.py` runs the three triangle-detection routines from the
`aegypti` package on a deterministic benchmark of ~10,000 small graphs and
scores each against an independent exact triangle oracle.

| Subject | Function | Complexity |
| ------- | -------- | ---------- |
| **Aegypti** (hybrid) | `algorithm.find_triangle_coordinates(graph)` | `O(n^2)` worst case |
| **Chiba–Nishizeki** | `algorithm.find_triangle_chiba_nishizeki(graph)` | `O(m^{3/2})` |
| **Matrix multiplication** | `algorithm.is_triangle_free_brute_force(sparse_matrix)` | `O(n^{2.37})` |

The benchmark spans both regimes of the Aegypti dispatch — sparse
(`m ≤ ⌈n^{4/3}⌉`) and dense (`m > ⌈n^{4/3}⌉`) — across six families: sparse and
dense Erdős–Rényi graphs, triangle-free bipartite graphs, planted-triangle
sparse graphs, planted-clique dense graphs, and structured graphs (complete,
even cycles, wheels, complete bipartite, random regular).

## Requirements

```bash
pip install aegypti      # installs the package and its dependency `hvala`
```

## Run

```bash
python car/car_experiment.py            # full ~10,000-instance suite
python car/car_experiment.py --quick    # smaller, faster sweep
```

Run from the repository root (the directory containing both `aegypti/` and
`car/`); the script falls back to adding the repo root to `sys.path` if the
package is not installed.

## Outputs (written into `car/`)

- `car_experiment.json` — full machine-readable results and summaries.
- `car_summary.csv` — per-regime, per-family, and overall summary.
- `car_by_instance.csv` — one row per instance.
- `CAR_REPORT.md` — human-readable report.

Each instance records `n`, `m`, regime, the exact-oracle verdict, and for every
subject whether it found a triangle, whether its witness is valid, whether it
matches the oracle, and its running time. The key column `aegypti_miss` flags
any instance where the oracle finds a triangle but Aegypti returns none — the
quantity that characterises dense-branch completeness in practice.

**Scope:** finite small-graph evidence with exact oracles — a reproducible
regression / integrity check, not a worst-case completeness proof for the dense
branch.
