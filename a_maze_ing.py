#!/usr/bin/env python3
"""A-Maze-ing: read a configuration file, build a maze, save and show it.

This is the thin entry point.  It only wires the pieces together: parse
the configuration (:mod:`app.config`), build the maze (:mod:`mazegen`),
write it to the output file, and hand it to the interactive display
(:mod:`app.menu`).

Usage:
    python3 ./a_maze_ing.py config.txt
"""

from __future__ import annotations

import sys

from app import menu
from app.config import ConfigError, build_maze, read_config


def main(argv: list[str]) -> int:
    """Run the program; return the exit status."""
    if len(argv) != 2:
        print(f"usage: {argv[0]} config.txt", file=sys.stderr)
        return 1
    try:
        config = read_config(argv[1])
        maze = build_maze(config)
    except ConfigError as err:
        print(f"Error: {err}", file=sys.stderr)
        return 1
    output = config["OUTPUT_FILE"]
    try:
        maze.save(output)
    except OSError as err:
        print(f"Error: cannot write {output}: {err.strerror}", file=sys.stderr)
        return 1
    if maze.pattern_error:
        print(f"Error: {maze.pattern_error}", file=sys.stderr)
    menu.run(maze, output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
