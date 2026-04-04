import lzma
import bz2
import numpy as np
import scipy.sparse as sparse
import networkx as nx

from . import utils

def create_sparse_matrix_from_file(file):
    """Creates a sparse matrix from a file containing a DIMACS format representation.

    Args:
        file: A file-like object (e.g., an opened file) containing the matrix data.

    Returns:
        A NetworkX Graph.

    Raises:
        ValueError: If the input matrix is not the correct DIMACS format.
    """
    graph = nx.Graph()
    for i, line in enumerate(file):
        line = line.strip()  # Remove newline characters
        parts = line.split(' ')
        if not line.startswith('c') and len(parts) == 3:
            # Check if this looks like an edge line (has numbers at the end)
            try:
                int(parts[-1])
                int(parts[-2])
                pass  # Process as edge
            except (ValueError, IndexError):
                continue  # Skip metadata lines
            edge = [np.int32(parts[-1]), np.int32(parts[-2])]
            if min(edge[0], edge[1]) <= 0:
                raise ValueError(f"The input file is not in the correct DIMACS format at line {i}")
            else:
                graph.add_edge(edge[0] - 1, edge[1] - 1)
    
    return graph

def save_sparse_matrix_to_file(matrix, filename):
    """
    Writes a SciPy sparse matrix to a DIMACS format.

    Args:
        matrix: The SciPy sparse matrix.
        filename: The name of the output text file.
    """
    rows, cols = matrix.nonzero()
    
    with open(filename, 'w') as f:
        f.write(f"p edge {matrix.shape[0]} {matrix.nnz // 2 - matrix.shape[0]//2}" + "\n")
        for i, j in zip(rows, cols):
            if i < j:
                f.write(f"e {i + 1} {j + 1}" + "\n")
    

def read(filepath):
    """Reads a file and returns its lines in an array format.

    Args:
        filepath: The path to the file.

    Returns:
        A NetworkX Graph.

    Raises:
        FileNotFoundError: If the file is not found.
    """

    try:
        extension = utils.get_extension_without_dot(filepath)
        if extension == 'xz' or extension == 'lzma':
            with lzma.open(filepath, 'rt') as file:
                matrix = create_sparse_matrix_from_file(file)
        elif extension == 'bz2' or extension == 'bzip2':
            with bz2.open(filepath, 'rt') as file:
                matrix = create_sparse_matrix_from_file(file)
        else:
            with open(filepath, 'r') as file:
                matrix = create_sparse_matrix_from_file(file)
        
        return matrix
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")