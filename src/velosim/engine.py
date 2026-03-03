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

        prompt = f"""
        Role: You are simulating a resident of Montreal deciding how to commute to work today.
        
        Person Profile:
        - Name: {citizen.name}
        - Age: {citizen.age}
        - Fitness Level: {citizen.fitness_level}/1.0
        - Winter Cycling Experience: {'Yes' if citizen.winter_cycling_experience else 'No'}
        - Owns E-Bike: {'Yes' if citizen.has_e_bike else 'No'}
        
        {route_info}
        
        Current Conditions:
        - Temperature: {weather.temperature}°C
        - Snow on ground: {weather.snow_depth_cm} cm
        - Precipitation: {'Snowing' if weather.is_snowing else ('Raining' if weather.is_raining else 'None')}
        - Wind: {weather.wind_speed_kmh} km/h
        
        City Policy:
        - Priority Snow Clearing on Bike Paths (Protected lanes are cleared first): {'Active' if policy.snow_clearing_priority else 'Inactive'}
        
        Task: 
        Decide the mode of transport (bike, metro, bus, car, or walk). 
        
        Consider:
        1. If Priority Clearing is Active, the 'Protected Paths' part of the route will be safer and faster.
        2. If Priority Clearing is Inactive, even the protected paths will have snow.
        3. Long distances (>5km) are much harder in deep snow without an e-bike.
        
        Response Format:
        Return ONLY a JSON object with the following fields:
        {{
            "mode": "one of: bike, metro, bus, car, walk",
            "reasoning": "a short sentence explaining why",
            "confidence": 0.9
        }}
        """
        
        # Try up to 3 times to get a valid response
        for attempt in range(3):
            try:
                response = ollama.generate(model=self.model_name, prompt=prompt, format="json")
                data = json.loads(response['response'])
                
                # Normalize mode if it's an invalid variant
                if 'mode' in data:
                    mode = data['mode'].lower().strip()
                    if mode in ['e-bike', 'ebike', 'electric bike']:
                        data['mode'] = 'bike'  # Treat e-bike as regular bike
                    elif mode not in ['bike', 'metro', 'bus', 'car', 'walk']:
                        data['mode'] = 'metro'  # Default fallback
                
                return CommuteDecision(**data)
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                if attempt == 2:  # Last attempt
                    # Return a fallback decision
                    return CommuteDecision(
                        mode=TransportMode.METRO,
                        reasoning="System fallback due to parsing error",
                        confidence=0.5
                    )
                continue
