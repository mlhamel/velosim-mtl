# VeloSim-MTL Roadmap

## 🟢 Phase 1: Foundation (Completed)
- [x] Project scaffolding with `uv`.
- [x] Basic models for Citizen, Weather, and Policy.
- [x] Initial Ollama integration for decision making.
- [x] Makefile for automated setup.

## 🟢 Phase 2: Spatial Routing (Completed)
- [x] Fetch Montreal bike network from OSM.
- [x] Implementation of `Router` for shortest bike paths.
- [x] Resilient tag-checking for infrastructure analysis (REV detection).
- [x] Route-aware reasoning in Ollama.

## 🟢 Phase 3: Population & Scale (Completed)
- [x] **Population Generator:** Create 100+ diverse agents based on spatial sampling.
- [x] **Batch Decision Engine:** Run 200+ reasoning calls via Ollama.
- [x] **Data Persistence:** Save results to Parquet for analysis.

## 🟡 Phase 4: Visualization & Reporting (Current)
- [x] **Policy Comparison Charts:** Bar charts showing modal shift (Standard vs. Priority).
- [x] **Infrastructure Correlation:** Boxplots linking route protection % to biking decisions.
- [x] **Spatial Demand Heatmaps:** Map exact route segments to see which streets are most "demanded" by agents.
- [x] **Interactive Folium Map:** HTML map showing agent home/work clusters and chosen routes.

## ⚪ Phase 5: Temporal Simulation (Upcoming)
- [ ] **Weather Time-Series:** Simulate a full winter week (e.g., storm day followed by clearing days).
- [ ] **Agent Memory/Fatigue:** Cumulative "bad days" influencing long-term modal shift.
- [ ] **Post-Simulation Report:** Generate a Markdown summary of policy effectiveness.

## ⚪ Long-term Ideas
- [ ] **Eco-Counter Validation:** Compare simulated demand with real Montreal bike counter data.
- [ ] **Multi-Model Comparison:** Test if different LLMs (Mistral vs. Llama) "perceive" winter safety differently.
