#                       Triangle Solver
#                          Frank Vega
#                      Juanary 14th, 2025

import argparse
import time
import networkx as nx

from . import algorithm
from . import parser
from . import applogger
from . import utils


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Solve the Triangle-Free Problem for an undirected graph encoded in DIMACS format.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-a', '--all', action='store_true', help='identify all triangles')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='compare with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--count', action='store_true', help='count the total amount of triangles')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.2.8')
    
    # Initialize the parameters
    args = helper.parse_args()
    filepath = args.inputFile
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    count_triangles = args.count
    all_triangles = args.all
    brute_force = args.bruteForce

    # Read and parse a dimacs file
    logger.info(f"Parsing the Input File started")
    started = time.time()
    
    sparse_matrix = parser.read(filepath)
    # Convert the sparse matrix to a NetworkX graph
    graph = nx.from_scipy_sparse_array(sparse_matrix)
    filename = utils.get_file_name(filepath)
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # A solution with a time complexity of O(n + m)
    logger.info("A solution with a time complexity of O(n + m) started")
    started = time.time()
    
    result = algorithm.find_triangle_coordinates(graph, not (count_triangles or all_triangles))

    logger.info(f"A solution with a time complexity of O(n + m) done in: {(time.time() - started) * 1000.0} milliseconds")

    # Output the smart solution
    answer = utils.string_complex_format(result, count_triangles)
    output = f"{filename}: {answer}" 
    utils.println(output, logger, args.log)

    # A Solution with brute force
    if brute_force:
        if count_triangles or all_triangles:
            logger.info("A solution with a time complexity of at least O(n^(3)) started")
        else:    
            logger.info("A solution with a time complexity of at least O(m^(1.407)) started")
        started = time.time()
        
        result = algorithm.find_triangle_coordinates_brute_force(sparse_matrix) if count_triangles or all_triangles else algorithm.is_triangle_free_brute_force(sparse_matrix)

        if count_triangles or all_triangles:
            logger.info(f"A solution with a time complexity of at least O(n^(3)) done in: {(time.time() - started) * 1000.0} milliseconds")
        else:
            logger.info(f"A solution with a time complexity of at least O(m^(1.407)) done in: {(time.time() - started) * 1000.0} milliseconds")
        
        answer = utils.string_complex_format(result, count_triangles) if count_triangles or all_triangles else utils.string_simple_format(result)
        output = f"{filename}: {answer}"
        utils.println(output, logger, args.log)
        

        
if __name__ == "__main__":
    main()