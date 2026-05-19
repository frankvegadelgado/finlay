# Modified on 04/04/2026
# Author: Frank Vega


import numpy as np
from scipy import sparse
import networkx as nx
from .disjoint import FastCliqueUF

def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    Hybrid approach:
    1. Phase 1 -- fast path: A clique-constrained Union-Find (FastCliqueUF)
       with *matching-first* edge ordering and *delete-on-reject*.  We
       compute M = nx.approximation.min_maximal_matching(G) and union all
       its edges first (each forms a 2-clique).  Then we iterate over the
       extra (non-matching) edges; each one whose union is rejected is
       deleted from the FastCliqueUF bitset structure (matching edges are
       never deleted).  If any union produces a clique of size >= 3, the
       triangle is returned.

    2. Phase 2 -- fallback: classical adjacency-intersection enumeration,
       skipping matching edges (proof: if Phase 1 returned no triangle,
       no matching edge is in any triangle), so the bound is
       O((m - |M|)^{3/2}) instead of O(m^{3/2}).

    Args:
        graph (nx.Graph): undirected simple graph.

    Returns:
        Optional[FrozenSet[Hashable]]: a frozenset of three triangle
            vertices, or None if the graph is triangle-free.
    """
    from itertools import islice

    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    disjoint_set = FastCliqueUF(graph)

    matching = nx.approximation.min_maximal_matching(graph)
    matching_set = set()
    for u, v in matching:
        matching_set.add(frozenset((u, v)))

    found_in_uf = False

    for u, v in matching:
        if disjoint_set.union(u, v):
            found_in_uf = True
            break

    if not found_in_uf:
        for u, v in graph.edges():
            if frozenset((u, v)) in matching_set:
                continue
            if disjoint_set.union(u, v):
                found_in_uf = True
                break
            disjoint_set.delete_edge(u, v)

    if found_in_uf:
        for component in disjoint_set.to_sets():
            if len(component) >= 3:
                return frozenset(islice(component, 3))

    adj_sets = {node: set(graph.neighbors(node)) for node in graph.nodes()}
    rank = {node: i for i, node in enumerate(graph.nodes())}

    for u in graph.nodes():
        for v in graph.neighbors(u):
            if rank[u] < rank[v]:
                if frozenset((u, v)) in matching_set:
                    continue
                common_neighbors = adj_sets[u] & adj_sets[v]
                for w in common_neighbors:
                    return frozenset({u, v, w})

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
