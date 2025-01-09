#                     Triangle-Free Solver
#                          Frank Vega
#                      Juanary 9th, 2024

import argparse
import time

from . import algorithm
from . import parser
from . import applogger
from . import cover
from . import utils


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with a brute-force approach using matrix multiplication')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument(
    '-c', '--coverTriangle', 
    action='store_true', 
    help="""
    Enable counting the size of the approximate minimum edge cover 
    of all triangles. 

    This is related to the Partial Feedback Edge Set problem, 
    which is NP-complete (Yannakakis, 1978, doi:10.1145/800133.804355).
    """)
    helper.add_argument('--version', action='version', version='%(prog)s 0.1.2')
    
    # Initialize the parameters
    args = helper.parse_args()
    filepath = args.inputFile
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger(args.verbose))
    cover_triangle = args.coverTriangle
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
    
    result = cover.size_triangle_cover(sparse_matrix) if (cover_triangle) else algorithm.is_triangle_free(sparse_matrix)

    logger.info(f"A solution with a time complexity of O(n + m) done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # Output the smart solution
    answer = utils.string_complex_format(result)
    output = f"{filename}: {answer}" 
    if (args.log):
        logger.info(output)
    print(output)

    # A Solution with at least O(m^(2.372)) Time Complexity
    if brute_force:
        logger.info("A solution with a time complexity of at least O(m^(2.372)) started")
        started = time.time()
        
        result = algorithm.is_triangle_free_brute_force(sparse_matrix)
        
        logger.info(f"A solution with a time complexity of at least O(m^(2.372)) done in: {(time.time() - started) * 1000.0} milliseconds")
    
        # Output the naive solution
        answer = utils.string_simple_format(result)
        output = f"{filename}: {answer}" 
        if (args.log):
            logger.info(output)
        print(output)

        
if __name__ == "__main__":
    main()