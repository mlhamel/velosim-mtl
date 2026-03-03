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

## 🟡 Phase 3: Population & Scale (Current)
- [x] **Population Generator:** Create 100+ diverse agents based on spatial sampling.
- [ ] **Batch Decision Engine:** Optimize Ollama calls for larger populations.
- [ ] **Aggregate Analysis:** Compare modal shifts across policy scenarios.

## ⚪ Phase 4: Visualization & Reporting
- [ ] **Demand Heatmaps:** Map route usage intensity.
- [ ] **Policy Dashboard:** Charts showing modal shift percentages.
- [ ] **Folium Maps:** Interactive HTML maps of simulated routes.

## ⚪ Phase 5: Temporal Simulation
- [ ] **Weather Time-Series:** Simulate a full winter week.
- [ ] **Agent Memory:** Cumulative fatigue/experience influencing decisions.
- [ ] **Feedback Loops:** High traffic density impacting route attractiveness.
