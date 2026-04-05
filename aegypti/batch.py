# Created on 04/04/2026
# Author: Frank Vega

import argparse
from . import utils
from . import app

def solutions(inputDirectory, verbose=False, log=False, count=False, bruteForce=False, approximation=False):
    """Finds the approximate clique for several instances.

    Args:
        inputDirectory: Input directory path.
        verbose: Enable verbose output.
        log: Enable file logging.
        count: Measure the size of the clique.
        bruteForce: Enable brute force approach.
        approximation: Enable an approximate approach within a ratio of at most polynomial.
    """
    
    file_names = utils.get_file_names(inputDirectory)

    if file_names:
        for file_name in file_names:
            inputFile = f"{inputDirectory}/{file_name}"
            print(f"Test: {inputDirectory}/{file_name}")
            app.solution(inputFile, verbose, log, count, bruteForce, approximation)


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="batch_clique", description="Compute the Approximate Clique for all undirected graphs encoded in DIMACS format and stored in a directory.")
    helper.add_argument('-i', '--inputDirectory', type=str, help='Input directory path', required=True)
    helper.add_argument('-a', '--approximation', action='store_true', help='enable comparison with a polynomial-time approximation approach within a polynomial factor')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='enable comparison with the exponential-time brute-force approach')
    helper.add_argument('-c', '--count', action='store_true', help='calculate the size of the clique')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.3.9')

    
    # Initialize the parameters
    args = helper.parse_args()
    solutions(args.inputDirectory, 
               verbose=args.verbose, 
               log=args.log,
               count=args.count,
               bruteForce=args.bruteForce,
               approximation=args.approximation)


if __name__ == "__main__":
  main()      