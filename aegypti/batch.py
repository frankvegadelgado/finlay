# Created on 26/07/2025
# Author: Frank Vega

import argparse
from . import utils
from . import app

def solutions(inputDirectory, verbose=False, log=False, count=False, bruteForce=False, all=False):
     
    file_names = utils.get_file_names(inputDirectory)

    if file_names:
        for file_name in file_names:
            inputFile = f"{inputDirectory}/{file_name}"
            print(f"Test: {inputDirectory}/{file_name}")
            app.solution(inputFile, verbose, log, count, bruteForce, all)


def main():
    
    # Define the parameters
    helper = argparse.ArgumentParser(prog="batch_triangle", description="Solve the Triangle-Free Problem for all undirected graphs encoded in DIMACS format and stored in a directory.")
    helper.add_argument('-i', '--inputDirectory', type=str, help='Input directory path', required=True)
    helper.add_argument('-a', '--all', action='store_true', help='identify all triangles')
    helper.add_argument('-b', '--bruteForce', action='store_true', help='compare with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--count', action='store_true', help='count the total amount of triangles')
    helper.add_argument('-v', '--verbose', action='store_true', help='anable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.3.7')
   
    # Initialize the parameters
    args = helper.parse_args()
    solutions(args.inputDirectory, 
               verbose=args.verbose, 
               log=args.log,
               count=args.count,
               bruteForce=args.bruteForce,
               all=args.all)


if __name__ == "__main__":
  main()      