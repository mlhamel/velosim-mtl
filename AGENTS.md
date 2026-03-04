# AGENTS.md - Repository Context for AI Agents

## 🎯 Project Overview

**VeloSim-MTL** is a multi-agent simulation of cycling patterns in Montreal that uses local LLMs (Ollama) to simulate human decision-making under varying weather and policy conditions.

### Core Objectives
- Measure the impact of snow clearing policies on winter cycling adoption
- Simulate modal shift (Car/Metro → Bike) based on infrastructure improvements  
- Use local AI agents to model human perception of safety and comfort

## 🏗️ Technical Architecture

### Environment Setup
- **Python**: 3.12.9 (managed via `uv`)
- **LLM Backend**: Ollama (local inference with llama3.2 model)
- **Geographic Data**: OpenStreetMap via `osmnx`
- **Data Processing**: Polars for analysis, Matplotlib/Seaborn for visualization
- **Agent Modeling**: Pydantic for structured data models

### Project Structure
```
velosim-mtl/
├── src/velosim/
│   ├── models.py          # Pydantic models (CitizenPersona, WeatherState, etc.)
│   ├── engine.py          # DecisionEngine using Ollama for commute decisions
│   ├── router.py          # Spatial routing and pathfinding
│   └── population.py      # Population generation and management
├── scripts/
│   ├── run_prototype.py           # Basic reasoning simulation
│   ├── run_spatial_prototype.py   # Spatial routing simulation
│   ├── run_population_sim.py      # Large-scale population simulation
│   ├── run_temporal_sim.py        # 5-day weather/policy simulation
│   ├── visualize_results.py       # Generate charts from results
│   ├── visualize_temporal.py      # Generate temporal charts
│   └── fetch_data.py              # Download OSM cycling network data
├── data/                  # Generated simulation results and map data
├── cache/                # Ollama response caching
└── notebooks/            # Jupyter notebooks for analysis
```

## 📊 Key Models & Components

### CitizenPersona (Pydantic Model)
- **Attributes**: age, fitness_level, winter_cycling_experience, has_e_bike
- **Spatial**: home_coords, work_coords (Montreal lat/lon)
- **Memory**: bad_day_history (tracks recent poor commute experiences)
- **Route Analysis**: current_route with distance, protected path percentage, duration

### DecisionEngine
- Uses Ollama (llama3.2) for natural language reasoning
- Takes CitizenPersona + WeatherState + PolicyState → CommuteDecision
- Returns structured JSON with mode, reasoning, and confidence

### Simulation Types
1. **Prototype**: Basic reasoning with 3 personas, snowy weather, 2 policy scenarios
2. **Spatial**: Routing-aware simulation using OSM bike network
3. **Population**: Large-scale simulation (1000+ agents from Census data)
4. **Temporal**: Multi-day weather progression simulation

## 🚀 Development Workflow

### Essential Commands
```bash
# Complete setup (first time)
make setup              # Pulls llama3.2, installs deps, fetches OSM data

# Run simulations
make run-prototype      # Quick reasoning test with 3 personas
make run-spatial        # Spatial routing simulation
make run-population     # Large-scale population simulation  
make run-temporal       # 5-day weather/policy simulation

# Generate visualizations
make visualize          # Charts from simulation results
make visualize-temporal # Temporal analysis charts

# Development
make test              # Run pytest (if tests/ exists)
make lint              # Code linting with ruff/flake8
make check             # Python syntax validation
make clean             # Remove data and cache files
```

### Dependencies Management
- **Package Manager**: `uv` (modern, fast Python package manager)
- **Virtual Environment**: `.venv/` (automatically managed by `uv`)
- **Production deps**: Listed in `pyproject.toml` under `dependencies`
- **Dev deps**: Listed under `dependency-groups.dev`

## 🗺️ Geographic Context

### Montreal Focus Areas
- **Plateau**: (45.5236, -73.5828) - Dense, bike-friendly neighborhood
- **Downtown**: (45.5017, -73.5673) - Business district
- **Rosemont**: (45.5468, -73.5905) - Residential area
- **Mile End**: (45.5260, -73.5950) - Creative district

### Infrastructure Data
- **Source**: OpenStreetMap cycling network via `osmnx`
- **Files**: `montreal_bike_network.graphml`, `montreal_bike_edges/nodes.gpkg`
- **Analysis**: Protected bike path percentage, route distances, elevation

## 🧪 Simulation Results

### Output Files
- **sim_results.parquet**: Population simulation results
- **temporal_results.parquet**: Multi-day simulation results  
- **Visualizations**: PNG charts in `data/` directory

### Key Metrics
- **Modal Split**: Distribution of transport choices (bike/metro/bus/car/walk)
- **Policy Impact**: Comparison between standard vs. priority snow clearing
- **Weather Sensitivity**: How conditions affect cycling adoption
- **Infrastructure Impact**: Effect of protected bike lane coverage

## 🤖 LLM Integration

### Ollama Configuration
- **Model**: llama3.2 (pulled via `ollama pull llama3.2`)
- **Response Format**: Structured JSON with mode, reasoning, confidence
- **Caching**: Responses cached in `cache/` directory for performance
- **Local Inference**: No external API calls, fully local processing

### Decision Reasoning
The LLM considers:
- Personal characteristics (age, fitness, experience)
- Route analysis (distance, protected paths, duration)  
- Weather conditions (temperature, snow, wind)
- Policy context (snow clearing priority)
- Memory (recent bad experiences)

## 🔄 Recent Changes

### Latest Commits
- **bd178c0**: Improve makefile (enhanced help system, colored output)
- **d3ecca9**: Adds temporal simulation (5-day weather progression)
- **f13330f**: Adds visualization (charts and analysis tools)
- **221ee07**: Initial commit - base setup

### Current Status
- ✅ Project successfully pushed to GitHub (`origin/main`)  
- ✅ Full development environment setup with uv
- ✅ Ollama integration working with llama3.2
- ✅ OSM data fetching and processing pipeline
- ✅ Multi-scenario simulation capability
- ✅ Visualization and analysis tools

## 💡 Guidelines for AI Agents

### Before Making Changes
1. **Run existing simulations** to understand current behavior:
   ```bash
   make run-prototype  # Quick test
   make visualize      # See current outputs
   ```

2. **Check dependencies** before adding new packages:
   ```bash
   uv add <package-name>  # Adds to pyproject.toml and installs
   ```

3. **Validate Ollama connectivity**:
   ```bash
   ollama list  # Check if llama3.2 is available
   ```

### Development Best Practices
- **Follow existing patterns**: Use Pydantic models for structured data
- **Test incrementally**: Start with `run-prototype` before large simulations
- **Cache-aware**: Large simulations cache LLM responses for efficiency
- **Montreal-centric**: Use realistic Montreal coordinates and neighborhoods
- **Memory-based reasoning**: Citizens remember recent experiences (frustration_level)

### Simulation Workflow
1. **Define personas** with realistic Montreal demographics
2. **Set weather/policy scenarios** to test specific hypotheses
3. **Run simulation** with appropriate script (prototype/spatial/population/temporal)
4. **Generate visualizations** to analyze results
5. **Iterate** based on findings

### Common Issues & Solutions
- **Ollama not running**: `ollama pull llama3.2` and ensure service is active
- **Missing map data**: `make fetch-data` to download OSM network
- **Cache issues**: `make clean` to reset data and cache files
- **Dependency conflicts**: `uv sync` to reconcile virtual environment

## 🎯 Future Development Areas

### Roadmap (from README)
- [x] Initial project scaffolding
- [x] Basic Citizen/Weather/Policy models  
- [x] Ollama integration for decision making
- [x] Makefile automation for setup and model management
- [ ] Integration with OSM graph for pathfinding
- [ ] Population generator (1,000+ agents from Census data)
- [ ] Time-series simulation (365 days of weather data)

### Potential Enhancements
- **Real-time weather integration** (Environment Canada API)
- **Census-based population generation** (Statistics Canada data)
- **Advanced routing algorithms** (elevation-aware, safety-weighted)
- **Policy scenario expansion** (bike-share, e-bike subsidies)
- **Validation against real data** (Eco-Counter bike path sensors)

---

*This document serves as a comprehensive guide for AI agents working on the VeloSim-MTL project. Always refer to the latest README.md and codebase for the most current information.*