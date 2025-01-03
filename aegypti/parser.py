import lzma
import bz2
import os
import numpy as np

def get_file_name(filepath):
    """
    Gets the file name from an absolute path.

    Args:
        filepath: The absolute path to the file.

    Returns:
        The file name, or None if no file is found.
    """

    return os.path.basename(filepath)
    
def get_extension_without_dot(filepath):
    """
    Gets the file extension without the dot from an absolute path.

    Args:
        filepath: The absolute path to the file.

    Returns:
        The file extension without the dot, or None if no extension is found.
    """

    filename = get_file_name(filepath)
    _, ext = os.path.splitext(filename)
    return ext[1:] if ext else None

def is_symmetric(matrix):
  """
  Checks if an adjacency matrix represents a directed graph.

  Args:
    matrix: A 2D NumPy array representing the adjacency matrix.

  Returns:
    True if the matrix is symmetric (i.e., not equal to its transpose), 
    False otherwise.
  """
  return np.allclose(matrix, matrix.T)

def has_one_on_diagonal(arr):
  """
  Checks if there is a 1 on the diagonal of a NumPy array.

  Args:
    arr: The input NumPy array.

  Returns:
    True if there is a 1 on the diagonal, False otherwise.
  """
  diagonal = np.diag(arr)
  return np.any(diagonal == 1)


def matrix(lines):
    """
    Parses a list of lines and returns a matrix.

    Args:
        lines: A list of lines from the matrix file.

    Returns:
        An n x n NumPy array representing the matrix.
    """

    n = len(lines)
    matrix = np.zeros((n, n), dtype=int)  # Create an n x n matrix of zeros

    for rowIndex, line in enumerate(lines):
        row = line.strip().split(' ')
        if len(row) != n:
            raise ValueError(f"Error: incorrect number of columns in row {rowIndex}")
        matrix[rowIndex] = [int(cell) for cell in row]

    symmetry = is_symmetric(matrix)
    one_on_diagonal = has_one_on_diagonal(matrix)

    if symmetry and not one_on_diagonal:
        return matrix
    elif one_on_diagonal:
        raise ValueError("The input matrix contains a 1 on the diagonal, which is invalid. Adjacency matrices for undirected graphs must have zeros on the diagonal (A[i][i] == 0 for all i).")
    else:
        raise ValueError("The input matrix is not symmetric. Adjacency matrices for undirected graphs must satisfy A[i][j] == A[j][i] for all i and j.")

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
        extension = get_extension_without_dot(filepath)
        if extension == 'txt':
            with open(filepath, 'r') as file:
                lines = file.readlines()
        elif extension == 'xz' or extension == 'lzma':
            with lzma.open(filepath, 'rt') as file:
                lines = file.readlines()
        elif extension == 'bz2' or extension == 'bzip2':
            with bz2.open(filepath, 'rt') as file:
                lines = file.readlines()
        else:
            raise ValueError(f"Unsupported file extension: {extension}")

        return matrix(lines)
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found: {filepath}")