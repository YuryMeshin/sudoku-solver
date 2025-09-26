from solver import SudokuSolver

def test_board():
    try:
        sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,1")
    except Exception as e:
        assert False, f"Sudoku solving workflow test failed with: {e}"
