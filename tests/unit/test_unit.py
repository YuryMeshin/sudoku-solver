import json
from pathlib import Path
import pytest
from solver import SudokuSolver

# Load test cases from JSON
DATA_PATH = Path(__file__).parent.parent / "unit" / "unit-tests.json"
with open(DATA_PATH) as f:
    CASES = json.load(f)

@pytest.mark.parametrize("case", CASES)
@pytest.mark.timeout(1)  # runtime limit: 1 second per test
def test_b(case):
    m = case["m"]
    n = case["n"]
    board = case["board"]
    expected = case["expected"]
    solved = SudokuSolver((m, n), board)
    solved.solve()
    result = ''.join([str(cell.pop()) for cell in solved.board.grid])
    
    assert result == expected
