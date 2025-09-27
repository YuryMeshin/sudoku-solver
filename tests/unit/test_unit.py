import json
from pathlib import Path
import pytest
from structures import CellStatus
from solver import SudokuSolver

DATA_PATH = Path(__file__).parent.parent / "unit" / "unit-tests.json"
with open(DATA_PATH) as f:
    CASES = json.load(f)

@pytest.mark.parametrize("case", CASES)
@pytest.mark.timeout(1)  # runtime limit: 1 second per test
def test(case):
    m, n, board, expected = case["m"], case["n"], case["board"], case.get("expected", None)
    solved = SudokuSolver((m, n), board)
    solved.solve()
    
    if expected: 
        assert solved.board.flatten() == expected
    else:
        assert all(cell.status == CellStatus.DETERMINED for cell in solved.board)
