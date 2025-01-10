#                       Triangle Solver
#                          Frank Vega
#                      Juanary 10th, 2025

import argparse
import time

from . import algorithm
from . import parser
from . import applogger
from . import cover
from . import utils


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Determine whether an undirected graph, represented by a {0, 1}-adjacency matrix read from a file, is triangle-free or contains an independent edge triangle cover.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--coverBruteForce', action='store_true', help='enable finding an independent edge triangle cover (brute force)')
    helper.add_argument(
    '-f', '--findTriangle', 
    action='store_true', 
    help="""
    Enable finding an independent edge triangle cover (polynomial-time solution). 
    
    This problem is NP-complete (See documentation: https://pypi.org/project/aegypti/).

    This algorithm constitutes a proof that P and NP are equivalent.
    """)
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.1.3')
    
    # Initialize the parameters
    args = helper.parse_args()
    filepath = args.inputFile
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    find_triangle = args.findTriangle
    cover_brute_force = args.coverBruteForce
    brute_force = args.bruteForce

    # Read and parse a dimacs file
    logger.info(f"Parsing the Input File started")
    started = time.time()
    
    sparse_matrix = parser.read(filepath)
    filename = parser.get_file_name(filepath)
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # A solution with a time complexity of O(n + m)
    logger.info("A solution with a time complexity of O(n + m) started")
    started = time.time()
    
    result = cover.is_independent_edge_triangle_cover_free(sparse_matrix) if (find_triangle or cover_brute_force) else algorithm.is_triangle_free(sparse_matrix)

    logger.info(f"A solution with a time complexity of O(n + m) done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # Output the smart solution
    answer = utils.string_simple_format(result, True) if (find_triangle or cover_brute_force) else utils.string_complex_format(result)
    output = f"{filename}: {answer}" 
    if (args.log):
        logger.info(output)
    print(output)

    # A Solution with brute force
    if brute_force or cover_brute_force:
        if cover_brute_force:
            logger.info("A solution with an exponential time complexity started")
        else:    
            logger.info("A solution with a time complexity of at least O(m^(1.407)) started")
        started = time.time()
        
        result = cover.is_independent_edge_triangle_cover_free_brute_force(sparse_matrix) if cover_brute_force else algorithm.is_triangle_free_brute_force(sparse_matrix)

        if cover_brute_force:
            logger.info(f"A solution with an exponential time complexity done in: {(time.time() - started) * 1000.0} milliseconds")
        else:
            logger.info(f"A solution with a time complexity of at least O(m^(1.407)) done in: {(time.time() - started) * 1000.0} milliseconds")
        
        answer = utils.string_simple_format(result, cover_brute_force)
        if (args.log):
            logger.info(output)
        print(output)
        

        
if __name__ == "__main__":
    main()