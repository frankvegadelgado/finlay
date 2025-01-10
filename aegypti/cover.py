# Created on 01/10/2025
# Author: Frank Vega

from . import utils

import scipy.sparse as sparse
from itertools import combinations
import networkx as nx
from networkx.algorithms import bipartite

def is_independent_edge_triangle_cover_free(adjacency_matrix):
  """
  Checks if a graph represented by a sparse adjacency matrix contains an independent edge triangle cover. Polynomial time complexity.
  
  A graph triangle is a set of three vertices that are all 
  adjacent to each other (i.e., a complete subgraph of size 3).

  Args:
      adjacency_matrix: A SciPy sparse matrix (e.g., csc_matrix) representing the adjacency matrix.
  Returns:
      True if no independent edge triangle cover exists, False otherwise.
  """
  
  if not sparse.issparse(adjacency_matrix):
      raise TypeError("Input must be a SciPy sparse matrix.")
  
  n = adjacency_matrix.shape[0]
  if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
      raise ValueError("Adjacency matrix must be square.")

    
  colors = {}
  stack = []
  universe = set()
  cover = {}
  for i in range(n):
    if i not in colors:
      stack = [(i, i)]
      
      while stack:
        current_node, parent = stack.pop()
        current_color = n * parent + current_node
        colors[current_node] = current_color
        current_row = adjacency_matrix.getrow(current_node)
        neighbors = current_row.nonzero()[1]
        for neighbor in neighbors:
          
          if neighbor in colors and adjacency_matrix[current_color // n, colors[neighbor] % n]:           
            u, v, w = (current_color // n), (current_color % n), (colors[neighbor] % n)
            minimum = min(u, v, w)
            maximum = max(u, v, w)
            betweenness = next(iter(set([u, v, w]) - {minimum, maximum}))
            triangle = frozenset({minimum, betweenness, maximum})
            universe.add(triangle)
            cover.setdefault(minimum, set()).add(triangle)
            cover.setdefault(maximum, set()).add(triangle)

        stack.extend([(node, current_node) for node in neighbors if node not in colors])

  return solve(universe, cover) if cover else True

def is_independent_edge_triangle_cover_free_brute_force(adj_matrix):
    """
    Checks if a graph represented by a sparse adjacency matrix contains an independent edge triangle cover. Exponential time complexity.
  
    Args:
        adj_matrix: A SciPy sparse CSR matrix representing the adjacency matrix of the graph.

    Returns:
        True if no independent edge triangle cover exists, False otherwise.
    """

    n = adj_matrix.shape[0]

    triangles = []
    for i in range(n):
      for j in range(i + 1, n):
        if adj_matrix[i, j] != 0:  # Check if edge (i, j) exists
          for k in range(j + 1, n):
            if adj_matrix[i, k] != 0 and adj_matrix[j, k] != 0:
              triangles.append(frozenset({i, j, k}))

    if not triangles:
        return 0

    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if adj_matrix[i, j] != 0:
                edges.append(frozenset({i, j}))

    
    for i in range(1, min(len(edges)+1,len(triangles)+1)): # optimization to avoid unnecessary computation
        for cover_candidate_edges in combinations(edges, i):
            cover_candidate_edges = set(cover_candidate_edges)
            covered_triangles = set()
            independent = True
            for triangle in triangles:
              for edge in cover_candidate_edges:
                if edge.issubset(triangle):
                  if triangle in covered_triangles:
                     independent = False
                     break
                  covered_triangles.add(triangle)
              if not independent:
                 break
            if independent and len(covered_triangles) == len(triangles): 
              return False
      
    return True

def fill_graph(universe, cover):
  """
  Fill the graph for the disjoint set cover of the universe. 
  
  Args:
    universe: A set of elements where each element appears exactly twice in subsets
    cover: A dictionary with a list of subsets of the universe.

  Returns:
      - An undirected graph.
  """

  graph = nx.Graph()
  map_element = {elem: i for i, elem in enumerate(universe)}
  new_element = len(universe)
  for key1, subset1 in cover.items():
    for key2, subset2 in cover.items():
      if key1 < key2 and subset1.intersection(subset2):
          for elem in subset1:
            graph.add_edge(new_element, map_element[elem])
          for elem in subset2:
            graph.add_edge(new_element + 1, map_element[elem])
          graph.add_edge(new_element, new_element + 1)
          new_element += 2
  
  return graph, len(universe) + (new_element - len(universe)) // 2

def coloring(graph):
    """
    Determines the bipartite partitions of a graph.
    
    Args:
        graph: The input graph.

    Returns:
        A list of tuples, where each tuple contains two sets representing the bipartite partitions of a connected component.
        Returns None if the graph is not bipartite.
        
    Raises:
        ValueError: If the graph is directed.    
    """

    if nx.is_directed(graph):
        raise ValueError("Invalid input: graph must be undirected.")
    
    if not bipartite.is_bipartite(graph):
        return None

    bipartite_components = nx.connected_components(graph)
    partitions = [(set(), set())]

    for component in bipartite_components:
        G = nx.induced_subgraph(graph, component)
        color_map = bipartite.color(G)
        set1, set0 = utils.create_sets_from_dict(color_map)
        partitions.append((set1, set0))

    return partitions  

def subset_sum(partitions, p, k):
    """
    Checks if there's a subset of the given partitions that sums up to a specific value.

    Args:
        partitions: A list of tuples, where each tuple contains two integers representing the sizes of two subsets.
        p: The total number of partitions.
        k: The target sum.

    Returns:
        - True if a subset sum exists, False otherwise.
    """

    dp_table = {}
    for i in range(p + 1):
        for j in range(k + 1):
            dp_table[(i, j)] = False
    
    dp_table[(0, 0)] = True

    for i in range(1, p + 1):
        for j in range(k + 1):
            dp_table[(i, j)] = (utils.evaluate(dp_table, i - 1, j - len(partitions[i][0]), p, k) 
            or utils.evaluate(dp_table, i - 1, j - len(partitions[i][1]), p, k))
                
    return dp_table[(p, k)]

def solve(universe, cover):
    """
    Determine whether there exists a disjoint set cover of the universe. 
    
    Args:
      universe: A set of elements where each element appears exactly twice in subsets
      cover: A dictionary with a list of subsets of the universe.

    Returns:
      True if no disjoint set cover exists, False otherwise.
    """
    
    graph, k = fill_graph(universe, cover)
    partitions = coloring(graph)
    
    if partitions is None:
        return True
    
    p = len(partitions) - 1
    return not subset_sum(partitions, p, k)


