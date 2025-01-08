# Triangle-Free Solver

![Honoring the Memory of Carlos Juan Finlay (Pioneer in the research of yellow fever)](docs/finlay.jpg)

This work builds upon [The Triangle Finding Problem](https://www.researchgate.net/publication/387698746_The_Triangle_Finding_Problem).

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

|        | c0    | c1  | c2    | c3  | c4  |
| ------ | ----- | --- | ----- | --- | --- |
| **r0** | 0     | 0   | 1     | 0   | 1   |
| **r1** | 0     | 0   | 0     | 1   | 0   |
| **r2** | **1** | 0   | 0     | 0   | 1   |
| **r3** | 0     | 1   | 0     | 0   | 0   |
| **r4** | **1** | 0   | **1** | 0   | 0   |

A matrix is represented in a text file using the following string representation:

```
00101
00010
10001
01000
10100
```

This represents a 5x5 matrix where each line corresponds to a row, and '1' indicates a connection or presence of an element, while '0' indicates its absence.

_Example Solution:_

Triangle Found `(0, 2, 4)`: In Rows `2` & `4` and Columns `0` & `2`

---

# Our Algorithm - Runtime $O(n + m)$

## The algorithm explanation:

We detect triangles in a graph using a Breadth-First Search (BFS) and a coloring scheme. During the BFS traversal, each visited node assigns unique, consecutive integer colors to its uncolored neighbors. A triangle exists if two adjacent nodes share two colored neighbors, and the colors assigned to these shared neighbors are the same.

## Runtime Analysis:

1. _Breadth-First Search (BFS)_: A standard Breadth-First Search (BFS) on a graph with $\mid V \mid$ vertices and $\mid E \mid$ edges has a time complexity of $O(\mid V \mid + \mid E \mid)$, where $\mid \ldots \mid$ represents the cardinality (e.g., $n = \mid V \mid$ and $m = \mid E \mid$). This is because in the worst case, we visit every vertex and explore every edge.
2. _Coloring and Checking for Color Difference:_ In the Breadth-First Search (BFS), each node performs either color assignment or a constant-time check of color differences with its neighbors. Because this operation is executed for every vertex during the BFS traversal, the overall computational complexity remains equivalent to the standard BFS algorithm's worst-case running time.
3. _Overall Runtime:_ The combined breadth-first search, coloring, and checking process has a time complexity of $O(\mid V \mid + \mid E \mid)$.

# Compile and Environment

## Install Python >=3.8.

## Install Aegypti's Library and its Dependencies with:

```bash
pip install aegypti
```

---

# Execute

---

1. Go to the package directory to use the benchmarks:

```bash
git clone https://github.com/frankvegadelgado/finlay.git
cd finlay
```

2. Execute the script:

```bash
triangle -i .\benchmarks\testMatrix1.txt
```

utilizing the `triangle` command provided by Aegypti's Library to execute the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt`. The file `testMatrix1.txt` represents the example described herein. We also support .xz, .lzma, .bz2, and .bzip2 compressed .txt files.

## The console output will display:

```
testMatrix1.txt: Triangle Found ('0', '2', '4')
```

which implies that the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt` contains a triangle combining the coordinates `(0, 2, 4)`.

# Command Options

To display the help message and available options, run the following command in your terminal:

```bash
triangle -h
```

This will output:

```
usage: triangle [-h] -i INPUTFILE [-b] [-v] [-l] [--version]

Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -b, --bruteForce      enable comparison with a brute-force approach using matrix multiplication
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

This output describes all available options.

---

A command-line tool, `test_triangle`, has been developed for testing algorithms on randomly generated, large sparse matrices. It accepts the following options:

```
usage: test_triangle [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-b] [-w] [-v] [-l] [--version]

The Finlay Testing Application.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -b, --bruteForce      enable comparison with a brute-force approach using matrix multiplication
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

**This tool is designed to benchmark algorithms for sparse matrix operations.**

It generates random square matrices with configurable dimensions (`-d`), sparsity levels (`-s`), and number of tests (`-n`). While a comparison with a brute-force matrix multiplication approach is available, it's recommended to avoid this for large datasets due to performance limitations. Additionally, the generated matrix can be written to the current directory (`-w`), and verbose output or file logging can be enabled with the (`-v`) or (`-l`) flag, respectively, to record test results.

# Code

- Python code by **Frank Vega**.

# Complexity

```diff
+ We propose an O(n + m) algorithm to solve the Triangle-Free Problem.
+ This algorithm provides multiple of applications to other computational problems in combinatorial optimization and computational geometry.
```

# License

- MIT.
