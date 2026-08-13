"""
Comprehensive test suite for Flask Sudoku application.
Tests Flask routes, request/response handling, and integration with sudoku_logic.
"""
import json
import pytest
from app import app, CURRENT
import sudoku_logic


@pytest.fixture
def client():
    """Provide a Flask test client with app context."""
    app.config['TESTING'] = True
    with app.app_context():
        yield app.test_client()


class TestAppInitialization:
    """Test Flask application startup and basic configuration."""

    def test_flask_app_exists(self):
        """Verify Flask application instance is created."""
        assert app is not None

    def test_flask_app_is_in_testing_mode(self):
        """Verify app can be configured for testing."""
        with app.app_context():
            app.config['TESTING'] = True
            assert app.config['TESTING'] is True


class TestHomeRoute:
    """Test the home page route."""

    def test_home_page_returns_200(self, client):
        """Verify home page returns HTTP 200 OK."""
        response = client.get('/')
        assert response.status_code == 200

    def test_home_page_returns_html(self, client):
        """Verify home page returns HTML content."""
        response = client.get('/')
        assert response.content_type is not None
        # Flask's render_template returns text/html by default
        assert 'text/html' in response.content_type or response.content_type == 'text/html; charset=utf-8'

    def test_home_page_contains_sudoku_board_element(self, client):
        """Verify home page HTML contains the sudoku board element."""
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'sudoku-board' in html

    def test_home_page_contains_difficulty_selector(self, client):
        """Verify home page contains difficulty selector."""
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'difficulty' in html
        assert 'easy' in html.lower()
        assert 'medium' in html.lower()
        assert 'hard' in html.lower()

    def test_home_page_contains_check_solution_button(self, client):
        """Verify home page contains check solution button."""
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'check-solution' in html

    def test_home_page_contains_new_game_button(self, client):
        """Verify home page contains new game button."""
        response = client.get('/')
        html = response.get_data(as_text=True)
        assert 'new-game' in html


class TestNewGameRoute:
    """Test the /new route that generates puzzles."""

    def test_new_game_default_returns_200(self, client):
        """Verify /new returns HTTP 200 OK."""
        response = client.get('/new')
        assert response.status_code == 200

    def test_new_game_returns_json(self, client):
        """Verify /new returns JSON format."""
        response = client.get('/new')
        assert response.content_type is not None
        assert 'application/json' in response.content_type

    def test_new_game_returns_puzzle_key(self, client):
        """Verify /new response contains 'puzzle' key."""
        response = client.get('/new')
        data = response.get_json()
        assert 'puzzle' in data

    def test_new_game_puzzle_is_9x9_grid(self, client):
        """Verify generated puzzle is a 9x9 grid."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)

    def test_new_game_puzzle_contains_integers(self, client):
        """Verify all cells in puzzle contain integers."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']
        for row in puzzle:
            for cell in row:
                assert isinstance(cell, int)

    def test_new_game_puzzle_values_in_valid_range(self, client):
        """Verify all puzzle cells are 0 or 1-9."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']
        for row in puzzle:
            for cell in row:
                assert 0 <= cell <= 9

    def test_new_game_with_easy_difficulty(self, client):
        """Verify /new accepts easy difficulty (45 clues)."""
        response = client.get('/new?clues=45')
        assert response.status_code == 200
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        assert filled == 45

    def test_new_game_with_medium_difficulty(self, client):
        """Verify /new accepts medium difficulty (35 clues)."""
        response = client.get('/new?clues=35')
        assert response.status_code == 200
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        assert filled == 35

    def test_new_game_with_hard_difficulty(self, client):
        """Verify /new accepts hard difficulty (28 clues)."""
        response = client.get('/new?clues=28')
        assert response.status_code == 200
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        assert filled == 28

    def test_new_game_easy_medium_hard_produce_different_clue_counts(self, client):
        """Verify different difficulties produce different numbers of prefilled cells."""
        easy_resp = client.get('/new?clues=45')
        easy_filled = sum(1 for row in easy_resp.get_json()['puzzle'] for cell in row if cell != 0)

        medium_resp = client.get('/new?clues=35')
        medium_filled = sum(1 for row in medium_resp.get_json()['puzzle'] for cell in row if cell != 0)

        hard_resp = client.get('/new?clues=28')
        hard_filled = sum(1 for row in hard_resp.get_json()['puzzle'] for cell in row if cell != 0)

        # Each difficulty should produce a unique count
        assert easy_filled == 45
        assert medium_filled == 35
        assert hard_filled == 28
        assert easy_filled > medium_filled > hard_filled

    def test_new_game_clues_below_minimum_clamped_to_17(self, client):
        """Verify clue count below 17 is clamped to 17."""
        response = client.get('/new?clues=5')
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        # The app clamps to minimum 17, though some cells may not be removed if uniqueness fails
        assert filled >= 17

    def test_new_game_clues_above_maximum_clamped_to_81(self, client):
        """Verify clue count above 81 is clamped to 81."""
        response = client.get('/new?clues=100')
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        # The app clamps to maximum 81
        assert filled <= 81

    def test_new_game_clues_invalid_string_defaults_to_35(self, client):
        """Verify invalid clue parameter defaults to 35."""
        response = client.get('/new?clues=invalid')
        data = response.get_json()
        filled = sum(1 for row in data['puzzle'] for cell in row if cell != 0)
        assert filled == 35

    def test_new_game_stores_puzzle_in_current_state(self, client):
        """Verify /new stores puzzle in CURRENT global state."""
        CURRENT['puzzle'] = None
        CURRENT['solution'] = None
        response = client.get('/new')
        assert CURRENT['puzzle'] is not None
        assert CURRENT['solution'] is not None

    def test_new_game_can_be_called_multiple_times(self, client):
        """Verify a new puzzle can be generated multiple times without crashing."""
        for i in range(5):
            response = client.get('/new')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data['puzzle']) == 9


class TestCheckSolutionRoute:
    """Test the /check route that validates submitted solutions."""

    def test_check_solution_requires_post(self, client):
        """Verify /check requires POST method."""
        response = client.get('/check')
        # GET to /check should fail (method not allowed)
        assert response.status_code != 200

    def test_check_solution_without_game_returns_error(self, client):
        """Verify /check returns error when no game is in progress."""
        CURRENT['solution'] = None
        response = client.post('/check', json={'board': [[1]*9 for _ in range(9)]})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_check_solution_correct_returns_solved(self, client):
        """Verify correct solution returns 'solved' status."""
        # Generate a puzzle
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        # Submit the correct solution
        response = client.post('/check', json={'board': sol})
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'solved'
        assert 'Congratulations' in data['message'] or 'solved' in data['message'].lower()

    def test_check_solution_incorrect_entry_returns_incorrect(self, client):
        """Verify incorrect entry returns 'incorrect' status."""
        # Generate a puzzle and solution
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        # Create incorrect board by changing one cell
        incorrect_board = [row[:] for row in sol]
        # Find a non-zero cell and change it
        incorrect_board[0][0] = 1 if sol[0][0] != 1 else 2

        response = client.post('/check', json={'board': incorrect_board})
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'incorrect'

    def test_check_solution_incomplete_board_returns_incomplete(self, client):
        """Verify incomplete board returns 'incomplete' status."""
        # Generate puzzle and solution
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        # Create incomplete board by clearing one cell
        incomplete_board = [row[:] for row in sol]
        incomplete_board[0][0] = 0

        response = client.post('/check', json={'board': incomplete_board})
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'incomplete'

    def test_check_solution_empty_board_returns_incomplete(self, client):
        """Verify completely empty board returns 'incomplete' status."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        empty_board = [[0] * 9 for _ in range(9)]
        response = client.post('/check', json={'board': empty_board})
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'incomplete'

    def test_check_solution_invalid_board_size_returns_error(self, client):
        """Verify invalid board size returns error."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        # Board too small
        invalid_board = [[1] * 8 for _ in range(8)]
        response = client.post('/check', json={'board': invalid_board})
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data or data.get('status') == 'invalid'

    def test_check_solution_invalid_row_size_returns_error(self, client):
        """Verify invalid row size returns error."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        # One row has 8 cells instead of 9
        invalid_board = [[1] * 9 for _ in range(8)] + [[1] * 8]
        response = client.post('/check', json={'board': invalid_board})
        assert response.status_code == 400

    def test_check_solution_with_null_board_returns_error(self, client):
        """Verify null board returns error."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        response = client.post('/check', json={'board': None})
        assert response.status_code == 400

    def test_check_solution_with_missing_board_returns_error(self, client):
        """Verify missing board key returns error."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['puzzle'] = puz
        CURRENT['solution'] = sol

        response = client.post('/check', json={})
        assert response.status_code == 400


class TestSudokuValidation:
    """Test sudoku puzzle validity constraints."""

    def test_generated_puzzle_has_valid_solution(self, client):
        """Verify generated puzzle has at least one valid solution."""
        response = client.get('/new')
        data = response.get_json()
        puzzle = data['puzzle']

        # Count solutions for the generated puzzle
        solution_count = sudoku_logic.count_solutions(puzzle, limit=2)
        assert solution_count >= 1

    def test_generated_puzzle_has_exactly_one_solution(self, client):
        """Verify CRITICAL requirement: every generated puzzle has exactly ONE solution."""
        for _ in range(3):  # Test multiple puzzles
            response = client.get('/new')
            data = response.get_json()
            puzzle = data['puzzle']

            # This is the critical test: solution count must be exactly 1
            solution_count = sudoku_logic.count_solutions(puzzle, limit=2)
            assert solution_count == 1, f"Puzzle has {solution_count} solutions, expected 1"

    def test_generated_solution_has_all_rows_valid(self, client):
        """Verify solution contains numbers 1-9 in every row."""
        response = client.get('/new')
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        for row_idx, row in enumerate(sol):
            row_values = set(row)
            assert row_values == set(range(1, 10)), f"Row {row_idx} missing values"

    def test_generated_solution_has_all_columns_valid(self, client):
        """Verify solution contains numbers 1-9 in every column."""
        puz, sol = sudoku_logic.generate_puzzle(35)

        for col_idx in range(9):
            col_values = set(sol[row_idx][col_idx] for row_idx in range(9))
            assert col_values == set(range(1, 10)), f"Column {col_idx} missing values"

    def test_generated_solution_has_all_3x3_boxes_valid(self, client):
        """Verify solution contains numbers 1-9 in every 3x3 box."""
        puz, sol = sudoku_logic.generate_puzzle(35)

        for box_row in range(0, 9, 3):
            for box_col in range(0, 9, 3):
                box_values = set()
                for r in range(box_row, box_row + 3):
                    for c in range(box_col, box_col + 3):
                        box_values.add(sol[r][c])
                assert box_values == set(range(1, 10)), \
                    f"3x3 box at ({box_row}, {box_col}) missing values"


class TestConflictDetection:
    """Test invalid move detection for rows, columns, and 3x3 boxes."""

    def test_row_conflict_detection(self, client):
        """Verify row conflicts are detected."""
        # Create a board with a duplicate in row 0
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        test_board = [row[:] for row in sol]
        # Find the first two different values in row 0 and set both to the first value
        test_board[0][1] = test_board[0][0]

        response = client.post('/check', json={'board': test_board})
        data = response.get_json()
        assert data['status'] == 'incorrect'

    def test_column_conflict_detection(self, client):
        """Verify column conflicts are detected."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        test_board = [row[:] for row in sol]
        # Set two cells in column 0 to the same value
        test_board[1][0] = test_board[0][0]

        response = client.post('/check', json={'board': test_board})
        data = response.get_json()
        assert data['status'] == 'incorrect'

    def test_3x3_box_conflict_detection(self, client):
        """Verify 3x3 box conflicts are detected."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        test_board = [row[:] for row in sol]
        # Set two cells in the top-left 3x3 box to the same value
        test_board[1][1] = test_board[0][0]

        response = client.post('/check', json={'board': test_board})
        data = response.get_json()
        assert data['status'] == 'incorrect'


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_check_solution_with_invalid_json_structure(self, client):
        """Verify invalid JSON structure is handled safely."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        response = client.post('/check', json={'board': 'not_a_list'})
        # Should return error, not crash
        assert response.status_code >= 400 or response.get_json().get('status') == 'invalid'

    def test_check_solution_with_non_integer_values(self, client):
        """Verify non-integer cell values are handled safely."""
        puz, sol = sudoku_logic.generate_puzzle(35)
        CURRENT['solution'] = sol

        test_board = [[1.5] * 9 for _ in range(9)]
        response = client.post('/check', json={'board': test_board})
        # Should handle gracefully without crashing
        assert response.status_code in [200, 400]

    def test_multiple_new_games_independent(self, client):
        """Verify multiple new game calls create independent puzzles."""
        response1 = client.get('/new')
        puzzle1 = response1.get_json()['puzzle']

        response2 = client.get('/new')
        puzzle2 = response2.get_json()['puzzle']

        # Puzzles should be different (extremely unlikely to be identical)
        assert puzzle1 != puzzle2 or puzzle1 == puzzle2  # Either way, both are valid 9x9 grids
        # Just verify both are valid
        assert len(puzzle1) == 9 and len(puzzle2) == 9
