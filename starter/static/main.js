// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const DIFFICULTY_CLUES = {
  easy: 45,
  medium: 35,
  hard: 28,
};
let puzzle = [];
let solution = [];
let timerInterval = null;
let elapsedSeconds = 0;
let timerRunning = false;
let hintsUsed = 0;
const hintedCells = new Set();
const LEADERBOARD_STORAGE_KEY = 'sudoku-top10-leaderboard';

function formatTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerEl = document.getElementById('timer');
  if (timerEl) {
    timerEl.textContent = formatTime(elapsedSeconds);
  }
}

function stopTimer() {
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  timerRunning = false;
}

function startTimer() {
  stopTimer();
  elapsedSeconds = 0;
  updateTimerDisplay();
  timerRunning = true;
  timerInterval = setInterval(() => {
    if (!timerRunning) {
      return;
    }
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function applyTheme(theme) {
  const body = document.body;
  const isDark = theme === 'dark';
  body.classList.toggle('dark-theme', isDark);
  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.textContent = isDark ? 'Light mode' : 'Dark mode';
  }
}

function loadTheme() {
  const savedTheme = localStorage.getItem('sudoku-theme') || 'light';
  applyTheme(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.body.classList.contains('dark-theme') ? 'dark' : 'light';
  const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('sudoku-theme', nextTheme);
  applyTheme(nextTheme);
}

function getSelectedDifficulty() {
  const difficulty = document.getElementById('difficulty').value;
  return DIFFICULTY_CLUES[difficulty] || DIFFICULTY_CLUES.medium;
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        validateImmediateMove(e.target);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz, solvedBoard = []) {
  puzzle = puz;
  hintedCells.clear();
  if (Array.isArray(solvedBoard) && solvedBoard.length === SIZE) {
    solution = solvedBoard.map((row) => [...row]);
  } else {
    solution = [];
  }
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
  clearMoveValidation();
  startTimer();
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function clearMoveValidation() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < inputs.length; i++) {
    const inp = inputs[i];
    const key = `${inp.dataset.row}:${inp.dataset.col}`;

    if (hintedCells.has(key)) {
      inp.className = 'sudoku-cell prefilled hinted';
      continue;
    }

    if (inp.disabled) {
      inp.className = 'sudoku-cell prefilled';
      continue;
    }

    inp.className = 'sudoku-cell';
  }

  const msg = document.getElementById('message');
  msg.style.color = '#d32f2f';
  msg.innerText = '';
}

function validateImmediateMove(input) {
  if (input.disabled || input.value === '') {
    clearMoveValidation();
    return;
  }

  const row = parseInt(input.dataset.row, 10);
  const col = parseInt(input.dataset.col, 10);
  const value = parseInt(input.value, 10);
  const board = getBoardFromInputs();
  const invalidCells = new Set();

  if (solution.length === SIZE && solution[row] && solution[row][col] !== value) {
    invalidCells.add(row * SIZE + col);
  }

  // Check the current row.
  for (let c = 0; c < SIZE; c++) {
    if (c !== col && board[row][c] === value) {
      invalidCells.add(row * SIZE + c);
    }
  }

  // Check the current column.
  for (let r = 0; r < SIZE; r++) {
    if (r !== row && board[r][col] === value) {
      invalidCells.add(r * SIZE + col);
    }
  }

  // Check the current 3x3 box.
  const boxRow = Math.floor(row / 3) * 3;
  const boxCol = Math.floor(col / 3) * 3;
  for (let r = boxRow; r < boxRow + 3; r++) {
    for (let c = boxCol; c < boxCol + 3; c++) {
      if ((r !== row || c !== col) && board[r][c] === value) {
        invalidCells.add(r * SIZE + c);
      }
    }
  }

  const msg = document.getElementById('message');
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    const key = `${inp.dataset.row}:${inp.dataset.col}`;
    if (inp.disabled) {
      if (hintedCells.has(key)) {
        inp.className = 'sudoku-cell prefilled hinted';
      } else {
        inp.className = 'sudoku-cell prefilled';
      }
      continue;
    }

    if (invalidCells.has(idx)) {
      inp.className = 'sudoku-cell invalid';
    } else {
      inp.className = 'sudoku-cell';
    }
  }

  if (invalidCells.size > 0) {
    invalidCells.add(row * SIZE + col);
    const invalidInput = inputs[row * SIZE + col];
    invalidInput.className = 'sudoku-cell invalid';
    msg.style.color = '#d32f2f';
    msg.innerText = 'Invalid move';
    return;
  }

  msg.innerText = '';
}

function applyHint() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const emptyInputs = [];

  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (!inp.disabled && inp.value === '') {
      emptyInputs.push(inp);
    }
  }

  if (emptyInputs.length === 0) {
    const msg = document.getElementById('message');
    msg.style.color = '#ed6c02';
    msg.innerText = 'No empty cells left.';
    return;
  }

  const target = emptyInputs[Math.floor(Math.random() * emptyInputs.length)];
  const row = parseInt(target.dataset.row, 10);
  const col = parseInt(target.dataset.col, 10);
  const correctValue = solution[row][col];

  if (!Number.isInteger(correctValue)) {
    const msg = document.getElementById('message');
    msg.style.color = '#d32f2f';
    msg.innerText = 'Unable to provide a hint right now.';
    return;
  }

  clearMoveValidation();
  hintsUsed += 1;
  target.value = correctValue;
  target.disabled = true;
  hintedCells.add(`${row}:${col}`);
  target.className = 'sudoku-cell prefilled hinted';

  const msg = document.getElementById('message');
  msg.style.color = '#2e7d32';
  msg.innerText = 'Hint used';
}

function getLeaderboardEntries() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    const parsed = raw ? JSON.parse(raw) : [];
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
}

function saveScoreToLeaderboard(player, difficulty, timeSeconds, hintCount) {
  const entries = getLeaderboardEntries();
  entries.push({
    player,
    timeSeconds,
    time: formatTime(timeSeconds),
    difficulty,
    hintsUsed: hintCount,
  });

  entries.sort((a, b) => {
    if (a.timeSeconds !== b.timeSeconds) {
      return a.timeSeconds - b.timeSeconds;
    }
    return a.hintsUsed - b.hintsUsed;
  });

  const topTen = entries.slice(0, 10);
  localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(topTen));
  updateLeaderboardDisplay();
}

function updateLeaderboardDisplay() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  if (!leaderboardBody) {
    return;
  }

  const entries = getLeaderboardEntries();
  leaderboardBody.innerHTML = '';

  if (!entries.length) {
    const emptyRow = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 5;
    cell.textContent = 'No scores yet';
    emptyRow.appendChild(cell);
    leaderboardBody.appendChild(emptyRow);
    return;
  }

  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    const rankCell = document.createElement('td');
    const playerCell = document.createElement('td');
    const timeCell = document.createElement('td');
    const difficultyCell = document.createElement('td');
    const hintsCell = document.createElement('td');

    rankCell.textContent = String(index + 1);
    playerCell.textContent = entry.player || 'Anonymous';
    timeCell.textContent = entry.time || formatTime(entry.timeSeconds || 0);
    difficultyCell.textContent = entry.difficulty || 'Medium';
    hintsCell.textContent = String(entry.hintsUsed || 0);

    row.append(rankCell, playerCell, timeCell, difficultyCell, hintsCell);
    leaderboardBody.appendChild(row);
  });
}

async function newGame() {
  hintsUsed = 0;
  hintedCells.clear();
  const clues = getSelectedDifficulty();
  const res = await fetch(`/new?clues=${clues}`);
  const data = await res.json();
  renderPuzzle(data.puzzle, data.solution);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');

  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  if (data.status === 'solved') {
    msg.style.color = '#2e7d32';
    msg.innerText = data.message;
    stopTimer();

    const playerName = window.prompt('Congratulations! Enter your name for the leaderboard:', 'Player');
    if (playerName !== null) {
      const trimmedName = (playerName || '').trim();
      if (trimmedName) {
        const difficultyName = document.getElementById('difficulty')?.value || 'medium';
        saveScoreToLeaderboard(trimmedName, difficultyName, elapsedSeconds, hintsUsed);
      }
    }
    return;
  }

  if (data.status === 'incomplete') {
    msg.style.color = '#ed6c02';
    msg.innerText = data.message;
    return;
  }

  if (data.status === 'incorrect') {
    // Clear previous move validation
    clearMoveValidation();
    
    msg.style.color = '#d32f2f';
    msg.innerText = data.message;
    
    // Highlight incorrect cells from backend response
    if (Array.isArray(data.incorrect) && data.incorrect.length > 0) {
      const incorrectSet = new Set();
      data.incorrect.forEach(([row, col]) => {
        incorrectSet.add(row * SIZE + col);
      });
      
      for (let idx = 0; idx < inputs.length; idx++) {
        const inp = inputs[idx];
        if (incorrectSet.has(idx)) {
          inp.className = 'sudoku-cell incorrect';
        }
      }
    }
    return;
  }

  msg.style.color = '#d32f2f';
  msg.innerText = data.message || 'Invalid board';
}

// Wire buttons
window.addEventListener('load', () => {
  loadTheme();
  updateTimerDisplay();
  updateLeaderboardDisplay();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint-button').addEventListener('click', applyHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('difficulty').addEventListener('change', () => {
    hintsUsed = 0;
    newGame();
  });
  // initialize
  newGame();
});