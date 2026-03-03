import ollama
from .models import CitizenPersona, WeatherState, PolicyState, CommuteDecision, TransportMode
import json

class DecisionEngine:
    def __init__(self, model_name: str = "llama3.2"):
        self.model_name = model_name

    def decide_commute(self, citizen: CitizenPersona, weather: WeatherState, policy: PolicyState) -> CommuteDecision:
        """Asks Ollama to decide the commute mode for a specific citizen."""
        
        prompt = f"""
        Role: You are simulating a resident of Montreal deciding how to commute to work today.
        
        Person Profile:
        - Name: {citizen.name}
        - Age: {citizen.age}
        - Fitness Level: {citizen.fitness_level}/1.0
        - Commute Distance: {citizen.commute_distance_km} km
        - Winter Cycling Experience: {'Yes' if citizen.winter_cycling_experience else 'No'}
        - Owns E-Bike: {'Yes' if citizen.has_e_bike else 'No'}
        
        Current Conditions:
        - Temperature: {weather.temperature}°C
        - Snow on ground: {weather.snow_depth_cm} cm
        - Precipitation: {'Snowing' if weather.is_snowing else ('Raining' if weather.is_raining else 'None')}
        - Wind: {weather.wind_speed_kmh} km/h
        
        City Policy:
        - Priority Snow Clearing on Bike Paths: {'Active' if policy.snow_clearing_priority else 'Inactive'}
        
        Task: 
        Decide the mode of transport (bike, metro, bus, car, or walk). 
        Consider the discomfort of cold, the safety risk of snow, and the efficiency of priority clearing.
        Montrealers are resilient, but they also value safety and comfort.
        
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
