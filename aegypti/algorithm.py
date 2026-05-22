# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
from scipy import sparse

from .disjoint import FastCliqueUF

PHASE1_LOOKAHEAD_BATCH = 32


def _probe_triangle_on_edge(u, v, degree, get_adj_set, limit=8):
    """
    Try a bounded common-neighbor probe around edge (u, v).

    This increases Phase 1's chance of detecting an existing triangle while
    keeping the total extra work linear: each edge checks at most ``limit``
    candidates, and adjacency sets are cached.
    """
    if degree[u] <= degree[v]:
        candidates = get_adj_set(u)
        membership = get_adj_set(v)
    else:
        candidates = get_adj_set(v)
        membership = get_adj_set(u)

    for checked, w in enumerate(candidates):
        if checked >= limit:
            break
        if w in membership:
            return frozenset({u, v, w})
    return None


def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    Hybrid approach:
    1. Phase 1 -- fast path: A clique-constrained Union-Find (FastCliqueUF)
       with matching-first edge ordering, bounded common-neighbor probes,
       and fixed-size delete lookahead.

    2. Phase 2 -- fallback: remove matching edges for the base-edge scan,
       compute a greedy linear-time 2-approximation vertex cover on those
       remaining edges, and run adjacency-intersection enumeration only
       from that cover. Intersections still use the full graph, so
       triangles touching a matching edge remain visible.
    """
    from itertools import islice

    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    disjoint_set = FastCliqueUF(graph)
    degree = dict(graph.degree())
    adj_sets = {}

    def get_adj_set(node):
        neighbors = adj_sets.get(node)
        if neighbors is None:
            neighbors = set(graph.neighbors(node))
            adj_sets[node] = neighbors
        return neighbors

    matching = nx.approximation.min_maximal_matching(graph)
    matching_set = {frozenset((u, v)) for u, v in matching}

    found_in_uf = False

    for u, v in matching:
        if disjoint_set.union(u, v):
            found_in_uf = True
            break

    if not found_in_uf:
        probe_budget = max(16, graph.number_of_nodes())
        rejected_lookahead = []
        for u, v in graph.edges():
            if frozenset((u, v)) in matching_set:
                continue
            if probe_budget > 0 and min(degree[u], degree[v]) >= 2:
                probe_budget -= 1
                probed_triangle = _probe_triangle_on_edge(u, v, degree, get_adj_set)
                if probed_triangle is not None:
                    return probed_triangle
            if disjoint_set.union(u, v):
                found_in_uf = True
                break
            rejected_lookahead.append((u, v))
            if len(rejected_lookahead) >= PHASE1_LOOKAHEAD_BATCH:
                for rejected_u, rejected_v in rejected_lookahead:
                    disjoint_set.delete_edge(rejected_u, rejected_v)
                rejected_lookahead.clear()
        else:
            for rejected_u, rejected_v in rejected_lookahead:
                disjoint_set.delete_edge(rejected_u, rejected_v)

    if found_in_uf:
        for component in disjoint_set.to_sets():
            if len(component) >= 3:
                return frozenset(islice(component, 3))

    vertex_cover = []
    covered = set()
    for u, v in graph.edges():
        if frozenset((u, v)) in matching_set:
            continue
        if u not in covered and v not in covered:
            vertex_cover.extend((u, v))
            covered.add(u)
            covered.add(v)

    rank = {node: i for i, node in enumerate(vertex_cover)}

    for u in vertex_cover:
        for v in graph.neighbors(u):
            if v in rank and rank[u] >= rank[v]:
                continue
            if frozenset((u, v)) in matching_set:
                continue

            u_neighbors = get_adj_set(u)
            if degree[u] <= degree[v]:
                candidates = u_neighbors
                membership = get_adj_set(v)
            else:
                candidates = get_adj_set(v)
                membership = u_neighbors

            for w in candidates:
                if w in membership:
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
