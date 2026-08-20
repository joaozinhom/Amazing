"""The shared vocabulary of the grid: cells, walls, moves and the "42".

Nothing here knows how a maze is *built*; this is only the language the
generator and the display both speak.  Walls are stored as a bitmask per
cell -- a bit is set when the wall is standing::

    NORTH = 1   EAST = 2   SOUTH = 4   WEST = 8

so ``0`` is a fully open cell and ``15`` (``ALL_WALLS``) a fully closed one.
"""

from __future__ import annotations

from typing import NamedTuple


class Cell(NamedTuple):
    """A grid position, addressed as ``cell.x`` / ``cell.y``.

    It is a plain ``(x, y)`` tuple underneath, so it unpacks, indexes and
    compares just like the coordinates used everywhere else.
    """

    x: int
    y: int


NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST


class Move(NamedTuple):
    """A step to a neighbouring cell, and the wall it crosses.

    Going north crosses the *north* wall of the cell we leave, which is
    the *south* wall of the cell above: one wall, but two bitmasks to
    update -- ``wall`` seen from here, ``back`` seen from the neighbour.
    """

    letter: str
    dx: int
    dy: int
    wall: int
    back: int


#: The four moves, in reading order.
MOVES: tuple[Move, ...] = (
    Move("N", 0, -1, NORTH, SOUTH),
    Move("E", 1, 0, EAST, WEST),
    Move("S", 0, 1, SOUTH, NORTH),
    Move("W", -1, 0, WEST, EAST),
)


def step(cell: Cell, move: Move) -> Cell:
    """Return the neighbour reached by taking `move` from `cell`."""
    return Cell(cell.x + move.dx, cell.y + move.dy)


def move_between(a: Cell, b: Cell) -> Move:
    """Return the :class:`Move` from `a` to the neighbouring cell `b`.

    Raises:
        ValueError: If `a` and `b` are not side by side.
    """
    for move in MOVES:
        if step(a, move) == b:
            return move
    raise ValueError(f"{tuple(a)} and {tuple(b)} are not neighbours")


#: The "42" drawing: "1" is a fully closed cell, "0" a normal corridor.
#: Its middle column and row stay open, keeping the centre of the maze
#: walkable even when the pattern is centred on it.
PATTERN_42: tuple[str, ...] = (
    "100101111",
    "100100001",
    "100100001",
    "111101111",
    "000101000",
    "000101000",
    "000101111",
)
