"""The runnable program around the reusable :mod:`mazegen` library.

Where :mod:`mazegen` is the throwaway-free, importable maze generator,
this package is the *application*: it reads the configuration file
(:mod:`app.config`), draws the maze in the terminal (:mod:`app.canvas`
and :mod:`app.render`) and runs the interactive menu (:mod:`app.menu`).
The thin ``a_maze_ing.py`` entry point at the repository root wires these
together.
"""
