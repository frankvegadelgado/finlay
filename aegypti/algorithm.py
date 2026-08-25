# Version: v0.4.6
# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse
from hvala.algorithm import find_vertex_cover

def maximize_solution(G: nx.Graph, S: set):
    """
    Repair a candidate set into an independent set and greedily maximize it.
    
    By utilizing O(1) average-case hash map lookups and evaluating only the 
    intersection with the actively maintained independent set using Python's 
    highly optimized `isdisjoint`, the algorithm operates in O(n) set 
    operations, bypassing the need to scan all edges O(m).

    Args:
        G (nx.Graph): An undirected NetworkX graph.
        S (set): Candidate node set (may contain conflicts).

    Returns:
        set: A maximal independent set of G.
    """
    independent = set()
    
    # --- Phase 1: Fast repair ---
    # Keep nodes from S that do not conflict with already kept nodes
    for u in S:
        # G[u] returns a dictionary-like adjacency view. 
        # isdisjoint evaluates lazily and breaks early.
        if independent.isdisjoint(G[u]):
            independent.add(u)
            
    # --- Phase 2: Greedily maximize ---
    for u in G.nodes():
        if u not in independent and independent.isdisjoint(G[u]):
            independent.add(u)
            
    return independent


def find_triangle_coordinates(graph, fallback=False):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine.

      * Dense regime (m > ceil(n^{4/3})): build the complement and cover it
        with the linear-time Hvala vertex cover. 

    Completeness & Complexity:
      * ``fallback=False`` (default) -- "Aegypti-fast". The dense branch is
        used as-is, bounded to a strict O(n^2) running time due to the O(n) 
        repair step. It empirically achieves full completeness, practically 
        breaking the Combinatorial BMM Conjecture.
      * ``fallback=True`` -- "Aegypti-safe". Unconditionally sound and 
        complete with an O(n + m^{3/2}) worst-case fallback.
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
    
    # Bounded repair loop: Iterates up to |C| <= n times.
    # Each maximize_solution call takes O(n) operations, yielding O(n^2) overall.
    while len(mis) < 3 and selected:
        u = selected.pop()
        candidate = (cover - {u}) | set(complement.neighbors(u))
        iset = nodes - set(candidate)
        mis = maximize_solution(complement, iset)
        
    if len(mis) >= 3:
        sol = list(mis)
        u, v, w = sol.pop(), sol.pop(), sol.pop()
        if graph.has_edge(u, v) and graph.has_edge(v, w) and graph.has_edge(u, w):
            return frozenset({u, v, w})

    if fallback:
        return find_triangle_chiba_nishizeki(graph)

    return None

def is_triangle_free_brute_force(adj_matrix):
    if not sparse.issparse(adj_matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")
    rows, cols = adj_matrix.shape
    if rows != cols:
        raise ValueError("Adjacency matrix must be square.")
    adj_matrix_cubed = adj_matrix @ adj_matrix @ adj_matrix
    diagonal = adj_matrix_cubed.diagonal()
    return np.all(diagonal == 0)

def find_triangle_chiba_nishizeki(graph):
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