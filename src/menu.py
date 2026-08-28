"""The interactive terminal menu.

Draws the maze with :mod:`src.render`, then loops over the user's
choices: re-generate, show or hide the shortest path, rotate the wall
colours, or quit.  When the output is piped (not a terminal) it simply
draws once and returns.
"""

from __future__ import annotations

import random
import sys

from mazegen import MazeGenerator

from .render import CLEAR, render, status

MENU = """=== A-Maze-ing ===
1. Re-generate a new maze
2. Show / Hide the shortest path
3. Rotate the wall colours
4. Quit"""


def show(maze: MazeGenerator, theme: int, show_path: bool,
         message: str) -> None:
    """Draw the maze, its summary and the menu."""
    print(CLEAR + render(maze, theme, show_path))
    print(status(maze))
    if message:
        print(message)
    print(MENU)


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
