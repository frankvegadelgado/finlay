# Created on 01/08/2025
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
      return f"Triangle Found {triangle}"
  else:
     return "Triangle Free"