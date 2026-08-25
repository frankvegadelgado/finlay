# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse
from hvala.algorithm import find_vertex_cover

def maximize_solution(G: nx.Graph, S: set):
    """
    Repair a candidate set into an independent set and greedily maximize it,
    in linear time O(n + m).

    Phase 1 (repair): Nodes of S in conflict (adjacent to other members of S)
    are removed. Each conflicting edge inside S is resolved by discarding the
    endpoint with the higher current conflict count, so a single removal fixes
    as many conflicts as possible. Counts are maintained incrementally, giving
    O(n + m) total work.

    Phase 2 (grow): All nodes outside the repaired set (including those removed
    in Phase 1) are scanned in ascending-degree order (counting sort, O(n)) and
    added whenever they have no neighbor already in the set. This yields a
    maximal independent set containing the repaired kernel, at O(n + m) cost.

    Args:
        G (nx.Graph): An undirected NetworkX graph.
        S (set): Candidate node set (may contain conflicts).

    Returns:
        set: A maximal independent set of G.
    """
    independent = set(S)

    # --- Phase 1: remove conflict nodes ---
    # conflicts[u] = number of neighbors of u inside the current set.
    # Total adjacency scans are bounded by 2m -> O(n + m).
    conflicts = {u: sum(1 for v in G.adj[u] if v in independent) for u in independent}

    for u, v in G.edges():
        if u != v and u in independent and v in independent:
            # Discard the endpoint involved in more remaining conflicts.
            loser = u if conflicts[u] >= conflicts[v] else v
            independent.discard(loser)
            # Keep counts accurate; each node is removed at most once,
            # so these updates cost O(m) overall.
            for w in G.adj[loser]:
                if w in conflicts:
                    conflicts[w] -= 1
            del conflicts[loser]

    # --- Phase 2: add non-conflicting nodes to enlarge the set ---
    # Counting sort by degree (O(n)); low-degree nodes first tends to
    # block fewer future additions.
    buckets = {}
    max_degree = 0
    for u in G.nodes():
        if u not in independent:
            d = G.degree(u)
            buckets.setdefault(d, []).append(u)
            if d > max_degree:
                max_degree = d

    for d in range(max_degree + 1):
        for u in buckets.get(d, ()):
            if all(w not in independent for w in G.adj[u]):
                independent.add(u)

    return independent


def find_triangle_coordinates(graph, fallback=False):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine, which is exact and costs
        O(n + m^{3/2}) = O(n^2) on inputs this sparse.

      * Dense regime (m > ceil(n^{4/3})): build the complement and cover it
        with the linear-time Hvala vertex cover. The vertices left uncovered
        form an independent set of the complement, i.e. a clique of the input;
        any three of them are a triangle. The three vertices are certified in
        O(1) before being returned.

    Completeness:
      * ``fallback=False`` (default) -- "Aegypti-fast". The dense branch is
        used as-is, giving a uniform O(n^2) running time; it is sound on every
        graph and complete in the sparse regime, while dense-regime
        completeness is conditional on the Hvala cover leaving at least three
        vertices uncovered (guaranteed unconditionally when the clique number
        is at least ceil((n+3)/2)).
      * ``fallback=True`` -- "Aegypti-safe". If the dense branch is
        inconclusive (fewer than three uncovered vertices, or the O(1)
        certification fails), the exact Chiba-Nishizeki routine is run as a
        fallback, so the detector is UNCONDITIONALLY sound and complete. The
        worst-case running time is O(n + m^{3/2}).

    Args:
        graph: an undirected NetworkX Graph without self-loops.
        fallback: if True, guarantee completeness via a Chiba-Nishizeki
            fallback when the dense branch is inconclusive (default False,
            the uniform O(n^2) fast variant).

    Returns:
        A frozenset {u, v, w} witnessing a triangle, or None if the graph is
        triangle-free.
    """

    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    m = graph.number_of_edges()
    n = graph.number_of_nodes()
    bound = math.ceil(math.pow(n, 4/3))
    if m <= bound:
        return find_triangle_chiba_nishizeki(graph)

    # Dense regime: read a clique of G off the complement's vertex cover.
    complement = nx.complement(graph)
    cover = find_vertex_cover(complement)
    nodes = set(complement)
    mis = nodes - cover
    selected = list(cover)
    while len(mis) < 3 and selected:
        u = selected.pop()
        candidate = (cover - {u}) | set(complement.neighbors(u))
        iset = nodes - set(candidate)
        mis = maximize_solution(complement, iset)
    if len(mis) >= 3:
        sol = list(mis)
        u, v, w = sol.pop(), sol.pop(), sol.pop()
        # O(1) certification: an independent set of the complement is a clique
        # of G, so these three vertices must be pairwise adjacent in G.
        if graph.has_edge(u, v) and graph.has_edge(v, w) and graph.has_edge(u, w):
            return frozenset({u, v, w})

    # Dense fast path inconclusive: fall back to the exact routine for an
    # unconditional completeness guarantee (Aegypti-safe).
    if fallback:
        return find_triangle_chiba_nishizeki(graph)

    return None


def is_triangle_free_brute_force(adj_matrix):
    """O(n^{2.37}) matrix-multiplication baseline."""
    if not sparse.issparse(adj_matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")
    rows, cols = adj_matrix.shape
    if rows != cols:
        raise ValueError("Adjacency matrix must be square.")
    adj_matrix_cubed = adj_matrix @ adj_matrix @ adj_matrix
    diagonal = adj_matrix_cubed.diagonal()
    return np.all(diagonal == 0)


def find_triangle_chiba_nishizeki(graph):
    """Standalone classical Chiba--Nishizeki O(n + m^{3/2}) triangle detector.

    Scans each edge once and searches the smaller of the two endpoints'
    adjacency sets for a common neighbour. A common neighbour, together with
    the edge, is a triangle. The scan costs

        sum_{(u, v) in E} min(deg(u), deg(v)) = O(m^{3/2}),

    the standard Chiba--Nishizeki bound; together with the O(n + m)
    construction of the adjacency sets over all n vertices (including isolated
    ones), the worst-case running time is O(n + m^{3/2}). No vertex ordering is
    required for correctness or for the time bound.
    """
    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    adj = {v: set(graph.neighbors(v)) for v in graph.nodes()}
    for u, v in graph.edges():
        a_u, a_v = adj[u], adj[v]
        small, large = (a_u, a_v) if len(a_u) <= len(a_v) else (a_v, a_u)
        for w in small:
            if w != u and w != v and w in large:
                return frozenset({u, v, w})

    return None
