"""Interactive Folium Map: HTML map showing agent home/work clusters
and chosen routes overlaid on Montreal."""

import os
import polars as pl
import networkx as nx
import osmnx as ox
import folium
from folium.plugins import MarkerCluster

from velosim.population import PopulationGenerator

# Colour palette per transport mode
MODE_COLOURS = {
    "bike": "#2ecc71",   # green
    "metro": "#3498db",  # blue
    "bus": "#f39c12",    # orange
    "car": "#e74c3c",    # red
    "walk": "#9b59b6",   # purple
}

MONTREAL_CENTER = (45.5236, -73.5828)


def _has_coords(df: pl.DataFrame) -> bool:
    """Check whether the parquet contains home/work coordinate columns."""
    return all(c in df.columns for c in ["home_lat", "home_lon", "work_lat", "work_lon"])


def build_interactive_map():
    graph_path = "data/montreal_bike_network.graphml"
    input_path = "data/sim_results.parquet"

    if not os.path.exists(graph_path):
        print(f"Graph file not found at {graph_path}. Run 'make fetch-data' first.")
        return

    print("Loading Montreal bike network...")
    G = ox.load_graphml(graph_path)

    # ── Load or generate agent data ──────────────────────────────────────
    if os.path.exists(input_path):
        df = pl.read_parquet(input_path)
        print(f"Loaded {len(df)} rows from {input_path}")
    else:
        df = None

    if df is not None and _has_coords(df):
        # Use saved coordinates from enhanced sim results
        agents_df = df.filter(pl.col("policy") == df["policy"][0]).unique(subset=["agent_id"])
        print(f"Using {len(agents_df)} agents with saved coordinates.")
        agents = []
        for row in agents_df.iter_rows(named=True):
            agents.append({
                "id": row["agent_id"],
                "home": (row["home_lat"], row["home_lon"]),
                "work": (row["work_lat"], row["work_lon"]),
                "mode": row["mode"],
                "age": row["age"],
            })
    else:
        # Fall back: generate a fresh population (no mode info without Ollama)
        print("Parquet missing coordinates — generating fresh population sample...")
        pop_gen = PopulationGenerator(graph_path)
        population = pop_gen.generate(50)
        agents = []
        for c in population:
            agents.append({
                "id": c.id,
                "home": c.home_coords,
                "work": c.work_coords,
                "mode": "bike",  # placeholder when no decision data
                "age": c.age,
            })

    # ── Build Folium map ─────────────────────────────────────────────────
    m = folium.Map(location=MONTREAL_CENTER, zoom_start=13, tiles="cartodbpositron")

    # Cluster layers for Home and Work markers
    home_cluster = MarkerCluster(name="🏠 Home Locations").add_to(m)
    work_cluster = MarkerCluster(name="🏢 Work Locations").add_to(m)

    # Route layer group
    route_group = folium.FeatureGroup(name="🚴 Bike Routes", show=True).add_to(m)

    routed = 0
    for agent in agents:
        mode = agent["mode"]
        colour = MODE_COLOURS.get(mode, "#888888")

        # Home marker (circle)
        folium.CircleMarker(
            location=agent["home"],
            radius=5,
            color=colour,
            fill=True,
            fill_opacity=0.7,
            popup=f"<b>Home</b><br>Agent {agent['id']}<br>Age {agent['age']}<br>Mode: {mode}",
        ).add_to(home_cluster)

        # Work marker (square-ish via DivIcon)
        folium.CircleMarker(
            location=agent["work"],
            radius=4,
            color=colour,
            fill=True,
            fill_color="#ffffff",
            fill_opacity=0.9,
            weight=2,
            popup=f"<b>Work</b><br>Agent {agent['id']}<br>Age {agent['age']}<br>Mode: {mode}",
        ).add_to(work_cluster)

        # Draw the actual route on the graph (only for bike commuters to keep map readable)
        if mode == "bike":
            orig = ox.distance.nearest_nodes(G, agent["home"][1], agent["home"][0])
            dest = ox.distance.nearest_nodes(G, agent["work"][1], agent["work"][0])
            try:
                route_nodes = nx.shortest_path(G, orig, dest, weight="length")
            except nx.NetworkXNoPath:
                continue

            coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route_nodes]
            folium.PolyLine(
                coords,
                color=colour,
                weight=2.5,
                opacity=0.5,
                popup=f"Agent {agent['id']} bike route",
            ).add_to(route_group)
            routed += 1

    print(f"Plotted {len(agents)} agents, {routed} bike routes.")

    # ── Legend ────────────────────────────────────────────────────────────
    legend_html = """
    <div style="position:fixed; bottom:30px; left:30px; z-index:1000;
                background:white; padding:12px 16px; border-radius:8px;
                box-shadow:0 2px 6px rgba(0,0,0,0.3); font-size:13px;">
        <b>Transport Mode</b><br>
    """
    for mode, colour in MODE_COLOURS.items():
        legend_html += f'<span style="color:{colour}">●</span> {mode.capitalize()}<br>'
    legend_html += "</div>"
    m.get_root().html.add_child(folium.Element(legend_html))

    # Layer control toggle
    folium.LayerControl(collapsed=False).add_to(m)

    output_path = "data/interactive_map.html"
    m.save(output_path)
    print(f"Interactive map saved: {output_path}")


if __name__ == "__main__":
    build_interactive_map()
