# Version: v0.4.9
# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
import itertools
from scipy import sparse
from hvala.algorithm import find_vertex_cover

def maximize_solution(G: nx.Graph, S: set):
    """
    Repair a candidate set into an independent set and greedily maximize it 
    up to a target size of 3.
    
    By capping the maximum independent set size at 3 (the exact size needed 
    to certify a triangle), conflict checks against the current independent 
    set take O(1) operations per node. This completely avoids iterating over 
    full neighborhoods, guaranteeing a strict O(n) overall runtime.

    Args:
        G (nx.Graph): An undirected NetworkX graph (the complement graph).
        S (set): Candidate node set (may contain conflicts).

    Returns:
        set: An independent set of G (capped at size 3).
    """
    independent = set()
    
    # --- Phase 1: Fast repair (capped at size 3) ---
    for u in S:
        conflict = False
        # O(1) inner loop since |independent| < 3
        for v in independent:
            if G.has_edge(u, v):
                conflict = True
                break
        
        if not conflict:
            independent.add(u)
            if len(independent) == 3:
                return independent
                
    # --- Phase 2: Greedily maximize (capped at size 3) ---
    for u in G.nodes():
        if u not in independent:
            conflict = False
            # O(1) inner loop since |independent| < 3
            for v in independent:
                if G.has_edge(u, v):
                    conflict = True
                    break
            
            if not conflict:
                independent.add(u)
                if len(independent) == 3:
                    return independent
                    
    return independent


def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine.

      * Dense regime (m > ceil(n^{4/3})): build the complement and cover it
        with the linear-time Hvala vertex cover. 
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
    visited = {frozenset({})}
    while len(mis) < 3 and selected:
        aux = frozenset(mis)
        if aux not in visited:
            visited.add(aux)    
            sol = list(mis)
            if len(mis) == 1:
                v = sol.pop()
                # O(n) to find G's neighbors using the complement graph
                neighbors_G = nodes - set(complement.neighbors(v)) - {v}
                
                # Check at most m_H + 1 pairs. Max time: O(m_H)
                for x, y in itertools.combinations(neighbors_G, 2):
                    if not complement.has_edge(x, y):
                        mis.update({x, y})
                        break
            else:
                v, w = sol.pop(), sol.pop()
                disconnected_v = nodes - set(complement.neighbors(v))
                disconnected_w = nodes - set(complement.neighbors(w))
                mis.update(disconnected_v & disconnected_w)
                if len(mis) < 3:
                    for z in [v, w]:
                        mis = {z}
                        aux = frozenset(mis)
                        if aux not in visited:
                            # Apply the same O(m_H) complement trick here
                            neighbors_G = nodes - set(complement.neighbors(z)) - {z}
                            for x, y in itertools.combinations(neighbors_G, 2):
                                if not complement.has_edge(x, y):
                                    mis.update({x, y})
                                    break
                            
                            if len(mis) >= 3:
                                break  
                visited.add(frozenset({v}))
                visited.add(frozenset({w}))
                                                    
            if len(mis) >= 3:
                break
        u = selected.pop()
        candidate = (cover - {u}) | set(complement.neighbors(u))
        iset = nodes - set(candidate)
        mis = maximize_solution(complement, iset)
        
    if len(mis) >= 3:
        sol = list(mis)
        u, v, w = sol.pop(), sol.pop(), sol.pop()
        if graph.has_edge(u, v) and graph.has_edge(v, w) and graph.has_edge(u, w):
            return frozenset({u, v, w})

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