"""Colouring the named blocks and turning them into terminal lines.

Each block name from :mod:`app.canvas` stands for a colour; a block is
printed as two spaces of that colour's background.  The wall, "42" and
path colours come from a rotating theme, so the menu can recolour the
maze on demand.
"""

from __future__ import annotations

from mazegen import MazeGenerator

from .canvas import build_canvas

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
             for row in build_canvas(maze, path)]
    return "\n".join(lines)


def status(maze: MazeGenerator) -> str:
    """Return a one line summary of the maze on screen."""
    mode = "perfect" if maze.perfect else "playable board"
    return (f"{maze.width}x{maze.height} - seed {maze.seed} - {mode} - "
            f"loops: {maze.loops()} - dead-ends: {len(maze.dead_ends())} - "
            f"path: {len(maze.path_string())} moves")
