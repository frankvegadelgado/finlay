# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
from scipy import sparse


def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    This implementation maps vertices to 0..n-1 and stores each
    neighbourhood as a Python integer bit mask.  It then scans unordered
    vertex pairs (u, v).  If (u, v) is an edge and their masks intersect,
    any set bit in the intersection gives a witness w such that
    {u, v, w} is a triangle.

    The outer scan performs O(n^2) pair iterations and O(n + m) setup.
    At the bit-complexity level, each mask intersection costs O(n / word).
    """
    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")

    nodes = list(graph.nodes())
    n = len(nodes)
    if n < 3 or graph.number_of_edges() == 0:
        return None

    node_to_id = {node: i for i, node in enumerate(nodes)}
    adj_masks = [0] * n

    for u, v in graph.edges():
        i = node_to_id[u]
        j = node_to_id[v]
        adj_masks[i] |= 1 << j
        adj_masks[j] |= 1 << i

    for i in range(n - 1):
        mask_i = adj_masks[i]
        for j in range(i + 1, n):
            if not (mask_i >> j) & 1:
                continue

            common = mask_i & adj_masks[j]
            if common:
                k = (common & -common).bit_length() - 1
                return frozenset({nodes[i], nodes[j], nodes[k]})

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
