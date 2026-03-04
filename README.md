# VeloSim-MTL

A multi-agent simulation of cycling patterns in Montreal, powered by local LLMs (Ollama) to simulate human reasoning under varying weather and policy conditions.

## 🎯 Objectives
- Measure the impact of **snow clearing policies** on winter cycling adoption.
- Simulate **modal shift** (Car/Metro -> Bike) based on infrastructure improvements.
- Use **local AI agents** to model human perception of safety and comfort.

## 🏗️ Architecture
- **Environment:** OpenStreetMap (OSM) data processed via `osmnx`.
- **Agents:** Pydantic models for diverse citizen personas.
- **Decision Engine:** Ollama (Llama 3.2) simulating individual commute choices.
- **Analysis:** Polars for data processing and Matplotlib for visualization.

## 🚀 Getting Started

### Prerequisites

#### 1. Install uv (Python Package Manager)
[uv](https://github.com/astral-sh/uv) is a modern, fast Python package and project manager written in Rust.

**Installation options:**
```bash
# Option 1: Using the official installer (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Option 2: Using pip (if you have Python already)
pip install uv

# Option 3: Using your system package manager
# On macOS with Homebrew:
brew install uv
# On Arch Linux:
pacman -S uv
```

**Why uv?**
- ⚡ **10-100x faster** than pip for dependency resolution
- 🔒 **Automatic virtual environment management**
- 📦 **Unified tool** for dependency management, project creation, and Python version management
- 🎯 **Drop-in replacement** for pip, pip-tools, and virtualenv

#### 2. Install Ollama (Local LLM)
[Ollama](https://ollama.ai/) provides local LLM inference for the decision engine.

```bash
# On Linux/macOS:
curl -fsSL https://ollama.com/install.sh | sh

# On Windows:
# Download from https://ollama.ai/download
```

### Installation & Setup

#### Quick Start (Recommended)
The Makefile handles everything automatically:
```bash
make setup
```
This command will:
1. Pull the required Ollama model (llama3.2)
2. Create and sync Python virtual environment with uv
3. Download Montreal cycling network data from OpenStreetMap

#### Manual Step-by-Step Setup
If you prefer to run each step manually:

```bash
# 1. Pull the LLM model
make pull-model

# 2. Install Python dependencies (creates .venv/ automatically)
make sync

# 3. Download Montreal OSM cycling network
make fetch-data
```

#### Working with uv Directly
If you want to use uv commands directly instead of the Makefile:

```bash
# Install dependencies and create virtual environment
uv sync

# Add new dependencies
uv add package-name

# Add development dependencies  
uv add --group dev package-name

# Run Python scripts
uv run python script.py
uv run scripts/run_prototype.py

# Activate virtual environment manually (optional)
source .venv/bin/activate  # Linux/macOS
# OR
.venv\Scripts\activate     # Windows
```

### Run Simulations

Once setup is complete, you can run different types of simulations:

```bash
# Quick reasoning test with 3 personas
make run-prototype

# Spatial routing simulation
make run-spatial

# Large-scale population simulation
make run-population

# Multi-day weather progression simulation
make run-temporal

# Generate visualization charts
make visualize
```

### Development Workflow

```bash
# Check available commands
make help

# Run syntax checks
make check

# Run linting (if available)
make lint

# Clean generated files
make clean
```

## 📈 Roadmap
- [x] Initial project scaffolding.
- [x] Basic Citizen/Weather/Policy models.
- [x] Ollama integration for decision making.
- [x] Makefile automation for setup and model management.
- [ ] Integration with OSM graph for pathfinding.
- [ ] Population generator (generating 1,000+ agents from Census data).
- [ ] Time-series simulation (365 days of weather data).
