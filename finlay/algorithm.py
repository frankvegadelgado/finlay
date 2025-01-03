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
               and values are lists of their neighbors.

    Returns:
      True if the graph is triangle-free, False otherwise.
    """
    colors = {}

    def dfs(node, color):
        """
        Recursive DFS helper function.

        Args:
            node: The current node being visited.
            color: The color to assign to the current node.
        """
        colors[node] = color

        for neighbor in graph[node]:
            if neighbor not in colors:
                triangle = dfs(neighbor, color + 1)
                if triangle:
                    return triangle
            elif (color - colors[neighbor]) == 2:
                common = (graph[node] & graph[neighbor]) - {node, neighbor}
                return (node, neighbor, next(iter(common)))

        return None

    # Start DFS traversal from each unvisited node
    for node in graph:
        if node not in colors:
            triangle = dfs(node, 1)
            if triangle:
                return triangle

    return None

def create_graph(adjacency_matrix):
  """
  Creates an adjacency list representation of a graph from its adjacency matrix (numpy array).

  Args:
    adjacency_matrix: A NumPy 2D array representing the adjacency matrix.

  Returns:
    An adjacency list that represents the graph as a dictionary, where keys are 
    vertex indices and values are lists of adjacent vertices.
  """

  n = adjacency_matrix.shape[0]  # Get the number of vertices from the matrix shape

  graph = {}
  for i in range(n):
    graph[i] = set(np.where(adjacency_matrix[i] == 1)[0].tolist()) 

  return graph

def string_format(triangle):
  """
  Returns a string indicating whether a graph is triangle-free.

  Args:
    triangle: An object value, None if the graph is triangle-free, triangle vertices otherwise.

  Returns:
    "Triangle Free" if triangle is None, "Triangle Found (a, b, c)" otherwise.
  """
  return "Triangle Free" if (triangle is None or triangle == True) else (f"Triangle Found {triangle}" if (triangle != False) else "Triangle Found")