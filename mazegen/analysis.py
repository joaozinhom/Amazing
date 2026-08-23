"""Read-only questions one may ask about a finished maze.

Nothing here changes the board; these functions only walk it: find the
shortest path (breadth-first search), spell it out as letters, count the
independent routes, or list the dead-ends.
"""

from __future__ import annotations

from collections import deque

from .board import Board
from .geometry import Cell, move_between


def solve(board: Board, entry: Cell, exit: Cell) -> list[Cell]:
    """Return the shortest path from `entry` to `exit`, as a list of cells.

    A breadth-first search grows outward from the entry, remembering
    where each cell was reached from; the path is then read backwards
    from the exit.  The list is empty when the exit is unreachable.
    """
    previous: dict[Cell, Cell] = {}
    seen: set[Cell] = {entry}
    queue: deque[Cell] = deque([entry])
    while queue:
        cell = queue.popleft()
        if cell == exit:
            break
        for other in board.neighbours(cell):
            if other not in seen and board.linked(cell, other):
                seen.add(other)
                previous[other] = cell
                queue.append(other)
    if exit not in seen:
        return []
    path = [exit]
    while path[-1] != entry:
        path.append(previous[path[-1]])
    path.reverse()
    return path


def path_string(board: Board, entry: Cell, exit: Cell) -> str:
    """Return the shortest path as ``N``/``E``/``S``/``W`` letters."""
    path = solve(board, entry, exit)
    return "".join(
        move_between(a, b).letter for a, b in zip(path, path[1:])
    )


def loops(board: Board) -> int:
    """Return the number of independent routes of the maze.

    A tree has one passage fewer than it has cells; every extra passage
    closes one more loop.  A perfect maze has none; a playable board
    needs at least two.
    """
    cells = board.corridors()
    passages = sum(
        1
        for cell in cells
        for other in board.neighbours(cell)
        if board.linked(cell, other)
    ) // 2                      # each passage is counted from both ends
    return passages - len(cells) + 1


def dead_ends(board: Board) -> list[Cell]:
    """Return the corridors having a single open side."""
    return [cell for cell in board.corridors() if board.exits(cell) == 1]
