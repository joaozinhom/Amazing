#!/usr/bin/env python3
"""A-Maze-ing: read a configuration file, build a maze, save and show it.

Usage:
    python3 ./a_maze_ing.py config.txt
"""

from __future__ import annotations

import sys

import display
from mazegen import Cell, MazeGenerator

MANDATORY = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")
TRUE_WORDS = ("true", "yes", "on", "1")
FALSE_WORDS = ("false", "no", "off", "0")


class ConfigError(Exception):
    """Raised when the configuration file cannot be used as it is."""


def read_config(filename: str) -> dict[str, str]:
    """Read a ``KEY=VALUE`` file into a dictionary.

    Args:
        filename: Path of the configuration file.

    Returns:
        The configuration, keys upper-cased, comments and blank lines
        dropped.

    Raises:
        ConfigError: If the file is unreadable, badly written, or if a
            mandatory key is missing.
    """
    config: dict[str, str] = {}
    try:
        with open(filename, "r", encoding="utf-8") as source:
            for number, raw in enumerate(source, start=1):
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"{filename}, line {number}: expected KEY=VALUE, "
                        f"got {line!r}"
                    )
                key, value = line.split("=", 1)
                config[key.strip().upper()] = value.strip()
    except OSError as err:
        raise ConfigError(f"cannot read {filename}: {err.strerror}") from err
    except UnicodeDecodeError as err:
        raise ConfigError(f"{filename} is not a plain text file") from err
    missing = [key for key in MANDATORY if key not in config]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")
    return config


def as_int(config: dict[str, str], key: str) -> int:
    """Read `key` as a whole number."""
    try:
        return int(config[key])
    except ValueError as err:
        raise ConfigError(
            f"{key} must be a whole number, got {config[key]!r}"
        ) from err


def as_cell(config: dict[str, str], key: str) -> Cell:
    """Read `key` as a pair of coordinates written ``x,y``."""
    try:
        x, y = [int(part) for part in config[key].split(",")]
    except ValueError as err:
        raise ConfigError(
            f"{key} must be written 'x,y', got {config[key]!r}"
        ) from err
    return Cell(x, y)


def as_bool(config: dict[str, str], key: str) -> bool:
    """Read `key` as a boolean."""
    value = config[key].lower()
    if value in TRUE_WORDS:
        return True
    if value in FALSE_WORDS:
        return False
    raise ConfigError(f"{key} must be True or False, got {config[key]!r}")


def build_maze(config: dict[str, str]) -> MazeGenerator:
    """Create the maze described by `config`.

    Raises:
        ConfigError: If a value is invalid or impossible to honour.
    """
    try:
        return MazeGenerator(
            width=as_int(config, "WIDTH"),
            height=as_int(config, "HEIGHT"),
            entry=as_cell(config, "ENTRY"),
            exit=as_cell(config, "EXIT"),
            perfect=as_bool(config, "PERFECT"),
            seed=as_int(config, "SEED") if "SEED" in config else None,
        )
    except ValueError as err:
        raise ConfigError(str(err)) from err


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
    display.run(maze, output)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
