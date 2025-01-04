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

Input: A Boolean adjacency matrix $M$.

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

_Example Solution:_

Triangle Found (4, 0, 2): In Rows 2 & 4 and Columns 0 & 2

# Our Algorithm - Runtime $O(n + m)$

## The algorithm explanation:

We detect triangles in a graph using a depth-first search (DFS) and a coloring scheme. During the DFS traversal, each visited node assigns unique, consecutive integer colors to its uncolored neighbors. Specifically, if a node assigns color $c$ to one neighbor, this neighbor assigns $c+1$ to the next, and so on. A triangle exists if two adjacent nodes share two colored neighbors, and the colors assigned to these shared neighbors differ by exactly two.

## Runtime Analysis:

1. _Depth-First Search (DFS)_: A standard depth-first search (DFS) on a graph with $\mid V \mid$ vertices and $\mid E \mid$ edges has a time complexity of $O(\mid V \mid + \mid E \mid)$, where $\mid \ldots \mid$ represents the cardinality (e.g., $n = \mid V \mid$ and $m = \mid E \mid$). This is because in the worst case, we visit every vertex and explore every edge.
2. _Coloring and Checking for Color Difference:_ In the Depth-First Search (DFS), each node performs either color assignment or a constant-time check of color differences with its neighbors. Because this operation is executed for every vertex during the DFS traversal, the overall computational complexity remains equivalent to the standard DFS algorithm's worst-case running time.
3. _Overall Runtime:_ The combined depth-first search, coloring, and checking process has a time complexity of $O(\mid V \mid + \mid E \mid)$.

# Compile and Environment

## Install Python >=3.8.

## Install Aegypti's Library and its Dependencies with:

```
pip install aegypti
```

---

# Execute

---

1. Go to the package directory to use the benchmarks:

```
git clone https://github.com/frankvegadelgado/finlay.git
cd finlay
```

2. Execute the script:

```
triangle -i .\benchmarks\testMatrix1.txt
```

utilizing the `triangle` command provided by Aegypti's Library to execute the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt`. The file `testMatrix1.txt` represents the example described herein. We also support .xz, .lzma, .bz2, and .bzip2 compressed .txt files.

## The console output will display:

```
testMatrix1.txt: Triangle Found (4, 0, 2)
```

which implies that the Boolean adjacency matrix `finlay\benchmarks\testMatrix1.txt` contains a triangle combining the coordinates `(4, 0, 2)`.

# Command Options

In the batch console, running the command:

```
triangle -h
```

will display the following help output:

```
usage: triangle [-h] -i INPUTFILE [-l]

Solve the Triangle-Free Problem for an undirected graph represented by a Boolean adjacency matrix given in a file.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        Input file path
  -l, --log             Enable file logging
```

where it is described all the possible options.

# Code

- Python code by **Frank Vega**.

# Complexity

```diff
+ We propose an O(n + m) algorithm to solve the Triangle-Free Problem.
+ This algorithm provides multiple of applications to other computational problems in combinatorial optimization and computational geometry.
```

# License

- MIT.
