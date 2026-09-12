# Version: v0.5.6
# Modified on 12/09/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse

def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX Graph.
    
    The algorithm splits on density at the threshold ceil(n^{4/3}):
      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki routine 
        optimized with non-decreasing degree ordering.
      * Dense regime (m > ceil(n^{4/3})): utilizes a square root partition strategy 
        combined with bipartite short-circuiting to heavily restrict iterations.
    """
    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    working_graph = graph.copy()
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
    
    isolates = list(nx.isolates(working_graph))
    working_graph.remove_nodes_from(isolates)

    m = working_graph.number_of_edges()
    n = working_graph.number_of_nodes()
    bound = math.ceil(math.pow(n, 4/3))
 
    if nx.is_bipartite(working_graph):
        return None
    elif m <= bound:
        return find_triangle_chiba_nishizeki(working_graph)
    else:
        sparse_graph = working_graph.copy()
        
        while m > bound:
                
            coloring = nx.greedy_color(sparse_graph, strategy='largest_first')
            pivot_vertices = {v for v, c in coloring.items() if c == 0}
            triangle = find_triangle_coloring_restricted(sparse_graph, pivot_vertices)
            if triangle is not None:
                return triangle
            
            sparse_graph.remove_nodes_from(pivot_vertices)
            
            m = sparse_graph.number_of_edges()
            n = sparse_graph.number_of_nodes()
            bound = math.ceil(math.pow(n, 4/3))

            # Short-circuit: A bipartite graph guarantees no triangles exist.
            if nx.is_bipartite(sparse_graph):
                return None

        return find_triangle_chiba_nishizeki(sparse_graph)    
 

def find_triangle_coloring_restricted(graph, pivot_vertices):
    """Chiba-Nishizeki with the outer loop restricted to pivot_vertices,
    but full adjacency (from `graph`, not an induced subgraph) used for
    every neighbor/intersection check."""
    degrees = dict(graph.degree())
    pivots_sorted = sorted(pivot_vertices, key=lambda x: degrees[x])
    adj = {v: set(graph.neighbors(v)) - pivot_vertices  for v in graph.nodes()}
    for u in pivots_sorted:
        a_u = adj[u]
        for v in list(a_u):
            a_v = adj[v]
            small, large = (a_u, a_v) if len(a_u) <= len(a_v) else (a_v, a_u)
            for w in small:
                if w != u and w != v and w in large:
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

    # Optimized: Sorted in non-decreasing degree order
    degrees = dict(graph.degree())
    nodes_sorted = sorted(graph.nodes(), key=lambda x: degrees[x])
    
    adj = {v: set(graph.neighbors(v)) for v in graph.nodes()}
    
    for u in nodes_sorted:
        a_u = adj[u]
        for v in list(a_u):
            a_v = adj[v]
            small, large = (a_u, a_v) if len(a_u) <= len(a_v) else (a_v, a_u)
            for w in small:
                if w != u and w != v and w in large:
                    return frozenset({u, v, w})
            # Dynamically remove evaluated edges to prune the search space
            adj[v].discard(u)
        adj[u].clear()

    return None