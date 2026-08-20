"""Terminal rendering and interactive menu of the A-Maze-ing project.

A maze is a grid of cells separated by walls, so drawing it needs one
square per cell *and* one square per wall: a WIDTH x HEIGHT maze is drawn
on a canvas of ``2 * WIDTH + 1`` by ``2 * HEIGHT + 1`` squares, here
called blocks::

    +---+---+           wall  wall  wall  wall  wall
    | a | b |           wall   a    gap    b    wall
    +---+---+    ->     wall  wall  wall  wall  wall
    | c   d |           wall   c    gap    d    wall
    +---+---+           wall  wall  wall  wall  wall

Each block is first given a name -- ``wall``, ``open``, ``pattern``,
``path``, ``entry`` or ``exit`` -- and then printed as two spaces of the
colour that name stands for.
"""

from __future__ import annotations

import random
import sys

from mazegen import EAST, SOUTH, Cell, MazeGenerator

Rgb = tuple[int, int, int]

RESET = "\x1b[0m"
CLEAR = "\x1b[2J\x1b[H"

CORRIDOR: Rgb = (16, 16, 20)
ENTRY: Rgb = (232, 84, 232)
EXIT: Rgb = (232, 70, 70)

#: Wall, "42" pattern and shortest path colours, rotated by the menu.
THEMES: list[tuple[Rgb, Rgb, Rgb]] = [
    ((222, 222, 226), (150, 150, 160), (86, 214, 214)),
    ((232, 150, 30), (245, 233, 214), (255, 240, 120)),
    ((60, 170, 235), (200, 230, 255), (255, 120, 190)),
    ((90, 200, 110), (190, 245, 200), (150, 150, 255)),
]

MENU = """=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit"""


# ----------------------------------------------------------------------
# from cells to blocks
# ----------------------------------------------------------------------

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


def _open_corners(canvas: list[list[str]]) -> None:
    """Open the wall blocks standing alone between four open ones.

    Those blocks are the corners of the grid, and a corner whose four
    sides are open is a pillar in the middle of nothing.
    """
    for y in range(2, len(canvas) - 1, 2):
        for x in range(2, len(canvas[0]) - 1, 2):
            around = (canvas[y - 1][x], canvas[y + 1][x],
                      canvas[y][x - 1], canvas[y][x + 1])
            if all(block == "open" for block in around):
                _fill(canvas, Cell(x, y), "open")


def _draw_path(canvas: list[list[str]], path: list[Cell]) -> None:
    """Walk the solution, painting every cell and every gap it crosses."""
    for a, b in zip(path, path[1:]):
        for block in (_block(a), _block(b), _gap(a, b)):
            _fill(canvas, block, "path")


def _canvas(maze: MazeGenerator, path: list[Cell]) -> list[list[str]]:
    """Turn the maze into a grid of named blocks, walls included."""
    rows = 2 * maze.height + 1
    cols = 2 * maze.width + 1
    canvas = [["wall"] * cols for _ in range(rows)]
    _draw_corridors(maze, canvas)
    _draw_pattern(maze, canvas)
    _open_corners(canvas)
    _draw_path(canvas, path)
    _fill(canvas, _block(maze.entry), "entry")
    _fill(canvas, _block(maze.exit), "exit")
    return canvas


# ----------------------------------------------------------------------
# from blocks to the screen
# ----------------------------------------------------------------------

def _paint(rgb: Rgb) -> str:
    """Return one block of the given background colour."""
    return f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m  "


def render(maze: MazeGenerator, theme: int, show_path: bool) -> str:
    """Return the maze as a block of coloured terminal lines."""
    walls, pattern, trail = THEMES[theme % len(THEMES)]
    colours: dict[str, Rgb] = {
        "wall": walls,
        "pattern": pattern,
        "open": CORRIDOR,
        "path": trail,
        "entry": ENTRY,
        "exit": EXIT,
    }
    path = maze.solve() if show_path else []
    lines = ["".join(_paint(colours[block]) for block in row) + RESET
             for row in _canvas(maze, path)]
    return "\n".join(lines)


def status(maze: MazeGenerator) -> str:
    """Return a one line summary of the maze on screen."""
    mode = "perfect" if maze.perfect else "playable board"
    return (f"{maze.width}x{maze.height} - seed {maze.seed} - {mode} - "
            f"loops: {maze.loops()} - dead-ends: {len(maze.dead_ends())} - "
            f"path: {len(maze.path_string())} moves")


def show(maze: MazeGenerator, theme: int, show_path: bool,
         message: str) -> None:
    """Draw the maze, its summary and the menu."""
    print(CLEAR + render(maze, theme, show_path))
    print(status(maze))
    if message:
        print(message)
    print(MENU)


# ----------------------------------------------------------------------
# the menu
# ----------------------------------------------------------------------

def _regenerate(maze: MazeGenerator, output: str) -> str:
    """Roll a new maze, save it, and return the message to display."""
    maze.generate(seed=random.randrange(1_000_000))
    try:
        maze.save(output)
    except OSError as err:
        return f"Error: cannot write {output}: {err}"
    return maze.pattern_error or f"new maze written to {output}"


def run(maze: MazeGenerator, output: str) -> None:
    """Display the maze and loop over the user choices.

    Args:
        maze: The maze to show; re-generated in place on demand.
        output: File rewritten every time a new maze is generated.
    """
    theme = 0
    show_path = False
    message = maze.pattern_error or f"maze written to {output}"
    if not sys.stdin.isatty():
        show(maze, theme, show_path, message)     # piped: draw once, leave
        return
    while True:
        show(maze, theme, show_path, message)
        try:
            choice = input("Choice? (1-4): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        message = ""
        if choice == "1":
            message = _regenerate(maze, output)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            theme += 1
        elif choice == "4":
            return
        else:
            message = f"unknown choice {choice!r}, please type 1, 2, 3 or 4"
