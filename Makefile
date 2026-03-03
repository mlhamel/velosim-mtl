.PHONY: help setup sync fetch-data run-prototype run-spatial pull-model clean test lint check install dev-install

# Default target: show help
help:
	@echo "VeloSim-MTL Management Commands:"
	@echo "  setup            - Complete setup (pull model, sync deps, fetch map data)"
	@echo "  pull-model       - Pull the required LLM model (llama3.2) via Ollama"
	@echo "  sync             - Sync Python dependencies using uv"
	@echo "  fetch-data       - Fetch Montreal cycling network data from OSM"
	@echo "  run-prototype    - Run the reasoning simulation prototype"
	@echo "  run-spatial      - Run the spatial routing simulation"
	@echo "  run-population   - Run large-scale population simulation"
	@echo "  visualize        - Generate charts from simulation results"
	@echo "  test             - Run all tests using pytest"
	@echo "  lint             - Run code linting (if available)"
	@echo "  check            - Run syntax check on all Python files"
	@echo "  install          - Install project dependencies"
	@echo "  dev-install      - Install project with dev dependencies"
	@echo "  clean            - Remove data and cache files"

# Full setup
setup: pull-model sync fetch-data

# Pull the Ollama model
pull-model:
	@if ! command -v ollama > /dev/null; then \
		echo "Error: 'ollama' command not found."; \
		echo "Please install Ollama first: curl -fsSL https://ollama.com/install.sh | sh"; \
		exit 1; \
	fi
	ollama pull llama3.2

# Sync dependencies
sync:
	uv sync

# Fetch OSM data
fetch-data:
	uv run scripts/fetch_data.py

# Run prototype
run-prototype:
	uv run scripts/run_prototype.py

run-spatial:
	uv run scripts/run_spatial_prototype.py

run-population:
	uv run scripts/run_population_sim.py

# Generate visualizations
visualize:
	uv run scripts/visualize_results.py

# Install dependencies
install:
	uv sync

# Install with dev dependencies
dev-install:
	uv sync --group dev

# Run tests
test:
	@if [ -d "tests" ]; then \
		uv run pytest; \
	else \
		echo "No tests directory found. Create tests/ directory and add test files."; \
	fi

# Syntax check all Python files
check:
	@echo "Checking Python syntax..."
	@find . -name "*.py" -not -path "./.venv/*" -exec python -m py_compile {} \;
	@echo "✓ All Python files have valid syntax"

# Run linting (if ruff or flake8 is available)
lint:
	@if command -v ruff > /dev/null; then \
		echo "Running ruff linter..."; \
		uv run ruff check .; \
	elif command -v flake8 > /dev/null; then \
		echo "Running flake8 linter..."; \
		uv run flake8 .; \
	else \
		echo "No linter found. Install ruff or flake8 for code linting."; \
	fi

# Cleanup
clean:
	rm -rf data/*.graphml data/*.gpkg
