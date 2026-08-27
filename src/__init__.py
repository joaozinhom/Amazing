"""The runnable program around the reusable :mod:`mazegen` library.

Where :mod:`mazegen` is the throwaway-free, importable maze generator,
this package is the program around it: it reads the configuration file
(:mod:`src.config`), draws the maze in the terminal (:mod:`src.canvas`
and :mod:`src.render`) and runs the interactive menu (:mod:`src.menu`).
The thin ``a_maze_ing.py`` entry point at the repository root wires these
together.
"""
