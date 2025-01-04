# Created on 01/03/2025
# Author: Frank Vega

import numpy as np

def is_triangle_free(adjacency_matrix):
  """
  Checks if a graph represented by an adjacency matrix is triangle-free.

  A graph is triangle-free if it contains no set of three vertices that are all 
  adjacent to each other (i.e., no complete subgraph of size 3).

  Args:
      adjacency_matrix: A NumPy array representing the adjacency matrix.
                          adjacency_matrix[i][j] is 1 if there's an edge 
                          between vertices i and j, 0 otherwise.

  Returns:
      True if the adjacency_matrix is triangle-free, False otherwise.
  """
  
  return triangle_free(create_graph(adjacency_matrix))


def triangle_free(graph):
  """
  Checks if a graph is Triangle-free using Depth-First Search (DFS).

  Args:
    graph: A dictionary representing the graph, where keys are nodes
          and values are sets of their neighbors.

  Returns:
    None if the graph is triangle-free, triangle vertices otherwise.
  """
  colors = {}
  stack = []

  for node in graph:
    if node not in colors:
      stack.append((node, 1))

      while stack:
        current_node, current_color = stack.pop()
        colors[current_node] = current_color

        for neighbor in graph[current_node]:

          if neighbor not in colors:

            stack.append((neighbor, current_color + 1))

          elif (current_color - colors[neighbor]) == 2:

            common = (graph[current_node] & graph[neighbor]) - {current_node, neighbor}
            return (current_node, neighbor, next(iter(common)))

  return None


def create_graph(adjacency_matrix):
  """
  Creates an adjacency list representation of a graph from its adjacency matrix (numpy array).

  Args:
    adjacency_matrix: A NumPy 2D array representing the adjacency matrix.

  Returns:
    An adjacency list that represents the graph as a dictionary, where keys are 
    vertex indices and values are sets of adjacent vertices.
  """

  n = adjacency_matrix.shape[0]  # Get the number of vertices from the matrix shape

  graph = {}
  for i in range(n):
    graph[i] = set(np.where(adjacency_matrix[i] == 1)[0].tolist()) 

  return graph


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