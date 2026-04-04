# Created on 04/04/2026
# Author: Frank Vega

import time
import argparse
import math
import networkx as nx

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
    helper = argparse.ArgumentParser(prog="test_clique", description="The Aegypti Testing Application using randomly generated, large sparse matrices.")
    helper.add_argument('-d', '--dimension', type=int, help="an integer specifying the dimensions of the square matrices", required=True)
    helper.add_argument('-n', '--num_tests', type=int, default=5, help="an integer specifying the number of tests to run")
    helper.add_argument('-s', '--sparsity', type=restricted_float, default=0.95, help="sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)")
    helper.add_argument('-a', '--approximation', action='store_true', help='enable comparison with a polynomial-time approximation approach within a polynomial factor')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with the exponential-time brute-force approach')
    helper.add_argument('-c', '--count', action='store_true', help='calculate the size of the clique')
    helper.add_argument('-w', '--write', action='store_true', help='write the generated random matrix to a file in the current directory')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.3.8')
    
    # Initialize the parameters
    args = helper.parse_args()
    num_tests = args.num_tests
    matrix_shape = (args.dimension, args.dimension)
    sparsity = args.sparsity
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    hash_string = utils.generate_short_hash(6 + math.ceil(math.log2(num_tests))) if args.write else None
    count = args.count
    bruteForce = args.bruteForce
    approximation = args.approximation
    # Perform the tests    
    for i in range(num_tests):
        
        logger.info(f"Creating Matrix {i + 1}")
        
        sparse_matrix = utils.random_matrix_tests(matrix_shape, sparsity)

        if sparse_matrix is None:
            continue

        graph = utils.sparse_matrix_to_graph(sparse_matrix)    
        logger.info(f"Matrix shape: {sparse_matrix.shape}")
        logger.info(f"Number of non-zero elements: {sparse_matrix.nnz}")
        logger.info(f"Sparsity: {1 - (sparse_matrix.nnz / (sparse_matrix.shape[0] * sparse_matrix.shape[1]))}")
        
        if approximation:
            logger.info("An approximate Solution with a polynomial-approximation ratio started")
            started = time.time()
            
            approximate_result = algorithm.find_clique_approximation(graph)

            logger.info(f"An approximate Solution with a polynomial-approximation ratio done in: {(time.time() - started) * 1000.0} milliseconds")
            
            answer = utils.string_result_format(approximate_result, count)
            output = f"{i + 1}-approximation Test: {answer}" 
            utils.println(output, logger, args.log)    
    
        if bruteForce:
            logger.info("A solution with an exponential-time complexity started")
            started = time.time()
            
            brute_force_result = algorithm.find_clique_brute_force(graph)

            logger.info(f"A solution with an exponential-time complexity done in: {(time.time() - started) * 1000.0} milliseconds")
            
            answer = utils.string_result_format(brute_force_result, count)
            output = f"{i + 1}-Brute Force Test: {answer}" 
            utils.println(output, logger, args.log)
        

        logger.info("Our Algorithm with an approximate solution started")
        started = time.time()
        
        novel_result = algorithm.find_clique(graph)

        logger.info(f"Our Algorithm with an approximate solution done in: {(time.time() - started) * 1000.0} milliseconds")

        answer = utils.string_result_format(novel_result, count)
        output = f"{i + 1}-Aegypti Test: {answer}" 
        utils.println(output, logger, args.log)

        if novel_result and (bruteForce or approximation):
            if bruteForce:    
                output = f"Exact Ratio (Aegypti/Optimal): {len(brute_force_result)/len(novel_result)}"
            elif approximation:
                log = math.log(graph.number_of_nodes())
                output = f"Upper Bound for Ratio (Aegypti/Optimal): {(graph.number_of_nodes()/(log*log)) * len(approximate_result)/len(novel_result)}"
            utils.println(output, logger, args.log)
        

        if args.write:
            output = f"Saving Matrix Test {i + 1}" 
            utils.println(output, logger, args.log)
    
            filename = f"sparse_matrix_{i + 1}_{hash_string}"
            parser.save_sparse_matrix_to_file(sparse_matrix, filename)
            output = f"Matrix Test {i + 1} written to file {filename}." 
            utils.println(output, logger, args.log)
    
if __name__ == "__main__":
  main()      