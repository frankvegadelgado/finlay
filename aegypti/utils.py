# Modified on 01/14/2025
# Author: Frank Vega

import scipy.sparse as sparse
import numpy as np
import random
import string
import os

def get_file_name(filepath):
    """
    Gets the file name from an absolute path.

    Args:
        filepath: The absolute path to the file.

    Returns:
        The file name, or None if no file is found.
    """

    return os.path.basename(filepath)
    
def get_extension_without_dot(filepath):
    """
    Gets the file extension without the dot from an absolute path.

    Args:
        filepath: The absolute path to the file.

    Returns:
        The file extension without the dot, or None if no extension is found.
    """

    filename = get_file_name(filepath)
    _, ext = os.path.splitext(filename)
    return ext[1:] if ext else None

def has_one_on_diagonal(adjacency_matrix):
    """
    Checks if there is a 1 on the diagonal of a SciPy sparse matrix.

    Args:
      adjacency_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.

    Returns:
        True if there is a 1 on the diagonal, False otherwise.
    """
    diagonal = adjacency_matrix.diagonal()
    return np.any(diagonal == 1)

def is_symmetric(matrix):
    """Checks if a SciPy sparse matrix is symmetric.

    Args:
        matrix: A SciPy sparse matrix.

    Returns:
        bool: True if the matrix is symmetric, False otherwise.
        Raises TypeError: if the input is not a sparse matrix.
    """
    if not sparse.issparse(matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")

    rows, cols = matrix.shape
    if rows != cols:
        return False  # Non-square matrices cannot be symmetric

    # Efficiently check for symmetry
    return (matrix != matrix.T).nnz == 0

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
    row_indices = np.random.randint(0, rows, size=num_elements, dtype=np.int32)
    col_indices = np.random.randint(0, cols, size=num_elements, dtype=np.int32)
    data = np.ones(num_elements, dtype=np.int8)

    sparse_matrix = sparse.csc_matrix((data, (row_indices, col_indices)), shape=(rows, cols))

    # Convert sparse_matrix to a symmetric matrix
    symmetric_matrix = make_symmetric(sparse_matrix)  

    # Set diagonal to 0
    symmetric_matrix.setdiag(0)

    return symmetric_matrix

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
    if count_result:
        return f"Triangles Count {len(result)}"
    else:
        formatted_string = f"{'; '.join(f'({", ".join(f"{x+1}" for x in sorted(fs))})' for fs in result)}"
        return f"Triangle{"s" if len(result) > 1 else ""} Found {formatted_string}"
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

def println(output, logger, file_logging=False):
    """ Log and Print the Final Output Message """
    if (file_logging):
        logger.info(output)
    print(output)

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
    if is_directed:
        for i, j in zip(rows, cols):
            edges.add((i, j))
    else:
        for i, j in zip(rows, cols):
            if i <= j: # Avoid duplicates in undirected graphs
                edges.add((i, j))
    return edges