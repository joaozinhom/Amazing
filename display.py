"""Terminal rendering and interactive menu of the A-Maze-ing project.

The maze is blown up into a grid of ``2 * size + 1`` blocks so that walls
and corridors both get their own square, then every block is printed as
two coloured spaces.
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


def _paint(rgb: Rgb) -> str:
    """Return one block of the given background colour."""
    return f"\x1b[48;2;{rgb[0]};{rgb[1]};{rgb[2]}m  "


def _canvas(maze: MazeGenerator, path: list[Cell]) -> list[list[str]]:
    """Turn the maze into a grid of named blocks, walls included."""
    rows = 2 * maze.height + 1
    cols = 2 * maze.width + 1
    canvas = [["wall"] * cols for _ in range(rows)]
    for y in range(maze.height):
        for x in range(maze.width):
            bx, by = 2 * x + 1, 2 * y + 1
            walls = maze.grid[y][x]
            if not walls & EAST:
                canvas[by][bx + 1] = "open"
            if not walls & SOUTH:
                canvas[by + 1][bx] = "open"
            if (x, y) not in maze.pattern_cells:
                canvas[by][bx] = "open"
                continue
            # Join the "42" cells together so the digits stay readable.
            canvas[by][bx] = "pattern"
            if (x + 1, y) in maze.pattern_cells:
                canvas[by][bx + 1] = "pattern"
            if (x, y + 1) in maze.pattern_cells:
                canvas[by + 1][bx] = "pattern"
            if {(x + 1, y), (x, y + 1), (x + 1, y + 1)} <= maze.pattern_cells:
                canvas[by + 1][bx + 1] = "pattern"
    _open_corners(canvas)
    for a, b in zip(path, path[1:]):
        canvas[2 * a[1] + 1][2 * a[0] + 1] = "path"
        canvas[2 * b[1] + 1][2 * b[0] + 1] = "path"
        canvas[a[1] + b[1] + 1][a[0] + b[0] + 1] = "path"
    canvas[2 * maze.entry[1] + 1][2 * maze.entry[0] + 1] = "entry"
    canvas[2 * maze.exit[1] + 1][2 * maze.exit[0] + 1] = "exit"
    return canvas


def _open_corners(canvas: list[list[str]]) -> None:
    """Open the wall corners surrounded by four open blocks."""
    for y in range(2, len(canvas) - 1, 2):
        for x in range(2, len(canvas[0]) - 1, 2):
            around = (canvas[y - 1][x], canvas[y + 1][x],
                      canvas[y][x - 1], canvas[y][x + 1])
            if all(block == "open" for block in around):
                canvas[y][x] = "open"


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
        show(maze, theme, show_path, message)
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
            maze.generate(seed=random.randrange(1_000_000))
            message = maze.pattern_error
            try:
                maze.save(output)
                message = message or f"new maze written to {output}"
            except OSError as err:
                message = f"Error: cannot write {output}: {err}"
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            theme += 1
        elif choice == "4":
            return
        else:
            message = f"unknown choice {choice!r}, please type 1, 2, 3 or 4"
