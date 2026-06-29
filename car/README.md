# `car/` — Triangle-Detection Comparison + Dense-Branch Stress Experiment

`car_experiment.py` runs four triangle-detection routines on a deterministic
benchmark (~12,000 instances) and scores each against an independent exact
triangle oracle. `find_triangle_coordinates` is run in both of its modes.

| Subject | Function | Complexity |
| ------- | -------- | ---------- |
| **Aegypti-safe** | `find_triangle_coordinates(graph, fallback=True)` | `O(n + m^{3/2})` worst case; unconditionally complete |
| **Aegypti-fast** | `find_triangle_coordinates(graph, fallback=False)` | `O(n^2)` worst case; one-sided certifier |
| **Chiba–Nishizeki** | `find_triangle_chiba_nishizeki(graph)` | `O(n + m^{3/2})`, exact |
| **Matrix multiplication** | `is_triangle_free_brute_force(sparse_matrix)` | reference baseline |

`fallback=False` (Aegypti-fast) is the default mode of the package; the safe
variant is opt-in. If the installed package predates the `fallback` parameter,
both reduce to the default call.

## Benchmark families

Both regimes of the dispatch are covered — sparse (`m ≤ ⌈n^{4/3}⌉`) and dense
(`m > ⌈n^{4/3}⌉`):

- **Random / structured:** sparse and dense Erdős–Rényi, triangle-free
  bipartite, planted-triangle sparse, planted-clique dense, and structured
  graphs (complete, even cycles, wheels, complete bipartite, random regular).
- **Adversarial dense, small clique number** (stress the fast dense branch,
  where "has a triangle" is far from "has a large clique"): complete tripartite
  `K_{a,b,c}` (ω = 3), complete 4-partite `K_{a,b,c,d}` (ω = 4), and balanced
  complete bipartite plus one intra-part edge (ω = 3).
- **Exhaustive:** every graph on at most 7 vertices (the NetworkX Graph Atlas).

## Requirements

```bash
pip install aegypti      # installs the package and its dependency `hvala`
```

## Run

```bash
python car/car_experiment.py            # full suite
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
matches the oracle, and its running time. For dense-regime instances it also
records the Hvala-cover diagnostics that determine Aegypti-fast completeness:
`cover_C` (|C|), `uncovered` (|V∖C|), `omega` (ω(G), exact for n ≤ 24),
`opt_vc_complement` (n − ω), `cover_ratio` (|C| / OPT), and the
`dense_success` / `fallback_triggered` flags. The key column
`aegypti_fast_miss` flags any instance where the oracle finds a triangle but the
fast dense branch returns none — the empirical content of the Hvala
independent-set hypothesis. Aegypti-safe converts every such case into a correct
answer through its fallback.

**Scope:** finite evidence (exhaustive only up to n = 7) — a reproducible
regression / integrity check, not a worst-case completeness proof for the fast
dense branch.
