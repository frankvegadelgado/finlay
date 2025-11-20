# Modified on 01/14/2025
# Author: Frank Vega


import numpy as np
from scipy import sparse
import networkx as nx

def find_triangle_coordinates(graph, first_triangle=True):
    """
    Finds triangles in an undirected NetworkX graph.
    
    A triangle is a set of three nodes where each node is connected to the other two.
    This function detects triangles by checking common neighbors for each node.
    
    Args:
        graph (nx.Graph): An undirected NetworkX graph (must have no self-loops or multiple edges).
        first_triangle (bool): If True, returns as soon as the first triangle is found 
                               (useful for quick triangle detection). 
                               If False, finds all triangles in the graph.
    
    Returns:
        Optional[List[FrozenSet[int]]]: 
            - List of sets, each containing 3 nodes forming a triangle, or
            - A list with a single triangle if first_triangle=True, or
            - None if no triangles exist or graph is empty.
    """
    # Input validation
    if not isinstance(graph, nx.Graph):                                 # Ensure the input is a NetworkX Graph
        raise ValueError("Input must be an undirected NetworkX Graph.")
    
    if nx.number_of_selfloops(graph) > 0:                               # Self-loops would invalidate triangle logic
        raise ValueError("Graph must not contain self-loops.")

    if graph.number_of_nodes() == 0 or graph.number_of_edges() == 0:   # Empty graph or no edges → no triangles
        return None

    triangles = []                                                      # Will collect all found triangles

    density = nx.density(graph)                                         # Graph density to choose the faster algorithm
    nodes = sorted(graph.nodes(), key=graph.degree, reverse=True)      # Process higher degree nodes first for speed

    # ------------------------- SPARSE GRAPH PATH (density < 0.1) -------------------------
    if density < 0.1:
        adj_sets = {node: set(graph.neighbors(node)) for node in graph}
        rank = {node: i for i, node in enumerate(nodes)}                # Assign a unique rank based on degree order
        for u in nodes:                                                 # Iterate over nodes in degree-descending order
            # 3. Iterate over neighbors 'v'
            for v in graph.neighbors(u):
                # ONLY traverse edge if u is "higher rank" (earlier in sorted list) than v
                # This replaces your 'visited_neighbors' logic with O(1) integer comparison
                if rank[u] < rank[v]:                                   # Guarantees each undirected edge {u,v} is processed once
                    
                    # 4. INTERSECTION (The Speedup)
                    # Instead of checking every pair (v, w), we just find the overlap.
                    # We cast to set for O(1) lookups or O(min(deg(u), deg(v))) intersection
                    common_neighbors = adj_sets[u] & adj_sets[v]
                    
                    for w in common_neighbors:                          # Each w connected to both u and v forms a triangle
                        # Ensure strict order u < v < w to avoid duplicates
                        if rank[v] < rank[w]:                           # Maintains canonical ordering → no duplicate triangles
                            triangles.append(frozenset({u, v, w}))
                            # Early return if we only need the first triangle
                            if first_triangle:
                                return triangles                          # Return immediately with the first found triangle
        
        
    # ------------------------- DENSE GRAPH PATH (density >= 0.1) -------------------------
    else:
        # Keep track of visited directed edges to avoid checking (u,v) and (v,u) twice
        visited_neighbors = {node: set() for node in graph.nodes()}     # Adjacency tracking for directed traversal
        for u in nodes:                                                 # Again, process high-degree nodes first
            # Collect all neighbors of u that haven't been processed from u's perspective
            neighbor_list = []                                          # Temporary list of "new" neighbors for this u
            for v in graph.neighbors(u):
                if v not in visited_neighbors[u]:                       # First time seeing directed edge (u→v)
                    visited_neighbors[u].add(v)
                    visited_neighbors[v].add(u)                         # Mark the reverse direction as visited too
                    neighbor_list.append(v)
            
            # Classic triangle enumeration: check every pair of neighbors of u
            for i in range(len(neighbor_list)):
                v = neighbor_list[i]
                for j in range(i + 1, len(neighbor_list)):
                    w = neighbor_list[j]
                    
                    # If v and w are connected, then {u, v, w} forms a triangle
                    if graph.has_edge(v, w):                            # Edge between the two neighbors → triangle found
                        triangles.append(frozenset({u, v, w}))    
                        # Early return if we only need the first triangle
                        if first_triangle:
                            return triangles                            # Stop as soon as one triangle is found
        
    # Return all found triangles, or None if none exist
    return triangles if triangles else None

def find_triangle_coordinates_brute_force(adjacency_matrix):
    """
    Finds the coordinates of all triangles in a given SciPy sparse matrix.

    Args:
        adjacency_matrix: A SciPy sparse matrix (e.g., csr_matrix).
    
    Returns:
        A list of sets, where each set represents the coordinates of a triangle.
        A triangle is defined by three non-negative entries forming a closed loop.
    """

    if not sparse.isspmatrix(adjacency_matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")
    
    rows, cols = adjacency_matrix.shape
    if rows != cols:
        raise ValueError("Input matrix must be square.")
    
    n = adjacency_matrix.shape[0]
    triangles = set()
    for i in range(n-2):
        for j in range(i + 1, n-1):
            if adjacency_matrix[i, j]:  # Check if edge (i, j) exists
                for k in range(j + 1, n):
                    if adjacency_matrix[i, k] and adjacency_matrix[j, k]:  # Check if edges (i, k) and (j, k) exist
                         triangles.add(frozenset({i, j, k}))
    
    return list(triangles) if triangles else None

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