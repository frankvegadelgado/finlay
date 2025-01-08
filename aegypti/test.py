# Created on 01/08/2024
# Author: Frank Vega

from . import algorithm
from . import applogger
from . import parser

import time
import numpy as np
import argparse
import scipy.sparse as sparse
import random
import string
import math


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

    symmetric_matrix = make_symmetric(sparse_matrix)  

    symmetric_matrix.setdiag(0)

    return symmetric_matrix

def restricted_float(x):
    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < 0.0 or x > 1.0:
        raise argparse.ArgumentTypeError("%r not in range [0.0, 1.0]"%(x,))
    return x

def generate_short_hash(length=6):
    """Generates a short random alphanumeric hash string.

    Args:
        length: The desired length of the hash string (default is 6).

    Returns:
        A random alphanumeric string of the specified length.
        Returns None if length is invalid.
    """

    if not isinstance(length, int) or length <= 0:
        print("Error: Length must be a positive integer.")
        return None

    characters = string.ascii_letters + string.digits  # alphanumeric chars
    return ''.join(random.choice(characters) for i in range(length))

def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="test_triangle", description="The Finlay Testing Application.")
    helper.add_argument('-d', '--dimension', type=int, help="an integer specifying the dimensions of the square matrices", required=True)
    helper.add_argument('-n', '--num_tests', type=int, default=5, help="an integer specifying the number of tests to run")
    helper.add_argument('-s', '--sparsity', type=restricted_float, default=0.95, help="sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)")
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with a brute-force approach using matrix multiplication')
    helper.add_argument('-w', '--write', action='store_true', help='write the generated random matrix to a file in the current directory')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.1.1')

    # Initialize the parameters
    args = helper.parse_args()
    num_tests = args.num_tests
    matrix_shape = (args.dimension, args.dimension)
    sparsity = args.sparsity
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    hash_string = generate_short_hash(6 + math.ceil(math.log2(num_tests))) if args.write else None
    brute_force = args.bruteForce

    # Perform the tests    
    for i in range(num_tests):
        
        logger.info(f"Creating Matrix {i + 1}")
        
        sparse_matrix = random_matrix_tests(matrix_shape, sparsity)

        if sparse_matrix is None:
            continue

        logger.info(f"Matrix shape: {sparse_matrix.shape}")
        logger.info(f"Number of non-zero elements: {sparse_matrix.nnz}")
        logger.info(f"Sparsity: {1 - (sparse_matrix.nnz / (sparse_matrix.shape[0] * sparse_matrix.shape[1]))}")
        
        # A Solution with O(n + m) Time Complexity
        logger.info("A solution with a time complexity of O(n + m) started")
        started = time.time()
        
        result = algorithm.is_triangle_free(sparse_matrix)

        logger.info(f"A solution with a time complexity of O(n + m) done in: {(time.time() - started) * 1000.0} milliseconds")

        answer =  algorithm.string_complex_format(result)
        output = f"Algorithm Smart Test {i + 1}: {answer}" 
        if (args.log):
            logger.info(output)
        print(output)

        # A Solution with at least O(m^(2.372)) Time Complexity
        if brute_force:
            logger.info("A solution with a time complexity of at least O(m^(2.372)) started")
            started = time.time()
            
            result = algorithm.is_triangle_free_brute_force(sparse_matrix)

            logger.info(f"A solution with a time complexity of at least O(m^(2.372)) done in: {(time.time() - started) * 1000.0} milliseconds")
            
            answer = algorithm.string_simple_format(result)
            output = f"Algorithm Naive Test {i + 1}: {answer}" 
            if (args.log):
                logger.info(output)
            print(output)


        if args.write:
            output = f"Saving Matrix Test {i + 1}" 
            if (args.log):
                logger.info(output)
            print(output)

            filename = f"sparse_matrix_{i + 1}_{hash_string}.txt"
            parser.save_sparse_matrix_to_file(sparse_matrix, filename)
            output = f"Matrix Test {i + 1} written to file {filename}." 
            if (args.log):
                logger.info(output)
            print(output)
if __name__ == "__main__":
  main()      