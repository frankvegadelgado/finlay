# Aegypti: Triangle-Free Solver

![Honoring the Memory of Carlos Juan Finlay (Pioneer in the research of yellow fever)](docs/finlay.jpg)

This work builds upon [The Aegypti Algorithm](https://dev.to/frank_vega_987689489099bf/the-aegypti-algorithm-52i9).

---

# Triangle-Free Problem

The Triangle-Free problem is a fundamental decision problem in graph theory. Given an undirected graph, the problem asks whether it's possible to determine if the graph contains no triangles (cycles of length 3). In other words, it checks if there exists a configuration where no three vertices are connected by edges that form a closed triangle.

This problem is important for various reasons:

- **Graph Analysis:** It's a basic building block for more complex graph algorithms and has applications in social network analysis, web graph analysis, and other domains.
- **Computational Complexity:** It serves as a benchmark problem in the study of efficient algorithms for graph properties. While the naive approach has a time complexity of $O(n^3)$, there are more efficient algorithms with subcubic complexity.

Understanding the Triangle-Free problem is essential for anyone working with graphs and graph algorithms.

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Question: Does $M$ contain no triangles?

Answer: True / False

### Example Instance: 5 x 5 matrix

|        | c1    | c2  | c3    | c4  | c5  |
| ------ | ----- | --- | ----- | --- | --- |
| **r1** | 0     | 0   | 1     | 0   | 1   |
| **r2** | 0     | 0   | 0     | 1   | 0   |
| **r3** | **1** | 0   | 0     | 0   | 1   |
| **r4** | 0     | 1   | 0     | 0   | 0   |
| **r5** | **1** | 0   | **1** | 0   | 0   |

The input for undirected graph is typically provided in [DIMACS](http://dimacs.rutgers.edu/Challenges) format. In this way, the previous adjacency matrix is represented in a text file using the following string representation:

```
p edge 5 4
e 1 3
e 1 5
e 2 4
e 3 5
```

This represents a 5x5 matrix in DIMACS format such that each edge $(v,w)$ appears exactly once in the input file and is not repeated as $(w,v)$. In this format, every edge appears in the form of

```
e W V
```

where the fields W and V specify the endpoints of the edge while the lower-case character `e` signifies that this is an edge descriptor line.

_Example Solution:_

Triangle Found `(1, 3, 5)`: In Rows `3` & `5` and Columns `1` & `3`

# Compile and Environment

## Install Python >=3.12.

## Install Aegypti's Library and its Dependencies with:

```bash
pip install aegypti
```

# Execute

1. Go to the package directory to use the benchmarks:

```bash
git clone https://github.com/frankvegadelgado/finlay.git
cd finlay
```

2. Execute the script:

```bash
triangle -i .\benchmarks\testMatrix1
```

utilizing the `triangle` command provided by Aegypti's Library to execute the Boolean adjacency matrix `finlay\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support .xz, .lzma, .bz2, and .bzip2 compressed text files.

## The console output will display:

```
Smart Algorithm for testMatrix1: Triangle Found (1, 3, 5)
```

which implies that the Boolean adjacency matrix `finlay\benchmarks\testMatrix1` contains a triangle combining the nodes `(1, 3, 5)`.

---

# Command Options

To display the help message and available options, run the following command in your terminal:

```bash
triangle -h
```

This will output:

```bash
usage: triangle [-h] -i INPUTFILE [-b] [-c] [-v] [-l] [--version]

Solve the Triangle-Free Problem for an undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --combinatorial   compare with the classical Chiba-Nishizeki O(m^{3/2}) adjacency-intersection baseline
  -v, --verbose         enable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

This output describes all available options.

## Batch Execution

Batch execution allows you to solve multiple graphs within a directory consecutively.

To view available command-line options for the `batch_triangle` command, use the following in your terminal or command prompt:

```bash
batch_triangle -h
```

This will display the following help information:

```bash
usage: batch_triangle [-h] -i INPUTDIRECTORY [-b] [-c] [-v] [-l] [--version]

Solve the Triangle-Free Problem for all undirected graphs encoded in DIMACS format and stored in a directory.

options:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        Input directory path
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --combinatorial   compare with the classical Chiba-Nishizeki O(m^{3/2}) adjacency-intersection baseline
  -v, --verbose         enable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
  ```

## The Finlay Testing Application

A command-line tool, `test_triangle`, has been developed for testing algorithms on randomly generated, large sparse matrices. It accepts the following options:

```bash
usage: test_triangle [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-b] [-c] [-w] [-v] [-l] [--version]

The Finlay Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --combinatorial   compare with the classical Chiba-Nishizeki O(m^{3/2}) adjacency-intersection baseline
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         enable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

**This tool is designed to benchmark algorithms for sparse matrix operations.**

It generates random square matrices with configurable dimensions (`-d`), sparsity levels (`-s`), and number of tests (`-n`). While a comparison with a brute-force matrix multiplication approach is available, it's recommended to avoid this for large datasets due to performance limitations. Additionally, the generated matrix can be written to the current directory (`-w`), and verbose output or file logging can be enabled with the (`-v`) or (`-l`) flag, respectively, to record test results.

---

# Car Experiment

The `car/` directory contains a reproducible comparison experiment that runs four triangle-detection routines against an independent exact triangle oracle. `find_triangle_coordinates` is run in both of its modes:

| Subject | Function | Notes |
| ------- | -------- | ----- |
| **Aegypti-safe** | `find_triangle_coordinates(graph, fallback=True)` | Unconditionally complete; falls back to Chiba–Nishizeki when the dense branch is inconclusive (`O(m^{3/2})` worst case). |
| **Aegypti-fast** | `find_triangle_coordinates(graph, fallback=False)` | Uniform `O(n^2)`; the dense branch may return `None` on a triangle-containing graph. |
| **Chiba–Nishizeki** | `find_triangle_chiba_nishizeki(graph)` | Exact, `O(m^{3/2})`. |
| **Matrix multiplication** | `is_triangle_free_brute_force(sparse_matrix)` | Reference baseline, `O(n^{2.37})`. |

`car/car_experiment.py` builds a deterministic benchmark of ~10,000 small graphs (fixed seed) drawn from six families that span both regimes of the Aegypti dispatch — sparse (`m ≤ ⌈n^{4/3}⌉`) and dense (`m > ⌈n^{4/3}⌉`): sparse and dense Erdős–Rényi graphs, triangle-free bipartite graphs, planted-triangle sparse graphs, planted-clique dense graphs, and structured graphs (complete, even cycles, wheels, complete bipartite, random regular). Each instance is scored against an exact neighbourhood-intersection oracle, and every returned witness is checked to be a genuine triangle.

Run it from the repository root:

```bash
python car/car_experiment.py            # full ~10,000-instance suite
python car/car_experiment.py --quick    # smaller, faster sweep
```

It writes `car_experiment.json`, `car_summary.csv`, `car_by_instance.csv`, and a human-readable `CAR_REPORT.md` into the `car/` folder. The key column `aegypti_fast_miss` flags any instance where the oracle finds a triangle but the fast dense branch returns none — the empirical content of the Hvala independent-set hypothesis. Aegypti-safe converts every such case into a correct answer through its fallback. (If the installed package predates the `fallback` parameter, both variants reduce to the default call.)

---

# Code

- Python code by **Frank Vega**.

---

# License

- MIT.
