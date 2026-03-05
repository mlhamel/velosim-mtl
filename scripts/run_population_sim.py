from velosim.models import WeatherState, PolicyState
from velosim.engine import DecisionEngine
from velosim.router import Router
from velosim.population import PopulationGenerator
from velosim.terminal_viz import PopulationDashboard
import polars as pl
import os

def run_large_sim(pop_size: int = 100):
    graph_path = "data/montreal_bike_network.graphml"
    
    router = Router(graph_path)
    engine = DecisionEngine(model_name="llama3.2")
    pop_gen = PopulationGenerator(graph_path)
    
    population = pop_gen.generate(pop_size)
    
    # A snowy day
    weather = WeatherState(
        temperature=-6.0, 
        snow_depth_cm=5.0, 
        is_raining=False, 
        is_snowing=False, 
        wind_speed_kmh=15.0
    )
    
    # ── Start live dashboard ─────────────────────────────────────────────
    dashboard = PopulationDashboard(pop_size=pop_size, weather=weather)
    dashboard.start()
    
    try:
        # Analyze routes first
        dashboard.begin_route_analysis()
        for c in population:
            c.current_route = router.get_route_analysis(c.home_coords, c.work_coords)
            dashboard.advance_route()
        
        scenarios = [
            PolicyState(snow_clearing_priority=False),
            PolicyState(snow_clearing_priority=True)
        ]
        
        results = []
        
        for policy in scenarios:
            policy_label = "Priority" if policy.snow_clearing_priority else "Standard"
            dashboard.begin_scenario(policy, policy_label)
            
            for citizen in population:
                # Distance logic
                if citizen.current_route.total_distance_km == 0:
                    mode = "metro"
                    reasoning = "No route found."
                elif citizen.current_route.total_distance_km > 12.0:
                    mode = "car" if citizen.age > 30 else "metro"
                    reasoning = "Distance too long for winter commute."
                else:
                    try:
                        decision = engine.decide_commute(citizen, weather, policy)
                        mode = decision.mode
                        reasoning = decision.reasoning
                    except Exception as e:
                        mode = "metro"
                        reasoning = f"Error: {e}"
                
                dashboard.record_decision(mode)
                
                results.append({
                    "agent_id": citizen.id,
                    "home_lat": citizen.home_coords[0],
                    "home_lon": citizen.home_coords[1],
                    "work_lat": citizen.work_coords[0],
                    "work_lon": citizen.work_coords[1],
                    "dist_km": citizen.current_route.total_distance_km,
                    "protected_%": citizen.current_route.protected_percentage,
                    "policy": policy_label,
                    "mode": mode,
                    "age": citizen.age
                })
    finally:
        dashboard.stop()
    
    # ── Final summary (printed after dashboard closes) ───────────────────
    df = pl.DataFrame(results)
    
    summary = df.group_by(["policy", "mode"]).len().sort(["policy", "mode"])
    print(f"\n=== Modal Shift Summary (Population: {pop_size}) ===")
    print(summary)
    
    output_path = "data/sim_results.parquet"
    df.write_parquet(output_path)
    print(f"\nFull results saved to {output_path}")

if __name__ == "__main__":
    pop_size = int(os.environ.get("VELOSIM_POP_SIZE", 100))
    run_large_sim(pop_size)
