# Created on 01/06/2025
# Author: Frank Vega

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
        neighbors = current_row.nonzero()[1].tolist()

        for neighbor in neighbors:

          if neighbor not in colors:

            stack.append((neighbor, current_color + 1))

          elif (current_color - colors[neighbor]) == 2:
            
            neighbor_row = adjacency_matrix.getrow(neighbor)
            adjacents = neighbor_row.nonzero()[1].tolist()
            common = set(neighbors + adjacents) - {current_node, neighbor}
            
            return (current_node, neighbor, next(iter(common)))

  return None

def find_all_triangles(adjacency_matrix):
  """
  Find all triangles in a graph represented by an adjacency matrix.

  A graph triangle is a set of three vertices that are all 
  adjacent to each other (i.e., a complete subgraph of size 3).

  Args:
      adjacency_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.

  Returns:
      None if the graph is triangle-free, triangle vertices otherwise.
      In the case of multiple triangles, returns a list of triangle vertices.
      Vertices are represented as a 2-tuple containing only two vertices of the triangle.
      Each vertex pair in the list represents a triangle, possibly with repetitions.
      The remaining vertex can be inferred from the adjacency matrix.
  """
  
  if not sparse.issparse(adjacency_matrix):
      raise TypeError("Input must be a SciPy sparse matrix.")
  
  n = adjacency_matrix.shape[0]
  if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
      raise ValueError("Adjacency matrix must be square.")

  colors = {}
  stack = []
  triangles = []

  for i in range(n):
    if i not in colors:
      stack.append((i, 1))

      while stack:
        current_node, current_color = stack.pop()
        colors[current_node] = current_color
        current_row = adjacency_matrix.getrow(current_node)
        neighbors = current_row.nonzero()[1].tolist()

        for neighbor in neighbors:

          if neighbor not in colors:

            stack.append((neighbor, current_color + 1))

          elif (current_color - colors[neighbor]) == 2:
            
            triangles.append((min(current_node, neighbor), max(current_node, neighbor)))
  
  return triangles if triangles else None

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


def string_all_results_format(triangles):
  """
  Returns a string indicating all the triangles found in a graph.

  Args:
    triangles: A list value, None if the graph is triangle-free, a list of triangle vertices otherwise.
    Vertices are represented as a 2-tuple containing only two vertices of the triangle.
    Each vertex pair in the list represents a triangle, possibly with repetitions.
    The remaining vertex can be inferred from the adjacency matrix.
  
  Returns:
    "Triangle Free" if triangle is None, "Triangles Found (a, b), (c, d), ...." otherwise.
  """
  return "Triangle Free" if triangles is None else f"Triangles Found {', '.join(map(str, triangles))}"