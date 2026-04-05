# Modified on 04/04/2026
# Author: Frank Vega


import numpy as np
from scipy import sparse
import networkx as nx
from .disjoint import FastCliqueUF

def find_triangle_coordinates(graph):
    """
    Detect a single triangle (3-clique) in an undirected NetworkX graph.

    A triangle is a set of three vertices {u, v, w} such that the edges
    (u, v), (v, w), and (u, w) all exist.

    This function uses a **hybrid approach** for efficiency:
    1. Primary fast path: A clique-constrained Union-Find (`FastCliqueUF`)
       that only merges two vertices when the resulting component remains
       a clique. As soon as any component reaches size ≥ 3, a triangle
       is guaranteed to exist.
    2. Fallback: If the UF pass does not detect a triangle, a standard
       O(m^{3/2})-style enumeration using adjacency-set intersections is
       performed (still early-exits on the first triangle found).

    Args:
        graph (nx.Graph):
            An undirected simple graph (no self-loops, no multi-edges).
            Nodes may be any hashable Python objects.

    Returns:
        Optional[FrozenSet[Hashable]]:
            A frozenset containing the three vertices of one triangle if
            a triangle exists, otherwise None.

    Raises:
        ValueError: If the input is not an undirected nx.Graph or contains
                    self-loops.
    """
    # --- Input validation ----------------------------------------------------
    if not isinstance(graph, nx.Graph) or graph.is_directed():
        raise ValueError("Input must be an undirected NetworkX Graph.")

    if nx.number_of_selfloops(graph) > 0:
        raise ValueError("Graph must not contain self-loops.")

    # Early exit: graphs with fewer than 3 nodes or no edges cannot contain triangles
    if graph.number_of_nodes() < 3 or graph.number_of_edges() == 0:
        return None

    # --- Fast path: Clique-constrained Union-Find ---------------------------
    # FastCliqueUF only performs a union when the resulting component is still
    # a clique. If union(u, v) returns True, a clique of size ≥ 3 was formed
    # → a triangle has been detected.
    disjoint_set = FastCliqueUF(graph)

    found_in_uf = False
    for u, v in graph.edges():
        if disjoint_set.union(u, v):
            found_in_uf = True
            break  # Triangle found — no need to process remaining edges

    if found_in_uf:
        # Extract the first clique of size ≥ 3 (guaranteed to be a triangle)
        # to_sets() returns all current components after full path compression.
        for component in disjoint_set.to_sets():
            if len(component) >= 3:
                return frozenset(component)
        # (This line should never be reached if FastCliqueUF is correct)

    # --- Fallback: Explicit triangle enumeration via adjacency intersection --
    # If the UF pass did not detect a triangle, we fall back to a standard
    # efficient triangle-finding algorithm:
    #   • Precompute adjacency sets for O(1) intersections.
    #   • Use node ranking to process each undirected edge {u, v} exactly once.
    #   • For each edge, compute common neighbors → any w forms a triangle.
    adj_sets = {node: set(graph.neighbors(node)) for node in graph.nodes()}
    rank = {node: i for i, node in enumerate(graph.nodes())}

    for u in graph.nodes():
        for v in graph.neighbors(u):
            # Process each undirected edge exactly once (u has lower rank than v)
            if rank[u] < rank[v]:
                # Intersection gives all common neighbors w (each forms a triangle)
                common_neighbors = adj_sets[u] & adj_sets[v]
                for w in common_neighbors:
                    return frozenset({u, v, w})

    # No triangle found after both passes
    return None

def is_triangle_free_brute_force(adj_matrix):
    """
    Checks if a graph represented by a sparse adjacency matrix is triangle-free using matrix multiplication.

    Args:
        adj_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.

    Returns:
        True if the graph is triangle-free, False otherwise.
        Raises ValueError if the input matrix is not square.
        Raises TypeError if the input is not a sparse matrix.
    """

    if not sparse.issparse(adj_matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")

    rows, cols = adj_matrix.shape
    if rows != cols:
        raise ValueError("Adjacency matrix must be square.")

    # Calculate A^3 (matrix multiplication of A with itself three times)
    adj_matrix_cubed = adj_matrix @ adj_matrix @ adj_matrix #more efficient than matrix power

    # Check the diagonal of A^3. A graph has a triangle if and only if A^3[i][i] > 0 for some i.
    # Because A^3[i][i] represents the number of paths of length 3 from vertex i back to itself.
    # Efficiently get the diagonal of a sparse matrix
    diagonal = adj_matrix_cubed.diagonal()
    return np.all(diagonal == 0)