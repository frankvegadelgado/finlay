import lzma
import bz2
import numpy as np
import scipy.sparse as sparse

from . import utils

def create_sparse_matrix_from_file(file):
    """Creates a sparse matrix from a file containing a DIMACS representation.

    Args:
        file: A file-like object (e.g., an opened file) containing the matrix data.

    Returns:
        A SciPy CSC sparse matrix if the input is valid (symmetric and no 1s on the diagonal).

    Raises:
        ValueError: If the input matrix is not in the correct DIMACS format.
    """
    data = []
    row_indices = []
    col_indices = []
    dimension = 0
    visited = {}
    for i, line in enumerate(file):
        line = line.strip()  # Remove newline characters
        if not line.startswith('c') and not line.startswith('p'):
            edge = [np.int32(node) for node in line.split(' ') if node != 'e']
            if len(edge) != 2 or min(edge[0], edge[1]) <= 0:
                raise ValueError(f"The input file is not in the correct DIMACS format at line {i}")
            elif (edge[0], edge[1]) in visited or (edge[1], edge[0]) in visited:
                raise ValueError(f"The input file contains a repeated edge at line {i}")
            else:
                data.append(np.int8(1))
                row_indices.append(edge[0] - 1)
                col_indices.append(edge[1] - 1)
                dimension = max(dimension, edge[0], edge[1])
                visited[(edge[0], edge[1])], visited[(edge[1], edge[0])] = True, True

    sparse_matrix = sparse.csc_matrix((data, (row_indices, col_indices)), shape=(dimension, dimension))
    
    # Convert sparse_matrix to a symmetric matrix
    symmetric_matrix = utils.make_symmetric(sparse_matrix)  

    # Set diagonal to 0
    symmetric_matrix.setdiag(0)

    return symmetric_matrix

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
        An n x n matrix of ones and zeros

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