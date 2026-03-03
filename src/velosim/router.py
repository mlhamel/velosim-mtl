import osmnx as ox
import networkx as nx
import os
import pandas as pd
from .models import RouteAnalysis
from typing import Tuple

class Router:
    def __init__(self, graph_path: str):
        if not os.path.exists(graph_path):
            raise FileNotFoundError(f"Graph file not found at {graph_path}. Run 'make fetch-data' first.")
        self.G = ox.load_graphml(graph_path)
        self.G = ox.add_edge_speeds(self.G)
        self.G = ox.add_edge_travel_times(self.G)

    def get_route_analysis(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> RouteAnalysis:
        """Finds the shortest bike route and analyzes its infrastructure."""
        
        # Get nearest nodes to lat/lon
        orig_node = ox.distance.nearest_nodes(self.G, origin[1], origin[0])
        dest_node = ox.distance.nearest_nodes(self.G, destination[1], destination[0])
        
        # Calculate shortest path by distance
        try:
            route = nx.shortest_path(self.G, orig_node, dest_node, weight="length")
        except nx.NetworkXNoPath:
            return RouteAnalysis(total_distance_km=0.0, protected_percentage=0.0, estimated_duration_min=0.0)

        # Analyze the route segments
        edges = ox.routing.route_to_gdf(self.G, route)
        
        total_length_m = edges['length'].sum()
        
        # Helper to safely check tags which might be missing or lists
        def is_protected(row):
            # Check 'highway' tag
            hw = row.get('highway', '')
            if isinstance(hw, list): hw = ' '.join(hw)
            if hw == 'cycleway': return True
            
            # Check 'cycleway' tag (might not exist in the DataFrame)
            cw = row.get('cycleway', '')
            if pd.isna(cw): cw = ''
            if isinstance(cw, list): cw = ' '.join(cw)
            if any(term in str(cw) for term in ['track', 'lane']): return True
            
            return False

        protected_mask = edges.apply(is_protected, axis=1)
        protected_length_m = edges[protected_mask]['length'].sum()
        
        # Estimated time (avg 15km/h for city cycling)
        duration_min = (total_length_m / 1000) / 15 * 60
        
        return RouteAnalysis(
            total_distance_km=round(total_length_m / 1000, 2),
            protected_percentage=round(protected_length_m / total_length_m, 2) if total_length_m > 0 else 0.0,
            estimated_duration_min=round(duration_min, 1)
        )
