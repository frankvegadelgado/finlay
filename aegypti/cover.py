# Created on 01/09/2025
# Author: Frank Vega

import scipy.sparse as sparse
from collections import deque
import itertools
import networkx as nx

def size_triangle_cover(adjacency_matrix):
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
  cover = set()
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
        
          elif current_color == colors[neighbor] and (n * current_node + neighbor) not in cover:
            cover.add(n * current_node + neighbor)
            cover.add(n * neighbor + current_node)
            
  return len(cover) // 2
  
def exact_vertex_cover_brute_force(adj_matrix):
    """
    Calculates the minimum vertex cover using brute-force (exponential time).

    Args:
        adj_matrix: A SciPy sparse adjacency matrix.

    Returns:
        A set of vertex indices representing the minimum vertex cover, or None if the graph is empty.
        Returns the size of the vertex cover as well.
    """

    n_vertices = adj_matrix.shape[0]

    if n_vertices == 0:
        return None, 0 # Handle empty graph

    min_cover = None
    min_cover_size = n_vertices + 1 # Initial value bigger than any possible cover

    for k in range(1, n_vertices + 1): # Iterate through all possible sizes of the cover
        for cover_candidate in itertools.combinations(range(n_vertices), k):
            cover_candidate = set(cover_candidate)
            is_cover = True
            for i in range(n_vertices):
                for j in range(i + 1, n_vertices): # Avoid checking edges twice
                    if adj_matrix[i, j] and i not in cover_candidate and j not in cover_candidate:
                        is_cover = False
                        break # Optimization: If one edge is not covered, no need to check others for this candidate
                if not is_cover:
                    break # Optimization: If one edge is not covered, no need to check other edges for this candidate
            if is_cover:
                min_cover = cover_candidate
                min_cover_size = k
                return min_cover, min_cover_size # Optimization: Once a cover is found for a size, no need to check bigger covers

    return min_cover, min_cover_size

def vertex_cover_approximation(adj_matrix):
    """
    Calculates vertex cover using networkx (suitable for smaller graphs).
    """
    graph = nx.from_scipy_sparse_array(adj_matrix)
    #networkx doesn't have a guaranteed minimum vertex cover function, so we use approximation
    vertex_cover = nx.approximation.vertex_cover.min_weighted_vertex_cover(graph)
    return vertex_cover