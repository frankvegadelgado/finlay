# Created on 04/04/2026
# Author: Frank Vega

import itertools
from . import utils

import networkx as nx
from .disjoint import FastCliqueUF

def find_clique(graph):
    """
    Compute an approximate clique set for an undirected graph by using a
    clique‑constrained FastCliqueUF structure. The largest resulting component
    that satisfies the clique constraint is returned.

    Args:
        graph (nx.Graph): A NetworkX Graph object representing the input graph.

    Returns:
        set: A set of vertex indices representing the approximate clique set.
             Returns an empty set if the graph is empty or has no edges.
    """
    
    # Ensure the input is a simple undirected graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
    
    # If the graph has no nodes, no clique can exist
    if graph.number_of_nodes() == 0:
        return set()
    
    # Work on a copy so the original graph remains unchanged
    working_graph = graph.copy()
    
    # Remove self-loops; they do not affect clique structure
    working_graph.remove_edges_from(list(nx.selfloop_edges(working_graph)))
    
    # Remove isolated nodes (degree 0), since they cannot belong to any clique
    isolates = list(nx.isolates(working_graph))
    working_graph.remove_nodes_from(isolates)
    
    # Initialize the clique-constrained UnionFind over all nodes
    if working_graph.number_of_edges() == 0:
        # If there are no edges, the largest clique is just one of the isolated nodes (if any)
        return {isolates[0]} if isolates else set()
    disjoint_set = FastCliqueUF(working_graph)
    
    # Attempt to union each edge; the modified UnionFind only merges
    # components if the union remains a clique in the graph
    for u, v in graph.edges():
        disjoint_set.union(u, v)
    
    # Extract all components of size >= 2 (potential cliques)
    cliques = [s for s in disjoint_set.to_sets() if len(s) >= 2]
    
    # Choose the largest clique-like component if any exist;
    approximate_clique = max(cliques, key=len)
    
    # Return the largest approximate clique found
    return approximate_clique

def find_clique_brute_force(graph):
    """
    Computes an exact maximum clique in exponential time.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the exact clique, or None if the graph is empty.
    """

    
    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    n_vertices = len(graph.nodes())

    n_max_vertices = 0
    best_solution = None

    for k in range(1, n_vertices + 1): # Iterate through all possible sizes of the cover
        for candidate in itertools.combinations(graph.nodes(), k):
            clique_candidate = set(candidate)
            if utils.is_clique(graph, clique_candidate) and len(clique_candidate) > n_max_vertices:
                n_max_vertices = len(clique_candidate)
                best_solution = clique_candidate
                
    return best_solution


def find_clique_approximation(graph):
    """
    Computes an approximate clique in polynomial time with a polynomial-approximation ratio for undirected graphs.

    Args:
        graph: A NetworkX Graph.

    Returns:
        A set of vertex indices representing the approximate clique, or None if the graph is empty.
    """

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:
        return None

    #networkx doesn't have a guaranteed maximum clique function, so we use approximation
    clique = nx.approximation.max_clique(graph)
    return clique