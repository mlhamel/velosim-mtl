from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class TransportMode(str, Enum):
    BIKE = "bike"
    METRO = "metro"
    BUS = "bus"
    CAR = "car"
    WALK = "walk"

class CitizenPersona(BaseModel):
    id: str
    name: str
    age: int
    fitness_level: float = Field(..., description="0.0 to 1.0 scale")
    winter_cycling_experience: bool = False
    has_e_bike: bool = False
    comfort_threshold_temp: float = Field(-10.0, description="Temperature below which they hesitate to bike")
    comfort_threshold_snow: float = Field(2.0, description="Snow depth in cm above which they hesitate")
    commute_distance_km: float
    
    # Memory of recent experiences
    bad_weather_experience_count: int = 0

class WeatherState(BaseModel):
    temperature: float
    snow_depth_cm: float
    is_raining: bool
    is_snowing: bool
    wind_speed_kmh: float

class PolicyState(BaseModel):
    snow_clearing_priority: bool = False  # If True, REV is cleared first
    protected_lane_network_coverage: float = 0.5 # 0 to 1 scale

class CommuteDecision(BaseModel):
    mode: TransportMode
    reasoning: str
    confidence: float
