# Aegypti: Approximate Clique Solver

![Honoring the Memory of Carlos Juan Finlay (Pioneer in the research of yellow fever)](docs/finlay.jpg)

This work builds upon [The Aegypti Algorithm](https://dev.to/frank_vega_987689489099bf/the-aegypti-algorithm-52i9).

---

# The Maximum Clique Problem: Overview

## **Description**

The **Maximum Clique Problem (MCP)** is a classic NP-hard problem in graph theory and computer science. Given an undirected graph $G = (V, E)$, a **clique** is a subset of vertices $C \subseteq V$ where every two distinct vertices are connected by an edge. The goal of MCP is to find the largest possible clique in $G$.

### **Key Definitions**

- **Clique**: A complete subgraph (all possible edges exist between vertices).
- **Maximum Clique**: The largest clique in the graph.
- **Clique Number ($\omega(G)$)**: The size of the maximum clique in $G$.

## **Theoretical Background**

- MCP is **NP-Hard**, meaning no known polynomial-time algorithm solves all cases unless $P = NP$.
- It is closely related to other problems like the **Independent Set Problem** (complement graph) and **Graph Coloring**.
- Decision version: "Does a clique of size $k$ exist?" is **NP-Complete**.

## **Approaches to Solve MCP**

### **Exact Algorithms**

1. **Brute Force**: Check all possible subsets (exponential time $O(2^n)$).
2. **Branch and Bound**: Prune search space by eliminating branches where clique size cannot exceed the current maximum.
3. **Integer Programming (IP)**: Formulate as an optimization problem with binary variables and constraints.
4. **Bron-Kerbosch Algorithm**: A recursive backtracking method for listing all maximal cliques.

### **Heuristic & Approximation Methods**

1. **Greedy Algorithms**: Iteratively add vertices with the highest degree or most connections to the current clique.
2. **Local Search**: Improve existing solutions via vertex swaps or perturbations.
3. **Metaheuristics**:
   - **Genetic Algorithms**: Evolve candidate solutions via selection, crossover, and mutation.
   - **Simulated Annealing**: Probabilistic technique inspired by thermodynamics.
   - **Tabu Search**: Avoid revisiting solutions using a "tabu list."

### **Advanced Techniques**

- **Reduction Rules**: Simplify the graph by removing vertices that cannot be part of the maximum clique.
- **Parallel & GPU Computing**: Speed up exhaustive searches using parallel processing.
- **Machine Learning**: Learn graph features to guide heuristic choices (emerging area).

## **Applications**

1. **Social Network Analysis**: Identifying tightly connected groups (communities).
2. **Bioinformatics**: Protein interaction networks, gene regulatory networks.
3. **Computer Vision**: Object recognition, pattern matching.
4. **Wireless Networks**: Resource allocation, interference modeling.
5. **Combinatorial Optimization**: Scheduling, coding theory, cryptography.

## **Challenges & Open Problems**

- Scalability for large graphs (millions of vertices).
- Improving approximation guarantees (best-known is $O(n / \log^2 n)$).
- Hybrid approaches combining exact and heuristic methods.

## **Conclusion**

The Maximum Clique Problem remains a fundamental challenge in computational complexity with broad practical implications. While exact methods are limited to small graphs, heuristic and hybrid approaches enable solutions for real-world applications.

---

## Problem Statement

Input: A Boolean Adjacency Matrix $M$.

Answer: Find a Maximum Clique.

### Example Instance: 5 x 5 matrix

|        | c1  | c2  | c3  | c4  | c5  |
| ------ | --- | --- | --- | --- | --- |
| **r1** | 0   | 0   | 1   | 0   | 1   |
| **r2** | 0   | 0   | 0   | 1   | 0   |
| **r3** | 1   | 0   | 0   | 0   | 1   |
| **r4** | 0   | 1   | 0   | 0   | 0   |
| **r5** | 1   | 0   | 1   | 0   | 0   |

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

Clique Found `1, 3, 5`: Nodes `1`, `3`, and `5` constitute an optimal solution.

---

# Compile and Environment

## Prerequisites

- Python ≥ 3.12

## Installation

```bash
pip install aegypti
```

## Execution

1. Clone the repository:

   ```bash
   git clone https://github.com/frankvegadelgado/aegypti.git
   cd aegypti
   ```

2. Run the script:

   ```bash
   clique -i ./benchmarks/testMatrix1
   ```

   utilizing the `clique` command provided by Aegypti's Library to execute the Boolean adjacency matrix `aegypti\benchmarks\testMatrix1`. The file `testMatrix1` represents the example described herein. We also support `.xz`, `.lzma`, `.bz2`, and `.bzip2` compressed text files.

   **Example Output:**

   ```
   testMatrix1: Clique Found 1, 3, 5
   ```

   This indicates nodes `1, 3, 5` form a clique.

---

## Clique Size

Use the `-c` flag to count the nodes in the clique:

```bash
clique -i ./benchmarks/testMatrix2 -c
```

**Output:**

```
testMatrix2: Clique Size 4
```

---

# Command Options

Display help and options:

```bash
clique -h
```

**Output:**

```bash
usage: clique [-h] -i INPUTFILE [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Clique for undirected graph encoded in DIMACS format.

options:
  -h, --help            show this help message and exit
  -i INPUTFILE, --inputFile INPUTFILE
                        input file path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a polynomial factor
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the clique
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Batch Execution

Batch execution allows you to solve multiple graphs within a directory consecutively.

To view available command-line options for the `batch_clique` command, use the following in your terminal or command prompt:

```bash
batch_clique -h
```

This will display the following help information:

```bash
usage: batch_clique [-h] -i INPUTDIRECTORY [-a] [-b] [-c] [-v] [-l] [--version]

Compute the Approximate Clique for all undirected graphs encoded in DIMACS format and stored in a directory.

options:
  -h, --help            show this help message and exit
  -i INPUTDIRECTORY, --inputDirectory INPUTDIRECTORY
                        Input directory path
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a polynomial factor
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the clique
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Testing Application

A command-line utility named `test_clique` is provided for evaluating the Algorithm using randomly generated, large sparse matrices. It supports the following options:

```bash
usage: test_clique [-h] -d DIMENSION [-n NUM_TESTS] [-s SPARSITY] [-a] [-b] [-c] [-w] [-v] [-l] [--version]

The Aegypti Testing Application using randomly generated, large sparse matrices.

options:
  -h, --help            show this help message and exit
  -d DIMENSION, --dimension DIMENSION
                        an integer specifying the dimensions of the square matrices
  -n NUM_TESTS, --num_tests NUM_TESTS
                        an integer specifying the number of tests to run
  -s SPARSITY, --sparsity SPARSITY
                        sparsity of the matrices (0.0 for dense, close to 1.0 for very sparse)
  -a, --approximation   enable comparison with a polynomial-time approximation approach within a polynomial factor
  -b, --bruteForce      enable comparison with the exponential-time brute-force approach
  -c, --count           calculate the size of the clique
  -w, --write           write the generated random matrix to a file in the current directory
  -v, --verbose         anable verbose output
  -l, --log             enable file logging
  --version             show program's version number and exit
```

---

# Code

- Python implementation by **Frank Vega**.

---

# License

- MIT License.
