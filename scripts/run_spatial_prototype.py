from velosim.models import CitizenPersona, WeatherState, PolicyState
from velosim.engine import DecisionEngine
from velosim.router import Router
import polars as pl
import os

def run_spatial_sim():
    # Initialize components
    graph_path = "data/montreal_bike_network.graphml"
    if not os.path.exists(graph_path):
        print("Data not found. Running fetch_data.py...")
        from scripts.fetch_data import fetch_montreal_cycling_network
        fetch_montreal_cycling_network()

    router = Router(graph_path)
    engine = DecisionEngine(model_name="llama3.2")
    
    # 1. Define Citizens with specific Montreal coordinates
    # Coordinates are approx (Lat, Lon)
    citizens = [
        CitizenPersona(
            id="1", name="Luc (Plateau to Downtown)", age=34, fitness_level=0.8, 
            winter_cycling_experience=True,
            home_coords=(45.5236, -73.5828), # Plateau
            work_coords=(45.5017, -73.5673)  # Downtown
        ),
        CitizenPersona(
            id="2", name="Sophie (Rosemont to Plateau)", age=28, fitness_level=0.5, 
            winter_cycling_experience=False,
            home_coords=(45.5468, -73.5905), # Rosemont
            work_coords=(45.5236, -73.5828)  # Plateau
        ),
        CitizenPersona(
            id="3", name="Andre (Petite-Patrie to Mile End)", age=55, fitness_level=0.4, 
            winter_cycling_experience=True, has_e_bike=True,
            home_coords=(45.5350, -73.6000), # Petite-Patrie
            work_coords=(45.5260, -73.5950)  # Mile End
        )
    ]
    
    # Pre-calculate routes for all citizens
    print("Calculating routes for all citizens...")
    for c in citizens:
        c.current_route = router.get_route_analysis(c.home_coords, c.work_coords)
        print(f"  - {c.name}: {c.current_route.total_distance_km}km ({c.current_route.protected_percentage*100:.0f}% protected)")
    
    # 2. Define Weather (A snowy day)
    weather = WeatherState(
        temperature=-5.0, snow_depth_cm=8.0, 
        is_raining=False, is_snowing=True, wind_speed_kmh=20.0
    )
    
    # 3. Define Scenarios
    scenarios = [
        PolicyState(snow_clearing_priority=False),
        PolicyState(snow_clearing_priority=True)
    ]
    
    results = []
    print(f"\nStarting Spatial Simulation (Weather: {weather.temperature}C, {weather.snow_depth_cm}cm snow)...")
    
    for policy in scenarios:
        policy_label = "Priority Clearing" if policy.snow_clearing_priority else "Standard Clearing"
        print(f"\n--- Scenario: {policy_label} ---")
        
        for citizen in citizens:
            decision = engine.decide_commute(citizen, weather, policy)
            print(f"[{citizen.name}] Distance: {citizen.current_route.total_distance_km}km | Protected: {citizen.current_route.protected_percentage*100:.0f}%")
            print(f"  -> Decision: {decision.mode.upper()}")
            print(f"  -> Reasoning: {decision.reasoning}")
            
            results.append({
                "name": citizen.name,
                "dist_km": citizen.current_route.total_distance_km,
                "protected_%": citizen.current_route.protected_percentage,
                "policy": policy_label,
                "mode": decision.mode,
                "reasoning": decision.reasoning
            })
            
    df = pl.DataFrame(results)
    print("\nDetailed Summary:")
    print(df)

if __name__ == "__main__":
    run_spatial_sim()
