VENV    := .venv
PY      := $(VENV)/bin/python
CONFIG  ?= config.txt
MAIN    := a_maze_ing.py

MYPY_FLAGS := --warn-return-any --warn-unused-ignores \
              --ignore-missing-imports --disallow-untyped-defs \
              --check-untyped-defs

.PHONY: all install run debug lint lint-strict package clean

all: run

# Development tools, installed in a local virtual environment.
$(VENV):
	python3 -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install flake8 mypy build

install: $(VENV)

# The program itself only needs the standard library.
run:
	python3 ./$(MAIN) $(CONFIG)

debug:
	python3 -m pdb ./$(MAIN) $(CONFIG)

lint: $(VENV)
	$(PY) -m flake8 .
	$(PY) -m mypy . $(MYPY_FLAGS)

lint-strict: $(VENV)
	$(PY) -m flake8 .
	$(PY) -m mypy . --strict

# Build the reusable module as a wheel, at the root of the repository.
package: $(VENV)
	rm -f mazegen-*.whl
	$(PY) -m build --wheel
	cp dist/mazegen-*.whl .

clean:
	rm -rf __pycache__ mazegen/__pycache__ .mypy_cache build dist *.egg-info
