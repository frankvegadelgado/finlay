#                     Triangle-Free Solver
#                            Finlay
#                          Frank Vega
#                      Juanary 3rd, 2024

import argparse
import time

from . import algorithm
from . import parser
from . import applogger


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.')
    helper.add_argument('-i', '--inputFile', type=str, help='Input file path', required=True)
    helper.add_argument('-l', '--log', action='store_true', help='Enable file logging')
    
    # Initialize the parameters
    args = helper.parse_args()
    filepath = args.inputFile
    logger = applogger.Logger(applogger.FileLogger() if (args.log) else applogger.ConsoleLogger())
    
    # Read and parse a dimacs file
    logger.info(f"Parsing the Input File started")
    started = time.time()
    
    testMatrix = parser.read(filepath)
    
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # Quadratic Time Solution
    logger.info("Quadratic Time Solution started")
    started = time.time()
    
    answer = algorithm.string_result_format(algorithm.is_triangle_free(testMatrix))
    
    logger.info(f"Quadratic Time Solution done in: {(time.time() - started) * 1000.0} milliseconds")
    
    # Output the solution
    output = f"{parser.get_file_name(filepath)}: {answer}" 
    if (args.log):
        logger.info(output)
    print(output)    
        
if __name__ == "__main__":
    main()