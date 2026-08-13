from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues = request.args.get('clues', 35)
    try:
        clues = int(clues)
    except (TypeError, ValueError):
        clues = 35
    if clues < 17:
        clues = 17
    if clues > 81:
        clues = 81
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle, 'solution': solution})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    if board is None or len(board) != sudoku_logic.SIZE:
        return jsonify({'status': 'invalid', 'message': 'Board is invalid.'}), 400

    for i in range(sudoku_logic.SIZE):
        if len(board[i]) != sudoku_logic.SIZE:
            return jsonify({'status': 'invalid', 'message': 'Board is invalid.'}), 400

    has_empty = False
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value == 0:
                has_empty = True
                continue
            if value != solution[i][j]:
                incorrect.append([i, j])

    if has_empty:
        return jsonify({'status': 'incomplete', 'message': 'Puzzle is not complete yet.'})

    if incorrect:
        return jsonify({'status': 'incorrect', 'message': 'There are incorrect entries.'})

    return jsonify({'status': 'solved', 'message': 'Congratulations! You solved the Sudoku!'})

if __name__ == '__main__':
    app.run(debug=True)