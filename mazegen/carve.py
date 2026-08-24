"""Carving the corridors: a randomised depth-first search.

This is the heart of the generator.  Starting from one cell, it walks to
a random unseen neighbour, opening the wall on the way, and steps back
when stuck.  Every corridor cell is reached exactly once, so the result
is connected and loop-free: a **perfect** maze.  A playable board is this
tree with a few extra walls removed afterwards (see :mod:`mazegen.braid`).
"""

from __future__ import annotations

import random

from .board import Board
from .geometry import Cell


def carve(board: Board, start: Cell, rng: random.Random) -> None:
    """Dig a spanning tree through every corridor cell, in place.

    Args:
        board: The fully closed board to carve.
        start: Cell the walk begins from (usually the entry).
        rng: Random source, so the maze is reproducible from a seed.
    """
    stack: list[Cell] = [start]
    visited: set[Cell] = {start}
    while stack:
        cell = stack[-1]
        unseen = [n for n in board.neighbours(cell) if n not in visited]
        if not unseen:
            stack.pop()
            continue
        chosen = rng.choice(unseen)
        board.open(cell, chosen)
        visited.add(chosen)
        stack.append(chosen)
