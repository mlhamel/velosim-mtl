from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict
from enum import Enum

class TransportMode(str, Enum):
    BIKE = "bike"
    METRO = "metro"
    BUS = "bus"
    CAR = "car"
    WALK = "walk"

class RouteAnalysis(BaseModel):
    total_distance_km: float
    protected_percentage: float = Field(..., description="Percentage of route on protected bike paths (REV, etc.)")
    elevation_gain_m: float = 0.0
    estimated_duration_min: float

class CitizenPersona(BaseModel):
    id: str
    name: str
    age: int
    fitness_level: float = Field(..., description="0.0 to 1.0 scale")
    winter_cycling_experience: bool = False
    has_e_bike: bool = False
    
    # Spatial locations (lat, lon)
    home_coords: Tuple[float, float]
    work_coords: Tuple[float, float]
    
    # Decisions are influenced by specific route analysis
    current_route: Optional[RouteAnalysis] = None
    
    # Temporal Memory: Track the last 7 days of "bad experiences"
    # A "bad experience" is when they biked in poor conditions.
    bad_day_history: List[bool] = Field(default_factory=list)

    @property
    def frustration_level(self) -> float:
        """Heuristic: Higher frustration based on recent bad experiences."""
        if not self.bad_day_history: return 0.0
        return sum(self.bad_day_history) / 7.0

class WeatherState(BaseModel):
    temperature: float
    snow_depth_cm: float
    is_raining: bool
    is_snowing: bool
    wind_speed_kmh: float

class PolicyState(BaseModel):
    snow_clearing_priority: bool = False 
    protected_lane_network_coverage: float = 0.5 

class CommuteDecision(BaseModel):
    mode: TransportMode
    reasoning: str
    confidence: float = 0.5
