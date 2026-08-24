"""Braiding: turning a perfect maze into a playable board.

A Pac-Man-like board must never trap a chased player, so it may not have
dead-ends.  :func:`braid` removes each one by opening one more wall
around it, which also adds an independent route.  A wall is kept when
opening it would leave a corridor wider than two cells (a 3x3 open room),
which the subject forbids.
"""

from __future__ import annotations

import random

from .board import Board
from .geometry import Cell


def braid(board: Board, rng: random.Random) -> None:
    """Remove every dead-end of `board`, in place.

    Args:
        board: A carved board (perfect maze) to open up.
        rng: Random source, so the braiding is reproducible.
    """
    cells = board.corridors()
    rng.shuffle(cells)
    for cell in cells:
        if board.exits(cell) != 1:
            continue                      # not a dead-end (any more)
        walled = [n for n in board.neighbours(cell)
                  if not board.linked(cell, n)]
        rng.shuffle(walled)
        # Merging two dead-ends fixes both at once, so try those first.
        candidates = [n for n in walled if board.exits(n) == 1]
        candidates += [n for n in walled if board.exits(n) != 1]
        for neighbour in candidates:
            board.open(cell, neighbour)
            if _would_make_room(board, cell, neighbour):
                board.close(cell, neighbour)   # would open a room
            else:
                break


def _would_make_room(board: Board, a: Cell, b: Cell) -> bool:
    """Tell whether opening the `a`-`b` wall completed a 3x3 room.

    Only a 3x3 square holding both cells can have been completed by that
    wall, so those are the only ones worth checking.
    """
    for top in range(min(a.y, b.y) - 2, max(a.y, b.y) + 1):
        for left in range(min(a.x, b.x) - 2, max(a.x, b.x) + 1):
            if (0 <= left <= board.width - 3
                    and 0 <= top <= board.height - 3
                    and _is_room(board, left, top)):
                return True
    return False


def _is_room(board: Board, left: int, top: int) -> bool:
    """Tell whether the 3x3 cells at ``(left, top)`` are all linked.

    Such a square has no inner wall left -- exactly what the "never wider
    than two cells" rule forbids.
    """
    for y in range(top, top + 3):
        for x in range(left, left + 3):
            here = Cell(x, y)
            if x < left + 2 and not board.linked(here, Cell(x + 1, y)):
                return False
            if y < top + 2 and not board.linked(here, Cell(x, y + 1)):
                return False
    return True
