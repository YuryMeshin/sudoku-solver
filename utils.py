from typing import Optional

class SudokuGrid():
    '''
    Sudoku grid with m*n unique elements and user defined segmentation \n
    If segmentation is undefined then standard block structure would be applied
    '''

    def __init__(self, m: int = 3, n: int = 3, segments: Optional[list[list[list[int]]]] = None):

        def get_subset(i: int) -> set[int]:
            bits = '{:9b}'.format(i)
            return set([_ + 1 for _ in range(9) if bits[_] == '1'])

        total = m * n
        self.dimensions = (total, total)
        self.values = [_ for _ in range(1, total + 1)]
        self.grid = [set(self.values) for _ in range(total ** 2)]
        self.areas = [[total * i + j for j in range(total)] for i in range(total)]
        self.areas += [[total * i + j for i in range(total)] for j in range(total)]
        if segments:
            assert len(segments) == total, f'Expected exactly {total} segments'
            assert all([len(s) == total for s in segments]), \
                f'Every segment must contain exactly {total} cells'
            idx = [[total * x[0] + x[1] for x in s] for s in segments]
            assert sorted(sum(idx, [])) == [_ for _ in range(total ** 2)], \
                'All the segments must cover the entire grid'
            self.areas += idx
        else:
            self.areas += [[total * m * i + n * j + total * r + s for r in range(m) for s in range(n)]  \
                           for i in range(n) for j in range(m)]
        self.subsets = {i: get_subset(i) for i in range(1, 2 ** total)}
    
    def __str__(self) -> str:

        def show_value(val: set[int]) -> str:
            if len(val) == 1:
                return str(list(val)[0])
            return '·'
        
        rows = self.dimensions[0]
        return '\n'.join([' '.join([show_value(self.grid[rows * i + j]) for j in range(rows)]) \
                          for i in range(rows)])

    def __repr__(self) -> str:
        mx = max(len(x) for x in self.grid) + 1
        d = self.dimensions[0]
        rows = []
        for i in range(d):
            vals = []
            for j in range(d):
                vals += [''.join(str(x) for x in sorted(self.grid[i * d + j])).rjust(mx)]
            rows.append('|'.join(vals))
            rows.append('-' * ((mx + 1) * d - 1))
        return '\n'.join(rows)
    
    @property
    def defined(self) -> list[bool]:
        return [len(x) == 1 for x in self.grid]
    
    @property
    def is_valid(self):

        def validate_area(area: list[int]) -> bool:
            vals = set().union(*[self.grid[i] for i in area])
            exact_vals = [list(self.grid[i])[0] for i in area if self.defined[i]]
            return (vals == set(self.values)) & (len(exact_vals) == len(set(exact_vals)))
        
        return all([validate_area(area) for area in self.areas])

    def set_values(self, row: int, col: int, values: set[int]):
        self.grid[row * self.dimensions[0] + col] = values

    def reduce_options(self):
        for area in self.areas:
            for idx in self.subsets:
                test_set = self.subsets[idx]
                test_idx = [i for i in area if not (self.grid[i] <= test_set)]
                if len(test_idx) == (self.dimensions[0] - len(test_set)):
                    for j in test_idx:
                        self.grid[j] -= test_set
    
    def simplify(self):
        options = sum([len(x) for x in self.grid])
        while True:
            self.reduce_options()
            new_options = sum([len(x) for x in self.grid])
            if new_options == options:
                break
            options = new_options


class SudokuSolver():
    '''Nuff said, just Sudoku solver'''

    def __init__(self, shape: tuple[int, int], board: list[list[str]], \
                 segments: Optional[list[list[list[int]]]] = None):
        assert len(board) == shape[0] * shape[1], \
            "Given board rows count doesn't match to dimensions"
        assert all([len(b) == shape[0] * shape[1] for b in board]), \
            "Given board columns count doesn't match to dimensions"
        self.grid = SudokuGrid(shape[0], shape[1], segments)
        for i in range(self.grid.dimensions[0]):
            for j in range(self.grid.dimensions[0]):
                if board[i][j] != '.':
                    assert (val := int(board[i][j])) in self.grid.values, f'Given value {val} is out of range'
                    self.grid.set_values(i, j, set([val]))
    
    def solve(self):
        self.grid.simplify()
        while not all(self.grid.defined):
            for idx in range(len(self.grid.grid)):
                if self.grid.defined[idx] == False:
                    row, col = idx // self.grid.dimensions[0], idx % self.grid.dimensions[0]
                    good_set = set()
                    for v in self.grid.grid[idx]:
                        new_grid = SudokuGrid()
                        for i in range(len(self.grid.grid)):
                            new_grid.grid[i] = self.grid.grid[i].copy()
                        new_grid.set_values(row, col, set([v]))
                        new_grid.simplify()
                        if new_grid.is_valid:
                            good_set |= {v}
                    self.grid.set_values(row, col, good_set)
                    self.grid.simplify()

if __name__ == '__main__':
    boards = [
        [
            ['3', '4', '5', '.', '.', '.', '.', '.', '.'], 
            ['.', '.', '6', '.', '.', '1', '.', '.', '.'], 
            ['8', '.', '1', '.', '7', '.', '2', '.', '.'], 
            ['.', '.', '3', '.', '.', '8', '.', '.', '.'], 
            ['6', '.', '.', '.', '.', '.', '.', '5', '.'], 
            ['.', '.', '4', '1', '9', '.', '6', '.', '.'], 
            ['.', '.', '.', '6', '.', '5', '1', '.', '3'], 
            ['.', '.', '.', '.', '.', '.', '7', '.', '.'], 
            ['.', '.', '.', '.', '.', '4', '.', '.', '.']
            ],
        [
            ['4', '.', '.', '.', '.', '.', '.', '1', '.'], 
            ['.', '7', '.', '.', '.', '.', '.', '.', '.'], 
            ['.', '.', '1', '.', '6', '.', '.', '3', '.'], 
            ['2', '.', '6', '8', '.', '.', '1', '4', '.'], 
            ['.', '3', '9', '4', '.', '.', '2', '.', '.'], 
            ['.', '.', '.', '.', '7', '.', '.', '9', '3'], 
            ['.', '.', '.', '.', '.', '8', '4', '2', '.'], 
            ['3', '.', '.', '.', '.', '.', '.', '8', '9'], 
            ['8', '.', '4', '.', '.', '2', '.', '.', '1']
        ],
    ]
    for board in boards:
        sl = SudokuSolver((3, 3), board)
        sl.solve()
        print(sl.grid, '\n')