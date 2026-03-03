import osmnx as ox
import os
from pathlib import Path

def fetch_montreal_cycling_network():
    """Fetches the cycling network for a central part of Montreal."""
    print("Fetching Montreal cycling network...")
    
    # Let's focus on a central, bike-heavy area for the prototype
    # Plateau Mont-Royal + Rosemont
    place_name = "Le Plateau-Mont-Royal, Montreal, Canada"
    
    # Custom filter for bike paths
    # We include everything that is specifically marked for bikes
    cf = (
        '["highway"~"cycleway"]["cycleway"~"track|lane|share_busway|sharrow"]'
        '["bicycle"~"yes|designated"]'
    )
    
    # Actually, osmnx has a built-in bike network type
    G = ox.graph_from_place(place_name, network_type="bike", simplify=True)
    
    # Save the graph
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    filepath = data_dir / "montreal_bike_network.graphml"
    ox.save_graphml(G, filepath)
    print(f"Graph saved to {filepath}")
    
    # Also save as GeoPackage for easy viewing in QGIS
    nodes, edges = ox.graph_to_gdfs(G)
    edges.to_file(data_dir / "montreal_bike_edges.gpkg", driver="GPKG")
    nodes.to_file(data_dir / "montreal_bike_nodes.gpkg", driver="GPKG")
    print("GeoPackage files saved.")

if __name__ == "__main__":
    fetch_montreal_cycling_network()
