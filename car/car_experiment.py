from __future__ import annotations

"""car/ -- 10,000-instance comparison experiment for Finlay (Aegypti).

This suite runs the three triangle-detection routines shipped in the
``aegypti`` package against an independent exact oracle, on a deterministic
benchmark of ~10,000 small graphs spanning both density regimes of the
Aegypti dispatch (sparse: m <= ceil(n^{4/3}); dense: m > ceil(n^{4/3})).

The three subjects are:

    1. Aegypti           algorithm.find_triangle_coordinates(graph)
    2. Chiba-Nishizeki   algorithm.find_triangle_chiba_nishizeki(graph)
    3. Matrix product    algorithm.is_triangle_free_brute_force(sparse_matrix)

Ground truth (does a triangle exist?) is computed independently of all three
subjects by direct neighbourhood intersection over every edge, so each subject
is scored against an oracle it does not itself produce.  For the two subjects
that return a witness triple, the witness is additionally checked to be a real
triangle.

Run from the repository root with:

    python car/car_experiment.py            # full ~10,000-instance suite
    python car/car_experiment.py --quick    # smaller, faster sweep

Outputs (written next to this script):

    car/car_experiment.json     full machine-readable results
    car/car_summary.csv         per-family / per-regime / overall summary
    car/car_by_instance.csv     one row per instance
    car/CAR_REPORT.md           human-readable report

Scope: this is finite empirical evidence on small graphs with exact oracles.
It is a reproducible regression / integrity check, not a proof of worst-case
completeness for the dense branch.
"""

import argparse
import csv
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

SEED = 20260629
OUT_DIR = Path(__file__).resolve().parent


# ----------------------------------------------------------------------------
# Independent exact oracle and helpers.
# ----------------------------------------------------------------------------
def regime_of(n: int, m: int) -> str:
    """Sparse vs dense exactly as the Aegypti dispatch decides."""
    bound = math.ceil(math.pow(n, 4.0 / 3.0)) if n > 0 else 0
    return "sparse" if m <= bound else "dense"


def has_triangle_exact(G: nx.Graph) -> bool:
    """Exact triangle existence by direct neighbourhood intersection.

    Independent of all three subjects: for every edge (u, v) it tests whether
    u and v share a neighbour.  O(sum_e min(deg)) time, exact on small graphs.
    """
    adj = {v: set(G.neighbors(v)) for v in G.nodes()}
    for u, v in G.edges():
        au, av = adj[u], adj[v]
        small, large = (au, av) if len(au) <= len(av) else (av, au)
        for w in small:
            if w != u and w != v and w in large:
                return True
    return False


def is_valid_triangle(G: nx.Graph, triangle) -> bool:
    """True iff `triangle` is three distinct, pairwise-adjacent vertices."""
    if triangle is None:
        return False
    nodes = list(triangle)
    if len(nodes) != 3 or len(set(nodes)) != 3:
        return False
    a, b, c = nodes
    return G.has_edge(a, b) and G.has_edge(b, c) and G.has_edge(a, c)


def to_sparse_matrix(G: nx.Graph, n: int) -> sp.csr_matrix:
    """Symmetric 0/1 adjacency matrix (no diagonal) for the matrix-mult baseline."""
    A = nx.to_scipy_sparse_array(G, nodelist=list(range(n)), dtype=np.int8, format="csr")
    return sp.csr_matrix(A)


# ----------------------------------------------------------------------------
# Per-instance evaluation of all three subjects.
# ----------------------------------------------------------------------------
def evaluate(name: str, family: str, G: nx.Graph) -> dict:
    G = nx.convert_node_labels_to_integers(G, ordering="sorted")
    n = G.number_of_nodes()
    m = G.number_of_edges()
    truth = has_triangle_exact(G)

    # 1) Aegypti hybrid
    t0 = time.perf_counter()
    aeg = algorithm.find_triangle_coordinates(G)
    aeg_ms = (time.perf_counter() - t0) * 1000.0
    aeg_found = aeg is not None
    aeg_valid = (not aeg_found) or is_valid_triangle(G, aeg)
    aeg_correct = (aeg_found == truth) and aeg_valid

    # 2) Chiba-Nishizeki
    t0 = time.perf_counter()
    cn = algorithm.find_triangle_chiba_nishizeki(G)
    cn_ms = (time.perf_counter() - t0) * 1000.0
    cn_found = cn is not None
    cn_valid = (not cn_found) or is_valid_triangle(G, cn)
    cn_correct = (cn_found == truth) and cn_valid

    # 3) Matrix multiplication baseline (True == triangle-free)
    A = to_sparse_matrix(G, n)
    t0 = time.perf_counter()
    mm_free = algorithm.is_triangle_free_brute_force(A)
    mm_ms = (time.perf_counter() - t0) * 1000.0
    mm_found = not bool(mm_free)
    mm_correct = (mm_found == truth)

    agree = (aeg_found == cn_found == mm_found)
    return {
        "name": name, "family": family, "n": n, "m": m,
        "regime": regime_of(n, m), "truth": truth,
        "aegypti_found": aeg_found, "aegypti_valid": aeg_valid,
        "aegypti_correct": aeg_correct, "aegypti_ms": aeg_ms,
        "aegypti_miss": bool(truth and not aeg_found),     # oracle says yes, Aegypti said no
        "chiba_found": cn_found, "chiba_valid": cn_valid,
        "chiba_correct": cn_correct, "chiba_ms": cn_ms,
        "matmul_found": mm_found, "matmul_correct": mm_correct, "matmul_ms": mm_ms,
        "all_agree": agree,
    }


# ----------------------------------------------------------------------------
# Deterministic benchmark families (~10,000 instances at full size).
# ----------------------------------------------------------------------------
def _gnp(n: int, p: float, seed: int) -> nx.Graph:
    return nx.gnp_random_graph(n, p, seed=seed)


def benchmark(rng: random.Random, big: bool) -> Iterable[tuple[str, str, nx.Graph]]:
    # counts chosen so the full suite is ~10,000 instances.
    counts = {
        "er_sparse": 2500, "er_dense": 2500, "tri_free_bipartite": 1500,
        "planted_triangle": 1500, "planted_clique": 1000, "structured": 1000,
    } if big else {
        "er_sparse": 60, "er_dense": 60, "tri_free_bipartite": 40,
        "planted_triangle": 40, "planted_clique": 30, "structured": 30,
    }

    # Sparse Erdos-Renyi: small p, low n^{4/3}-relative density -> sparse regime.
    for i in range(counts["er_sparse"]):
        n = rng.randint(12, 60)
        p = rng.choice([0.02, 0.04, 0.06, 0.08])
        yield (f"er_sparse_{i:05d}", "er_sparse", _gnp(n, p, rng.randrange(2**31)))

    # Dense Erdos-Renyi: large p -> dense regime.
    for i in range(counts["er_dense"]):
        n = rng.randint(10, 40)
        p = rng.choice([0.4, 0.55, 0.7, 0.85])
        yield (f"er_dense_{i:05d}", "er_dense", _gnp(n, p, rng.randrange(2**31)))

    # Triangle-free bipartite: ground truth is always False.
    for i in range(counts["tri_free_bipartite"]):
        a = rng.randint(3, 18)
        b = rng.randint(3, 18)
        p = rng.choice([0.3, 0.5, 0.7, 0.9])
        G = nx.bipartite.random_graph(a, b, p, seed=rng.randrange(2**31))
        yield (f"bip_{i:05d}", "tri_free_bipartite", G)

    # Planted single triangle in an otherwise sparse graph (sparse regime, truth True).
    for i in range(counts["planted_triangle"]):
        n = rng.randint(15, 60)
        G = _gnp(n, rng.choice([0.01, 0.03, 0.05]), rng.randrange(2**31))
        t = rng.sample(range(n), 3)
        G.add_edges_from([(t[0], t[1]), (t[1], t[2]), (t[0], t[2])])
        yield (f"plant_tri_{i:05d}", "planted_triangle", G)

    # Planted clique inside a dense graph (dense regime, truth True, large clique).
    for i in range(counts["planted_clique"]):
        n = rng.randint(12, 36)
        G = _gnp(n, rng.choice([0.4, 0.5, 0.6]), rng.randrange(2**31))
        k = rng.randint(3, max(3, n // 2))
        clique = rng.sample(range(n), k)
        G.add_edges_from((clique[a], clique[b])
                         for a in range(k) for b in range(a + 1, k))
        yield (f"plant_clq_{i:05d}", "planted_clique", G)

    # Structured graphs: complete, cycles, wheels, complete-bipartite, regular.
    for i in range(counts["structured"]):
        kind = i % 5
        if kind == 0:
            n = rng.randint(4, 30)
            yield (f"complete_{i:05d}", "structured", nx.complete_graph(n))
        elif kind == 1:
            n = 2 * rng.randint(3, 25)  # even cycle -> triangle-free
            yield (f"cycle_{i:05d}", "structured", nx.cycle_graph(n))
        elif kind == 2:
            n = rng.randint(5, 30)
            yield (f"wheel_{i:05d}", "structured", nx.wheel_graph(n))
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


# ----------------------------------------------------------------------------
# Aggregation.
# ----------------------------------------------------------------------------
def _mean(xs: list[float]) -> float | None:
    return statistics.fmean(xs) if xs else None


def summarise(rows: list[dict]) -> dict:
    if not rows:
        return {"instances": 0}
    return {
        "instances": len(rows),
        "truth_positive": sum(1 for r in rows if r["truth"]),
        "aegypti_correct": sum(1 for r in rows if r["aegypti_correct"]),
        "chiba_correct": sum(1 for r in rows if r["chiba_correct"]),
        "matmul_correct": sum(1 for r in rows if r["matmul_correct"]),
        "aegypti_misses": sum(1 for r in rows if r["aegypti_miss"]),
        "invalid_witnesses": sum(1 for r in rows if not (r["aegypti_valid"] and r["chiba_valid"])),
        "all_agree": sum(1 for r in rows if r["all_agree"]),
        "mean_aegypti_ms": _mean([r["aegypti_ms"] for r in rows]),
        "mean_chiba_ms": _mean([r["chiba_ms"] for r in rows]),
        "mean_matmul_ms": _mean([r["matmul_ms"] for r in rows]),
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

    n_correct_aeg = overall["aegypti_correct"]
    n = overall["instances"]
    result = {
        "experiment": "car/ 10,000-instance three-algorithm triangle comparison for Finlay",
        "aegypti_version": AEGYPTI_VERSION,
        "seed": SEED,
        "subjects": {
            "aegypti": "algorithm.find_triangle_coordinates",
            "chiba_nishizeki": "algorithm.find_triangle_chiba_nishizeki",
            "matrix_multiplication": "algorithm.is_triangle_free_brute_force",
        },
        "oracle": "independent exact neighbourhood-intersection triangle test",
        "conclusion": {
            "instances": n,
            "aegypti_correct": n_correct_aeg,
            "aegypti_accuracy": (n_correct_aeg / n) if n else None,
            "aegypti_misses": overall["aegypti_misses"],
            "chiba_correct": overall["chiba_correct"],
            "matmul_correct": overall["matmul_correct"],
            "invalid_witnesses": overall["invalid_witnesses"],
            "all_three_agree": overall["all_agree"],
            "all_correct": n_correct_aeg == overall["chiba_correct"] == overall["matmul_correct"] == n,
            "scope_warning": "Finite small-graph evidence with exact oracles; not a worst-case completeness proof for the dense branch.",
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

    # Per-instance CSV.
    if rows:
        with (OUT_DIR / "car_by_instance.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    # Summary CSV.
    summ_cols = ["scope", "instances", "truth_positive", "aegypti_correct",
                 "chiba_correct", "matmul_correct", "aegypti_misses",
                 "invalid_witnesses", "all_agree", "mean_aegypti_ms",
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

    # Human-readable report.
    fam_rows = [{"family": k, **v} for k, v in by_family.items()]
    reg_rows = [{"regime": k, **v} for k, v in by_regime.items()]
    report = f"""# Finlay (Aegypti) CAR Experiment

Generated: {datetime.now(timezone.utc).isoformat()}
Aegypti version imported: {AEGYPTI_VERSION}
Seed: {SEED}

This report compares three triangle-detection routines from the installed
`aegypti` package on {n} deterministic small-graph instances, scored against an
independent exact triangle oracle.

Subjects:
1. **Aegypti** -- `find_triangle_coordinates` (hybrid, O(n^2) worst case)
2. **Chiba-Nishizeki** -- `find_triangle_chiba_nishizeki` (O(m^{{3/2}}))
3. **Matrix multiplication** -- `is_triangle_free_brute_force` (O(n^{{2.37}}))

## Headline

- Instances: {n}
- Aegypti correct: {n_correct_aeg}/{n}
- Aegypti misses (oracle says triangle, Aegypti said none): {overall['aegypti_misses']}
- Chiba-Nishizeki correct: {overall['chiba_correct']}/{n}
- Matrix multiplication correct: {overall['matmul_correct']}/{n}
- Invalid witnesses returned: {overall['invalid_witnesses']}
- All three agree: {overall['all_agree']}/{n}

Scope: finite small-graph evidence with exact oracles; this is a reproducible
regression / integrity check, not a worst-case completeness proof for the dense
branch of Aegypti.

## By regime

{_md_table(reg_rows, ["regime", "instances", "truth_positive", "aegypti_correct", "chiba_correct", "matmul_correct", "aegypti_misses", "mean_aegypti_ms", "mean_chiba_ms", "mean_matmul_ms"])}

## By family

{_md_table(fam_rows, ["family", "instances", "truth_positive", "aegypti_correct", "chiba_correct", "matmul_correct", "aegypti_misses", "mean_aegypti_ms", "mean_chiba_ms", "mean_matmul_ms"])}

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
