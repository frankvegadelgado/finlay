# Aegypti: Triangle-Free Solver

![Honoring the Memory of Carlos Juan Finlay (Pioneer in the research of yellow fever)](docs/finlay.jpg)

This work builds upon [The Triangle Finding Problem](https://hal.science/hal-04887444).

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

# Our Algorithm - Runtime $O(n + m)$

## The algorithm explanation:

Triangle detection in a graph is performed using a Depth-First Search (DFS) combined with a coloring scheme. As the DFS traverses the graph, each visited node colors its uncolored neighbors with unique integers. A triangle is identified when two adjacent nodes share two colored neighbors whose colors form a triangle.

## Runtime Analysis:

1. _Depth-First Search (DFS)_: A standard Depth-First Search (DFS) on a graph with $\mid V \mid$ vertices and $\mid E \mid$ edges has a time complexity of $O(\mid V \mid + \mid E \mid)$, where $\mid \ldots \mid$ represents the cardinality (e.g., $n = \mid V \mid$ and $m = \mid E \mid$). This is because in the worst case, we visit every vertex and explore every edge.
2. _Coloring and Checking for Color Behavior:_ During the Depth-First Search (DFS), each node performs either color assignment or a constant-time check of its neighbors' colors. Since this operation is executed for each vertex during the DFS traversal, the overall computational complexity remains $O(\mid V \mid + \mid E \mid)$, equivalent to the standard DFS algorithm's worst-case running time.
3. _Overall Runtime:_ The combined Depth-First Search (DFS), coloring, and checking process has a time complexity of $O(\mid V \mid + \mid E \mid)$.

# Compile and Environment

## Install Python >=3.10.

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
testMatrix1: Triangle Found (1, 3, 5)
```

which implies that the Boolean adjacency matrix `finlay\benchmarks\testMatrix1` contains a triangle combining the nodes `(1, 3, 5)`.

---

## Find and Count All Triangles - Runtime $O(n + m)$

The `-a` flag enables the discovery of all triangles within the graph.

**Example:**

```bash
triangle -i .\benchmarks\testMatrix2 -a
```

**Output:**

```
testMatrix2: Triangles Found (1, 3, 9); (1, 2, 11); (1, 3, 4); (1, 2, 8); (1, 3, 11); (2, 4, 11); (3, 4, 11); (2, 4, 9); (1, 4, 11); (4, 5, 11); (1, 4, 9); (1, 2, 9); (3, 4, 9); (1, 2, 6); (4, 5, 9); (1, 2, 4)
```

When multiple triangles exist, the output provides a list of their vertices.

Similarly, the `-c` flag counts all triangles in the graph.

**Example:**

```bash
triangle -i .\benchmarks\testMatrix2 -c
```

**Output:**

```
testMatrix2: Triangles Count 16
```

## Runtime Analysis:

We employ the same algorithm used to solve the triangle-free problem.

---

# Command Options

To display the help message and available options, run the following command in your terminal:

```bash
triangle -h
```

This will output:

```
usage: triangle [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Solve the Triangle-Free Problem for an undirected graph represented by a Boolean Adjacency Matrix given in a File.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --all             identify all triangles
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --count           count the total amount of triangles
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

This output describes all available options.

## The Finlay Testing Application

A command-line tool, `test_triangle`, has been developed for testing algorithms on randomly generated, large sparse matrices. It accepts the following options:

```
usage: test_triangle [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Finlay Testing Application.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --all             identify all triangles
  -b, --bruteForce      compare with a brute-force approach using matrix multiplication
  -c, --count           count the total amount of triangles
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

**This tool is designed to benchmark algorithms for sparse matrix operations.**

It generates random square matrices with configurable dimensions (`-d`), sparsity levels (`-s`), and number of tests (`-n`). While a comparison with a brute-force matrix multiplication approach is available, it's recommended to avoid this for large datasets due to performance limitations. Additionally, the generated matrix can be written to the current directory (`-w`), and verbose output or file logging can be enabled with the (`-v`) or (`-l`) flag, respectively, to record test results.

---

# Code

- Python code by **Frank Vega**.

---

# Complexity

```diff
+ We propose an O(n + m) algorithm to solve the Triangle-Free Problem.
+ The algorithm for the Triangle-Free Problem can be adapted to identify and count all triangles in O(n + m) time.
+ This algorithm provides multiple of applications to other computational problems in combinatorial optimization and computational geometry.
```

---

# License

- MIT.
