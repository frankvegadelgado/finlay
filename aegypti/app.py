#                       Triangle Solver
#                          Frank Vega
#                      April 4th, 2026

import argparse
import time

from . import algorithm
from . import parser
from . import applogger
from . import utils


def solution(inputFile, verbose=False, log=False, bruteForce=False, combinatorial=False):

    # Initialize the parameters
    filepath = inputFile
    logger = applogger.Logger(applogger.FileLogger() if (log) else applogger.ConsoleLogger(verbose))
    brute_force = bruteForce
    use_combinatorial = combinatorial

    # Read and parse a dimacs file
    logger.info(f"Parsing the Input File started")
    started = time.time()

    sparse_matrix = parser.read(filepath)
    # Convert the sparse matrix to a NetworkX graph
    graph = utils.sparse_matrix_to_graph(sparse_matrix)
    filename = utils.get_file_name(filepath)
    logger.info(f"Parsing the Input File done in: {(time.time() - started) * 1000.0} milliseconds")

    # A solution with a fast running-time complexity (Aegypti hybrid heuristic)
    logger.info("A solution with a fast running-time complexity started")
    started = time.time()

    result = algorithm.find_triangle_coordinates(graph)

    logger.info(f"A solution with a fast running-time complexity done in: {(time.time() - started) * 1000.0} milliseconds")

    # Output the smart solution
    answer = utils.string_complex_format(result)
    output = f"Smart Algorithm for {filename}: {answer}"
    utils.println(output, logger, log)

    # A solution with the classical Chiba-Nishizeki combinatorial baseline
    if use_combinatorial:
        logger.info("Chiba-Nishizeki combinatorial baseline started")
        started_cn = time.time()

        cn_result = algorithm.find_triangle_chiba_nishizeki(graph)

        logger.info(f"Chiba-Nishizeki combinatorial baseline done in: {(time.time() - started_cn) * 1000.0} milliseconds")

        answer = utils.string_complex_format(cn_result)
        output = f"Chiba-Nishizeki Algorithm for {filename}: {answer}"
        utils.println(output, logger, log)

    # A Solution with brute force (matrix multiplication)
    if brute_force:
        logger.info("Matrix-Multiplication baseline started")
        started_bf = time.time()

        bf_result = algorithm.is_triangle_free_brute_force(sparse_matrix)

        logger.info(f"Matrix-Multiplication baseline done in: {(time.time() - started_bf) * 1000.0} milliseconds")

        answer = utils.string_simple_format(bf_result)
        output = f"Matrix-Multiplication Algorithm for {filename}: {answer}"
        utils.println(output, logger, log)

def main():

    # Define the parameters
    helper = argparse.ArgumentParser(prog="triangle", description='Solve the Triangle-Free Problem for an undirected graph encoded in DIMACS format.')
    helper.add_argument('-i', '--inputFile', type=str, help='input file path', required=True)
    helper.add_argument('-b', '--bruteForce', action='store_true', help='compare with a brute-force approach using matrix multiplication')
    helper.add_argument('-c', '--combinatorial', action='store_true', help='compare with the classical Chiba-Nishizeki O(m^{3/2}) adjacency-intersection baseline')
    helper.add_argument('-v', '--verbose', action='store_true', help='enable verbose output')
    helper.add_argument('-l', '--log', action='store_true', help='enable file logging')
    helper.add_argument('--version', action='version', version='%(prog)s 0.4.3')

    # Initialize the parameters
    args = helper.parse_args()
    solution(args.inputFile,
               verbose=args.verbose,
               log=args.log,
               bruteForce=args.bruteForce,
               combinatorial=args.combinatorial)
        
if __name__ == "__main__":
    main()