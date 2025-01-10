# Triangle Solver

![Honoring the Memory of Carlos Juan Finlay (Pioneer in the research of yellow fever)](docs/finlay.jpg)

This work builds upon [The Triangle Complexity Problems](https://www.researchgate.net/publication/387698746_The_Triangle_Complexity_Problems).

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

# Our Algorithm - Runtime $O(n + m)$

## The algorithm explanation:

We detect triangles in a graph using a Depth-First Search (DFS) and a coloring scheme. During the DFS traversal, each visited node assigns unique integer colors to its uncolored neighbors. A triangle exists if two adjacent nodes have two colored neighbors such that these colors assigned to these shared neighbors determine a triangle.

## Runtime Analysis:

1. _Depth-First Search (DFS)_: A standard Depth-First Search (DFS) on a graph with $\mid V \mid$ vertices and $\mid E \mid$ edges has a time complexity of $O(\mid V \mid + \mid E \mid)$, where $\mid \ldots \mid$ represents the cardinality (e.g., $n = \mid V \mid$ and $m = \mid E \mid$). This is because in the worst case, we visit every vertex and explore every edge.
2. _Coloring and Checking for Color Behavior:_ In the Depth-First Search (DFS), each node performs either color assignment or a constant-time check of color behavior with its neighbors. Because this operation is executed for every vertex during the DFS traversal, the overall computational complexity remains equivalent to the standard DFS algorithm's worst-case running time.
3. _Overall Runtime:_ The combined Depth-First Search (DFS), coloring, and checking process has a time complexity of $O(\mid V \mid + \mid E \mid)$.

# Compile and Environment

## Install Python >=3.8.

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
triangle -i .\benchmarks\testMatrix1.txt
```

utilizing the `triangle` command provided by Aegypti's Library to execute the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt`. The file `testMatrix1.txt` represents the example described herein. We also support .xz, .lzma, .bz2, and .bzip2 compressed .txt files.

## The console output will display:

```
testMatrix1.txt: Triangle Found ('0', '2', '4')
```

which implies that the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt` contains a triangle combining the coordinates `(0, 2, 4)`.

---

# Independent Edge Triangle Cover Problem

## Definition:

Given an undirected graph $G = (V, E)$, find a subset of edges $E' \subseteq E$ such that:

1. Triangle Cover: For every cycle of length 3 (triangle) in $G$, at least one edge of that triangle is in $E'$.

2. Independence: No two edges in $E'$ belong to the same triangle.

## NP-hardness

1. The Monotone 1-in-3 SAT Problem

- The Monotone 1-in-3 SAT problem deals with Boolean formulas in Conjunctive Normal Form (CNF) where each clause consists of exactly three variables, and all variables are unnegated (monotone). The objective is to determine if a truth assignment exists for the variables such that precisely one variable in every clause evaluates to `true`. This specific truth assignment, if it exists, is referred to as a valid satisfying truth assignment for the given instance of the Monotone 1-in-3 SAT problem. This problem is NP-complete (See reference: [Schaefer, 1978](https://doi.org/10.1145/800133.804350))

2. Constructing the Graph:

- For each variable $x$ in the Monotone 1-in-3 SAT formula $\phi$, create a corresponding node labeled $x$. For each clause $(x \vee y \vee z)$ in $\phi$, introduce three edges: $(x, y)$, $(y, z)$, and $(x, z)$. These edges collectively form a triangle within the graph.

3. Satisfying a Clause:

- An edge within a triangle is considered `covered` if it is selected. A clause is satisfied if and only if exactly one edge within its corresponding triangle is covered.

4. Variable Assignment:

- If the edge $(y, z)$ from the clause $(x \vee y \vee z)$ is selected, it implies that variable $x$ is assigned the value `true` in the satisfying truth assignment.

5. Relating Solutions:

- We establish a bijection between valid satisfying truth assignments for $\phi$ and Independent Edge Triangle Covers in the corresponding graph $G$.

  - From Monotone 1-in-3 SAT to Independent Edge Triangle Cover:
    - Given a valid satisfying truth assignment for $\phi$, let $x$ be a variable assigned `True`.
    - Since each clause must have exactly one true variable, the node $x$ in $G$ will not be incident to any selected edge.
    - For every clause $(x \vee y \vee z)$ in $\phi$, include the edge $(y, z)$ in the Independent Edge Triangle Cover $E'$.
    - Each triangle in $G$ shares exactly one edge with $E'$, ensuring that at least one edge in every triangle is covered.
    - This directly corresponds to having exactly one true variable per clause in $\phi$.
    - Since no two edges in $E'$ belong to the same triangle, the cover is independent.

6. Conclusion:

   We have shown a polynomial-time reduction from Monotone 1-in-3 SAT to Independent Edge Triangle Cover. Since Monotone 1-in-3 SAT is NP-complete, Independent Edge Triangle Cover is also NP-hard.

# Execute

The `-f` flag enables finding an independent edge triangle cover.

**Example:**

```bash
triangle -i .\benchmarks\testMatrix2.txt -f
```

**Output:**

```
testMatrix2.txt: Independent Edge Triangle Cover Found
```

# Command Options

To display the help message and available options, run the following command in your terminal:

```bash
triangle -h
```

This will output:

```
usage: triangle [-h] -i INPUTFILE [-b] [-c] [-f] [-v] [-l] [--version]

Determine whether an undirected graph, represented by a {0, 1}-adjacency matrix read from a file, is triangle-free or
contains an independent edge triangle cover.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -b, --bruteForce      enable comparison with a brute-force approach using matrix multiplication
  -c, --coverBruteForce
                        enable finding an independent edge triangle cover (brute force)
  -f, --findTriangle    Enable finding an independent edge triangle cover (polynomial-time solution). This problem is NP-
                        complete (See documentation: https://pypi.org/project/aegypti/). This algorithm constitutes a proof
                        that P and NP are equivalent.
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

This output describes all available options.

---

A command-line tool, `test_triangle`, has been developed for testing algorithms on randomly generated, large sparse matrices. It accepts the following options:

```
usage: test_triangle [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-b] [-c] [-f] [-w] [-v] [-l] [--version]

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
  -c, --coverBruteForce
                        enable finding an independent edge triangle cover (brute force)
  -f, --findTriangle    Enable finding an independent edge triangle cover (polynomial-time solution). This problem is NP-
                        complete (See documentation: https://pypi.org/project/aegypti/). This algorithm constitutes a proof
                        that P and NP are equivalent.
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

**This tool is designed to benchmark algorithms for sparse matrix operations.**

It generates random square matrices with configurable dimensions (`-d`), sparsity levels (`-s`), and number of tests (`-n`). While a comparison with a brute-force matrix multiplication approach and the exponential finding of an independent edge triangle cover are available, it's recommended to avoid these for large datasets due to performance limitations. Additionally, the generated matrix can be written to the current directory (`-w`), and verbose output or file logging can be enabled with the (`-v`) or (`-l`) flag, respectively, to record test results.

# Code

- Python code by **Frank Vega**.

# Complexity

```diff
+ We propose an O(n + m) algorithm to solve the Triangle-Free Problem.
+ This algorithm provides multiple of applications to other computational problems in combinatorial optimization and computational geometry.
+ We present a polynomial-time algorithm for finding an Independent Edge Triangle Cover.
+ If we can solve the Independent Edge Triangle Cover problem in polynomial time, and the Independent Edge Triangle Cover problem is NP-complete, then P = NP.
```

# License

- MIT.
