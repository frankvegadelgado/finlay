#                     Triangle-Free Solver
#                          Frank Vega
#                      Juanary 8th, 2024

import argparse
import time

from . import algorithm
from . import parser
from . import applogger


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-a', '--all', action='store_true', help='identify all triangles')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--count', action='store_true', help='count the total amount of triangles')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.1.0')

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
    filename = parser.get_file_name(filepath)
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # A solution with a time complexity of O(n + m)
    logger.info("A solution with a time complexity of O(n + m) started")
    started = time.time()
    
    result = algorithm.find_triangle_coordinates(sparse_matrix, not all_triangles and not count_triangles)

    logger.info(f"A solution with a time complexity of O(n + m) done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # Output the smart solution
    if result and count_triangles and not all_triangles:
        result = len(result)        
    answer = algorithm.string_complex_format(result)
    output = f"{filename}: {answer}" 
    if (args.log):
        logger.info(output)
    print(output)

    # A Solution with at least O(m^(2.372)) Time Complexity
    if brute_force:
        logger.info("A solution with a time complexity of at least O(m^(2.372)) started")
        started = time.time()
        
        result = algorithm.find_triangle_coordinates_brute_force(sparse_matrix) if all_triangles or count_triangles else algorithm.is_triangle_free_brute_force(sparse_matrix)
        
        logger.info(f"A solution with a time complexity of at least O(m^(2.372)) done in: {(time.time() - started) * 1000.0} milliseconds")
    
        # Output the naive solution
        if result and count_triangles and not all_triangles:
            result = len(result)        
        answer = algorithm.string_complex_format(result) if all_triangles or count_triangles else algorithm.string_simple_format(result)
        output = f"{filename}: {answer}" 
        if (args.log):
            logger.info(output)
        print(output)

        
if __name__ == "__main__":
    main()