# Modified on 04/04/2026
# Author: Frank Vega

import time
import argparse
import math

from . import algorithm
from . import applogger
from . import parser
from . import utils

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
    helper = argparse.ArgumentParser(prog="test_triangle", description="The Finlay Testing Application using randomly generated, large sparse matrices.")
    helper.add_argument('-d', '--dimension', type=int, help="an integer specifying the dimensions of the square matrices", required=True)
    helper.add_argument('-n', '--num_tests', type=int, default=5, help="an integer specifying the number of tests to run")
    helper.add_argument('-s', '--sparsity', type=restricted_float, default=0.95, help="sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)")
    helper.add_argument('-b', '--bruteForce', action='store_true', help='compare with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--combinatorial', action='store_true', help='compare with the classical Chiba-Nishizeki O(m^{3/2}) adjacency-intersection baseline')
    helper.add_argument('-w', '--write', action='store_true', help='write the generated random matrix to a file in the current directory')
    helper.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.4.1')

    # Initialize the parameters
    args = helper.parse_args()
    num_tests = args.num_tests
    matrix_shape = (args.dimension, args.dimension)
    sparsity = args.sparsity
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    hash_string = utils.generate_short_hash(6 + math.ceil(math.log2(num_tests))) if args.write else None
    brute_force = args.bruteForce
    combinatorial = args.combinatorial
    write = args.write
    # Perform the tests    
    for i in range(num_tests):
        
        logger.info(f"Creating Matrix {i + 1}")
        
        sparse_matrix = utils.random_matrix_tests(matrix_shape, sparsity)

        if sparse_matrix is None:
            continue
        # Convert the sparse matrix to a NetworkX graph
        graph = utils.sparse_matrix_to_graph(sparse_matrix)    
        logger.info(f"Matrix shape: {sparse_matrix.shape}")
        logger.info(f"Number of non-zero elements: {sparse_matrix.nnz}")
        logger.info(f"Sparsity: {1 - (sparse_matrix.nnz / (sparse_matrix.shape[0] * sparse_matrix.shape[1]))}")
        
        # A Solution with a fast running-time complexity
        # A solution with a fast running-time complexity
        logger.info("A solution with a fast running-time complexity started")
        started = time.time()
        
        result = algorithm.find_triangle_coordinates(graph)

        logger.info(f"A solution with a fast running-time complexity done in: {(time.time() - started) * 1000.0} milliseconds")

        answer = utils.string_complex_format(result)
        output = f"Smart Algorithm for Test {i + 1}: {answer}" 
        utils.println(output, logger, args.log)

        # A Solution with the classical Chiba-Nishizeki combinatorial baseline
        if combinatorial:
            logger.info("Chiba-Nishizeki combinatorial baseline started")
            started_cn = time.time()

            cn_result = algorithm.find_triangle_chiba_nishizeki(graph)

            logger.info(f"Chiba-Nishizeki combinatorial baseline done in: {(time.time() - started_cn) * 1000.0} milliseconds")

            answer = utils.string_complex_format(cn_result)
            output = f"Chiba-Nishizeki Algorithm for Test {i + 1}: {answer}"
            utils.println(output, logger, args.log)

        # A Solution with brute force (matrix multiplication)
        if brute_force:
            logger.info("Matrix-Multiplication baseline started")
            started = time.time()

            brute_force_result = algorithm.is_triangle_free_brute_force(sparse_matrix)

            logger.info(f"Matrix-Multiplication baseline done in: {(time.time() - started) * 1000.0} milliseconds")

            answer = utils.string_simple_format(brute_force_result)
            output = f"Matrix-Multiplication Algorithm for Test {i + 1}: {answer}"
            utils.println(output, logger, args.log)
        
        if write:
            output = f"Saving Matrix Test {i + 1}" 
            utils.println(output, logger, args.log)

            filename = f"sparse_matrix_{i + 1}_{hash_string}"
            parser.save_sparse_matrix_to_file(sparse_matrix, filename)
            output = f"Matrix Test {i + 1} written to file {filename}." 
            utils.println(output, logger, args.log)
if __name__ == "__main__":
  main()      