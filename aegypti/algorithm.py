# Created on 01/07/2025
# Author: Frank Vega

import numpy as np
import scipy.sparse as sparse


def is_triangle_free(adjacency_matrix):
  """
  Checks if a graph represented by an adjacency matrix is triangle-free.

  A graph is triangle-free if it contains no set of three vertices that are all 
  adjacent to each other (i.e., no complete subgraph of size 3).

  Args:
      adjacency_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.

  Returns:
      None if the graph is triangle-free, triangle vertices otherwise.
  """
  
  if not sparse.issparse(adjacency_matrix):
      raise TypeError("Input must be a SciPy sparse matrix.")
  
  n = adjacency_matrix.shape[0]
  if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
      raise ValueError("Adjacency matrix must be square.")

  colors = {}
  stack = []

  for i in range(n):
    if i not in colors:
      stack.append((i, 1))

      while stack:
        current_node, current_color = stack.pop()
        colors[current_node] = current_color
        current_row = adjacency_matrix.getrow(current_node)
        neighbors = current_row.nonzero()[1]
        for neighbor in neighbors:
          
          if neighbor not in colors:

            stack.append((neighbor, current_color + 1))
        
          elif current_color == colors[neighbor]:
            
            neighbor_row = adjacency_matrix.getrow(neighbor)
            adjacents = neighbor_row.nonzero()[1].tolist()
            common = set(neighbors.tolist() + adjacents) - {current_node, neighbor}
            
            return (str(current_node), str(neighbor), str(next(iter(common))))
          
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

def string_simple_format(is_free):
  """
  Returns a string indicating whether a graph is triangle-free.

  Args:
    is_free: An Boolean value, True if the graph is triangle-free, False otherwise.

  Returns:
    "Triangle Free" if triangle is True, "Triangle Found" otherwise.
  """
  return "Triangle Free" if is_free  else "Triangle Found"


def string_result_format(triangle):
  """
  Returns a string indicating whether a graph is triangle-free.

  Args:
    triangle: An object value, None if the graph is triangle-free, triangle vertices otherwise.

  Returns:
    "Triangle Free" if triangle is None, "Triangle Found (a, b, c)" otherwise.
  """
  return "Triangle Free" if triangle is None else f"Triangle Found {triangle}"