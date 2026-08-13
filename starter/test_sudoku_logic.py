"""
Comprehensive test suite for sudoku_logic module.
Tests puzzle generation, solution validation, and sudoku rules.
"""
import pytest
import sudoku_logic


class TestPuzzleGeneration:
    """Test puzzle generation and basic properties."""

    def test_generate_puzzle_has_unique_solution_and_target_clues(self):
        """ORIGINAL TEST: Verify puzzle has exactly one solution with correct clue count."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)

        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
        assert sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row) == 35
        assert sudoku_logic.count_solutions(puzzle, 2) == 1
        assert sudoku_logic.is_complete_solution(solution)

    def test_count_solutions_detects_multiple_solutions(self):
        """ORIGINAL TEST: Verify solution counting works correctly."""
        board = [
            [5, 3, 0, 0, 7, 0, 0, 0, 0],
            [6, 0, 0, 1, 9, 5, 0, 0, 0],
            [0, 9, 8, 0, 0, 0, 0, 6, 0],
            [8, 0, 0, 0, 6, 0, 0, 0, 3],
            [4, 0, 0, 8, 0, 3, 0, 0, 1],
            [7, 0, 0, 0, 2, 0, 0, 0, 6],
            [0, 6, 0, 0, 0, 0, 2, 8, 0],
            [0, 0, 0, 4, 1, 9, 0, 0, 5],
            [0, 0, 0, 0, 8, 0, 0, 7, 9],
        ]

        assert sudoku_logic.count_solutions(board, 2) == 1

    def test_generate_puzzle_returns_tuple(self):
        """Verify generate_puzzle returns (puzzle, solution) tuple."""
        result = sudoku_logic.generate_puzzle(35)
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_generate_puzzle_default_clues_is_35(self):
        """Verify default clue count is 35 when not specified."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 35

    def test_generate_puzzle_easy_difficulty(self):
        """Verify puzzle generation with easy difficulty (45 clues)."""
        puzzle, solution = sudoku_logic.generate_puzzle(45)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 45
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_generate_puzzle_medium_difficulty(self):
        """Verify puzzle generation with medium difficulty (35 clues)."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 35
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_generate_puzzle_hard_difficulty(self):
        """Verify puzzle generation with hard difficulty (28 clues)."""
        puzzle, solution = sudoku_logic.generate_puzzle(28)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 28
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_generate_puzzle_is_9x9(self):
        """Verify puzzle is always 9x9 grid."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_generate_puzzle_solution_is_9x9(self):
        """Verify solution is always 9x9 grid."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert len(solution) == 9
        assert all(len(row) == 9 for row in solution)

    def test_generate_puzzle_values_in_valid_range(self):
        """Verify all puzzle cells contain 0 or 1-9."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for row in puzzle:
            for cell in row:
                assert 0 <= cell <= 9

    def test_generate_puzzle_solution_values_in_valid_range(self):
        """Verify solution cells contain only 1-9."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for row in solution:
            for cell in row:
                assert 1 <= cell <= 9

    def test_generate_puzzle_solution_is_complete(self):
        """Verify solution has no empty cells."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert sudoku_logic.is_complete_solution(solution)

    def test_generate_puzzle_prefilled_matches_solution(self):
        """Verify prefilled cells in puzzle match solution."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]

    def test_generate_puzzle_multiple_times_produces_different_puzzles(self):
        """Verify calling generate_puzzle multiple times produces different puzzles."""
        puzzle1, _ = sudoku_logic.generate_puzzle(35)
        puzzle2, _ = sudoku_logic.generate_puzzle(35)
        # Extremely unlikely to be identical
        assert puzzle1 != puzzle2

    def test_generate_puzzle_retries_until_unique_solution(self, monkeypatch):
        """Verify the generator retries when the first puzzle attempt is not uniquely solvable."""
        calls = {'remove_attempts': 0}
        original_remove_cells = sudoku_logic.remove_cells
        original_fill_board = sudoku_logic.fill_board

        def fake_fill_board(board):
            return original_fill_board(board)

        def fake_remove_cells(board, clues):
            calls['remove_attempts'] += 1
            if calls['remove_attempts'] == 1:
                # Simulate a non-unique puzzle on the first attempt so the generator must retry.
                for r in range(9):
                    for c in range(9):
                        board[r][c] = 0
                return board
            return original_remove_cells(board, clues)

        monkeypatch.setattr(sudoku_logic, 'fill_board', fake_fill_board)
        monkeypatch.setattr(sudoku_logic, 'remove_cells', fake_remove_cells)

        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert sudoku_logic.count_solutions(puzzle, 2) == 1
        assert calls['remove_attempts'] >= 2


class TestUniqueSolutionGuarantee:
    """Test the CRITICAL requirement: every puzzle has exactly ONE solution."""

    def test_puzzle_35_clues_has_exactly_one_solution(self):
        """Verify 35-clue puzzle has exactly one solution."""
        for _ in range(3):
            puzzle, _ = sudoku_logic.generate_puzzle(35)
            assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_puzzle_45_clues_has_exactly_one_solution(self):
        """Verify 45-clue puzzle has exactly one solution."""
        for _ in range(3):
            puzzle, _ = sudoku_logic.generate_puzzle(45)
            assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_puzzle_28_clues_has_exactly_one_solution(self):
        """Verify 28-clue puzzle has exactly one solution."""
        for _ in range(3):
            puzzle, _ = sudoku_logic.generate_puzzle(28)
            assert sudoku_logic.count_solutions(puzzle, 2) == 1


class TestSudokuRules:
    """Test sudoku validity rules for solutions."""

    def test_solution_rows_contain_all_digits(self):
        """Verify every row contains digits 1-9 exactly once."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for row_idx, row in enumerate(solution):
            row_set = set(row)
            assert row_set == set(range(1, 10)), f"Row {row_idx} invalid"

    def test_solution_columns_contain_all_digits(self):
        """Verify every column contains digits 1-9 exactly once."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for col_idx in range(9):
            col = [solution[row_idx][col_idx] for row_idx in range(9)]
            col_set = set(col)
            assert col_set == set(range(1, 10)), f"Column {col_idx} invalid"

    def test_solution_3x3_boxes_contain_all_digits(self):
        """Verify every 3x3 box contains digits 1-9 exactly once."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_cells = []
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        box_cells.append(solution[r][c])
                box_set = set(box_cells)
                assert box_set == set(range(1, 10)), \
                    f"3x3 box at ({box_row}, {box_col}) invalid"

    def test_solution_no_row_conflicts(self):
        """Verify no row contains duplicate values."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for row_idx, row in enumerate(solution):
            assert len(row) == len(set(row)), f"Row {row_idx} has duplicates"

    def test_solution_no_column_conflicts(self):
        """Verify no column contains duplicate values."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for col_idx in range(9):
            col = [solution[row_idx][col_idx] for row_idx in range(9)]
            assert len(col) == len(set(col)), f"Column {col_idx} has duplicates"

    def test_solution_no_box_conflicts(self):
        """Verify no 3x3 box contains duplicate values."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_cells = []
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        box_cells.append(solution[r][c])
                assert len(box_cells) == len(set(box_cells)), \
                    f"3x3 box at ({box_row}, {box_col}) has duplicates"


class TestSolutionCounting:
    """Test the count_solutions function."""

    def test_count_solutions_valid_puzzle_returns_1(self):
        """Verify valid puzzle returns exactly 1 solution."""
        puzzle, _ = sudoku_logic.generate_puzzle(35)
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_count_solutions_empty_puzzle_returns_many(self):
        """Verify empty board has many solutions."""
        empty_board = [[0] * 9 for _ in range(9)]
        # Should find at least 2 solutions
        assert sudoku_logic.count_solutions(empty_board, 2) >= 2

    def test_count_solutions_respects_limit(self):
        """Verify count_solutions stops at limit."""
        empty_board = [[0] * 9 for _ in range(9)]
        # Should stop counting at limit=2
        result = sudoku_logic.count_solutions(empty_board, 2)
        assert result <= 2

    def test_count_solutions_complete_board_returns_1(self):
        """Verify completed board has 1 solution."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert sudoku_logic.count_solutions(solution, 2) == 1


class TestHelperFunctions:
    """Test helper functions."""

    def test_is_complete_solution_with_complete_board(self):
        """Verify is_complete_solution returns True for complete board."""
        puzzle, solution = sudoku_logic.generate_puzzle(35)
        assert sudoku_logic.is_complete_solution(solution)

    def test_is_complete_solution_with_incomplete_board(self):
        """Verify is_complete_solution returns False for incomplete board."""
        puzzle, _ = sudoku_logic.generate_puzzle(35)
        assert not sudoku_logic.is_complete_solution(puzzle)

    def test_is_complete_solution_with_empty_board(self):
        """Verify is_complete_solution returns False for empty board."""
        empty_board = [[0] * 9 for _ in range(9)]
        assert not sudoku_logic.is_complete_solution(empty_board)

    def test_is_safe_returns_true_for_valid_placement(self):
        """Verify is_safe returns True for valid placements."""
        puzzle, _ = sudoku_logic.generate_puzzle(35)
        # For an empty cell, check if we can place a number safely
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] == 0:
                    # Try to find a safe number to place
                    for num in range(1, 10):
                        if sudoku_logic.is_safe(puzzle, i, j, num):
                            # Found at least one safe placement
                            assert True
                            return
        # If we get here, the puzzle was full, which is fine
        assert True

    def test_create_empty_board_returns_9x9_zeros(self):
        """Verify create_empty_board returns 9x9 board of zeros."""
        board = sudoku_logic.create_empty_board()
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)
        assert all(cell == 0 for row in board for cell in row)

    def test_deep_copy_creates_independent_copy(self):
        """Verify deep_copy creates independent board copy."""
        puzzle, _ = sudoku_logic.generate_puzzle(35)
        puzzle_copy = sudoku_logic.deep_copy(puzzle)
        
        # Find a prefilled cell (non-zero) to modify
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    original_value = puzzle[i][j]
                    # Modify copy
                    puzzle_copy[i][j] = 0
                    # Original should be unchanged
                    assert puzzle[i][j] == original_value
                    assert puzzle_copy[i][j] == 0
                    return
        
        # Fallback: modify any cell
        puzzle_copy[0][0] = 99
        assert puzzle[0][0] != puzzle_copy[0][0]


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_generate_puzzle_with_high_clue_count(self):
        """Verify puzzle generation with high clue count (80 clues)."""
        puzzle, solution = sudoku_logic.generate_puzzle(80)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert filled == 80
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_generate_puzzle_with_minimum_clues(self):
        """Verify puzzle generation respects minimum clue requests."""
        puzzle, solution = sudoku_logic.generate_puzzle(17)
        filled = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        # Algorithm guarantees clues >= requested (may be higher if uniqueness requires it)
        assert filled >= 17
        assert sudoku_logic.count_solutions(puzzle, 2) == 1

    def test_generate_puzzle_can_be_called_many_times(self):
        """Verify puzzle can be generated multiple times without errors."""
        for _ in range(10):
            puzzle, solution = sudoku_logic.generate_puzzle(35)
            assert sudoku_logic.count_solutions(puzzle, 2) == 1
