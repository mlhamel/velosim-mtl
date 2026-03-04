"""Spatial Demand Heatmap: Maps exact route segments to see which streets
are most "demanded" by agents in the simulation."""

import os
import networkx as nx
import osmnx as ox
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
from collections import Counter

from velosim.population import PopulationGenerator


def build_demand_heatmap(pop_size: int = 200):
    graph_path = "data/montreal_bike_network.graphml"
    if not os.path.exists(graph_path):
        print(f"Graph file not found at {graph_path}. Run 'make fetch-data' first.")
        return

    print(f"Loading Montreal bike network...")
    G = ox.load_graphml(graph_path)

    # Generate a population and compute shortest-path routes
    print(f"Generating {pop_size} agents and computing routes...")
    pop_gen = PopulationGenerator(graph_path)
    population = pop_gen.generate(pop_size)

    # Count how many agents traverse each edge (u, v)
    edge_counts: Counter = Counter()
    routed = 0

    for citizen in population:
        orig_node = ox.distance.nearest_nodes(G, citizen.home_coords[1], citizen.home_coords[0])
        dest_node = ox.distance.nearest_nodes(G, citizen.work_coords[1], citizen.work_coords[0])
        try:
            route = nx.shortest_path(G, orig_node, dest_node, weight="length")
        except nx.NetworkXNoPath:
            continue

        # Tally each edge along the route
        for u, v in zip(route[:-1], route[1:]):
            edge_counts[(u, v)] += 1
        routed += 1

    print(f"Successfully routed {routed}/{pop_size} agents.")

    if not edge_counts:
        print("No routes computed — cannot generate heatmap.")
        return

    # Build edge GeoDataFrame and attach demand counts
    _, edges_gdf = ox.graph_to_gdfs(G)
    edges_gdf = edges_gdf.reset_index()

    # Map demand counts to edges
    edges_gdf["demand"] = edges_gdf.apply(
        lambda row: edge_counts.get((row["u"], row["v"]), 0), axis=1
    )

    max_demand = edges_gdf["demand"].max()

    # ── Plot ──────────────────────────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(14, 14))

    # Draw all edges in light grey first (background network)
    edges_gdf[edges_gdf["demand"] == 0].plot(
        ax=ax, linewidth=0.3, color="#cccccc", alpha=0.4
    )

    # Draw demanded edges with a colour ramp
    demanded = edges_gdf[edges_gdf["demand"] > 0].copy()
    if not demanded.empty:
        cmap = plt.cm.hot_r
        norm = mcolors.Normalize(vmin=1, vmax=max_demand)

        demanded.plot(
            ax=ax,
            column="demand",
            cmap=cmap,
            norm=norm,
            linewidth=demanded["demand"].apply(lambda d: 0.5 + 3.0 * d / max_demand),
            alpha=0.85,
        )

        # Colour-bar legend
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, fraction=0.03, pad=0.02)
        cbar.set_label("Number of Agents Using Segment", fontsize=12)

    ax.set_title(
        f"Montreal Cycling Demand Heatmap ({pop_size} Agents)",
        fontsize=18,
        fontweight="bold",
    )
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.set_axis_off()

    plt.tight_layout()
    output_path = "data/spatial_demand_heatmap.png"
    plt.savefig(output_path, dpi=150)
    print(f"Heatmap saved: {output_path}")

    # Print top 10 most-demanded segments
    top_edges = demanded.nlargest(10, "demand")[["u", "v", "demand", "name", "length"]]
    print(f"\nTop 10 Most-Demanded Street Segments:")
    for _, row in top_edges.iterrows():
        street = row.get("name", "unnamed")
        if isinstance(street, list):
            street = ", ".join(street)
        print(f"  {street}: {int(row['demand'])} agents ({row['length']:.0f}m)")


if __name__ == "__main__":
    build_demand_heatmap(200)
