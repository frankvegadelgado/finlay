# Created on 01/09/2025
# Author: Frank Vega

import scipy.sparse as sparse
import networkx as nx
import numpy as np
import random
import string


def generate_short_hash(length=6):
    """Generates a short random alphanumeric hash string.

    Args:
        length: The desired length of the hash string (default is 6).

    Returns:
        A random alphanumeric string of the specified length.
        Returns None if length is invalid.
    """

    if not isinstance(length, int) or length <= 0:
        print("Error: Length must be a positive integer.")
        return None

    characters = string.ascii_letters + string.digits  # alphanumeric chars
    return ''.join(random.choice(characters) for i in range(length))

def make_symmetric(matrix):
    """Makes an arbitrary sparse matrix symmetric efficiently.

    Args:
        matrix: A SciPy sparse matrix (e.g., csc_matrix, csr_matrix, etc.).

    Returns:
        scipy.sparse.csc_matrix: A symmetric sparse matrix.
    Raises:
        TypeError: if the input is not a sparse matrix.
    """

    if not sparse.issparse(matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")

    rows, cols = matrix.shape
    if rows != cols:
        raise ValueError("Matrix must be square to be made symmetric.")

    # Convert to COO for efficient duplicate handling
    coo = matrix.tocoo()

    # Concatenate row and column indices, and data with their transposes
    row_sym = np.concatenate([coo.row, coo.col])
    col_sym = np.concatenate([coo.col, coo.row])
    data_sym = np.concatenate([coo.data, coo.data])

    # Create the symmetric matrix in CSC format
    symmetric_matrix = sparse.csc_matrix((data_sym, (row_sym, col_sym)), shape=(rows, cols))
    symmetric_matrix.sum_duplicates() #sum the duplicates

    return symmetric_matrix

def random_matrix_tests(matrix_shape, sparsity=0.9):
    """
    Performs random tests on a sparse matrix.

    Args:
        matrix_shape (tuple): Shape of the matrix (rows, columns).
        num_tests (int): Number of random tests to perform.
        sparsity (float): Sparsity of the matrix (0.0 for dense, close to 1.0 for very sparse).

    Returns:
        list: A list containing the results of each test.
        sparse matrix: the sparse matrix that was tested.
    """

    rows, cols = matrix_shape
    size = rows * cols

    # Generate a sparse matrix using random indices and data
    num_elements = int(size * (1 - sparsity))  # Number of non-zero elements
    row_indices = np.random.randint(0, rows, size=num_elements)
    col_indices = np.random.randint(0, cols, size=num_elements)
    data = np.ones(num_elements, dtype=np.int8)

    sparse_matrix = sparse.csc_matrix((data, (row_indices, col_indices)), shape=(rows, cols))

    symmetric_matrix = make_symmetric(sparse_matrix)  

    symmetric_matrix.setdiag(0)

    return symmetric_matrix

def generate_triangles_from_edges(adjacency_matrix, triangles):
    """
    Optimized version: Generate triangles given a list of edge pairs.
    Avoids redundant set creation.

    Args:
        adjacency_matrix: A SciPy sparse adjacency matrix.
        triangles: A list of tuples, where each tuple (u, v) represents an edge.

    Returns:
        All triangles formed using at least on side in the given edges.
        Raises TypeError if inputs are not of the correct type.
        Raises ValueError if the input matrix is not square or vertex indices are out of range.
    """
    if not sparse.isspmatrix(adjacency_matrix):
        raise TypeError("adjacency_matrix must be a SciPy sparse matrix.")
    if not all(isinstance(edge, tuple) and len(edge) == 2 for edge in triangles):
        raise TypeError("Each element in triangles must be a 2-tuple.")

    rows, cols = adjacency_matrix.shape
    if rows != cols:
        raise ValueError("Input matrix must be square.")

    visited = set()
    for current_node, neighbor in triangles:
        if not (0 <= current_node < adjacency_matrix.shape[0] and 0 <= neighbor < adjacency_matrix.shape[0]):
            raise ValueError("Vertex indices in triangles are out of range.")
        current_row_indices = adjacency_matrix.getrow(current_node).indices
        neighbor_row_indices = adjacency_matrix.getrow(neighbor).indices

        i = j = 0
        while i < len(current_row_indices) and j < len(neighbor_row_indices):
            if current_row_indices[i] == neighbor_row_indices[j]:
                minimum = min(current_node, neighbor, current_row_indices[i])
                maximum = max(current_node, neighbor, current_row_indices[i])
                betweenness = set([current_node, neighbor, current_row_indices[i]]) - {minimum, maximum}
                if betweenness:
                  new_triangle = (str(minimum), str(next(iter(betweenness))), str(maximum))
                  if new_triangle not in visited:
                    visited.add(new_triangle)
                i += 1
                j += 1
            elif current_row_indices[i] < neighbor_row_indices[j]:
                i += 1
            else:
                j += 1
    return visited

def edges_to_sparse_matrix(edges, num_vertices=None, is_directed=False):
    """
    Converts a set of edges to a SciPy sparse matrix.

    Args:
        edges: A list or set of tuples/lists representing edges.
        num_vertices: The total number of vertices (optional, inferred if None).
        is_directed: Whether the graph is directed (default: False).

    Returns:
        A SciPy CSR sparse matrix.
    """

    if not edges: #Handle empty edge case
        if num_vertices is None:
            raise ValueError("Number of vertices must be specified if edges are empty")
        return sparse.csr_matrix((num_vertices, num_vertices))

    rows = []
    cols = []
    data = []

    for u, v in edges:
        rows.append(u)
        cols.append(v)
        data.append(1)  # Assuming unweighted graph

        if not is_directed:
            rows.append(v)
            cols.append(u)
            data.append(1)

    if num_vertices is None:
        num_vertices = max(max(row, col) for row, col in zip(rows, cols)) + 1
    
    return sparse.csr_matrix((data, (rows, cols)), shape=(num_vertices, num_vertices))

def sparse_matrix_to_edges(adj_matrix, is_directed=False):
    """
    Converts a SciPy sparse adjacency matrix to a set of edges.

    Args:
        adj_matrix: A SciPy sparse adjacency matrix.
        is_directed: Whether the matrix represents a directed graph (default: False).

    Returns:
        A set of tuples representing the edges.
    """

    edges = set()
    rows, cols = adj_matrix.nonzero()

    for i, j in zip(rows, cols):
        edges.add((i, j))
        if not is_directed:
            edges.add((j, i))

    return edges

def sparse_matrix_to_edges_efficient(adj_matrix, is_directed=False):
    """
    Converts a SciPy sparse adjacency matrix to a set of edges efficiently.

    Args:
        adj_matrix: A SciPy sparse adjacency matrix.
        is_directed: Whether the matrix represents a directed graph (default: False).

    Returns:
        A set of tuples representing the edges.
    """

    edges = set()
    rows, cols = adj_matrix.nonzero()
    if is_directed:
        for i, j in zip(rows, cols):
            edges.add((i, j))
    else:
        for i, j in zip(rows, cols):
            if i <= j: # Avoid duplicates in undirected graphs
                edges.add((i, j))
    return edges

def nx_to_sparse(graph, format='csr'):
    """
    Converts a NetworkX graph to a SciPy sparse adjacency matrix.

    Args:
        graph: The NetworkX graph.
        format: The desired sparse matrix format (e.g., 'csr', 'csc', 'coo', 'lil', 'dok'). Default is 'csr'.

    Returns:
        A SciPy sparse adjacency matrix in the specified format, or None if the graph is empty.
    Raises:
        ValueError: If the specified format is invalid.
    """

    if not graph:
        return None

    adj_matrix = nx.to_scipy_sparse_array(graph, format=format)
    return adj_matrix


def nx_to_sparse_alternative(graph):
    """
    Converts a NetworkX graph to a SciPy sparse adjacency matrix using an alternative method.

    Args:
        graph: The NetworkX graph.

    Returns:
        A SciPy CSR sparse adjacency matrix, or None if the graph is empty.
    """
    if not graph:
        return None
    adj_matrix = nx.adjacency_matrix(graph)
    return adj_matrix

def find_triangle_coordinates_brute_force(adjacency_matrix):
    """
    Finds the coordinates of all triangles in a given SciPy sparse matrix.

    Args:
        adjacency_matrix: A SciPy sparse matrix (e.g., csr_matrix).
    
    Returns:
        A list of tuples, where each tuple represents the coordinates of a triangle.
        A triangle is defined by three non-zero entries forming a closed loop.
    """

    if not sparse.isspmatrix(adjacency_matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")
    
    rows, cols = adjacency_matrix.shape
    if rows != cols:
        raise ValueError("Input matrix must be square.")
    
    n = adjacency_matrix.shape[0]
    visited = set()
    for i in range(n-2):
        for j in range(i + 1, n-1):
            if adjacency_matrix[i, j]:  # Check if edge (i, j) exists
                for k in range(j + 1, n):
                    if adjacency_matrix[i, k] and adjacency_matrix[j, k]:  # Check if edges (i, k) and (j, k) exist
                         visited.add((str(i), str(j), str(k)))
    return visited

def string_simple_format(is_free):
  """
  Returns a string indicating whether a graph is triangle-free.

  Args:
    is_free: An Boolean value, True if the graph is triangle-free, False otherwise.

  Returns:
    "Triangle Free" if triangle is True, "Triangle Found" otherwise.
  """
  return "Triangle Free" if is_free  else "Triangle Found"

def string_complex_format(triangle):
  """
  Returns a string indicating all the triangles found in a graph.

  Args:
    triangle: A tuple value, 
    None if the graph is triangle-free,
    a tuples of triangle vertices otherwise.
  
  Returns:
    "Triangle Free" if triangle is None, "Triangles Found (a, b, c)" otherwise.
  """
  if triangle:
      if isinstance(triangle, int):
        return f"Cover Size {triangle}"
      return f"Triangle Found {triangle}"
  else:
     return "Triangle Free"