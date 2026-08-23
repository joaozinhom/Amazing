"""Placement of the "42" pattern in the middle of the maze.

The pattern is a fixed drawing of fully closed cells (see
:data:`mazegen.geometry.PATTERN_42`).  :func:`place_pattern` works out
where it lands on a given maze, or explains why it cannot be drawn -- the
maze being too small, or the entry/exit standing on the drawing.
"""

from __future__ import annotations

from .geometry import PATTERN_42, Cell


def place_pattern(
    width: int,
    height: int,
    entry: Cell,
    exit: Cell,
    enabled: bool = True,
) -> tuple[set[Cell], str]:
    """Return the cells reserved by the "42", and why it might be absent.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.
        entry: Entry cell; the pattern is dropped if it lands here.
        exit: Exit cell; the pattern is dropped if it lands here.
        enabled: Draw the pattern at all.

    Returns:
        A ``(cells, error)`` pair.  ``cells`` is empty and ``error``
        explains why whenever the pattern cannot be drawn; otherwise
        ``error`` is empty.
    """
    if not enabled:
        return set(), ""
    rows = len(PATTERN_42)
    cols = len(PATTERN_42[0])
    left = width // 2 - cols // 2
    top = height // 2 - rows // 2
    if (left < 1 or top < 1
            or left + cols > width - 1
            or top + rows > height - 1):
        return set(), (
            f'the "42" pattern needs a maze of at least '
            f"{cols + 2}x{rows + 2} cells, it is not drawn"
        )
    cells = {
        Cell(left + x, top + y)
        for y, row in enumerate(PATTERN_42)
        for x, closed in enumerate(row)
        if closed == "1"
    }
    if entry in cells or exit in cells:
        return set(), (
            'ENTRY or EXIT stands on the "42" pattern, it is not drawn'
        )
    return cells, ""
