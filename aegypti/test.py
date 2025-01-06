# Created on 01/06/2024
# Author: Frank Vega

from . import algorithm
from . import applogger

import time
import numpy as np
import argparse
import scipy.sparse as sparse

def make_symmetric(matrix):
    """Makes an arbitrary sparse matrix symmetric efficiently.

    Args:
        matrix: A SciPy sparse matrix (e.g., csc_matrix, csr_matrix, etc.).

    Returns:
        scipy.sparse.csc_matrix: A symmetric sparse matrix.
    Raises:
        TypeError: if the input is not a sparse matrix.
    """

    if not sparse.issparse(matrix):
        raise TypeError("Input must be a SciPy sparse matrix.")

    rows, cols = matrix.shape
    if rows != cols:
        raise ValueError("Matrix must be square to be made symmetric.")

    # Convert to COO for efficient duplicate handling
    coo = matrix.tocoo()

    # Concatenate row and column indices, and data with their transposes
    row_sym = np.concatenate([coo.row, coo.col])
    col_sym = np.concatenate([coo.col, coo.row])
    data_sym = np.concatenate([coo.data, coo.data])

    # Create the symmetric matrix in CSC format
    symmetric_matrix = sparse.csc_matrix((data_sym, (row_sym, col_sym)), shape=(rows, cols))
    symmetric_matrix.sum_duplicates() #sum the duplicates

    return symmetric_matrix

def random_matrix_tests(matrix_shape, sparsity=0.9):
    """
    Performs random tests on a sparse matrix.

    Args:
        matrix_shape (tuple): Shape of the matrix (rows, columns).
        num_tests (int): Number of random tests to perform.
        sparsity (float): Sparsity of the matrix (0.0 for dense, close to 1.0 for very sparse).

    Returns:
        list: A list containing the results of each test.
        sparse matrix: the sparse matrix that was tested.
    """

    rows, cols = matrix_shape
    size = rows * cols

    # Generate a sparse matrix using random indices and data
    num_elements = int(size * (1 - sparsity))  # Number of non-zero elements
    row_indices = np.random.randint(0, rows, size=num_elements)
    col_indices = np.random.randint(0, cols, size=num_elements)
    data = np.ones(num_elements, dtype=np.int8)

    sparse_matrix = sparse.csc_matrix((data, (row_indices, col_indices)), shape=(rows, cols))

    symmetric_matrix = make_symmetric(sparse_matrix) - sparse.diags(sparse_matrix.diagonal())

    return symmetric_matrix

def is_triangle_free(adj_matrix):
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

def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x

def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="test_triangle", description="The Finlay Testing application.")
    helper.add_argument('-d', '--dimension', type=int, help="An integer specifying the square dimensions of random matrix tests.", required=True)
    helper.add_argument('-n', '--num_tests', type=int, default=5, help="An integer specifying the number of random matrix tests.")
    helper.add_argument('-s', '--sparsity', type=restricted_float, default=0.95, help="Sparsity of the matrix (0.0 for dense, close to 1.0 for very sparse).")
    helper.add_argument('-l', '--log', action='store_true', help='Enable file logging')
    
    # Initialize the parameters
    args = helper.parse_args()
    num_tests = args.num_tests
    matrix_shape = (args.dimension, args.dimension)
    sparsity = args.sparsity
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger())
    

    for i in range(num_tests):
      
      print(f"Creating Matrix {i + 1}")
      
      sparse_matrix = random_matrix_tests(matrix_shape, sparsity)

      if sparse_matrix is None:
          continue

      print(f"Matrix shape: {sparse_matrix.shape}")
      print(f"Number of non-zero elements: {sparse_matrix.nnz}")
      print(f"Sparsity: {1 - (sparse_matrix.nnz / (sparse_matrix.shape[0] * sparse_matrix.shape[1]))}")
      
      # A Solution with O(n + m) Time Complexity
      logger.info("A Solution with O(n + m) Time Complexity started")
      started = time.time()
      
      answer = algorithm.string_result_format(algorithm.is_triangle_free(sparse_matrix))
      
      logger.info(f"A Solution with O(n + m) Time Complexity done in: {(time.time() - started) * 1000.0} milliseconds")
      
      print(f"Algorithm Smart Test {i + 1}: {answer}")
      
      # A Solution with O(n + m) Time Complexity
      logger.info("A Solution of at least O(m^(2.372)) Time Complexity started")
      started = time.time()
      
      answer = algorithm.string_simple_format(is_triangle_free(sparse_matrix))
      
      logger.info(f"A Solution with at least O(m^(2.372)) Time Complexity done in: {(time.time() - started) * 1000.0} milliseconds")
      
      print(f"Algorithm Naive Test {i + 1}: {answer}")
        
if __name__ == "__main__":
  main()      