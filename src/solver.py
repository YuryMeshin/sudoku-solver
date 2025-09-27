from structures import CellStatus, GridCell, SudokuGrid

class SudokuSolver():
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self._board = board
        self.board = SudokuGrid.read_board(shape, board)
    
    def prune_cell_options(self) -> None:

        def get_subareas(area: list[int], mask: int) -> tuple[list[int], list[int]]:
            ''' Returns area cells indices which could be covered by certain set of values defined by its bitmask '''
            masked, unmasked = [], []
            for i in area:
                if self.board.grid[i].check_mask(mask):
                    masked.append(i)
                else:
                    unmasked.append(i)
            return masked, unmasked

        def update_cells(selection: list[int], exclude_mask: int) -> None:
            ''' Updates given selection cells by excluding some set defined by its bitmask  '''
            for i in selection:
                self.board.grid[i].set(self.board.grid[i].bitmask & ~exclude_mask)

        for area in self.board._areas:
            masks = set(self.board.grid[i].bitmask for i in area)
            if 0 in masks:
                self.board._is_valid = False
                return 
            for mask in masks:
                masked, unmasked = get_subareas(area, mask)
                if len(masked) == mask.bit_count():
                    update_cells(unmasked, mask) # eliminate appearances of set of values defined by its btimask
                elif len(masked) > mask.bit_count():
                    update_cells(area, (1 << self.board.slots) - 1) # if we found more matching cells then contradiction found
                    self.board._is_valid = False
    
    def narrow_possibilities(self) -> None:

        if not self.board.is_valid:
            return # there is nothing to do there, we have found a contradiction
        options = sum([len(cell.options) for cell in self.board.grid])
        while True:
            self.prune_cell_options()
            if not self.board.is_valid:
                return # there is nothing to do there, we have found a contradiction
            new_options = sum([len(x.options) for x in self.board.grid])
            if new_options == options:
                break
            options = new_options

    def copy(self) -> "SudokuSolver":
        return SudokuSolver(self.block_shape, self._board)
    
    def solve(self) -> None:
        self.narrow_possibilities()
        if not self.board.is_valid:
            return # There is nothing to do there, contradiction has found
        while not all(cell.status == CellStatus.DETERMINED for cell in self.board):
            for idx in range(len(self.board.grid)):
                if self.board[idx].status != CellStatus.DETERMINED:
                    cell_mask = 0
                    for v in self.board.grid[idx]:
                        new_solver = self.copy()
                        new_solver.board[idx] = GridCell(new_solver.board.slots, 1 << (v - 1))
                        new_solver.narrow_possibilities()
                        if new_solver.board.is_valid:
                            if all(cell.status == CellStatus.DETERMINED for cell in new_solver.board):
                                self.board = new_solver.board
                                return
                            cell_mask += 1 << (v - 1)
                    self.board[idx] = GridCell(self.board.slots, cell_mask)
                    self.narrow_possibilities()

if __name__ == '__main__':
    sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,1")
    sl.solve()
    print(sl.board)
    print(repr(sl.board))
