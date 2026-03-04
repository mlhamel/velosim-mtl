# Colors for terminal output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
MAGENTA := \033[35m
CYAN := \033[36m
WHITE := \033[37m
BOLD := \033[1m
RESET := \033[0m

.PHONY: help setup sync fetch-data run-prototype run-spatial run-population run-temporal pull-model clean test lint check install dev-install visualize visualize-temporal visualize-heatmap visualize-map generate-report

# Default target: show help
help:
	@echo "$(BOLD)$(BLUE)🚴 VeloSim-MTL - Montreal Cycling Simulation$(RESET)"
	@echo ""
	@echo "$(BOLD)$(GREEN)📋 SETUP COMMANDS:$(RESET)"
	@echo "  $(CYAN)setup$(RESET)            - Complete setup (pull model, sync deps, fetch map data)"
	@echo "  $(CYAN)install$(RESET)          - Install project dependencies"
	@echo "  $(CYAN)dev-install$(RESET)      - Install project with dev dependencies"
	@echo "  $(CYAN)pull-model$(RESET)       - Pull the required LLM model (llama3.2) via Ollama"
	@echo "  $(CYAN)sync$(RESET)             - Sync Python dependencies using uv"
	@echo "  $(CYAN)fetch-data$(RESET)       - Fetch Montreal cycling network data from OSM"
	@echo ""
	@echo "$(BOLD)$(YELLOW)🧪 SIMULATION COMMANDS:$(RESET)"
	@echo "  $(CYAN)run-prototype$(RESET)    - Run the reasoning simulation prototype"
	@echo "  $(CYAN)run-spatial$(RESET)      - Run the spatial routing simulation"
	@echo "  $(CYAN)run-population$(RESET)   - Run large-scale population simulation"
	@echo "  $(CYAN)run-temporal$(RESET)     - Run 5-day weather/policy simulation"
	@echo ""
	@echo "$(BOLD)$(MAGENTA)📊 VISUALIZATION COMMANDS:$(RESET)"
	@echo "  $(CYAN)visualize$(RESET)        - Generate charts from simulation results"
	@echo "  $(CYAN)visualize-temporal$(RESET) - Generate charts from weekly simulation results"
	@echo "  $(CYAN)visualize-heatmap$(RESET) - Generate spatial demand heatmap"
	@echo "  $(CYAN)visualize-map$(RESET)     - Generate interactive Folium HTML map"
	@echo "  $(CYAN)generate-report$(RESET)   - Generate Markdown post-simulation report"
	@echo ""
	@echo "$(BOLD)$(RED)🔧 DEVELOPMENT COMMANDS:$(RESET)"
	@echo "  $(CYAN)test$(RESET)             - Run all tests using pytest"
	@echo "  $(CYAN)lint$(RESET)             - Run code linting (if available)"
	@echo "  $(CYAN)check$(RESET)            - Run syntax check on all Python files"
	@echo "  $(CYAN)clean$(RESET)            - Remove data and cache files"
	@echo ""

# ============================================================================
# 📋 SETUP COMMANDS
# ============================================================================

# Full setup
setup: pull-model sync fetch-data
	@echo "$(BOLD)$(GREEN)✅ Setup complete!$(RESET)"

# Install dependencies
install:
	@echo "$(BOLD)$(GREEN)📦 Installing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✅ Dependencies installed!$(RESET)"

# Install with dev dependencies
dev-install:
	@echo "$(BOLD)$(GREEN)📦 Installing with dev dependencies...$(RESET)"
	uv sync --group dev
	@echo "$(GREEN)✅ Dev dependencies installed!$(RESET)"

# Pull the Ollama model
pull-model:
	@echo "$(BOLD)$(GREEN)🤖 Checking Ollama installation...$(RESET)"
	@if ! command -v ollama > /dev/null; then \
		echo "$(RED)❌ Error: 'ollama' command not found.$(RESET)"; \
		echo "$(YELLOW)Please install Ollama first: curl -fsSL https://ollama.com/install.sh | sh$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)🔄 Pulling llama3.2 model...$(RESET)"
	ollama pull llama3.2
	@echo "$(GREEN)✅ Model pulled successfully!$(RESET)"

# Sync dependencies
sync:
	@echo "$(BOLD)$(GREEN)🔄 Syncing dependencies...$(RESET)"
	uv sync
	@echo "$(GREEN)✅ Dependencies synced!$(RESET)"

# Fetch OSM data
fetch-data:
	@echo "$(BOLD)$(GREEN)🗺️  Fetching Montreal cycling network data...$(RESET)"
	uv run scripts/fetch_data.py
	@echo "$(GREEN)✅ Data fetched successfully!$(RESET)"

# ============================================================================
# 🧪 SIMULATION COMMANDS
# ============================================================================

# Run prototype
run-prototype:
	@echo "$(BOLD)$(YELLOW)🧪 Running reasoning simulation prototype...$(RESET)"
	uv run scripts/run_prototype.py
	@echo "$(GREEN)✅ Prototype simulation completed!$(RESET)"

run-spatial:
	@echo "$(BOLD)$(YELLOW)🗺️  Running spatial routing simulation...$(RESET)"
	uv run scripts/run_spatial_prototype.py
	@echo "$(GREEN)✅ Spatial simulation completed!$(RESET)"

run-population:
	@echo "$(BOLD)$(YELLOW)👥 Running large-scale population simulation...$(RESET)"
	uv run scripts/run_population_sim.py
	@echo "$(GREEN)✅ Population simulation completed!$(RESET)"

# Run temporal simulation
run-temporal:
	@echo "$(BOLD)$(YELLOW)🗓️  Running 5-day temporal simulation...$(RESET)"
	uv run scripts/run_temporal_sim.py
	@echo "$(GREEN)✅ Temporal simulation completed!$(RESET)"

# ============================================================================
# 📊 VISUALIZATION COMMANDS
# ============================================================================

# Generate visualizations
visualize:
	@echo "$(BOLD)$(MAGENTA)📊 Generating charts from simulation results...$(RESET)"
	uv run scripts/visualize_results.py
	@echo "$(MAGENTA)✅ Visualization charts generated!$(RESET)"

# Generate temporal visualizations
visualize-temporal:
	@echo "$(BOLD)$(MAGENTA)📊 Generating temporal charts...$(RESET)"
	uv run scripts/visualize_temporal.py
	@echo "$(MAGENTA)✅ Temporal visualization charts generated!$(RESET)"

# Generate spatial demand heatmap
visualize-heatmap:
	@echo "$(BOLD)$(MAGENTA)🗺️  Generating spatial demand heatmap...$(RESET)"
	uv run scripts/visualize_heatmap.py
	@echo "$(MAGENTA)✅ Demand heatmap generated!$(RESET)"

# Generate interactive Folium map
visualize-map:
	@echo "$(BOLD)$(MAGENTA)🗺️  Generating interactive Folium map...$(RESET)"
	uv run scripts/visualize_map.py
	@echo "$(MAGENTA)✅ Interactive map generated!$(RESET)"

# Generate post-simulation Markdown report
generate-report:
	@echo "$(BOLD)$(MAGENTA)📝 Generating post-simulation report...$(RESET)"
	uv run scripts/generate_report.py
	@echo "$(MAGENTA)✅ Simulation report generated!$(RESET)"

# ============================================================================
# 🔧 DEVELOPMENT COMMANDS
# ============================================================================

# Run tests
test:
	@echo "$(BOLD)$(RED)🧪 Running tests...$(RESET)"
	@if [ -d "tests" ]; then \
		uv run pytest; \
		echo "$(GREEN)✅ Tests completed!$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  No tests directory found. Create tests/ directory and add test files.$(RESET)"; \
	fi

# Syntax check all Python files
check:
	@echo "$(BOLD)$(RED)🔍 Checking Python syntax...$(RESET)"
	@find . -name "*.py" -not -path "./.venv/*" -exec python -m py_compile {} \;
	@echo "$(GREEN)✅ All Python files have valid syntax$(RESET)"

# Run linting (if ruff or flake8 is available)
lint:
	@echo "$(BOLD)$(RED)🧩 Running code linter...$(RESET)"
	@if command -v ruff > /dev/null; then \
		echo "$(CYAN)Using ruff linter...$(RESET)"; \
		uv run ruff check .; \
		echo "$(GREEN)✅ Linting completed!$(RESET)"; \
	elif command -v flake8 > /dev/null; then \
		echo "$(CYAN)Using flake8 linter...$(RESET)"; \
		uv run flake8 .; \
		echo "$(GREEN)✅ Linting completed!$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  No linter found. Install ruff or flake8 for code linting.$(RESET)"; \
	fi

# Cleanup
clean:
	@echo "$(BOLD)$(RED)🧹 Cleaning up data files...$(RESET)"
	rm -rf data/*.graphml data/*.gpkg
	@echo "$(GREEN)✅ Cleanup completed!$(RESET)"
