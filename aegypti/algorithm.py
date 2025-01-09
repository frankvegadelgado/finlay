# Created on 01/09/2025
# Author: Frank Vega

import numpy as np
import scipy.sparse as sparse
from collections import deque

def is_triangle_free(adjacency_matrix):
  """
  Checks if a graph represented by a sparse adjacency matrix is triangle-free using matrix multiplication.

  A graph triangle is a set of three vertices that are all 
  adjacent to each other (i.e., a complete subgraph of size 3).

  Args:
      adjacency_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.
  Returns:
      None if the graph is triangle-free, otherwise a triangle vertices.
  """
  
  if not sparse.issparse(adjacency_matrix):
      raise TypeError("Input must be a SciPy sparse matrix.")
  
  n = adjacency_matrix.shape[0]
  if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
      raise ValueError("Adjacency matrix must be square.")

  colors = {}
  queue = deque()
  for i in range(n):
    if i not in colors:
      queue.append((i, 1))
      colors[i] = 1

      while queue:
        current_node, current_color = queue.popleft()
        current_row = adjacency_matrix.getrow(current_node)
        neighbors = current_row.nonzero()[1]
        for neighbor in neighbors:
          
          if neighbor not in colors:

            queue.append((neighbor, current_color + 1))
            colors[neighbor] = current_color + 1
        
          elif current_color == colors[neighbor]:           
            current_row_indices = adjacency_matrix.getrow(current_node).indices
            neighbor_row_indices = adjacency_matrix.getrow(neighbor).indices

            i = j = 0
            while i < len(current_row_indices) and j < len(neighbor_row_indices):
                if current_row_indices[i] == neighbor_row_indices[j]: 
                    if (current_row_indices[i] != current_node and 
                        current_row_indices[i] != neighbor):
                        return (str(current_node), str(neighbor), str(current_row_indices[i]))
                    else:
                        i += 1
                        j += 1
                elif current_row_indices[i] < neighbor_row_indices[j]:
                    i += 1
                else:
                    j += 1

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
