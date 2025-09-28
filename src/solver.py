from structures import CellStatus, GridCell, SudokuGrid, BoardStatus


class SudokuSolver():
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self.board = SudokuGrid.read_board(shape, board)
        self.board.narrow_possibilities()
    
    def test_cell(self, cell_idx: int, value: int) -> BoardStatus:
        
        with self.board.cloned_board() as draft:
            draft[cell_idx] = GridCell(self.board.slots, 1 << (value - 1))
            draft.update_status()
            draft.narrow_possibilities()
            response = draft.status
            if response == BoardStatus.SOLVED:
                self.board = draft
            return response
    
    def solve(self) -> None:
        if self.board.status == BoardStatus.CONTRADICTION:
            return # There is nothing to do there, contradiction has found
        
        while self.board.status == BoardStatus.OPTIONAL:
            for idx in range(len(self.board.grid)):
                if self.board[idx].status != CellStatus.DETERMINED:
                    cell_mask = 0
                    for v in self.board.grid[idx]:
                        response = self.test_cell(idx, v)
                        match response:
                            case BoardStatus.SOLVED:
                                return
                            case BoardStatus.OPTIONAL:
                                cell_mask += 1 << (v - 1)
                            
                    self.board[idx] = GridCell(self.board.slots, cell_mask)
                    self.board.narrow_possibilities()

if __name__ == '__main__':
    sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,1")
    sl.solve()
    print(sl.board)
    print(sl.board.status)
