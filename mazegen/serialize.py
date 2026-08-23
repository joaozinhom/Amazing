"""Writing a maze to the project's output format.

One hexadecimal digit per cell encodes its closed walls (see
:mod:`mazegen.geometry`), stored row by row.  :func:`save` adds the
entry, the exit and the shortest path below an empty line, as the subject
requires.
"""

from __future__ import annotations

from .board import Board
from .geometry import Cell


def to_hex_rows(board: Board) -> list[str]:
    """Return the maze as one hexadecimal string per row of cells."""
    return ["".join(f"{cell:x}" for cell in row) for row in board.grid]


def save(filename: str, board: Board, entry: Cell, exit: Cell,
         path: str) -> None:
    """Write the maze, its entry, exit and solution to a file.

    Args:
        filename: Path of the output file, overwritten if it exists.
        board: The maze to write.
        entry: Entry cell, written below the map.
        exit: Exit cell, written below the entry.
        path: Shortest path as ``N``/``E``/``S``/``W`` letters.

    Raises:
        OSError: If the file cannot be written.
    """
    lines = to_hex_rows(board)
    lines += [
        "",
        f"{entry.x},{entry.y}",
        f"{exit.x},{exit.y}",
        path,
    ]
    with open(filename, "w", encoding="utf-8") as output:
        output.write("\n".join(lines) + "\n")
