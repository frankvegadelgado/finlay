# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse
from hvala.algorithm import find_vertex_cover


def find_triangle_coordinates(graph, fallback=False):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine, which is exact and costs O(m^{3/2})
        = O(n^2) on inputs this sparse.

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
        worst-case running time is O(m^{3/2}).

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
    mis = set(complement) - find_vertex_cover(complement)
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
    """Standalone classical Chiba--Nishizeki O(m^{3/2}) baseline."""
    import heapq

    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    adj = {v: set(graph.neighbors(v)) for v in graph.nodes()}
    remaining = {v: set(neigh) for v, neigh in adj.items()}
    rank = {}
    order = []
    heap = [(len(remaining[v]), v) for v in remaining]
    heapq.heapify(heap)
    removed = set()
    while heap:
        d, v = heapq.heappop(heap)
        if v in removed:
            continue
        if len(remaining[v]) != d:
            heapq.heappush(heap, (len(remaining[v]), v))
            continue
        rank[v] = len(order)
        order.append(v)
        removed.add(v)
        for w in list(remaining[v]):
            remaining[w].discard(v)
            heapq.heappush(heap, (len(remaining[w]), w))
        remaining[v].clear()

    for u, v in graph.edges():
        if rank[u] > rank[v]:
            u, v = v, u
        a_u = adj[u]
        a_v = adj[v]
        if len(a_u) > len(a_v):
            small, large = a_v, a_u
        else:
            small, large = a_u, a_v
        for w in small:
            if w != u and w != v and w in large:
                return frozenset({u, v, w})

    return None
