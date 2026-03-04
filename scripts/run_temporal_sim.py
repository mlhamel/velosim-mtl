from velosim.models import WeatherState, PolicyState, TransportMode
from velosim.engine import DecisionEngine
from velosim.router import Router
from velosim.population import PopulationGenerator
import polars as pl
from tqdm import tqdm
import os

def run_temporal_sim(pop_size: int = 10):
    graph_path = "data/montreal_bike_network.graphml"
    router = Router(graph_path)
    engine = DecisionEngine(model_name="llama3.2")
    pop_gen = PopulationGenerator(graph_path)
    
    print(f"Generating population of {pop_size} agents...")
    population = pop_gen.generate(pop_size)
    for c in population:
        c.current_route = router.get_route_analysis(c.home_coords, c.work_coords)

    # Define a 5-day "Stormy Week"
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

    all_results = []

    for policy in scenarios:
        policy_label = "Priority" if policy.snow_clearing_priority else "Standard"
        print(f"\n--- Starting 5-Day Simulation for Policy: {policy_label} ---")
        
        # Reset population memory for each policy scenario
        for c in population:
            c.bad_day_history = []

        for day_idx, weather in enumerate(week_weather):
            day_name = ["Mon", "Tue", "Wed", "Thu", "Fri"][day_idx]
            print(f"\n[Day {day_idx+1}: {day_name}] Temp: {weather.temperature}C, Snow: {weather.snow_depth_cm}cm")
            
            for citizen in tqdm(population, desc=f"Deciding for {day_name}"):
                decision = engine.decide_commute(citizen, weather, policy)
                
                # Update Memory: 
                # If they bike in > 5cm snow OR < -7C, it's a "bad experience"
                is_bad = (decision.mode == TransportMode.BIKE) and (weather.snow_depth_cm > 5.0 or weather.temperature < -7.0)
                citizen.bad_day_history.append(is_bad)
                if len(citizen.bad_day_history) > 7:
                    citizen.bad_day_history.pop(0)

                all_results.append({
                    "policy": policy_label,
                    "day": day_idx + 1,
                    "day_name": day_name,
                    "agent_id": citizen.id,
                    "mode": str(decision.mode.value),
                    "frustration": citizen.frustration_level,
                    "snow": weather.snow_depth_cm
                })

    df = pl.DataFrame(all_results)
    
    # Summary of modal shift over the week
    summary = df.group_by(["policy", "day", "day_name", "mode"]).len().sort(["policy", "day"])
    print("\n=== Weekly Simulation Results ===")
    print(summary)
    
    output_path = "data/temporal_results.parquet"
    df.write_parquet(output_path)
    print(f"\nResults saved to {output_path}")

if __name__ == "__main__":
    run_temporal_sim(10)
