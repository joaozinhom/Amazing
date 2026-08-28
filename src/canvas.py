"""Turning a maze into a grid of named blocks, walls included.

A maze is a grid of cells separated by walls, so drawing it needs one
square per cell *and* one square per wall: a WIDTH x HEIGHT maze is drawn
on a canvas of ``2 * WIDTH + 1`` by ``2 * HEIGHT + 1`` squares, here
called blocks::

    +---+---+           wall  wall  wall  wall  wall
    | a | b |           wall   a    gap    b    wall
    +---+---+    ->     wall  wall  wall  wall  wall
    | c   d |           wall   c    gap    d    wall
    +---+---+           wall  wall  wall  wall  wall

Each block is given a name -- ``wall``, ``open``, ``pattern``, ``path``,
``entry`` or ``exit`` -- which :mod:`src.render` later turns into a
colour.

Only cells and gaps are ever opened.  The blocks sitting at the *corners*
of the grid -- even row and even column -- always stay walls, even when
the four gaps around them are open.  That lone pillar is what keeps a
corridor exactly one block wide on screen: without it, the 2x2 open areas
the subject allows would melt into a 3x3 square and the drawing would
read as a wide room rather than as two crossing corridors.
"""

from __future__ import annotations

from mazegen import EAST, SOUTH, Cell, MazeGenerator


def _block(cell: Cell) -> Cell:
    """Return the block holding a maze cell."""
    return Cell(2 * cell.x + 1, 2 * cell.y + 1)


def _gap(a: Cell, b: Cell) -> Cell:
    """Return the block standing between two neighbouring cells."""
    return Cell(a.x + b.x + 1, a.y + b.y + 1)


def _fill(canvas: list[list[str]], block: Cell, name: str) -> None:
    """Give a name -- so a colour -- to one block of the canvas."""
    canvas[block.y][block.x] = name


def _draw_corridors(maze: MazeGenerator, canvas: list[list[str]]) -> None:
    """Open one block per cell, plus one per wall the maze removed."""
    for y in range(maze.height):
        for x in range(maze.width):
            cell = Cell(x, y)
            walls = maze.grid[y][x]
            if not walls & EAST:
                _fill(canvas, _gap(cell, Cell(x + 1, y)), "open")
            if not walls & SOUTH:
                _fill(canvas, _gap(cell, Cell(x, y + 1)), "open")
            if cell not in maze.pattern_cells:
                _fill(canvas, _block(cell), "open")


def _draw_pattern(maze: MazeGenerator, canvas: list[list[str]]) -> None:
    """Paint the "42" cells, and the gaps between two of them.

    Painting the gaps as well glues the neighbouring cells of the drawing
    together, so the digits read as solid shapes instead of a cloud of
    squares.
    """
    for cell in maze.pattern_cells:
        x, y = cell
        right = Cell(x + 1, y)
        below = Cell(x, y + 1)
        corner = Cell(x + 1, y + 1)
        _fill(canvas, _block(cell), "pattern")
        for other in (right, below):
            if other in maze.pattern_cells:
                _fill(canvas, _gap(cell, other), "pattern")
        if {right, below, corner} <= maze.pattern_cells:
            _fill(canvas, _gap(cell, corner), "pattern")   # a full 2x2 square


def _draw_path(canvas: list[list[str]], path: list[Cell]) -> None:
    """Walk the solution, painting every cell and every gap it crosses."""
    for a, b in zip(path, path[1:]):
        for block in (_block(a), _block(b), _gap(a, b)):
            _fill(canvas, block, "path")


def build_canvas(maze: MazeGenerator, path: list[Cell]) -> list[list[str]]:
    """Turn the maze into a grid of named blocks, walls included."""
    rows = 2 * maze.height + 1
    cols = 2 * maze.width + 1
    canvas = [["wall"] * cols for _ in range(rows)]
    _draw_corridors(maze, canvas)
    _draw_pattern(maze, canvas)
    _draw_path(canvas, path)
    _fill(canvas, _block(maze.entry), "entry")
    _fill(canvas, _block(maze.exit), "exit")
    return canvas
