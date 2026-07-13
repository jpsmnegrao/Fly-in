VENV := venv
PYTHON := $(VENV)/bin/python3
PIP := $(VENV)/bin/pip
MAIN := main.py
# MAP ?= maps/medium/02_circular_loop.txt

# MAP ?= maps/easy/01_linear_path.txt
# 4 <= 6
# MAP ?= maps/easy/02_simple_fork.txt
# 4 <= 8
# MAP ?= maps/easy/03_basic_capacity.txt
# 4 <= 6
# MAP ?= maps/medium/01_dead_end_trap.txt
# 8 <= 12
MAP ?= maps/medium/02_circular_loop.txt
# infinite <= 15
# MAP ?= maps/medium/03_priority_puzzle.txt
# 8 <= 12
# MAP ?= maps/hard/01_maze_nightmare.txt
# 14 <= 30
# MAP ?= maps/hard/02_capacity_hell.txt
# 16 <= 35
# MAP ?= maps/hard/03_ultimate_challenge.txt
# 26 <= 45
# MAP ?= maps/challenger/01_the_impossible_dream.txt
# infinite <= 45

.PHONY: install run debug clean lint lint-strict

all: install

install:
	@if [ -d "$(VENV)" ]; then \
		echo "Already installed. Run 'make clean' and 'make install' to reinstall."; \
	else \
		python3 -m venv $(VENV); \
		$(PIP) install --upgrade pip; \
		$(PIP) install -r requirements.txt; \
		echo "Installation complete!"; \
	fi

run:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Not installed yet. Run 'make install' to setup the project."; \
	else \
		$(VENV)/bin/python $(MAIN) $(MAP); \
	fi

debug:
	$(PYTHON) -m pdb $(MAIN) $(MAP)

clean:
	@if [ ! -d "$(VENV)" ]; then \
		echo "Nothing to clean. Run 'make install' to setup the project."; \
	else \
		rm -rf $(VENV) .mypy_cache .pytest_cache/ ; \
		find . -type d -name "__pycache__" -exec rm -rf {} + ; \
		echo "Cleanup complete!"; \
	fi

lint:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	$(VENV)/bin/flake8 .
	$(VENV)/bin/mypy . --strict