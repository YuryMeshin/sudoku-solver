from structures import CellStatus, GridCell, SudokuGrid, BoardStatus


class SudokuSolver():
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self.board = SudokuGrid.read_board(shape, board)
        self.aux_board = self.board.copy()

    def restore_aux_board(self) -> None:
        self.aux_board = self.board.copy()
    
    def prune_cell_options(self, aux: bool = False) -> None:

        def get_subareas(area: list[int], mask: int) -> tuple[list[int], list[int]]:
            ''' Returns area cells indices which could be covered by certain set of values defined by its bitmask '''
            masked, unmasked = [], []
            for i in area:
                if board.grid[i].check_mask(mask):
                    masked.append(i)
                else:
                    unmasked.append(i)
            return masked, unmasked

        def update_cells(selection: list[int], exclude_mask: int) -> None:
            ''' Updates given selection cells by excluding some set defined by its bitmask  '''
            for i in selection:
                board.grid[i].set(board.grid[i].bitmask & ~exclude_mask)
        
        board = self.aux_board if aux else self.board

        for area in board._areas:
            masks = set(board.grid[i].bitmask for i in area)
            if 0 in masks:
                board._is_valid = False
                board._status = BoardStatus.CONTRADICTION
                return 
            for mask in masks:
                masked, unmasked = get_subareas(area, mask)
                if len(masked) == mask.bit_count():
                    update_cells(unmasked, mask) # eliminate appearances of set of values defined by its btimask
                elif len(masked) > mask.bit_count():
                    update_cells(area, (1 << board.slots) - 1) # if we found more matching cells then contradiction found
                    board._is_valid = False
                    board._status = BoardStatus.CONTRADICTION
    
    def narrow_possibilities(self, aux: bool = False) -> None:

        board = self.aux_board if aux else self.board
        if not board.is_valid:
            return # there is nothing to do there, we have found a contradiction
        
        options = sum([len(cell.options) for cell in board.grid])
        while True:
            self.prune_cell_options(aux)
            if not board.is_valid:
                return # there is nothing to do there, we have found a contradiction
            new_options = sum([len(x.options) for x in board.grid])
            if new_options == options:
                break
            options = new_options
    
    def test_cell(self, cell_idx: int, value: int) -> BoardStatus:
        self.aux_board[cell_idx] = GridCell(self.board.slots, 1 << (value - 1))
        self.narrow_possibilities(aux=True)
        if self.aux_board.is_valid:
            if all(cell.status == CellStatus.DETERMINED for cell in self.aux_board):
                response = BoardStatus.SOLVED
            else:
                response = BoardStatus.OPTIONAL
                self.restore_aux_board()
        else:
            response = BoardStatus.CONTRADICTION
            self.restore_aux_board()
        
        return response
    
    def solve(self) -> None:
        self.narrow_possibilities()
        if not self.board.is_valid:
            return # There is nothing to do there, contradiction has found
        
        while not all(cell.status == CellStatus.DETERMINED for cell in self.board):
            for idx in range(len(self.board.grid)):
                if self.board[idx].status != CellStatus.DETERMINED:
                    cell_mask = 0
                    for v in self.board.grid[idx]:
                        response = self.test_cell(idx, v)
                        match response:
                            case BoardStatus.SOLVED:
                                self.board = self.aux_board.copy()
                                return
                            case BoardStatus.OPTIONAL:
                                cell_mask += 1 << (v - 1)
                            
                    self.board[idx] = GridCell(self.board.slots, cell_mask)
                    self.restore_aux_board()
                    self.narrow_possibilities()

if __name__ == '__main__':
    sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,1")
    sl.solve()
    print(sl.board)
