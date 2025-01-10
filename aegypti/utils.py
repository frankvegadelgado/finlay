# Created on 01/10/2025
# Author: Frank Vega

import scipy.sparse as sparse
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
    row_indices = np.random.randint(0, rows, size=num_elements, dtype=np.int64)
    col_indices = np.random.randint(0, cols, size=num_elements, dtype=np.int64)
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

def string_simple_format(is_free):
  """
  Returns a string indicating whether a graph is triangle-free.

  Args:
    is_free: A Boolean value, True if the graph is triangle-free, False otherwise.
  Returns:
    - "Triangle Free" if triangle is True, "Triangle Found" otherwise.
  """
  return "Triangle Free" if is_free  else "Triangle Found"

def string_complex_format(result, count_result=False):
  """
  Returns a string indicating whether the graph is triangle-free.
  
  Args:
    result: None if the graph is triangle-free, the triangle vertices otherwise.
    count_result: Count the number of triangles found (default is False).

  Returns:
    - "Triangle Free" if triangle is None, "Triangle{s} Found {a, b, c}, ...." otherwise.
  """
  if result:
      if isinstance(result, list):
        if count_result:
           return f"Triangles Count {len(result)}"
        else:
            formatted_string = f"{' ; '.join(f'({", ".join(f"'{x}'" for x in sorted(fs))})' for fs in result)}"
            return f"Triangles Found {formatted_string}"
      formatted_string = f'({", ".join(f"'{x}'" for x in sorted(result))})'
      return f"Triangle Found {formatted_string}"
  else:
     return "Triangle Free"

def iterative_dfs(graph, start):
  """
  Performs Depth-First Search (DFS) iteratively on a graph.

  Args:
      graph: A dictionary representing the graph where keys are nodes
             and values are lists of their neighbors.
      start: The starting node for the DFS traversal.

  Returns:
      A list containing the nodes visited in DFS order.
      Returns an empty list if the graph or start node is invalid.
  """

  if not graph or start not in graph:
    return []

  visited = set()  # Keep track of visited nodes
  stack = [start]  # Use a stack for iterative DFS
  traversal_order = []

  while stack:
    node = stack.pop()

    if node not in visited:
      visited.add(node)
      traversal_order.append(node)

      # Important: Reverse the order of neighbors before adding to the stack
      # This ensures that the left-most neighbors are explored first,
      # mimicking the recursive DFS behavior.
      neighbors = list(graph[node]) #Create a copy to avoid modifying the original graph
      neighbors.reverse()
      stack.extend(neighbors)

  return traversal_order