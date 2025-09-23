def int2set(val: int, bits: int) -> set[int]:
    return set([i + 1 for i in range(bits) if val & (1 << i)])


def map_index(coeffs: list[int], indices: list[int]) -> int:
    assert len(coeffs) == len(indices), 'Given coeffs and indices size do not match'
    index = 0
    for i in range(len(coeffs)):
        index += coeffs[i] * indices[i]
    return index


class SudokuGrid():
    ''' Sudoku grid with m x n block structure '''

    def __init__(self, m: int = 3, n: int = 3):

        total = m * n
        self.dimensions = (total, total)
        self.values = [_ for _ in range(1, total + 1)]
        self.grid = [set(self.values) for _ in range(total ** 2)]
        self.areas = [[map_index([total, 1], [i, j]) for j in range(total)] for i in range(total)]
        self.areas += [[map_index([total, 1], [i, j]) for i in range(total)] for j in range(total)]
        self.areas += [[map_index([total * m, n, total, 1], [i, j, r, s]) for r in range(m) for s in range(n)] for i in range(n) for j in range(m)]
        self.subsets = {i: int2set(i, total) for i in range(1, 1 << total)}
    
    def __str__(self) -> str:

        def show_value(val: set[int]) -> str:
            return str(list(val)[0]) if len(val) == 1 else '·'
        
        rows = self.dimensions[0]
        return '\n'.join([' '.join([show_value(self.grid[map_index([rows, 1], [i, j])]) for j in range(rows)]) for i in range(rows)])

    def __repr__(self) -> str:
        mx = max(len(x) for x in self.grid) + 1
        d = self.dimensions[0]
        rows = ['-' * ((mx + 1) * d + 1)]
        for i in range(d):
            vals = ['']
            for j in range(d):
                vals += [''.join(str(x) for x in sorted(self.grid[map_index([d, 1], [i, j])])).rjust(mx)]
            rows.append('|'.join(vals) + '|')
            rows.append('-' * ((mx + 1) * d + 1))
        return '\n'.join(rows)

    @classmethod
    def read_board(cls, shape: tuple[int, int], board: str):
        assert len(board) == (shape[0] * shape[1]) ** 2, 'Given board does not match to dimensions'
        grid = cls(shape[0], shape[1])
        for i, val in enumerate(board):
            if val != '.':
                assert (int(val)) in grid.values, f'Given value {val} is out of range'
                grid.set_values(i // grid.dimensions[0], i % grid.dimensions[0], set([int(val)]))
        return grid
        
    
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
    ''' Nuff said, just Sudoku solver '''

    def __init__(self, shape: tuple[int, int], board: str):
        self.block_shape = shape
        self.board = SudokuGrid.read_board(shape, board)
    
    def solve(self):
        self.board.simplify()
        while not all(self.board.defined):
            for idx in range(len(self.board.grid)):
                if self.board.defined[idx] == False:
                    row, col = idx // self.board.dimensions[0], idx % self.board.dimensions[0]
                    good_set = set()
                    for v in self.board.grid[idx]:
                        new_grid = SudokuGrid(self.block_shape[0], self.block_shape[1])
                        for i in range(len(self.board.grid)):
                            new_grid.grid[i] = self.board.grid[i].copy()
                        new_grid.set_values(row, col, set([v]))
                        new_grid.simplify()
                        if new_grid.is_valid:
                            if all(new_grid.defined):
                                self.board = new_grid
                                return
                            good_set |= {v}
                    self.board.set_values(row, col, good_set)
                    self.board.simplify()
