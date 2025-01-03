# Created on 01/03/2024
# Author: Frank Vega

from . import parser
from . import algorithm

import numpy as np
import random

import numpy as np
import random

def generate_bipartite_graph(k):
  """
  Generates a random bipartite graph with at least k vertices on each side.

  Args:
    k: Minimum number of vertices on each side of the bipartition.

  Returns:
    A NumPy array representing the adjacency matrix of the bipartite graph.
  """
  matrix = np.zeros((2 * k, 2 * k), dtype=int)  # Initialize matrix with zeros

  for _ in range(2 * k):
    i = random.randint(0, k-1)
    j = random.randint(k, 2*k-1)
    matrix[i, j] = 1
    matrix[j, i] = 1

  return matrix

def generate_random_matrix(k):
  """
  Generates a random adjacency matrix as a NumPy array.

  Args:
    k: Upper bound of vertices.

  Returns:
    A NumPy array representing the adjacency matrix.
  """
  matrix = np.zeros((2 * k, 2 * k), dtype=int)  # Initialize matrix with zeros

  for _ in range(2 * k):
    i = random.randint(0, 2*k-1)
    j = random.randint(0, 2*k-1)
    if i == j:
      continue
    matrix[i, j] = 1
    matrix[j, i] = 1

  return matrix

def is_triangle_free(matrix):
  """
  Checks if a graph represented by an adjacency matrix (numpy array) is triangle-free.

  Args:
    matrix: A 2D NumPy array representing the adjacency matrix.

  Returns:
    True if the graph is triangle-free, False otherwise.
  """

  n = matrix.shape[0]  # Get the number of vertices from the matrix shape

  for i in range(n):
    for j in range(i + 1, n):
      if matrix[i, j] == 1:  # Use NumPy indexing for clarity
        if np.any(matrix[i, j+1:] & matrix[j, j+1:]):  # Check for any common neighbors
          return False
  return True

# Run all algorithm test cases
for i in range(1, 28):
    testMatrix = parser.read('benchmarks/testMatrix' + str(i) + '.txt')
    result = algorithm.string_format(algorithm.is_triangle_free(testMatrix))
    print("Algorithm Test Case " + str(i) + ": " + result)
    print("Algorithm Brute Force Test " + str(i) + ": " + algorithm.string_format(is_triangle_free(testMatrix)))

for i in range(28, 42):
    randomMatrix = generate_bipartite_graph(i)
    result = algorithm.string_format(algorithm.is_triangle_free(randomMatrix))
    print("Algorithm Triangle-Free Test " + str(i) + ": " + result)
    print("Algorithm Brute Force Test " + str(i) + ": " + algorithm.string_format(is_triangle_free(randomMatrix)))

for i in range(42, 56):
    randomMatrix = generate_random_matrix(i)
    result = algorithm.string_format(algorithm.is_triangle_free(randomMatrix))
    print("Algorithm Random Test " + str(i) + ": " + result)
    print("Algorithm Brute Force Test " + str(i) + ": " + algorithm.string_format(is_triangle_free(randomMatrix)))

