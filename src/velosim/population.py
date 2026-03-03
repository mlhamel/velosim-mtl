import random
import uuid
import osmnx as ox
from .models import CitizenPersona
from typing import List

class PopulationGenerator:
    def __init__(self, graph_path: str):
        self.G = ox.load_graphml(graph_path)
        self.nodes_gdf = ox.graph_to_gdfs(self.G, edges=False)

    def _get_random_coords(self):
        """Samples a random node from the graph and returns its (lat, lon)."""
        node = self.nodes_gdf.sample(1).iloc[0]
        return (node['y'], node['x'])

    def generate(self, size: int = 100) -> List[CitizenPersona]:
        """Generates a list of diverse citizen personas."""
        population = []
        
        for i in range(size):
            # Sample Home and Work
            home = self._get_random_coords()
            work = self._get_random_coords()
            
            # Ensure they aren't the exact same node
            while home == work:
                work = self._get_random_coords()

            # Randomize attributes
            age = random.randint(18, 65)
            
            # Heuristic: younger people might have higher fitness, but highly variable
            base_fitness = random.uniform(0.3, 0.9)
            fitness = max(0.1, min(1.0, base_fitness - (max(0, age-40) * 0.01)))
            
            # 15% chance of owning an e-bike
            has_e_bike = random.random() < 0.15
            
            # 30% chance of having winter cycling experience
            winter_exp = random.random() < 0.30

            citizen = CitizenPersona(
                id=str(uuid.uuid4())[:8],
                name=f"Agent_{i}",
                age=age,
                fitness_level=round(fitness, 2),
                winter_cycling_experience=winter_exp,
                has_e_bike=has_e_bike,
                home_coords=home,
                work_coords=work
            )
            population.append(citizen)
            
        return population
