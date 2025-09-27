from typing import Optional, Iterator
from enum import Enum


def get_block_indices(left_corner: tuple[int, int], block_shape: tuple[int, int], side_len: int) -> list[int]:
    ''' Returns flattened block p x q with left corner (x, y) in square grid of side_len x side_len '''
    
    assert all(0 <= left_corner[i] <= side_len - block_shape[i] for i in range(2)) and (min(block_shape) >= 1), \
        f"Incorrect input {left_corner=} {block_shape=} {side_len=}"

    offset = left_corner[0] * side_len + left_corner[1]
    return [offset + r * side_len + c for r in range(block_shape[0]) for c in range(block_shape[1])]
 

class CellStatus(Enum):
    EMPTY = 0
    DETERMINED = 1
    OPTIONAL = 2


class GridCell():
    ''' Cell for sudoku grid, represented as bitmask of given slots size '''

    def __init__(self, slots: int, bitmask: Optional[int] = None):
        assert 1 < slots < 17, f"{slots=} must be between 2 and 16 exclusively" 
        default_bitmask = (1 << slots) - 1
        if not (bitmask is None):
            assert 0 <= bitmask <= default_bitmask, f"{bitmask=} must be between 0 and {default_bitmask}"
        self.slots = slots
        self._bitmask = bitmask if bitmask else default_bitmask
        self._options = self._get_options()

    def _get_options(self) -> list[int]:
        ''' Extracts 1-based values from bitmask '''
        return [i + 1 for i in range(self.slots) if self._bitmask & (1 << i)]

    @property
    def options(self) -> list[int]:
        return self._options

    @property
    def bitmask(self) -> int:
        return self._bitmask

    def __str__(self) -> str:
        return ",".join([str(v) for v in self.options])
    
    @property
    def status(self) -> CellStatus:
        match self._bitmask.bit_count():
            case 0: return CellStatus.EMPTY
            case 1: return CellStatus.DETERMINED
            case _: return CellStatus.OPTIONAL

    def set(self, bitmask: int) -> None:
        default_bitmask = (1 << self.slots) - 1
        assert 0 <= bitmask <= default_bitmask, f"{bitmask=} must be between 0 and {default_bitmask}"
        self._bitmask = bitmask
        self._options = self._get_options()
    
    def __iter__(self) -> Iterator[int]:
        return iter(self.options)
    
    def check_mask(self, mask: int) -> bool:
        ''' Checks if given cell possible options belongs to certain set defined by its bitmask '''
        assert 0 < mask < (1 << self.slots), f"Incorrect {mask=} given"
        return (self._bitmask & ~mask) == 0


class SudokuGrid():
    ''' Sudoku grid with m x n block structure '''

    def __init__(self, m: int = 3, n: int = 3):
        
        self.m = m
        self.n = n
        self.slots = m * n
        self.grid: list[GridCell] = [GridCell(self.slots) for _ in range(self.slots ** 2)]
        
        self._areas: list[list[int]] = []
        
        # add rows
        for i in range(self.slots):
            self._areas.append(get_block_indices((i, 0), (1, self.slots), self.slots))
        
        # add columns
        for i in range(self.slots):
            self._areas.append(get_block_indices((0, i), (self.slots, 1), self.slots))
        
        # add blocks
        for i in range(self.n):
            for j in range(self.m):
                self._areas.append(get_block_indices((i * self.m, j * self.n), (self.m, self.n), self.slots))

        self._is_valid = True
    
    @property
    def is_valid(self) -> bool:
        return self._is_valid
    
    def __str__(self) -> str:

        def show_value(cell: GridCell) -> str:
            match cell.status:
                case CellStatus.EMPTY: return "#"
                case CellStatus.DETERMINED: return str(cell)
                case _: return "."
        
        rows = [get_block_indices((i, 0), (1, self.slots), self.slots) for i in range(self.slots)]
        return "\n".join([" ".join([show_value(self.grid[i]) for i in row]) for row in rows])

    def __repr__(self) -> str:
        cells = [str(cell) for cell in self.grid]
        mx = max(len(cell) for cell in cells)
        lines = ["-" * ((mx + 1) * self.slots + 1)]
        rows = [get_block_indices((i, 0), (1, self.slots), self.slots) for i in range(self.slots)]
        for row in rows:
            vals = [""]
            for i in row:
                vals.append(str(self.grid[i]).rjust(mx))
            lines.append("|".join(vals) + "|")
            lines.append("-" * ((mx + 1) * self.slots + 1))
        return "\n".join(lines)

    @classmethod
    def read_board(cls, shape: tuple[int, int], board: str) -> "SudokuGrid":
        cells = board.split(",")
        assert len(cells) == (shape[0] * shape[1]) ** 2, "Given board does not match to dimensions"
        grid = cls(shape[0], shape[1])
        for i, val in enumerate(cells):
            if val != ".":
                assert 1 <= int(val) <= grid.slots, f"Given value {val} is out of range"
                grid[i] = GridCell(grid.slots, 1 << (int(val) - 1))
        return grid
    
    def __setitem__(self, index: int, value: GridCell) -> None:
        self.grid[index] = value

    def __getitem__(self, index: int) -> GridCell:
        return self.grid[index]
    
    def __iter__(self) -> Iterator[GridCell]:
        return iter(self.grid)

    def reduce_options(self) -> None:
        ''' Eliminates potential values in given grid cells '''

        def get_subareas(area: list[int], mask: int) -> tuple[list[int], list[int]]:
            ''' Returns area cells indices which could be covered by certain set of values defined by its bitmask '''
            masked, unmasked = [], []
            for i in area:
                if self.grid[i].check_mask(mask):
                    masked.append(i)
                else:
                    unmasked.append(i)
            return masked, unmasked

        def update_cells(selection: list[int], exclude_mask: int) -> None:
            ''' Updates given selection cells by excluding some set defined by its bitmask  '''
            for i in selection:
                self.grid[i].set(self.grid[i].bitmask & ~exclude_mask)

        for area in self._areas:
            masks = set(self.grid[i].bitmask for i in area)
            if 0 in masks:
                self._is_valid = False
                return 
            for mask in masks:
                masked, unmasked = get_subareas(area, mask)
                if len(masked) == mask.bit_count():
                    update_cells(unmasked, mask) # eliminate appearances of set of values defined by its btimask
                elif len(masked) > mask.bit_count():
                    update_cells(area, (1 << self.slots) - 1) # if we found more matching cells then contradiction found
                    self._is_valid = False
    
    def simplify(self) -> None:
        ''' Reducing potential grid cells options as long as possible '''
        if not self.is_valid:
            return # there is nothing to do there, we have found a contradiction
        options = sum([len(cell.options) for cell in self.grid])
        while True:
            self.reduce_options()
            if not self.is_valid:
                return # there is nothing to do there, we have found a contradiction
            new_options = sum([len(x.options) for x in self.grid])
            if new_options == options:
                break
            options = new_options
    
    def flatten(self) -> str:
        if self.is_valid:
            return ",".join([str(cell) if cell.status == CellStatus.DETERMINED else "." for cell in self.grid])
        else:
            return ""

     
class SudokuSolver():
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self.board = SudokuGrid.read_board(shape, board)
    
    def solve(self) -> None:
        self.board.simplify()
        if not self.board.is_valid:
            return # There is nothing to do there, contradiction has found
        while not all(cell.status == CellStatus.DETERMINED for cell in self.board):
            for idx in range(len(self.board.grid)):
                if self.board[idx].status != CellStatus.DETERMINED:
                    cell_mask = 0
                    for v in self.board.grid[idx]:
                        new_grid = SudokuGrid.read_board(self.block_shape, self.board.flatten())
                        new_grid[idx] = GridCell(new_grid.slots, 1 << (v - 1))
                        new_grid.simplify()
                        if new_grid.is_valid:
                            if all(cell.status == CellStatus.DETERMINED for cell in new_grid):
                                self.board = new_grid
                                return
                            cell_mask += 1 << (v - 1)
                    self.board[idx] = GridCell(self.board.slots, cell_mask)
                    self.board.simplify()

if __name__ == '__main__':
    sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,1")
    sl.solve()
    print(sl.board)
    print(repr(sl.board))
