#                   Approximate Clique Solver
#                          Frank Vega
#                       April 4th, 2026

import argparse
import time
import math
from . import algorithm
from . import parser
from . import applogger
from . import utils

def solution(inputFile, verbose=False, log=False, count=False, bruteForce=False, approximation=False):
    """Finds the approximate clique.

    Args:
        inputFile: Input file path.
        verbose: Enable verbose output.
        log: Enable file logging.
        count: Measure the size of the clique.
        bruteForce: Enable brute force approach.
        approximation: Enable an approximate approach within a ratio of at most polynomial.
    """
    
    logger = applogger.Logger(applogger.FileLogger() if (log) else applogger.ConsoleLogger(verbose))
    # Read and parse a dimacs file
    logger.info(f"Parsing the Input File started")
    started = time.time()
    
    graph = parser.read(inputFile)
    filename = utils.get_file_name(inputFile)
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")
    
    if approximation:
        logger.info("An approximate Solution with a polynomial-approximation ratio started")
        started = time.time()
        
        approximate_result = algorithm.find_clique_approximation(graph)

        logger.info(f"An approximate Solution with a polynomial-approximation ratio done in: {(time.time() - started) * 1000.0} milliseconds")
        
        answer = utils.string_result_format(approximate_result, count)
        output = f"{filename}: (approximation) {answer}"
        utils.println(output, logger, log)

    if bruteForce:
        logger.info("A solution with an exponential-time complexity started")
        started = time.time()
        
        brute_force_result = algorithm.find_clique_brute_force(graph)

        logger.info(f"A solution with an exponential-time complexity done in: {(time.time() - started) * 1000.0} milliseconds")
        
        answer = utils.string_result_format(brute_force_result, count)
        output = f"{filename}: (Brute Force) {answer}"
        utils.println(output, logger, log)
        
    logger.info("Our Algorithm with an approximate solution started")
    started = time.time()
    
    novel_result = algorithm.find_clique(graph)

    logger.info(f"Our Algorithm with an approximate solution done in: {(time.time() - started) * 1000.0} milliseconds")

    answer = utils.string_result_format(novel_result, count)
    output = f"{filename}: {answer}"
    utils.println(output, logger, log)
    if novel_result and (bruteForce or approximation):
        if bruteForce:    
            output = f"Exact Ratio (Aegypti/Optimal): {len(brute_force_result)/len(novel_result)}"
        elif approximation:
            log = math.log(graph.number_of_nodes())
            output = f"Upper Bound for Ratio (Aegypti/Optimal): {(graph.number_of_nodes()/(log*log)) * len(approximate_result)/len(novel_result)}"
        utils.println(output, logger, log)
          
def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="clique", description='Compute the Approximate Clique for undirected graph encoded in DIMACS format.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-a', '--approximation', action='store_true', help='enable comparison with a polynomial-time approximation approach within a polynomial factor')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with the exponential-time brute-force approach')
    helper.add_argument('-c', '--count', action='store_true', help='calculate the size of the clique')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.3.8')
    
    # Initialize the parameters
    args = helper.parse_args()
    solution(args.inputFile, 
               verbose=args.verbose, 
               log=args.log,
               count=args.count,
               bruteForce=args.bruteForce,
               approximation=args.approximation)
  

if __name__ == "__main__":
    main()