import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


# Sudoku solving logic: backtracking search for valid placements.
def solve_board(board, limit=None):
    """Return a list of solutions up to the provided limit."""
    solutions = []

    def backtrack():
        if len(solutions) >= (limit if limit is not None else float('inf')):
            return

        row = None
        col = None
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == EMPTY:
                    row, col = r, c
                    break
            if row is not None:
                break

        if row is None:
            solutions.append(deep_copy(board))
            return

        for num in range(1, SIZE + 1):
            if is_safe(board, row, col, num):
                board[row][col] = num
                backtrack()
                board[row][col] = EMPTY
                if limit is not None and len(solutions) >= limit:
                    return

    backtrack()
    return solutions


# Solution counting: we stop once more than one solution is found.
def count_solutions(board, limit=2):
    """Count solutions up to the given limit; returns early once exceeded."""
    solutions = 0

    def backtrack():
        nonlocal solutions
        if solutions >= limit:
            return

        row = None
        col = None
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == EMPTY:
                    row, col = r, c
                    break
            if row is not None:
                break

        if row is None:
            solutions += 1
            return

        for num in range(1, SIZE + 1):
            if is_safe(board, row, col, num):
                board[row][col] = num
                backtrack()
                board[row][col] = EMPTY
                if solutions >= limit:
                    return

    backtrack()
    return solutions


def remove_cells(board, clues):
    # Puzzle generation: create the full solution, then remove cells until the clue count is reached.
    cells_to_remove = SIZE * SIZE - clues
    positions = [(r, c) for r in range(SIZE) for c in range(SIZE)]
    random.shuffle(positions)

    for row, col in positions:
        if cells_to_remove <= 0:
            break
        if board[row][col] == EMPTY:
            continue
        original_value = board[row][col]
        board[row][col] = EMPTY
        # Unique-solution validation: a puzzle is only accepted if it has exactly one valid completion.
        if count_solutions(deep_copy(board), limit=2) != 1:
            board[row][col] = original_value
        else:
            cells_to_remove -= 1

    return board


def is_complete_solution(board):
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False
    return True


def generate_puzzle(clues=35):
    # Generate a valid completed Sudoku solution and retry if the final puzzle is not uniquely solvable.
    if clues < 17:
        clues = 17
    if clues > 81:
        clues = 81

    for _ in range(100):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)

        # Remove numbers while preserving uniqueness of the final puzzle.
        puzzle = deep_copy(solution)
        remove_cells(puzzle, clues)

        if count_solutions(puzzle, limit=2) == 1:
            # The generator must keep the true solution so Check Solution can compare against it.
            return puzzle, solution

    # Fallback in the rare event that a random board cannot be reduced to a uniquely solvable puzzle.
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    puzzle = deep_copy(solution)
    remove_cells(puzzle, clues)
    if count_solutions(puzzle, limit=2) != 1:
        raise ValueError('Failed to generate a Sudoku puzzle with exactly one solution.')
    return puzzle, solution
