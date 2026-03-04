import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import os

def visualize_temporal():
    input_path = "data/temporal_results.parquet"
    if not os.path.exists(input_path):
        print(f"File {input_path} not found. Run 'make run-temporal' first.")
        return

    df = pl.read_parquet(input_path)
    
    # 1. Calculate Biking Percentage per Day per Policy
    # Total agents per day/policy (should be 10)
    total_agents = df.group_by(["policy", "day", "day_name"]).len()
    
    # Biking agents
    bike_agents = df.filter(pl.col("mode") == "bike").group_by(["policy", "day", "day_name"]).len()
    
    # Join and calculate %
    stats = total_agents.join(bike_agents, on=["policy", "day", "day_name"], how="left").fill_null(0)
    stats = stats.with_columns(
        bike_percentage = (pl.col("len_right") / pl.col("len")) * 100
    ).sort("day")
    
    # Convert to pandas for plotting
    plot_df = stats.to_pandas()

    # Create the Plot
    plt.figure(figsize=(14, 7))
    sns.set_style("whitegrid")
    
    # Line chart for Biking %
    ax = sns.lineplot(data=plot_df, x="day_name", y="bike_percentage", hue="policy", 
                      marker='o', linewidth=3, markersize=10, palette={"Standard": "#e74c3c", "Priority": "#2ecc71"})
    
    # Add Weather annotations (visual cues for the storm)
    plt.axvspan(0.8, 1.2, color='gray', alpha=0.2, label='Snow Storm (15cm)')
    plt.text(1, 105, "❄️ STORM", ha='center', fontsize=12, fontweight='bold')
    
    plt.title("Montreal Biking Resilience: Impacts of a 5-Day Winter Storm", fontsize=18, fontweight='bold')
    plt.ylabel("% of Population Choosing to Bike", fontsize=14)
    plt.xlabel("Day of the Week", fontsize=14)
    plt.ylim(0, 110)
    plt.legend(title="Policy Scenario", fontsize=12)
    
    # Annotate values
    for i in range(len(plot_df)):
        plt.annotate(f"{plot_df.iloc[i]['bike_percentage']:.0f}%", 
                     (plot_df.iloc[i]['day_name'], plot_df.iloc[i]['bike_percentage']),
                     textcoords="offset points", xytext=(0,10), ha='center', fontsize=10)

    plt.tight_layout()
    plt.savefig("data/temporal_modal_shift.png")
    print("Weekly chart saved: data/temporal_modal_shift.png")

if __name__ == "__main__":
    visualize_temporal()
