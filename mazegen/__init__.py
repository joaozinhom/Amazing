"""Reusable maze generation for the 42 *A-Maze-ing* project.

The single public class, :class:`MazeGenerator`, builds either a
**perfect** maze (one path between any two cells) or a **braided** board
for a Pac-Man-like game (many loops, no dead-end).  A "42" pattern of
closed cells is drawn in the middle whenever it fits.

    from mazegen import MazeGenerator

    maze = MazeGenerator(width=20, height=15)   # generated on creation
    maze.save("maze.txt")                       # map + entry/exit + path

Every parameter but ``width`` and ``height`` is optional: ``entry`` and
``exit`` (``(x, y)`` cells), ``perfect`` (single path, default braided),
``seed`` (reproducible maze) and ``pattern`` (draw the "42", default on).

``maze.grid[y][x]`` is the wall bitmask of a cell (see :mod:`geometry`);
the helpers below avoid touching it directly::

    maze.linked(a, b)   # can one walk between two neighbouring cells?
    maze.exits(cell)    # number of open sides of a cell
    maze.corridors()    # every cell not part of the "42"
    maze.dead_ends()    # corridors with a single open side
    maze.loops()        # number of independent routes
    maze.solve()        # shortest path, as a list of cells
    maze.path_string()  # the same path, as "SSEENNE..."
    maze.to_hex_rows()  # the wall map, one string per row

Install it with ``pip install mazegen-1.0.0-py3-none-any.whl``.
"""

from __future__ import annotations

import random
from collections import deque

from .geometry import (
    ALL_WALLS,
    EAST,
    MOVES,
    NORTH,
    PATTERN_42,
    SOUTH,
    WEST,
    Cell,
    move_between,
    step,
)

__all__ = [
    "MazeGenerator",
    "Cell",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
]


class MazeGenerator:
    """A maze, generated with a randomised depth-first search.

    Args:
        width: Number of cells per row (>= 2).
        height: Number of cells per column (>= 2).
        entry: Entry cell ``(x, y)``, top-left by default.
        exit: Exit cell ``(x, y)``, bottom-right by default.
        perfect: ``True`` for a single path, ``False`` (default) for a
            looping, playable board.
        seed: Seed of the random generator, for reproducible mazes.
        pattern: Draw the "42" pattern when the maze is big enough.

    Raises:
        ValueError: If the size is too small, or if entry and exit are
            equal or fall outside the maze.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: Cell = Cell(0, 0),
        exit: Cell | None = None,
        perfect: bool = False,
        seed: int | None = None,
        pattern: bool = True,
    ) -> None:
        if width < 2 or height < 2:
            raise ValueError("the maze must be at least 2x2 cells")
        if not perfect and width * height <= 4:
            raise ValueError(
                "a playable board needs more than 2x2 cells, as it must "
                "offer at least two independent routes"
            )
        self.width = width
        self.height = height
        self.entry = Cell(*entry)
        self.exit = (
            Cell(*exit) if exit is not None else Cell(width - 1, height - 1)
        )
        self.perfect = perfect
        self.seed = seed
        self.pattern = pattern
        self._inside(self.entry, "ENTRY")
        self._inside(self.exit, "EXIT")
        if self.entry == self.exit:
            raise ValueError("ENTRY and EXIT must be two different cells")
        #: Walls of every cell, as ``grid[y][x]``; filled by `generate`.
        self.grid: list[list[int]] = []
        #: Cells reserved by the "42", left fully closed.
        self.pattern_cells: set[Cell] = set()
        #: Why the "42" could not be drawn; empty when all went well.
        self.pattern_error: str = ""
        self._rng = random.Random(seed)
        self.generate()

    def _inside(self, cell: Cell, name: str) -> None:
        """Check that `cell` belongs to the maze."""
        if not (0 <= cell.x < self.width and 0 <= cell.y < self.height):
            raise ValueError(
                f"{name} {tuple(cell)} is outside the "
                f"{self.width}x{self.height} maze"
            )

    # ------------------------------------------------------------------
    # generation, in three steps
    # ------------------------------------------------------------------

    def generate(self, seed: int | None = None) -> None:
        """Build a brand new maze in place.

        Every cell starts fully closed; the "42" cells are reserved, the
        corridors are carved, and dead-ends are removed for a playable
        board.

        Args:
            seed: New seed to use; the previous one is kept when omitted,
                which rebuilds the very same maze.
        """
        if seed is not None:
            self.seed = seed
        self._rng = random.Random(self.seed)
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self._place_pattern()
        self._carve()
        if not self.perfect:
            self._braid()

    def _place_pattern(self) -> None:
        """Reserve the cells drawing the "42" in the middle of the maze.

        Nothing is reserved -- and `pattern_error` says why -- when the
        maze is too small or when the entry or exit would be buried under
        the drawing.
        """
        self.pattern_cells = set()
        self.pattern_error = ""
        if not self.pattern:
            return
        rows = len(PATTERN_42)
        cols = len(PATTERN_42[0])
        left = self.width // 2 - cols // 2
        top = self.height // 2 - rows // 2
        if (left < 1 or top < 1
                or left + cols > self.width - 1
                or top + rows > self.height - 1):
            self.pattern_error = (
                f'the "42" pattern needs a maze of at least '
                f"{cols + 2}x{rows + 2} cells, it is not drawn"
            )
            return
        cells = {
            Cell(left + x, top + y)
            for y, row in enumerate(PATTERN_42)
            for x, closed in enumerate(row)
            if closed == "1"
        }
        if self.entry in cells or self.exit in cells:
            self.pattern_error = (
                'ENTRY or EXIT stands on the "42" pattern, it is not drawn'
            )
            return
        self.pattern_cells = cells

    def _carve(self) -> None:
        """Dig a spanning tree through every corridor cell (DFS).

        Walk to a random unseen neighbour, opening the wall on the way,
        and step back when stuck.  Every cell is reached exactly once, so
        the corridors end up connected and loop-free: a perfect maze.
        """
        stack: list[Cell] = [self.entry]
        visited: set[Cell] = {self.entry}
        while stack:
            cell = stack[-1]
            unseen = [n for n in self._neighbours(cell) if n not in visited]
            if not unseen:
                stack.pop()
                continue
            chosen = self._rng.choice(unseen)
            self._open(cell, chosen)
            visited.add(chosen)
            stack.append(chosen)

    def _braid(self) -> None:
        """Remove every dead-end by opening one more wall around it.

        Each removed wall adds an independent route, which is what a
        Pac-Man-like board needs.  A wall is kept when it would create a
        corridor wider than two cells.
        """
        cells = self.corridors()
        self._rng.shuffle(cells)
        for cell in cells:
            if self.exits(cell) != 1:
                continue                      # not a dead-end (any more)
            walled = [n for n in self._neighbours(cell)
                      if not self.linked(cell, n)]
            self._rng.shuffle(walled)
            # Merging two dead-ends fixes both at once, so try those first.
            candidates = [n for n in walled if self.exits(n) == 1]
            candidates += [n for n in walled if self.exits(n) != 1]
            for neighbour in candidates:
                self._open(cell, neighbour)
                if self._too_wide(cell, neighbour):
                    self._close(cell, neighbour)   # would open a room
                else:
                    break

    # ------------------------------------------------------------------
    # walls
    # ------------------------------------------------------------------

    def _open(self, a: Cell, b: Cell) -> None:
        """Remove the wall shared by two neighbouring cells."""
        move = move_between(a, b)
        self.grid[a.y][a.x] &= ~move.wall
        self.grid[b.y][b.x] &= ~move.back

    def _close(self, a: Cell, b: Cell) -> None:
        """Put back the wall shared by two neighbouring cells."""
        move = move_between(a, b)
        self.grid[a.y][a.x] |= move.wall
        self.grid[b.y][b.x] |= move.back

    def _is_corridor(self, cell: Cell) -> bool:
        """Tell whether `cell` is in the maze and free of the "42"."""
        return (0 <= cell.x < self.width and 0 <= cell.y < self.height
                and cell not in self.pattern_cells)

    def _neighbours(self, cell: Cell) -> list[Cell]:
        """Return the corridor cells standing right next to `cell`."""
        candidates = (step(cell, move) for move in MOVES)
        return [c for c in candidates if self._is_corridor(c)]

    def linked(self, a: Cell, b: Cell) -> bool:
        """Tell whether one can walk straight from `a` to `b`."""
        return not self.grid[a.y][a.x] & move_between(a, b).wall

    def exits(self, cell: Cell) -> int:
        """Return the number of open sides of `cell`."""
        walls = self.grid[cell.y][cell.x]
        return sum(1 for move in MOVES if not walls & move.wall)

    def _is_room(self, left: int, top: int) -> bool:
        """Tell whether the 3x3 cells at ``(left, top)`` are all linked.

        Such a square has no inner wall left -- exactly what the "never
        wider than two cells" rule forbids.
        """
        for y in range(top, top + 3):
            for x in range(left, left + 3):
                here = Cell(x, y)
                if x < left + 2 and not self.linked(here, Cell(x + 1, y)):
                    return False
                if y < top + 2 and not self.linked(here, Cell(x, y + 1)):
                    return False
        return True

    def _too_wide(self, a: Cell, b: Cell) -> bool:
        """Tell whether opening the `a`-`b` wall completed a room.

        Only a 3x3 square holding both cells can have been completed by
        that wall, so those are the only ones worth checking.
        """
        for top in range(min(a.y, b.y) - 2, max(a.y, b.y) + 1):
            for left in range(min(a.x, b.x) - 2, max(a.x, b.x) + 1):
                if (0 <= left <= self.width - 3
                        and 0 <= top <= self.height - 3
                        and self._is_room(left, top)):
                    return True
        return False

    # ------------------------------------------------------------------
    # reading the result
    # ------------------------------------------------------------------

    def corridors(self) -> list[Cell]:
        """Return every cell that is not part of the "42" pattern."""
        return [Cell(x, y)
                for y in range(self.height)
                for x in range(self.width)
                if self._is_corridor(Cell(x, y))]

    def dead_ends(self) -> list[Cell]:
        """Return the corridors having a single open side."""
        return [cell for cell in self.corridors() if self.exits(cell) == 1]

    def loops(self) -> int:
        """Return the number of independent routes of the maze.

        A tree has one passage fewer than it has cells; every extra
        passage closes one more loop.  A perfect maze has none; a
        playable board needs at least two.
        """
        cells = self.corridors()
        passages = sum(
            1
            for cell in cells
            for other in self._neighbours(cell)
            if self.linked(cell, other)
        ) // 2                      # each passage is counted from both ends
        return passages - len(cells) + 1

    def solve(self) -> list[Cell]:
        """Return the shortest path from entry to exit, as a list of cells.

        A breadth-first search grows outward from the entry, remembering
        where each cell was reached from; the path is then read backwards
        from the exit.  The list is empty when the exit is unreachable.
        """
        previous: dict[Cell, Cell] = {}
        seen: set[Cell] = {self.entry}
        queue: deque[Cell] = deque([self.entry])
        while queue:
            cell = queue.popleft()
            if cell == self.exit:
                break
            for other in self._neighbours(cell):
                if other not in seen and self.linked(cell, other):
                    seen.add(other)
                    previous[other] = cell
                    queue.append(other)
        if self.exit not in seen:
            return []
        path = [self.exit]
        while path[-1] != self.entry:
            path.append(previous[path[-1]])
        path.reverse()
        return path

    def path_string(self) -> str:
        """Return the shortest path as ``N``/``E``/``S``/``W`` letters."""
        path = self.solve()
        return "".join(
            move_between(a, b).letter for a, b in zip(path, path[1:])
        )

    def to_hex_rows(self) -> list[str]:
        """Return the maze as one hexadecimal string per row of cells."""
        return ["".join(f"{cell:x}" for cell in row) for row in self.grid]

    def __str__(self) -> str:
        """Return the hexadecimal wall map."""
        return "\n".join(self.to_hex_rows())

    def save(self, filename: str) -> None:
        """Write the maze, its entry, exit and solution to a file.

        Args:
            filename: Path of the output file, overwritten if it exists.

        Raises:
            OSError: If the file cannot be written.
        """
        lines = self.to_hex_rows()
        lines += [
            "",
            f"{self.entry.x},{self.entry.y}",
            f"{self.exit.x},{self.exit.y}",
            self.path_string(),
        ]
        with open(filename, "w", encoding="utf-8") as output:
            output.write("\n".join(lines) + "\n")
