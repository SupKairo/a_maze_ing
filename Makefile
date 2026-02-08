PYTHON = python3
PIP = pip3
MAIN_SCRIPT = a_maze_ing.py
CONFIG_FILE = config.txt

install:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install flake8 mypy
	@echo "Dependencies installed successfully!"

run:
	$(PYTHON) $(MAIN_SCRIPT) $(CONFIG_FILE)

debug:
	$(PYTHON) -m pdb $(MAIN_SCRIPT) $(CONFIG_FILE)

clean:
	@find . -type d -name "__pycache__" | xargs rm -rf
	@find . -type d -name ".mypy_cache" | xargs rm -rf
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name "*.log" -delete
	@echo "Cleaned..."

lint:
	@echo "Running flake8..."
	flake8 .
	@echo ""
	@echo "Running mypy..."
	@mypy . --explicit-package-bases --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
	@echo ""
	@echo "Linting complete!"

lint-strict:
	@echo "Running flake8..."
	flake8 .
	@echo ""
	@echo "Running mypy (strict mode)..."
	mypy . --strict --explicit-package-bases
	@echo ""
	@echo "Strict linting complete!"

.PHONY: help install run debug clean lint lint-strict