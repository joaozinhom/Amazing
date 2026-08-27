"""Reading the ``KEY=VALUE`` configuration file into a maze.

The configuration is a plain text file, one ``KEY=VALUE`` per line, with
``#`` comments.  This module turns it into a :class:`~mazegen.MazeGenerator`,
raising :class:`ConfigError` -- never crashing -- on anything wrong: a
missing key, a bad number, an impossible maze.
"""

from __future__ import annotations

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
