from typing import Optional
from enum import Enum

def int2set(val: int, bits: int) -> set[int]:
    return set([i + 1 for i in range(bits) if val & (1 << i)])


def map_index(coeffs: list[int], indices: list[int]) -> int:
    assert len(coeffs) == len(indices), 'Given coeffs and indices size do not match'
    index = 0
    for i in range(len(coeffs)):
        index += coeffs[i] * indices[i]
    return index


class CellStatus(Enum):
    EMPTY = 0
    DETERMINED = 1
    OPTIONAL = 2


class GridCell():
    ''' Cell for sudoku grid'''

    def __init__(self, slots: int, value: Optional[int] = None):
        assert 1 < slots < 17, f'{slots=} must be between 2 and 16 exclusively' 
        if value:
            assert 0 <= value < (1 << slots), f'{value=} must be between 0 and {(1 << slots) - 1}'
        self.slots = slots
        self.value = value if value else (1 << slots) - 1

    @property
    def options(self) -> list[int]:
        return [i + 1 for i in range(self.slots) if self.value & (1 << i)]

    def __str__(self) -> str:
        return ','.join([str(v) for v in self.options])
    
    @property
    def status(self) -> CellStatus:
        match len(self.options):
            case 0: return CellStatus.EMPTY
            case 1: return CellStatus.DETERMINED
            case _: return CellStatus.OPTIONAL

    def set(self, value: int):
        self.value = value
    
    def __iter__(self):
        for v in self.options:
            yield v
    
    def check_mask(self, mask: int) -> bool:
        assert 0 < mask < (1 << self.slots), f'Incorrect {mask=} given'
        return (self.value & ~mask) == 0


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
    
    def __str__(self) -> str:

        def show_value(cell: GridCell) -> str:
            match cell.status:
                case CellStatus.EMPTY: return '#'
                case CellStatus.DETERMINED: return str(cell)
                case _: return '.'
        
        rows = self.slots
        return '\n'.join([' '.join([show_value(self.grid[map_index([rows, 1], [i, j])]) for j in range(rows)]) for i in range(rows)])

    def __repr__(self) -> str:
        cells = [str(cell) for cell in self.grid]
        mx = max(len(cell) for cell in cells)
        rows = ['-' * ((mx + 1) * self.slots + 1)]
        for i in range(self.slots):
            vals = ['']
            for j in range(self.slots):
                vals.append(str(self.grid[map_index([self.slots, 1], [i, j])]).rjust(mx))
            rows.append('|'.join(vals) + '|')
            rows.append('-' * ((mx + 1) * self.slots + 1))
        return '\n'.join(rows)

    @classmethod
    def read_board(cls, shape: tuple[int, int], board: str):
        cells = board.split(',')
        assert len(cells) == (shape[0] * shape[1]) ** 2, 'Given board does not match to dimensions'
        grid = cls(shape[0], shape[1])
        for i, val in enumerate(cells):
            if val != '.':
                assert 1 <= int(val) <= grid.slots, f'Given value {val} is out of range'
                grid[i] = GridCell(grid.slots, 1 << (int(val) - 1))
        return grid
    
    @property
    def defined(self) -> list[bool]:
        return [x.status == CellStatus.DETERMINED for x in self.grid]
    
    @property
    def is_valid(self):

        def validate_area(area: list[int]) -> bool:
            vals = set().union(*[set(self.grid[i].options) for i in area])
            exact_vals = [str(self.grid[i]) for i in area if self.grid[i].status == CellStatus.DETERMINED]
            return (vals == set(range(1, self.slots + 1))) & (len(exact_vals) == len(set(exact_vals)))
        
        return all([validate_area(area) for area in self.areas])

    def __setitem__(self, index: int, value: GridCell):
        self.grid[index] = value

    def __getitem__(self, index: int) -> GridCell:
        return self.grid[index]

    def reduce_options(self):
        for area in self.areas:
            for mask in range(1, 1 << self.slots):
                masked = [i for i in area if self.grid[i].check_mask(mask)]
                if len(masked) == mask.bit_count():
                    for j in area:
                        if not j in masked:
                            self.grid[j].set(self.grid[j].value & ~mask)
    
    def simplify(self):
        options = sum([len(x.options) for x in self.grid])
        while True:
            self.reduce_options()
            new_options = sum([len(x.options) for x in self.grid])
            if new_options == options:
                break
            options = new_options
    
    def flatten(self) -> str:
        return ','.join([str(cell) if cell.status == CellStatus.DETERMINED else '.' for cell in self.grid])
        
class SudokuSolver():
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self.board = SudokuGrid.read_board(shape, board)
    
    def solve(self):
        self.board.simplify()
        while not all(self.board.defined):
            for idx in range(len(self.board.grid)):
                if self.board.defined[idx] == False:
                    value = 0
                    for v in self.board.grid[idx]:
                        new_grid = SudokuGrid.read_board(self.block_shape, self.board.flatten())
                        new_grid[idx] = GridCell(new_grid.slots, 1 << (v - 1))
                        new_grid.simplify()
                        if new_grid.is_valid:
                            if all(new_grid.defined):
                                self.board = new_grid
                                return
                            value += 1 << (v - 1)
                    self.board[idx] = GridCell(self.board.slots, value)
                    self.board.simplify()

if __name__ == '__main__':
    sl = SudokuSolver((3, 3), "4,.,.,.,.,.,.,1,.,.,7,.,.,.,.,.,.,.,.,.,1,.,6,.,.,3,.,2,.,6,8,.,.,1,4,.,.,3,9,4,.,.,2,.,.,.,.,.,.,7,.,.,9,3,.,.,.,.,.,8,4,2,.,3,.,.,.,.,.,.,8,9,8,.,4,.,.,2,.,.,.")
    sl.solve()
    print(sl.board)