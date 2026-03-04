from velosim.models import WeatherState, PolicyState, TransportMode
from velosim.engine import DecisionEngine
from velosim.router import Router
from velosim.population import PopulationGenerator
from velosim.terminal_viz import TemporalDashboard
import polars as pl
import os

def run_temporal_sim(pop_size: int = 10):
    graph_path = "data/montreal_bike_network.graphml"
    router = Router(graph_path)
    engine = DecisionEngine(model_name="llama3.2")
    pop_gen = PopulationGenerator(graph_path)
    
    population = pop_gen.generate(pop_size)
    for c in population:
        c.current_route = router.get_route_analysis(c.home_coords, c.work_coords)

    # Define a 5-day "Stormy Week"
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    week_weather = [
        WeatherState(temperature=-2.0, snow_depth_cm=0.0, is_raining=False, is_snowing=False, wind_speed_kmh=10.0), # Mon: Clear
        WeatherState(temperature=-5.0, snow_depth_cm=15.0, is_raining=False, is_snowing=True, wind_speed_kmh=30.0), # Tue: Big Storm
        WeatherState(temperature=-8.0, snow_depth_cm=12.0, is_raining=False, is_snowing=False, wind_speed_kmh=20.0), # Wed: Cold & Slushy
        WeatherState(temperature=-10.0, snow_depth_cm=8.0, is_raining=False, is_snowing=False, wind_speed_kmh=15.0), # Thu: Frozen
        WeatherState(temperature=-4.0, snow_depth_cm=2.0, is_raining=False, is_snowing=False, wind_speed_kmh=10.0), # Fri: Cleared
    ]

    scenarios = [
        PolicyState(snow_clearing_priority=False),
        PolicyState(snow_clearing_priority=True)
    ]

    # ── Start live dashboard ─────────────────────────────────────────────
    dashboard = TemporalDashboard(pop_size=pop_size, num_days=len(week_weather))
    dashboard.start()

    all_results = []

    try:
        for policy in scenarios:
            policy_label = "Priority" if policy.snow_clearing_priority else "Standard"
            dashboard.begin_scenario(policy, policy_label)
            
            # Reset population memory for each policy scenario
            for c in population:
                c.bad_day_history = []

            for day_idx, weather in enumerate(week_weather):
                day_name = day_names[day_idx]
                dashboard.begin_day(day_name, weather)
                
                for citizen in population:
                    decision = engine.decide_commute(citizen, weather, policy)
                    
                    # Update Memory: 
                    # If they bike in > 5cm snow OR < -7C, it's a "bad experience"
                    is_bad = (decision.mode == TransportMode.BIKE) and (weather.snow_depth_cm > 5.0 or weather.temperature < -7.0)
                    citizen.bad_day_history.append(is_bad)
                    if len(citizen.bad_day_history) > 7:
                        citizen.bad_day_history.pop(0)

                    # Compute average frustration across the population
                    avg_frust = sum(c.frustration_level for c in population) / len(population)
                    dashboard.record_decision(str(decision.mode.value), avg_frustration=avg_frust)

                    all_results.append({
                        "policy": policy_label,
                        "day": day_idx + 1,
                        "day_name": day_name,
                        "agent_id": citizen.id,
                        "mode": str(decision.mode.value),
                        "frustration": citizen.frustration_level,
                        "snow": weather.snow_depth_cm
                    })

                dashboard.end_day()
    finally:
        dashboard.stop()

    # ── Final summary (printed after dashboard closes) ───────────────────
    df = pl.DataFrame(all_results)
    
    summary = df.group_by(["policy", "day", "day_name", "mode"]).len().sort(["policy", "day"])
    print("\n=== Weekly Simulation Results ===")
    print(summary)
    
    output_path = "data/temporal_results.parquet"
    df.write_parquet(output_path)
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    run_temporal_sim(10)
