from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

# Valid difficulty levels
VALID_DIFFICULTIES = {'easy', 'medium', 'hard'}


def validate_board_data(board):
    """
    Validate Sudoku board data format and values.
    Returns (is_valid, error_message).
    """
    # Check if board is a list
    if not isinstance(board, list):
        return False, 'Board must be a list.'
    
    # Check for exactly 9 rows
    if len(board) != sudoku_logic.SIZE:
        return False, f'Board must have exactly {sudoku_logic.SIZE} rows.'
    
    # Check each row
    for i, row in enumerate(board):
        # Check if row is a list
        if not isinstance(row, list):
            return False, f'Row {i} must be a list.'
        
        # Check for exactly 9 columns
        if len(row) != sudoku_logic.SIZE:
            return False, f'Row {i} must have exactly {sudoku_logic.SIZE} columns.'
        
        # Check each cell value
        for j, value in enumerate(row):
            # Value must be an integer
            if not isinstance(value, int):
                return False, f'Cell [{i},{j}] must be an integer.'
            
            # Value must be 0 (empty) or 1-9
            if value != 0 and (value < 1 or value > 9):
                return False, f'Cell [{i},{j}] must be empty (0) or a digit 1-9.'
    
    return True, None


def validate_difficulty(difficulty_str):
    """
    Validate difficulty parameter.
    Returns (is_valid, clues_count, error_message).
    """
    if not isinstance(difficulty_str, str):
        return False, None, 'Difficulty must be a string.'
    
    difficulty_lower = difficulty_str.lower()
    
    if difficulty_lower not in VALID_DIFFICULTIES:
        return False, None, f'Difficulty must be one of: {", ".join(VALID_DIFFICULTIES)}.'
    
    difficulty_map = {
        'easy': 45,
        'medium': 35,
        'hard': 28
    }
    
    return True, difficulty_map[difficulty_lower], None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues = request.args.get('clues', 'medium')
    
    # Try to parse as numeric clue count first
    try:
        clues = int(clues)
        # Validate clue range
        if clues < 17 or clues > 81:
            return jsonify({'error': 'Clues must be between 17 and 81.'}), 400
    except (TypeError, ValueError):
        # Not numeric, try as difficulty name
        is_valid, clues_count, error = validate_difficulty(clues)
        if not is_valid:
            return jsonify({'error': error}), 400
        clues = clues_count
    
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'solution': solution})

@app.route('/check', methods=['POST'])
def check_solution():
    # Validate request has JSON content
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON.'}), 400
    
    data = request.json
    if data is None:
        return jsonify({'error': 'Request body is empty.'}), 400
    
    board = data.get('board')
    
    # Validate board data structure and values
    is_valid, error_msg = validate_board_data(board)
    if not is_valid:
        return jsonify({'error': error_msg}), 400
    
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    has_empty = False
    incorrect = []
    # Check all cells for correctness and completeness
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value == 0:
                has_empty = True
            elif value != solution[i][j]:
                incorrect.append([i, j])

    # If incorrect cells exist, return them regardless of board completion
    if incorrect:
        return jsonify({
            'status': 'incorrect',
            'message': 'There are incorrect entries.',
            'incorrect': incorrect
        })

    # If no incorrect cells but board is incomplete, report incompleteness
    if has_empty:
        return jsonify({
            'status': 'incomplete',
            'message': 'Puzzle is not complete yet.',
            'incomplete': True
        })

    # Board is complete and correct
    return jsonify({'status': 'solved', 'message': 'Congratulations! You solved the Sudoku!'})

if __name__ == '__main__':
    app.run(debug=True)