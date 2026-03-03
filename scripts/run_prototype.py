from velosim.models import CitizenPersona, WeatherState, PolicyState
from velosim.engine import DecisionEngine
import polars as pl

def run_mini_sim():
    engine = DecisionEngine(model_name="llama3.2")
    
    # 1. Define Citizens with Montreal coordinates
    citizens = [
        CitizenPersona(
            id="1", name="Sébastien", age=34, fitness_level=0.8, 
            winter_cycling_experience=True,
            home_coords=(45.5236, -73.5828), # Plateau
            work_coords=(45.5017, -73.5673)  # Downtown
        ),
        CitizenPersona(
            id="2", name="Marie-Eve", age=28, fitness_level=0.5, 
            winter_cycling_experience=False,
            home_coords=(45.5468, -73.5905), # Rosemont
            work_coords=(45.5236, -73.5828)  # Plateau
        ),
        CitizenPersona(
            id="3", name="Jean-Francois", age=55, fitness_level=0.4, 
            winter_cycling_experience=False, has_e_bike=True,
            home_coords=(45.5350, -73.6000), # Petite-Patrie
            work_coords=(45.5260, -73.5950)  # Mile End
        )
    ]
    
    # 2. Define Weather (A snowy day in January)
    weather = WeatherState(
        temperature=-8.0, snow_depth_cm=10.0, 
        is_raining=False, is_snowing=True, wind_speed_kmh=25.0
    )
    
    # 3. Define Scenarios (Policies)
    scenarios = [
        PolicyState(snow_clearing_priority=False),
        PolicyState(snow_clearing_priority=True)
    ]
    
    results = []
    
    print(f"Starting Simulation Prototype (Weather: {weather.temperature}C, {weather.snow_depth_cm}cm snow)...")
    
    for policy in scenarios:
        policy_label = "Priority Clearing" if policy.snow_clearing_priority else "Standard Clearing"
        print(f"\n--- Scenario: {policy_label} ---")
        
        for citizen in citizens:
            decision = engine.decide_commute(citizen, weather, policy)
            print(f"[{citizen.name}] decides to take the {decision.mode.upper()}. Reasoning: {decision.reasoning}")
            
            results.append({
                "citizen": citizen.name,
                "policy": policy_label,
                "mode": decision.mode,
                "reasoning": decision.reasoning
            })
            
    df = pl.DataFrame(results)
    print("\nSummary Table:")
    print(df)

if __name__ == "__main__":
    run_mini_sim()
