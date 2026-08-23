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

``maze.grid[y][x]`` is the wall bitmask of a cell (see :mod:`.geometry`);
the helpers below avoid touching it directly::

    maze.linked(a, b)   # can one walk between two neighbouring cells?
    maze.exits(cell)    # number of open sides of a cell
    maze.corridors()    # every cell not part of the "42"
    maze.dead_ends()    # corridors with a single open side
    maze.loops()        # number of independent routes
    maze.solve()        # shortest path, as a list of cells
    maze.path_string()  # the same path, as "SSEENNE..."
    maze.to_hex_rows()  # the wall map, one string per row

The package is split so each step lives on its own, one job per file::

    geometry.py    # the vocabulary: cells, walls, moves, the "42"
    board.py       # the grid state and the wall primitives
    pattern.py     # where the "42" lands, or why it cannot
    carve.py       # carve the corridors (depth-first search)
    braid.py       # remove the dead-ends of a playable board
    analysis.py    # solve, count loops and dead-ends
    serialize.py   # the hexadecimal output format
    generator.py   # MazeGenerator, the orchestrator tying it together

Install it with ``pip install mazegen-1.0.0-py3-none-any.whl``.
"""

from __future__ import annotations

from .generator import MazeGenerator
from .geometry import ALL_WALLS, EAST, NORTH, SOUTH, WEST, Cell

__all__ = [
    "MazeGenerator",
    "Cell",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
]
