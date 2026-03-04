import ollama
from .models import CitizenPersona, WeatherState, PolicyState, CommuteDecision, TransportMode
import json

class DecisionEngine:
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def decide_commute(self, citizen: CitizenPersona, weather: WeatherState, policy: PolicyState) -> CommuteDecision:
        """Asks Ollama to decide the commute mode for a specific citizen."""
        
        route_info = ""
        if citizen.current_route:
            ra = citizen.current_route
            route_info = f"""
            Route Analysis:
            - Total Distance: {ra.total_distance_km} km
            - Percentage on Protected Paths (REV, etc): {ra.protected_percentage * 100}%
            - Estimated Cycling Time: {ra.estimated_duration_min} minutes
            """

        memory_info = ""
        if citizen.frustration_level > 0:
            memory_info = f"Recent Experience: This person has had {sum(citizen.bad_day_history)} difficult commutes in the last 7 days. They are feeling frustrated and more likely to seek comfort."

        prompt = f"""
        Role: You are simulating a resident of Montreal deciding how to commute to work today.
        
        Person Profile:
        - Name: {citizen.name}
        - Age: {citizen.age}
        - Fitness Level: {citizen.fitness_level}/1.0
        - Winter Cycling Experience: {'Yes' if citizen.winter_cycling_experience else 'No'}
        - Owns E-Bike: {'Yes' if citizen.has_e_bike else 'No'}
        
        {route_info}
        {memory_info}
        
        Current Conditions:
        - Temperature: {weather.temperature}°C
        - Snow on ground: {weather.snow_depth_cm} cm
        - Precipitation: {'Snowing' if weather.is_snowing else ('Raining' if weather.is_raining else 'None')}
        - Wind: {weather.wind_speed_kmh} km/h
        
        City Policy:
        - Priority Snow Clearing on Bike Paths: {'Active' if policy.snow_clearing_priority else 'Inactive'}
        
        Task: 
        Decide the mode of transport (bike, metro, bus, car, or walk). 
        
        Consider:
        1. Memory matters: If they had a rough week, they might give up on biking today even if conditions are okay.
        2. Priority Clearing: Only helps if they are actually biking.
        
        Response Format:
        Return ONLY a JSON object with the following fields:
        {{
            "mode": "one of: bike, metro, bus, car, walk",
            "reasoning": "a short sentence explaining why",
            "confidence": 0.9
        }}
        """
        
        response = ollama.generate(model=self.model_name, prompt=prompt, format="json")
        data = json.loads(response['response'])
        
        return CommuteDecision(**data)
