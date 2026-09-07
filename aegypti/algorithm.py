# Version: v0.5.0
# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse
from .disjoint import FastCliqueUF


def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine.

      * Dense regime (m > ceil(n^{4/3})): build the disjoint set
        for finding the detection. 
    """

    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")
    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    # Work on a copy so the original graph remains unchanged
    working_graph = graph.copy()
    
    # Remove self-loops; they do not affect clique structure
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
    
    # Remove isolated nodes (degree 0), since they cannot belong to any clique
    isolates = list(nx.isolates(working_graph))
    working_graph.remove_nodes_from(isolates)

    m = working_graph.number_of_edges()
    n = working_graph.number_of_nodes()
    bound = math.ceil(math.pow(n, 4/3))
    if m <= bound:
        return find_triangle_chiba_nishizeki(working_graph)
    else:
        disjoint_set = FastCliqueUF(working_graph)
        found = None
        for u in working_graph:
            neighbors = list(working_graph.neighbors(u))
            for v in neighbors:
                if disjoint_set.add(v):
                    found = u
                    break
            if found is not None:
                break
            while neighbors:
                w = neighbors.pop()
                disjoint_set.remove(w)
        if found is not None:
            # Extract all components of size >= 2 (potential cliques)
            cliques = [s for s in disjoint_set.to_sets() if len(s) >= 2]
    
            # Choose the largest clique-like component if any exist;
            max_clique = max(cliques, key=len)  
            sol = list(max_clique) + [found]
            u, v, w = sol.pop(), sol.pop(), sol.pop()
            if working_graph.has_edge(u, v) and working_graph.has_edge(v, w) and working_graph.has_edge(u, w):
                return frozenset({u, v, w})
            else:    
                raise RuntimeError(f"The strict quadratic reduction failed with {(u, v, w)}")

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