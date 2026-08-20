*This project has been created as part of the 42 curriculum by mpinto-l.*

<!-- Team of 2+: add your teammates above, e.g. "by mpinto-l, <login2>, <login3>". -->

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in pure Python (standard library only).
It reads a plain text configuration file, generates a random maze and writes it
to a file using a hexadecimal wall encoding, then displays it in the terminal
with an interactive menu.

Two very different mazes can be produced:

| `PERFECT` | Result |
| --------- | ------ |
| `True` | A **perfect maze**: exactly one path between any two cells, no loop at all. |
| `False` (default) | A **playable Pac-Man board**: full connectivity, many independent routes, the four corners and the centre open, and **no dead-end at all** (the bonus). |

In both modes the maze contains a visible **"42"** drawn with fully closed
cells, no corridor is wider than two cells, the outer border is fully walled,
and the shortest path from the entry to the exit is computed and saved.

The generation itself lives in `mazegen`, a standalone package that can be
installed with `pip` and reused by a later project.

## Instructions

The program needs **Python 3.10 or later** and no third-party dependency.

```bash
python3 ./a_maze_ing.py config.txt
```

The `Makefile` automates the usual tasks:

| Rule | What it does |
| ---- | ------------ |
| `make install` | Create `.venv` and install the development tools (`flake8`, `mypy`, `build`). |
| `make run` | Run the program on `config.txt` (`make run CONFIG=other.txt` for another file). |
| `make debug` | Run the program under `pdb`. |
| `make lint` | `flake8 .` and `mypy .` with the mandatory flags. |
| `make lint-strict` | `flake8 .` and `mypy . --strict`. |
| `make package` | Rebuild `mazegen-1.0.0-py3-none-any.whl` at the root of the repository. |
| `make clean` | Remove caches and build artefacts. |

Every error is reported with a clear message and a non-zero exit status: missing
or unreadable file, bad syntax, missing key, invalid value, entry or exit
outside the maze, unwritable output file...

### Interactive display

The maze is drawn in the terminal with coloured blocks: walls, corridors, the
entry (pink), the exit (red), the "42" pattern and the shortest path each have
their own colour. The menu offers:

```
=== A-Maze-ing ===
1. Re-generate a new maze     <- new random seed, the output file is rewritten
2. Show / Hide the shortest path
3. Rotate the wall colours    <- 4 themes, walls + "42" + path
4. Quit
```

When the standard input is not a terminal (a pipe, a moulinette), the maze is
drawn once and the program exits instead of waiting for an answer.

A maze is a grid of cells *separated by walls*, so drawing it needs one square
per cell **and** one square per wall: a `WIDTH x HEIGHT` maze is drawn on a
canvas of `2 * WIDTH + 1` by `2 * HEIGHT + 1` squares, called blocks.

```
+---+---+           wall  wall  wall  wall  wall
| a | b |           wall   a    gap    b    wall
+---+---+    ->     wall  wall  wall  wall  wall
| c   d |           wall   c    gap    d    wall
+---+---+           wall  wall  wall  wall  wall
```

Each block is first given a name — `wall`, `open`, `pattern`, `path`, `entry` or
`exit` — and only then printed as two spaces of the colour that name stands for.
Naming first and colouring last is what keeps the drawing code short: the theme
is a simple name → colour dictionary.

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` and blank lines are
ignored, spaces around the key and the value are trimmed, and keys are
case-insensitive. The complete format:

| Key | Mandatory | Value | Example |
| --- | --------- | ----- | ------- |
| `WIDTH` | yes | Number of cells per row, `>= 2` | `WIDTH=20` |
| `HEIGHT` | yes | Number of cells per column, `>= 2` | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell, written `x,y` (`0,0` is top-left) | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell, written `x,y`, different from `ENTRY` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | File the maze is written to | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True`/`False` (also `yes`/`no`, `on`/`off`, `1`/`0`) | `PERFECT=False` |
| `SEED` | no | Integer seed, for a reproducible maze | `SEED=42` |

`config.txt`, at the root of the repository, is the default configuration.

### Output file

One hexadecimal digit per cell, one line per row of cells. Each digit is the
bitmask of the **closed** walls of the cell: north `1`, east `2`, south `4`,
west `8` (so `f` is a fully closed cell and `0` a fully open one). Then an
empty line, then three lines: the entry coordinates, the exit coordinates, and
the shortest path as a string of `N`, `E`, `S`, `W` moves. Every line ends
with `\n`.

```
91395539555139513913
86c693c6953ac43c46aa
...
c56c555554454546c6c6

0,0
19,14
SSEEEESEEESSENNEESSESWSSSSSESSESEEENESENESE
```

## The algorithm

Generation happens in three steps.

1. **The "42" pattern.** The cells drawing the digits are reserved and left
   fully closed (all four walls). The drawing is centred, and its middle column
   is a corridor, so the centre of the maze always stays open — which the
   Pac-Man mode requires. If the maze is too small (less than 11x9 cells), or if
   the entry or the exit stands on the drawing, the pattern is skipped and an
   error message is printed on the console.

2. **Carving: randomised depth-first search** (recursive backtracker). Starting
   from the entry, the algorithm walks to a random unvisited neighbour, removes
   the wall between the two cells, and backtracks when it is stuck. Reserved
   cells are never visited. This produces a **spanning tree** of the corridors:
   every cell is reachable and there is exactly one path between any two cells,
   which is precisely a perfect maze. With `PERFECT=True` the work stops here.

3. **Braiding** (only when `PERFECT=False`). Every dead-end — a cell with a
   single open side — gets one more wall removed, preferably towards another
   dead-end so both are fixed at once. Each removed wall closes a loop, so the
   board ends up with many independent routes and no dead-end. A wall is kept
   whenever removing it would create a 3x3 open area, which is how the
   "corridors are never wider than two cells" rule is enforced.

The shortest path is then found with a **breadth-first search** from the entry.

### Why this algorithm

* The recursive backtracker is simple, has no failure case, and is *by
  construction* correct on the hardest requirements: a spanning tree is fully
  connected, has no isolated cell, and contains no loop — so `PERFECT=True` is
  satisfied without any extra check or repair pass.
* It runs in O(cells) with an explicit stack, so it never hits the Python
  recursion limit, even on a large maze.
* It produces long winding corridors, which look much better than the short
  branches of Prim's or Kruskal's algorithms.
* Being a tree, it is the perfect starting point for the second mode: adding
  loops afterwards is a controlled, local operation, whereas removing loops
  from a random board is not.
* Reproducibility is free: a single `random.Random(seed)` instance drives the
  whole generation.

## The reusable module

The whole generation logic is the `MazeGenerator` class of the `mazegen`
package — a standalone module that knows nothing about the config file, the
output format or the display. `a_maze_ing.py` only parses the configuration and
`display.py` only draws; both are throwaway around the module.

The package is built as `mazegen-1.0.0-py3-none-any.whl`, available at the root
of the repository and rebuildable with `make package` (or
`python3 -m build --wheel`). It is released under the MIT License, see
`LICENSE.md`, so any later project may reuse and redistribute it.

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Instantiate and use

The maze is generated by the constructor:

```python
from mazegen import MazeGenerator

maze = MazeGenerator(width=20, height=15)
print(maze)                 # the hexadecimal wall map
maze.save("maze.txt")       # map + entry + exit + shortest path
```

### Pass custom parameters

Everything but `width` and `height` is optional:

```python
maze = MazeGenerator(
    width=25,               # number of cells, >= 2
    height=19,
    entry=(0, 0),           # (x, y), defaults to the top-left cell
    exit=(24, 18),          # (x, y), defaults to the bottom-right cell
    perfect=True,           # one single path (default: playable board)
    seed=42,                # any int, for a reproducible maze
    pattern=True,           # draw the "42" pattern (default: True)
)
maze.generate(seed=7)       # re-roll the same object with a new seed
```

### Access the structure and the solution

`maze.grid` is a list of rows of integers, each integer being the bitmask of the
**closed** walls of one cell (`NORTH=1`, `EAST=2`, `SOUTH=4`, `WEST=8`). It is
the structure used internally, and it does not have to be read through the
output format:

```python
maze.grid[y][x]                 # walls of the cell (x, y)
maze.linked((0, 0), (1, 0))     # can one walk between both cells?
maze.exits((0, 0))              # number of open sides of a cell
maze.pattern_cells              # cells used by the "42" pattern
maze.corridors()                # every cell that is not in the pattern
maze.dead_ends()                # corridors with a single open side
maze.loops()                    # number of independent routes

maze.solve()                    # shortest path, as a list of (x, y)
maze.path_string()              # the same path, as "SSEENNE..."
maze.to_hex_rows()              # the wall map, one string per row
```

## Files

| File | Role |
| ---- | ---- |
| `a_maze_ing.py` | Main program: configuration parsing, error handling, entry point. |
| `mazegen/__init__.py` | The reusable `MazeGenerator` class and its documentation. |
| `display.py` | Terminal rendering and interactive menu. |
| `config.txt` | Default configuration. |
| `pyproject.toml`, `setup.cfg` | Package build and linter settings. |
| `mazegen-1.0.0-py3-none-any.whl` | The reusable module, ready for `pip`. |

### Reading the code

Every step above is one small function, in the order it runs:

| Step | Function |
| ---- | -------- |
| Read `KEY=VALUE` lines, check the mandatory keys | `read_config` |
| Convert one value, or complain | `as_int`, `as_cell`, `as_bool` |
| Build the maze from the configuration | `build_maze` |
| Reserve the "42" cells | `MazeGenerator._place_pattern` |
| Carve the corridors (DFS) | `MazeGenerator._carve` |
| Remove the dead-ends (braiding) | `MazeGenerator._braid` |
| Refuse a wall that would open a 3x3 room | `_too_wide`, `_is_room` |
| Find the shortest path (BFS) | `MazeGenerator.solve` |
| Write the output file | `MazeGenerator.save` |
| Name every block of the canvas | `_canvas` and its `_draw_*` helpers |
| Colour the blocks and print them | `render`, `_paint` |
| Show the menu and react | `run` |

Only three helpers know about the geometry of the maze, and every other function
goes through them: `_direction` (which wall stands between two cells),
`_neighbours` (the cells one may walk to) and `linked` (is that wall open?).
That is why no bitmask arithmetic is ever written twice.

## Bonus

The default board is fully **braided**: it has no dead-end at all, so a chased
player is never trapped (`--max-dead-ends 0`). This was checked on several
hundred mazes of different sizes and seeds.

## Team and project management

<!-- Fill in with your team. Roles below reflect the split we agreed on. -->

| Member | Role |
| ------ | ---- |
| mpinto-l | Generation algorithm, reusable module and packaging |
| `<login2>` | Configuration parsing, output format and error handling |
| `<login3>` | Terminal display, interactions and documentation |

**Anticipated planning and how it evolved.** The plan was to build the project
bottom-up: first the reusable generator, then the configuration and the output
file, then the display. The generator took longer than expected, because the
"42" pattern and the "no dead-end" rule interact: a badly drawn pattern traps
corridors that no braiding can fix. Redrawing the digits so every reserved cell
leaves its neighbours at least two ways out solved it, and the rest of the
planning held.

**What worked well and what could be improved.** Keeping the module free of any
knowledge about files and display made it easy to test on its own, and the
audit script (a few hundred mazes checked against every rule of the subject)
caught the pattern bug immediately. What could be improved: only one generation
algorithm is implemented, and the display is terminal-only — an MLX rendering
and a generation animation would be natural next steps.

**Tools.** Git, `make`, `flake8` and `mypy` (both the mandatory flags and
`--strict`), `venv` and `build` for the packaging.

## Resources

* [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) — Wikipedia, overview of the classic algorithms.
* [Buckblog: Maze Generation — Recursive Backtracking](https://weblog.jamisbuck.org/2010/12/27/maze-generation-recursive-backtracking) — Jamis Buck, the reference explanation of the algorithm used here.
* *Mazes for Programmers*, Jamis Buck (Pragmatic Bookshelf) — braiding, dead-end removal and maze quality.
* [Think Labyrinth: Maze Algorithms](http://www.astrolog.org/labyrnth/algrithm.htm) — Walter Pullen, taxonomy of mazes (perfect, braided, unicursal).
* [Spanning tree](https://en.wikipedia.org/wiki/Spanning_tree) — Wikipedia, the graph theory behind perfect mazes.
* [Python `random`](https://docs.python.org/3/library/random.html), [`collections.deque`](https://docs.python.org/3/library/collections.html#collections.deque), [Packaging Python projects](https://packaging.python.org/en/latest/tutorials/packaging-projects/) — official documentation.
* [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code) — 24-bit colours used by the terminal display.

### How AI was used

AI (Claude) was used as a coding assistant on this project, mainly to:

* turn the subject into an explicit checklist of rules to satisfy, and discuss
  the trade-offs between generation algorithms before choosing one;
* write a first version of the generation, display and packaging code, which we
  then read, questioned and reworked — the "42" pattern in particular was
  redesigned by hand after the audit showed it forced dead-ends;
* write the audit script that checks every rule of the subject (wall coherence,
  connectivity, corridor width, loops, dead-ends, output format) on hundreds of
  random mazes.

It was **not** used as a substitute for understanding: every part of the code is
explained above, and we can walk through the algorithm, the bitmask encoding and
the braiding pass on request.
