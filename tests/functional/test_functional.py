from solver import SudokuSolver

def test_board():
    try:
        sl = SudokuSolver((3, 3), '345........6..1...8.1.7.2....3..8...6......5...419.6.....6.51.3......7.......4...')
    except Exception as e:
        assert False, f"Sudoku solving workflow test failed with: {e}"
