# Version: v0.5.1
# Modified on 04/04/2026
# Author: Frank Vega

import networkx as nx
import numpy as np
import math
from scipy import sparse


def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    The algorithm splits on density at the threshold ceil(n^{4/3}):

      * Sparse regime (m <= ceil(n^{4/3})): run the Chiba-Nishizeki
        adjacency-intersection routine.

      * Dense regime (m > ceil(n^{4/3})): build a reduction graph
        and run the Chiba-Nishizeki algorithm. 
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
        mapping = {u: k for k, u in enumerate(working_graph.nodes())}
        sqrt = max(2, math.floor(math.sqrt(working_graph.number_of_nodes())))
        nodes = {}
        for u in working_graph.nodes():
            nodes.setdefault(mapping[u] % sqrt, set()).add(u)
        for k in nodes.keys():
            working_subgraph = working_graph.subgraph(nodes[k]) 
            triangle = find_triangle_chiba_nishizeki(working_subgraph) 
            if triangle is not None:
                return triangle
        G = nx.Graph()
        for u, v in working_graph.edges():
            i, j = mapping[u] % sqrt, mapping[v] % sqrt
            if not G.has_edge(i, j): 
                G.add_edge(i, j)      
        adj = {v: set(G.neighbors(v)) for v in G.nodes()}
        for u, v in G.edges():
            a_u, a_v = adj[u], adj[v]
            small, large = (a_u, a_v) if len(a_u) <= len(a_v) else (a_v, a_u)
            for w in small:
                if w in large:
                    component = nodes[u] | nodes[v] | nodes[w]
                    working_subgraph = working_graph.subgraph(component) 
                    triangle = find_triangle_chiba_nishizeki(working_subgraph) 
                    if triangle is not None:
                        return triangle
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