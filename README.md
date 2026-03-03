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
- [uv](https://github.com/astral-sh/uv)
- [Ollama](https://ollama.ai/) running locally.
  - *On Linux, you can install it with:* `curl -fsSL https://ollama.com/install.sh | sh`

### Installation & Setup

1.  **Full Setup:**
    This will pull the required model, sync dependencies, and fetch initial map data.
    ```bash
    make setup
    ```

    *Alternatively, step-by-step:*
    ```bash
    make pull-model  # Pulls llama3.2 via Ollama
    make sync        # Installs Python deps
    make fetch-data  # Downloads OSM bike network
    ```

### Run the Simulation

To run the reasoning prototype and see how different personas decide their commute:
```bash
make run-prototype
```

## 📈 Roadmap
- [x] Initial project scaffolding.
- [x] Basic Citizen/Weather/Policy models.
- [x] Ollama integration for decision making.
- [x] Makefile automation for setup and model management.
- [ ] Integration with OSM graph for pathfinding.
- [ ] Population generator (generating 1,000+ agents from Census data).
- [ ] Time-series simulation (365 days of weather data).
