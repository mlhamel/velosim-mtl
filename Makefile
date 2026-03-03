.PHONY: help setup sync fetch-data run-prototype pull-model clean

# Default target: show help
help:
	@echo "VeloSim-MTL Management Commands:"
	@echo "  setup            - Complete setup (pull model, sync deps, fetch map data)"
	@echo "  pull-model       - Pull the required LLM model (llama3.2) via Ollama"
	@echo "  sync             - Sync Python dependencies using uv"
	@echo "  fetch-data       - Fetch Montreal cycling network data from OSM"
	@echo "  run-prototype    - Run the reasoning simulation prototype"
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

# Cleanup
clean:
	rm -rf data/*.graphml data/*.gpkg
