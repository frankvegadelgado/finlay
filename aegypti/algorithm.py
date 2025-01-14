# Modified on 01/14/2025
# Author: Frank Vega

import numpy as np
import scipy.sparse as sparse

def find_triangle_coordinates(adjacency_matrix, first_triangle=True):
  """
    Finds the coordinates of all triangles in a given SciPy sparse matrix.

    Args:
        adjacency_matrix: A SciPy sparse matrix (e.g., csr_matrix).
        first_triangle: A boolean indicating whether to return only the first found triangle.

    Returns:
        A list of sets, where each set represents the coordinates of a triangle.
        A triangle is defined by three non-negative entries forming a closed loop.
        Returns None if no triangles are found.
        Raises ValueError if the input matrix is not square.
        Raises TypeError if the input is not a sparse matrix.
  """
  
  if not sparse.issparse(adjacency_matrix):
      raise TypeError("Input must be a SciPy sparse matrix.")
  
  n = np.int64(adjacency_matrix.shape[0])
  if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
      raise ValueError("Adjacency matrix must be square.")
    
  colors = {}
  stack = []
  triangles = set()
  for i in range(n):
    if i not in colors:
      stack = [(np.int64(i), np.int64(i))]
      
      while stack:
        current_node, parent = stack.pop()
        current_color = n * parent + current_node
        colors[current_node] = current_color
        current_row = adjacency_matrix.getrow(current_node)
        neighbors = current_row.nonzero()[1]
        for neighbor in neighbors:
          
          if neighbor in colors and adjacency_matrix[current_color // n, colors[neighbor] % n]:           
            u, v, w = (current_color // n), (current_color % n), (colors[neighbor] % n)
            triangles.add(frozenset({u, v, w}))
            if first_triangle:
              return list(triangles)

        stack.extend([(node, current_node) for node in neighbors if node not in colors])
            
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