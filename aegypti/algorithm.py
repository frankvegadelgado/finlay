# Version: v0.5.5
# Modified on 11/09/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
import secrets
from scipy import sparse
from hvala.algorithm import find_vertex_cover

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
        complement = nx.complement(working_graph)
        
        while m > bound:
            # Short-circuit: A bipartite graph guarantees no triangles exist.
            if nx.is_bipartite(sparse_graph):
                return None
                
            cover = find_vertex_cover(complement)
            mis = set(complement) - cover
            if len(mis) >= 3:
                sol = list(mis)
                u, v, w = sol.pop(), sol.pop(), sol.pop()
                if working_graph.has_edge(u, v) and working_graph.has_edge(v, w) and working_graph.has_edge(u, w):
                    return frozenset({u, v, w})
                else:
                    raise RuntimeError(f"Invalid reduction producing a false triangle {(u, v, w)}")
            
            sqrt = max(2, math.floor(math.sqrt(n)))
            coloring = nx.greedy_color(sparse_graph, strategy='largest_first')
            pivot_vertices = [v for v, c in coloring.items() if c > 1]
            if len(pivot_vertices) <= sqrt:
                return find_triangle_coloring_restricted(sparse_graph, pivot_vertices)
            
            # Alternative Bisection Partitioning Strategy
            vertices = list(sparse_graph.nodes())
            secrets.SystemRandom().shuffle(vertices)
            
            mapping = {u: k for k, u in enumerate(vertices)}
            nodes = {}
            for u in sparse_graph.nodes():
                nodes.setdefault(mapping[u] % sqrt, set()).add(u)
            
            for k in nodes.keys():
                working_subgraph = sparse_graph.subgraph(nodes[k]) 
                if working_subgraph.number_of_edges() > 0:
                    triangle = find_triangle_chiba_nishizeki(working_subgraph) 
                    if triangle is not None:
                        return triangle
                    else:
                        edges_subgraph = list(working_subgraph.edges())
                        sparse_graph.remove_edges_from(edges_subgraph)
                        complement.add_edges_from(edges_subgraph)

            isolates = list(nx.isolates(sparse_graph))
            sparse_graph.remove_nodes_from(isolates)
            complement.remove_nodes_from(isolates)

            m = sparse_graph.number_of_edges()
            n = sparse_graph.number_of_nodes()
            bound = math.ceil(math.pow(n, 4/3))

        return find_triangle_chiba_nishizeki(sparse_graph)    
 

def find_triangle_coloring_restricted(graph, pivot_vertices):
    """Chiba-Nishizeki with the outer loop restricted to pivot_vertices,
    but full adjacency (from `graph`, not an induced subgraph) used for
    every neighbor/intersection check."""
    degrees = dict(graph.degree())
    pivots_sorted = sorted(pivot_vertices, key=lambda x: degrees[x])
    adj = {v: set(graph.neighbors(v)) for v in graph.nodes()}
    for u in pivots_sorted:
        a_u = adj[u]
        for v in list(a_u):
            a_v = adj[v]
            small, large = (a_u, a_v) if len(a_u) <= len(a_v) else (a_v, a_u)
            for w in small:
                if w != u and w != v and w in large:
                    return frozenset({u, v, w})
            # NOTE: unlike the standard routine, we do NOT prune a_u/a_v
            # here by removing evaluated edges -- pivots are a strict
            # subset of all vertices, so an edge (u, v) with v not a
            # pivot would never get its own outer-loop pass to complete
            # the pruning invariant the original routine relies on.
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