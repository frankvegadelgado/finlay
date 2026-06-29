from __future__ import annotations

"""car/ -- triangle-detection comparison + dense-branch stress experiment.

Runs four routines against an independent exact oracle on a deterministic
benchmark spanning both density regimes of the Aegypti dispatch
(sparse: m <= ceil(n^{4/3}); dense: m > ceil(n^{4/3})):

    1. Aegypti-safe    find_triangle_coordinates(graph, fallback=True)
    2. Aegypti-fast    find_triangle_coordinates(graph, fallback=False)
    3. Chiba-Nishizeki find_triangle_chiba_nishizeki(graph)
    4. Matrix product  is_triangle_free_brute_force(sparse_matrix)

The benchmark now includes families designed to *stress the fast dense branch*,
where the gap between "has a triangle" and "has a large clique" is widest:

    * complete tripartite graphs K_{a,b,c}      (dense, clique number 3)
    * complete 4-partite graphs K_{a,b,c,d}     (dense, clique number 4)
    * balanced complete bipartite + one edge     (dense, clique number 3)
    * an exhaustive sweep of all graphs n <= 7   (NetworkX Graph Atlas)

plus the original random/structured families. For every dense-regime instance
the script additionally records the Hvala-cover diagnostics that determine
Aegypti-fast completeness: |C|, |V\\C| (uncovered), omega(G), OPT_VC(complement)
= n - omega(G), the ratio |C| / OPT_VC, and whether the dense branch succeeded
or the safe fallback would trigger.

Ground truth (does a triangle exist?) is computed independently of all subjects
by direct neighbourhood intersection.

Run from the repository root with:

    python car/car_experiment.py            # full suite
    python car/car_experiment.py --quick    # smaller, faster sweep

Outputs (written next to this script): car_experiment.json, car_summary.csv,
car_by_instance.csv, CAR_REPORT.md.

Scope: finite empirical evidence (exhaustive only up to n = 7), not a proof of
worst-case completeness for the fast dense branch.
"""

import argparse
import csv
import inspect
import json
import math
import platform
import random
import statistics
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import networkx as nx
import numpy as np
import scipy.sparse as sp

try:
    from aegypti import algorithm
except ModuleNotFoundError:  # pragma: no cover - convenience for direct runs
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from aegypti import algorithm

try:
    import aegypti
    AEGYPTI_VERSION = getattr(aegypti, "__version__", "unknown")
except Exception:  # pragma: no cover
    AEGYPTI_VERSION = "unknown"

# Hvala vertex cover, used to recompute the dense-branch diagnostics directly.
try:
    from hvala.algorithm import find_vertex_cover as _hvala_cover
    _HAS_HVALA = True
except Exception:  # pragma: no cover
    _HAS_HVALA = False

# Whether the installed package exposes the `fallback` parameter that selects
# the safe (complete) vs fast (uniform O(n^2)) variant.
_HAS_FALLBACK = "fallback" in inspect.signature(
    algorithm.find_triangle_coordinates).parameters


def _aegypti_safe(G):
    if _HAS_FALLBACK:
        return algorithm.find_triangle_coordinates(G, fallback=True)
    return algorithm.find_triangle_coordinates(G)


def _aegypti_fast(G):
    if _HAS_FALLBACK:
        return algorithm.find_triangle_coordinates(G, fallback=False)
    return algorithm.find_triangle_coordinates(G)


SEED = 20260629
OUT_DIR = Path(__file__).resolve().parent
OMEGA_CAP = 24  # exact clique number only computed for n <= OMEGA_CAP


# ----------------------------------------------------------------------------
# Independent exact oracle and helpers.
# ----------------------------------------------------------------------------
def regime_of(n: int, m: int) -> str:
    bound = math.ceil(math.pow(n, 4.0 / 3.0)) if n > 0 else 0
    return "sparse" if m <= bound else "dense"


def has_triangle_exact(G: nx.Graph) -> bool:
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    for u, v in G.edges():
        au, av = adj[u], adj[v]
        small, large = (au, av) if len(au) <= len(av) else (av, au)
        for w in small:
            if w != u and w != v and w in large:
                return True
    return False


def clique_number(G: nx.Graph) -> int:
    if G.number_of_nodes() == 0:
        return 0
    return max((len(c) for c in nx.find_cliques(G)), default=1)


def is_valid_triangle(G: nx.Graph, triangle) -> bool:
    if triangle is None:
        return False
    nodes = list(triangle)
    if len(nodes) != 3 or len(set(nodes)) != 3:
        return False
    a, b, c = nodes
    return G.has_edge(a, b) and G.has_edge(b, c) and G.has_edge(a, c)


def to_sparse_matrix(G: nx.Graph, n: int) -> sp.csr_matrix:
    A = nx.to_scipy_sparse_array(G, nodelist=list(range(n)), dtype=np.int8, format="csr")
    return sp.csr_matrix(A)


def _time(fn, *args):
    t0 = time.perf_counter()
    out = fn(*args)
    return out, (time.perf_counter() - t0) * 1000.0


# ----------------------------------------------------------------------------
# Per-instance evaluation of all four subjects + dense-branch diagnostics.
# ----------------------------------------------------------------------------
def evaluate(name: str, family: str, G: nx.Graph) -> dict:
    G = nx.convert_node_labels_to_integers(G, ordering="sorted")
    n = G.number_of_nodes()
    m = G.number_of_edges()
    regime = regime_of(n, m)
    truth = has_triangle_exact(G)

    safe, safe_ms = _time(_aegypti_safe, G)
    safe_found = safe is not None
    safe_valid = (not safe_found) or is_valid_triangle(G, safe)
    safe_correct = (safe_found == truth) and safe_valid

    fast, fast_ms = _time(_aegypti_fast, G)
    fast_found = fast is not None
    fast_valid = (not fast_found) or is_valid_triangle(G, fast)
    fast_correct = (fast_found == truth) and fast_valid

    cn, cn_ms = _time(algorithm.find_triangle_chiba_nishizeki, G)
    cn_found = cn is not None
    cn_valid = (not cn_found) or is_valid_triangle(G, cn)
    cn_correct = (cn_found == truth) and cn_valid

    A = to_sparse_matrix(G, n)
    mm_free, mm_ms = _time(algorithm.is_triangle_free_brute_force, A)
    mm_found = not bool(mm_free)
    mm_correct = (mm_found == truth)

    # Dense-branch diagnostics (only when the dense branch actually runs).
    cover_C = uncovered = omega = opt_vc = cover_ratio = None
    dense_branch_runs = (regime == "dense")
    dense_success = fallback_triggered = None
    if dense_branch_runs and _HAS_HVALA:
        H = nx.complement(G)
        C = _hvala_cover(H)
        cover_C = len(C)
        uncovered = n - cover_C            # |V \ C| = |mis|
        dense_success = uncovered >= 3      # then certified as a triangle of G
        fallback_triggered = not dense_success
        if n <= OMEGA_CAP:
            omega = clique_number(G)        # = alpha(complement)
            opt_vc = n - omega              # OPT_VC(complement)
            cover_ratio = (cover_C / opt_vc) if opt_vc and opt_vc > 0 else None

    agree = (safe_found == fast_found == cn_found == mm_found)
    return {
        "name": name, "family": family, "n": n, "m": m,
        "regime": regime, "truth": truth,
        "aegypti_safe_found": safe_found, "aegypti_safe_valid": safe_valid,
        "aegypti_safe_correct": safe_correct, "aegypti_safe_ms": safe_ms,
        "aegypti_safe_miss": bool(truth and not safe_found),
        "aegypti_fast_found": fast_found, "aegypti_fast_valid": fast_valid,
        "aegypti_fast_correct": fast_correct, "aegypti_fast_ms": fast_ms,
        "aegypti_fast_miss": bool(truth and not fast_found),
        "chiba_found": cn_found, "chiba_valid": cn_valid,
        "chiba_correct": cn_correct, "chiba_ms": cn_ms,
        "matmul_found": mm_found, "matmul_correct": mm_correct, "matmul_ms": mm_ms,
        "all_agree": agree,
        # dense-branch diagnostics
        "dense_branch_runs": dense_branch_runs,
        "cover_C": cover_C, "uncovered": uncovered,
        "omega": omega, "opt_vc_complement": opt_vc, "cover_ratio": cover_ratio,
        "dense_success": dense_success, "fallback_triggered": fallback_triggered,
    }


# ----------------------------------------------------------------------------
# Deterministic benchmark families.
# ----------------------------------------------------------------------------
def _gnp(n: int, p: float, seed: int) -> nx.Graph:
    return nx.gnp_random_graph(n, p, seed=seed)


def _balanced_bipartite_plus_edge(n: int) -> nx.Graph:
    """Balanced complete bipartite K_{a,b} plus one intra-part edge.

    Dense and triangle-containing, but clique number only 3 (a Turan-type
    near-extremal graph: hostile to large-clique arguments)."""
    a = n // 2
    G = nx.complete_bipartite_graph(a, n - a)  # left 0..a-1, right a..n-1
    if a >= 2:
        G.add_edge(0, 1)  # one intra-(left)-part edge -> triangles, omega = 3
    return G


def benchmark(rng: random.Random, big: bool) -> Iterable[tuple[str, str, nx.Graph]]:
    counts = {
        "er_sparse": 2500, "er_dense": 2500, "tri_free_bipartite": 1500,
        "planted_triangle": 1500, "planted_clique": 1000, "structured": 1000,
        "omega3_tripartite": 400, "omega4_fourpartite": 300, "near_turan": 400,
    } if big else {
        "er_sparse": 60, "er_dense": 60, "tri_free_bipartite": 40,
        "planted_triangle": 40, "planted_clique": 30, "structured": 30,
        "omega3_tripartite": 30, "omega4_fourpartite": 30, "near_turan": 30,
    }

    for i in range(counts["er_sparse"]):
        n = rng.randint(12, 60)
        p = rng.choice([0.02, 0.04, 0.06, 0.08])
        yield (f"er_sparse_{i:05d}", "er_sparse", _gnp(n, p, rng.randrange(2**31)))

    for i in range(counts["er_dense"]):
        n = rng.randint(10, 40)
        p = rng.choice([0.4, 0.55, 0.7, 0.85])
        yield (f"er_dense_{i:05d}", "er_dense", _gnp(n, p, rng.randrange(2**31)))

    for i in range(counts["tri_free_bipartite"]):
        a = rng.randint(3, 18)
        b = rng.randint(3, 18)
        p = rng.choice([0.3, 0.5, 0.7, 0.9])
        G = nx.bipartite.random_graph(a, b, p, seed=rng.randrange(2**31))
        yield (f"bip_{i:05d}", "tri_free_bipartite", G)

    for i in range(counts["planted_triangle"]):
        n = rng.randint(15, 60)
        G = _gnp(n, rng.choice([0.01, 0.03, 0.05]), rng.randrange(2**31))
        t = rng.sample(range(n), 3)
        G.add_edges_from([(t[0], t[1]), (t[1], t[2]), (t[0], t[2])])
        yield (f"plant_tri_{i:05d}", "planted_triangle", G)

    for i in range(counts["planted_clique"]):
        n = rng.randint(12, 36)
        G = _gnp(n, rng.choice([0.4, 0.5, 0.6]), rng.randrange(2**31))
        k = rng.randint(3, max(3, n // 2))
        clique = rng.sample(range(n), k)
        G.add_edges_from((clique[a], clique[b])
                         for a in range(k) for b in range(a + 1, k))
        yield (f"plant_clq_{i:05d}", "planted_clique", G)

    for i in range(counts["structured"]):
        kind = i % 5
        if kind == 0:
            yield (f"complete_{i:05d}", "structured", nx.complete_graph(rng.randint(4, 30)))
        elif kind == 1:
            yield (f"cycle_{i:05d}", "structured", nx.cycle_graph(2 * rng.randint(3, 25)))
        elif kind == 2:
            yield (f"wheel_{i:05d}", "structured", nx.wheel_graph(rng.randint(5, 30)))
        elif kind == 3:
            a, b = rng.randint(3, 15), rng.randint(3, 15)
            yield (f"kbip_{i:05d}", "structured", nx.complete_bipartite_graph(a, b))
        else:
            n = rng.randint(6, 30)
            d = rng.randint(2, 4)
            if (n * d) % 2:
                n += 1
            try:
                G = nx.random_regular_graph(d, n, seed=rng.randrange(2**31))
            except nx.NetworkXError:
                G = nx.cycle_graph(n)
            yield (f"reg_{i:05d}", "structured", G)

    # --- Adversarial dense families: dense, but small clique number ---------
    # Complete tripartite K_{a,b,c}: dense, clique number exactly 3, K4-free.
    for i in range(counts["omega3_tripartite"]):
        a, b, c = (rng.randint(2, 10) for _ in range(3))
        yield (f"tripart_{i:05d}", "omega3_tripartite",
               nx.complete_multipartite_graph(a, b, c))

    # Complete 4-partite K_{a,b,c,d}: dense, clique number exactly 4, K5-free.
    for i in range(counts["omega4_fourpartite"]):
        a, b, c, d = (rng.randint(2, 8) for _ in range(4))
        yield (f"fourpart_{i:05d}", "omega4_fourpartite",
               nx.complete_multipartite_graph(a, b, c, d))

    # Balanced complete bipartite + one intra-part edge: dense, clique number 3.
    for i in range(counts["near_turan"]):
        n = rng.randint(8, 40)
        yield (f"near_turan_{i:05d}", "near_turan", _balanced_bipartite_plus_edge(n))

    # --- Exhaustive sweep of all graphs up to n = 7 (NetworkX Graph Atlas) ---
    try:
        from networkx.generators.atlas import graph_atlas_g
        for idx, G in enumerate(graph_atlas_g()):
            if G.number_of_nodes() >= 3 and G.number_of_edges() >= 1:
                yield (f"atlas_{idx:04d}", "atlas_exhaustive_n<=7", G)
    except Exception:  # pragma: no cover
        pass


# ----------------------------------------------------------------------------
# Aggregation.
# ----------------------------------------------------------------------------
def _mean(xs: list[float]) -> float | None:
    return statistics.fmean(xs) if xs else None


def _max(xs: list[float]) -> float | None:
    return max(xs) if xs else None


def _min(xs: list[int]) -> int | None:
    return min(xs) if xs else None


def summarise(rows: list[dict]) -> dict:
    if not rows:
        return {"instances": 0}
    dense_rows = [r for r in rows if r["dense_branch_runs"]]
    dense_pos = [r for r in dense_rows if r["truth"]]
    ratios = [r["cover_ratio"] for r in dense_rows if r["cover_ratio"] is not None]
    unc_pos = [r["uncovered"] for r in dense_pos if r["uncovered"] is not None]
    return {
        "instances": len(rows),
        "truth_positive": sum(1 for r in rows if r["truth"]),
        "aegypti_safe_correct": sum(1 for r in rows if r["aegypti_safe_correct"]),
        "aegypti_safe_misses": sum(1 for r in rows if r["aegypti_safe_miss"]),
        "aegypti_fast_correct": sum(1 for r in rows if r["aegypti_fast_correct"]),
        "aegypti_fast_misses": sum(1 for r in rows if r["aegypti_fast_miss"]),
        "chiba_correct": sum(1 for r in rows if r["chiba_correct"]),
        "matmul_correct": sum(1 for r in rows if r["matmul_correct"]),
        "invalid_witnesses": sum(
            1 for r in rows
            if not (r["aegypti_safe_valid"] and r["aegypti_fast_valid"] and r["chiba_valid"])),
        "all_agree": sum(1 for r in rows if r["all_agree"]),
        "mean_aegypti_safe_ms": _mean([r["aegypti_safe_ms"] for r in rows]),
        "mean_aegypti_fast_ms": _mean([r["aegypti_fast_ms"] for r in rows]),
        "mean_chiba_ms": _mean([r["chiba_ms"] for r in rows]),
        "mean_matmul_ms": _mean([r["matmul_ms"] for r in rows]),
        # dense-branch diagnostics
        "dense_instances": len(dense_rows),
        "dense_positives": len(dense_pos),
        "dense_branch_successes": sum(1 for r in dense_rows if r["dense_success"]),
        "fallback_triggered": sum(1 for r in dense_rows if r["fallback_triggered"]),
        "fast_dense_misses": sum(1 for r in dense_pos if r["aegypti_fast_miss"]),
        "max_cover_ratio": _max(ratios),
        "min_uncovered_on_positive": _min(unc_pos),
    }


def _fmt(v: Any) -> str:
    if v is None:
        return "--"
    if isinstance(v, float):
        return f"{v:.4f}"
    return str(v)


def _md_table(rows: list[dict], cols: list[str]) -> str:
    lines = ["| " + " | ".join(cols) + " |", "| " + " | ".join("---" for _ in cols) + " |"]
    for r in rows:
        lines.append("| " + " | ".join(_fmt(r.get(c)) for c in cols) + " |")
    return "\n".join(lines)


# ----------------------------------------------------------------------------
# Driver.
# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--quick", action="store_true", help="smaller, faster sweep")
    args = ap.parse_args()
    big = not args.quick
    rng = random.Random(SEED)

    started = time.time()
    rows: list[dict] = []
    for name, family, G in benchmark(rng, big):
        if G.number_of_nodes() < 3 or G.number_of_edges() == 0:
            continue
        rows.append(evaluate(name, family, G))

    overall = summarise(rows)
    by_family = {fam: summarise([r for r in rows if r["family"] == fam])
                 for fam in sorted({r["family"] for r in rows})}
    by_regime = {reg: summarise([r for r in rows if r["regime"] == reg])
                 for reg in sorted({r["regime"] for r in rows})}

    n = overall["instances"]
    result = {
        "experiment": "car/ four-subject triangle comparison + dense-branch stress for Finlay",
        "aegypti_version": AEGYPTI_VERSION,
        "fallback_parameter_available": _HAS_FALLBACK,
        "hvala_diagnostics_available": _HAS_HVALA,
        "omega_cap": OMEGA_CAP,
        "seed": SEED,
        "subjects": {
            "aegypti_safe": "find_triangle_coordinates(G, fallback=True)",
            "aegypti_fast": "find_triangle_coordinates(G, fallback=False)",
            "chiba_nishizeki": "find_triangle_chiba_nishizeki(G)",
            "matrix_multiplication": "is_triangle_free_brute_force(A)",
        },
        "oracle": "independent exact neighbourhood-intersection triangle test",
        "conclusion": {
            "instances": n,
            "aegypti_safe_correct": overall["aegypti_safe_correct"],
            "aegypti_safe_misses": overall["aegypti_safe_misses"],
            "aegypti_fast_correct": overall["aegypti_fast_correct"],
            "aegypti_fast_misses": overall["aegypti_fast_misses"],
            "chiba_correct": overall["chiba_correct"],
            "matmul_correct": overall["matmul_correct"],
            "invalid_witnesses": overall["invalid_witnesses"],
            "all_four_agree": overall["all_agree"],
            "safe_all_correct": overall["aegypti_safe_correct"] == n,
            "dense_instances": overall["dense_instances"],
            "dense_positives": overall["dense_positives"],
            "fast_dense_misses": overall["fast_dense_misses"],
            "fallback_triggered": overall["fallback_triggered"],
            "max_cover_ratio_complement": overall["max_cover_ratio"],
            "min_uncovered_on_positive": overall["min_uncovered_on_positive"],
            "scope_warning": "Finite evidence (exhaustive only up to n=7); "
                             "not a worst-case completeness proof for the fast dense branch.",
        },
        "overall_summary": overall,
        "summary_by_family": by_family,
        "summary_by_regime": by_regime,
        "elapsed_seconds": time.time() - started,
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "networkx": nx.__version__,
            "numpy": np.__version__,
            "scipy": sp.__version__ if hasattr(sp, "__version__") else "unknown",
        },
    }

    (OUT_DIR / "car_experiment.json").write_text(
        json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")

    if rows:
        with (OUT_DIR / "car_by_instance.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    summ_cols = ["scope", "instances", "truth_positive",
                 "aegypti_safe_correct", "aegypti_safe_misses",
                 "aegypti_fast_correct", "aegypti_fast_misses",
                 "chiba_correct", "matmul_correct", "invalid_witnesses", "all_agree",
                 "dense_instances", "dense_positives", "dense_branch_successes",
                 "fallback_triggered", "fast_dense_misses",
                 "max_cover_ratio", "min_uncovered_on_positive",
                 "mean_aegypti_safe_ms", "mean_aegypti_fast_ms",
                 "mean_chiba_ms", "mean_matmul_ms"]
    with (OUT_DIR / "car_summary.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=summ_cols)
        w.writeheader()
        for label, s in [("regime:" + k, v) for k, v in by_regime.items()] + \
                        [("family:" + k, v) for k, v in by_family.items()] + \
                        [("OVERALL", overall)]:
            row = {"scope": label}
            row.update({k: s.get(k) for k in summ_cols if k != "scope"})
            w.writerow(row)

    tbl_cols = ["instances", "truth_positive", "aegypti_fast_misses",
                "dense_instances", "dense_positives", "fallback_triggered",
                "max_cover_ratio", "min_uncovered_on_positive",
                "mean_aegypti_fast_ms", "mean_chiba_ms"]
    fam_rows = [{"family": k, **v} for k, v in by_family.items()]
    reg_rows = [{"regime": k, **v} for k, v in by_regime.items()]
    report = f"""# Finlay (Aegypti) CAR Experiment

Generated: {datetime.now(timezone.utc).isoformat()}
Aegypti version: {AEGYPTI_VERSION}   `fallback` param: {_HAS_FALLBACK}   Hvala diagnostics: {_HAS_HVALA}
Seed: {SEED}

Four subjects on {n} instances, scored against an independent exact oracle:
**Aegypti-safe** `(fallback=True)`, **Aegypti-fast** `(fallback=False)`,
**Chiba-Nishizeki**, and **matrix multiplication**. The benchmark adds dense
small-clique families (complete tri-/four-partite, balanced bipartite + one
edge) and an exhaustive sweep of all graphs with n <= 7 (Graph Atlas), to
stress the fast dense branch.

## Headline

- Instances: {n}  (with a triangle: {overall['truth_positive']})
- Aegypti-safe correct: {overall['aegypti_safe_correct']}/{n}  (misses: {overall['aegypti_safe_misses']})
- Aegypti-fast correct: {overall['aegypti_fast_correct']}/{n}  (dense-branch misses: {overall['aegypti_fast_misses']})
- Chiba-Nishizeki correct: {overall['chiba_correct']}/{n}
- Matrix multiplication correct: {overall['matmul_correct']}/{n}
- Invalid witnesses: {overall['invalid_witnesses']}    All four agree: {overall['all_agree']}/{n}

### Dense-branch diagnostics (Hypothesis 1)

- Dense-regime instances: {overall['dense_instances']}  (triangle-containing: {overall['dense_positives']})
- Fast dense-branch misses on positives: {overall['fast_dense_misses']}
- Safe fallback triggered: {overall['fallback_triggered']}
- Max |C| / OPT_VC(complement) observed: {_fmt(overall['max_cover_ratio'])}
- Min |V\\C| over triangle-containing dense instances: {_fmt(overall['min_uncovered_on_positive'])}

`fast_dense_misses` is the empirical content of Hypothesis 1: triangle-containing
dense inputs on which the fast branch left fewer than three vertices uncovered.
Aegypti-safe converts each into a correct answer via its fallback.

## By regime

{_md_table(reg_rows, ["regime"] + tbl_cols)}

## By family

{_md_table(fam_rows, ["family"] + tbl_cols)}

## Reproduction

    pip install aegypti        # installs aegypti and its dependency hvala
    python car/car_experiment.py

Outputs: `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`,
`CAR_REPORT.md` (this file).
"""
    (OUT_DIR / "CAR_REPORT.md").write_text(report, encoding="utf-8")

    print(json.dumps(result["conclusion"], indent=2))


if __name__ == "__main__":
    main()
