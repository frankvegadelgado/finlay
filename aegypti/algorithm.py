# Modified on 01/14/2025
# Author: Frank Vega


import numpy as np
from scipy import sparse
import networkx as nx

def find_triangle_coordinates(graph, first_triangle=True):
    """
    Finds the coordinates of all triangles in a given undirected NetworkX graph.

    Args:
        graph: An undirected NetworkX graph.
        first_triangle: A boolean indicating whether to return only the first found triangle.

    Returns:
        A list of sets, where each set represents the coordinates of a triangle.
        A triangle is defined by three non-negative integer entries forming a closed loop.
        Returns None if no triangles are found.
    """
    # Validate input graph
    if not isinstance(graph, nx.Graph):
        raise ValueError("Input must be an undirected NetworkX Graph.")
    # Initialize data structures
    visited = {}  # Tracks visited nodes
    triangles = set()  # Stores unique triangles as frozensets
    # Iterate over all nodes
    for i in graph.nodes():
        if i not in visited:
            stack = [(i, i)]  # (current_node, parent_node)

            # Perform DFS to find triangles
            while stack:
                current_node, parent = stack.pop()
                visited[current_node] = True

                # Check for triangles
                for neighbor in graph.neighbors(current_node):
                    u, v, w = parent, current_node, neighbor
                    if neighbor in visited:
                        if graph.has_edge(parent, neighbor):
                            nodes = frozenset({u, v, w})
                            # Check whether it is a triangle or not
                            if len(nodes) == 3:
                                triangles.add(nodes)
                                if first_triangle:
                                    return list(triangles)

                    # Add unvisited neighbors to the stack
                    if neighbor not in visited:
                        stack.append((neighbor, current_node))

    return list(triangles) if triangles else None

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