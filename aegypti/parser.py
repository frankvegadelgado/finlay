import lzma
import bz2
import numpy as np
import scipy.sparse as sparse

from . import utils

def create_sparse_matrix_from_file(file):
    """Creates a sparse matrix from a file containing a binary representation.

    The file should contain lines of '0's and '1's, where '1' indicates a non-zero element.
    This function is intended to create adjacency matrices for undirected graphs, therefore:
    - The resulting matrix must be symmetric.
    - The matrix must have zeros on the diagonal.

    Args:
        file: A file-like object (e.g., an opened file) containing the matrix data.

    Returns:
        A SciPy CSC sparse matrix if the input is valid (symmetric and no 1s on the diagonal).

    Raises:
        ValueError: If the input matrix is not symmetric or contains a '1' on the diagonal.
    """
    data = []
    row_indices = []
    col_indices = []
    rows = 0
    cols = 0

    for i, line in enumerate(file):
        line = line.strip()  # Remove newline characters
        cols = max(cols, len(line)) # Update the number of columns if needed.
        for j, char in enumerate(line):
            if char == '1':
                data.append(np.int8(1))
                row_indices.append(np.int64(i))
                col_indices.append(np.int64(j))
        rows += 1

    matrix = sparse.csc_matrix((data, (row_indices, col_indices)), shape=(rows, cols))

    symmetry = utils.is_symmetric(matrix) #Check if the matrix is symmetric
    one_on_diagonal = utils.has_one_on_diagonal(matrix) #Check if there is a '1' on the diagonal

    if symmetry and not one_on_diagonal:
        return matrix
    elif one_on_diagonal:
        raise ValueError("The input matrix contains a 1 on the diagonal, which is invalid. Adjacency matrices for undirected graphs must have zeros on the diagonal (A[i][i] == 0 for all i).")
    else:
        raise ValueError("The input matrix is not symmetric. Adjacency matrices for undirected graphs must satisfy A[i][j] == A[j][i] for all i and j.")

def save_sparse_matrix_to_file(matrix, filename):
    """
    Writes a SciPy sparse matrix to a text file in 0/1 format.

    Args:
        matrix: The SciPy sparse matrix.
        filename: The name of the output text file.
    """
    with open(filename, 'w') as f:
        for i in range(matrix.shape[0]):
            row = matrix.getrow(i)  # Get the i-th row as a sparse row
            row_str = np.zeros(matrix.shape[1], dtype='U1') #Preallocate an array of unicode strings
            row_str[:] = '0' # Fill with '0'
            row_indices = row.nonzero()[1] #Get the non zero indices of the row
            row_str[row_indices] = '1' # Set '1' at non zero indices
            f.write("".join(row_str) + "\n")


def read(filepath):
    """Reads a file and returns its lines in an array format.

    Args:
        filepath: The path to the file.

    Returns:
        An n x n matrix of ones and zeros

    Raises:
        ValueError: If the file extension is not supported.
        FileNotFoundError: If the file is not found.
    """

    try:
        matrix = None
        extension = utils.get_extension_without_dot(filepath)
        if extension is None or extension == 'txt':
            with open(filepath, 'r') as file:
                matrix = create_sparse_matrix_from_file(file)
        elif extension == 'xz' or extension == 'lzma':
            with lzma.open(filepath, 'rt') as file:
                matrix = create_sparse_matrix_from_file(file)
        elif extension == 'bz2' or extension == 'bzip2':
            with bz2.open(filepath, 'rt') as file:
                matrix = create_sparse_matrix_from_file(file)
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

        return matrix
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")