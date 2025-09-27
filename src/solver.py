from typing import Optional
from enum import Enum


def map_index(coeffs: list[int], indices: list[int]) -> int:
    assert len(coeffs) == len(indices), "Given coeffs and indices size do not match"
    index = 0
    for i in range(len(coeffs)):
        index += coeffs[i] * indices[i]
    return index


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
        self.bitmask = bitmask if bitmask else default_bitmask

    @property
    def options(self) -> list[int]:
        return [i + 1 for i in range(self.slots) if self.bitmask & (1 << i)]

    def __str__(self) -> str:
        return ",".join([str(v) for v in self.options])
    
    @property
    def status(self) -> CellStatus:
        match self.bitmask.bit_count():
            case 0: return CellStatus.EMPTY
            case 1: return CellStatus.DETERMINED
            case _: return CellStatus.OPTIONAL

    def set(self, bitmask: int):
        default_bitmask = (1 << self.slots) - 1
        assert 0 <= bitmask <= default_bitmask, f"{bitmask=} must be between 0 and {default_bitmask}"
        self.bitmask = bitmask
    
    def __iter__(self):
        for v in self.options:
            yield v
    
    def check_mask(self, mask: int) -> bool:
        ''' Checks if given cell possible options belongs to certain set defined by its bitmask '''
        assert 0 < mask < (1 << self.slots), f"Incorrect {mask=} given"
        return (self.bitmask & ~mask) == 0


class SudokuGrid():
    ''' Sudoku grid with m x n block structure '''

    def __init__(self, m: int = 3, n: int = 3):
        
        self.m = m
        self.n = n
        self.slots = m * n
        self.grid = [GridCell(self.slots) for _ in range(self.slots ** 2)]
        self.areas = [[map_index([self.slots, 1], [i, j]) for j in range(self.slots)] for i in range(self.slots)]
        self.areas += [[map_index([self.slots, 1], [i, j]) for i in range(self.slots)] for j in range(self.slots)]
        self.areas += [[map_index([self.slots * m, n, self.slots, 1], [i, j, r, s]) for r in range(m) for s in range(n)] for i in range(n) for j in range(m)]
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
        
        rows = self.slots
        return "\n".join([" ".join([show_value(self.grid[map_index([rows, 1], [i, j])]) for j in range(rows)]) for i in range(rows)])

    def __repr__(self) -> str:
        cells = [str(cell) for cell in self.grid]
        mx = max(len(cell) for cell in cells)
        rows = ["-" * ((mx + 1) * self.slots + 1)]
        for i in range(self.slots):
            vals = [""]
            for j in range(self.slots):
                vals.append(str(self.grid[map_index([self.slots, 1], [i, j])]).rjust(mx))
            rows.append("|".join(vals) + "|")
            rows.append("-" * ((mx + 1) * self.slots + 1))
        return "\n".join(rows)

    @classmethod
    def read_board(cls, shape: tuple[int, int], board: str):
        cells = board.split(",")
        assert len(cells) == (shape[0] * shape[1]) ** 2, "Given board does not match to dimensions"
        grid = cls(shape[0], shape[1])
        for i, val in enumerate(cells):
            if val != ".":
                assert 1 <= int(val) <= grid.slots, f"Given value {val} is out of range"
                grid[i] = GridCell(grid.slots, 1 << (int(val) - 1))
        return grid
    
    def __setitem__(self, index: int, value: GridCell):
        self.grid[index] = value

    def __getitem__(self, index: int) -> GridCell:
        return self.grid[index]
    
    def __iter__(self):
        for cell in self.grid:
            yield cell

    def reduce_options(self):
        ''' Eliminates potential values in given grid cells '''

        for area in self.areas:
            masks = set(self.grid[i].bitmask for i in area)
            for mask in masks:
                # seeking all cells in area which options belong to certain subset described by bitmask
                masked = [i for i in area if self.grid[i].check_mask(mask)]
                if len(masked) == mask.bit_count():
                    # if we found exact number of cell for given subset 
                    # we should eliminate those values from remaing cells in this area
                    for j in area:
                        if not j in masked:
                            self.grid[j].set(self.grid[j].bitmask & ~mask)
                elif len(masked) > mask.bit_count():
                    # if we found more then contradiction found and nothing to do there
                    for j in area:
                        self.grid[j] = GridCell(self.slots, 0)
                    self._is_valid = False
    
    def simplify(self):
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
    
    def solve(self):
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