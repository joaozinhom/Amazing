"""The single public class of the package: :class:`MazeGenerator`.

It is the orchestrator.  It validates its arguments, holds one
:class:`~mazegen.board.Board`, and drives the generation by calling the
one-job modules in order -- reserve the "42"
(:func:`~mazegen.pattern.place_pattern`), carve the corridors
(:func:`~mazegen.carve.carve`) and, for a playable board, braid away the
dead-ends (:func:`~mazegen.braid.braid`).  Reading the result
(:mod:`~mazegen.analysis`, :mod:`~mazegen.serialize`) is delegated the
same way, so this class stays thin and every algorithm lives on its own.
"""

from __future__ import annotations

import random

from . import analysis, serialize
from .board import Board
from .braid import braid
from .carve import carve
from .geometry import Cell
from .pattern import place_pattern


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
        #: Why the "42" could not be drawn; empty when all went well.
        self.pattern_error: str = ""
        #: The grid state; (re)built by `generate`.
        self._board = Board(width, height, set())
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

        The "42" cells are reserved, the corridors are carved from a fully
        closed grid, and dead-ends are braided away for a playable board.

        Args:
            seed: New seed to use; the previous one is kept when omitted,
                which rebuilds the very same maze.
        """
        if seed is not None:
            self.seed = seed
        rng = random.Random(self.seed)
        cells, self.pattern_error = place_pattern(
            self.width, self.height, self.entry, self.exit, self.pattern
        )
        self._board = Board(self.width, self.height, cells)
        carve(self._board, self.entry, rng)
        if not self.perfect:
            braid(self._board, rng)

    # ------------------------------------------------------------------
    # reading the result -- delegated to the one-job modules
    # ------------------------------------------------------------------

    @property
    def grid(self) -> list[list[int]]:
        """Walls of every cell, as ``grid[y][x]`` (see :mod:`.geometry`)."""
        return self._board.grid

    @property
    def pattern_cells(self) -> set[Cell]:
        """Cells reserved by the "42", left fully closed."""
        return self._board.pattern_cells

    def linked(self, a: Cell, b: Cell) -> bool:
        """Tell whether one can walk straight from `a` to `b`."""
        return self._board.linked(a, b)

    def exits(self, cell: Cell) -> int:
        """Return the number of open sides of `cell`."""
        return self._board.exits(cell)

    def corridors(self) -> list[Cell]:
        """Return every cell that is not part of the "42" pattern."""
        return self._board.corridors()

    def dead_ends(self) -> list[Cell]:
        """Return the corridors having a single open side."""
        return analysis.dead_ends(self._board)

    def loops(self) -> int:
        """Return the number of independent routes of the maze."""
        return analysis.loops(self._board)

    def solve(self) -> list[Cell]:
        """Return the shortest path from entry to exit, as a list of cells."""
        return analysis.solve(self._board, self.entry, self.exit)

    def path_string(self) -> str:
        """Return the shortest path as ``N``/``E``/``S``/``W`` letters."""
        return analysis.path_string(self._board, self.entry, self.exit)

    def to_hex_rows(self) -> list[str]:
        """Return the maze as one hexadecimal string per row of cells."""
        return serialize.to_hex_rows(self._board)

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
        serialize.save(
            filename, self._board, self.entry, self.exit, self.path_string()
        )
