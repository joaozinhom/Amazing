"""The mutable grid and the low-level wall operations.

:class:`Board` is the shared state every generation step reads and writes:
one wall bitmask per cell (see :mod:`mazegen.geometry`) plus the cells
reserved by the "42" pattern.  It knows nothing about *how* a maze is
built -- it only offers the primitives the algorithms speak in: open or
close a wall, ask whether two cells are linked, list the neighbours of a
cell.

It is an internal helper: the public interface of the package stays the
single :class:`mazegen.MazeGenerator` class, which owns one board.
"""

from __future__ import annotations

from .geometry import ALL_WALLS, MOVES, Cell, move_between, step


class Board:
    """The wall grid of a maze, with the moves one may make on it.

    Args:
        width: Number of cells per row.
        height: Number of cells per column.
        pattern_cells: Cells reserved by the "42"; left fully closed and
            never treated as corridors.
    """

    def __init__(self, width: int, height: int,
                 pattern_cells: set[Cell]) -> None:
        self.width = width
        self.height = height
        self.pattern_cells = pattern_cells
        #: Walls of every cell, as ``grid[y][x]``; starts fully closed.
        self.grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)
        ]

    def open(self, a: Cell, b: Cell) -> None:
        """Remove the wall shared by two neighbouring cells."""
        move = move_between(a, b)
        self.grid[a.y][a.x] &= ~move.wall
        self.grid[b.y][b.x] &= ~move.back

    def close(self, a: Cell, b: Cell) -> None:
        """Put back the wall shared by two neighbouring cells."""
        move = move_between(a, b)
        self.grid[a.y][a.x] |= move.wall
        self.grid[b.y][b.x] |= move.back

    def linked(self, a: Cell, b: Cell) -> bool:
        """Tell whether one can walk straight from `a` to `b`."""
        return not self.grid[a.y][a.x] & move_between(a, b).wall

    def exits(self, cell: Cell) -> int:
        """Return the number of open sides of `cell`."""
        walls = self.grid[cell.y][cell.x]
        return sum(1 for move in MOVES if not walls & move.wall)

    def is_corridor(self, cell: Cell) -> bool:
        """Tell whether `cell` is in the maze and free of the "42"."""
        return (0 <= cell.x < self.width and 0 <= cell.y < self.height
                and cell not in self.pattern_cells)

    def neighbours(self, cell: Cell) -> list[Cell]:
        """Return the corridor cells standing right next to `cell`."""
        candidates = (step(cell, move) for move in MOVES)
        return [c for c in candidates if self.is_corridor(c)]

    def corridors(self) -> list[Cell]:
        """Return every cell that is not part of the "42" pattern."""
        return [Cell(x, y)
                for y in range(self.height)
                for x in range(self.width)
                if self.is_corridor(Cell(x, y))]
