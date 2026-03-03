import polars as pl
import matplotlib.pyplot as plt
import seaborn as sns
import os

def visualize():
    input_path = "data/sim_results.parquet"
    if not os.path.exists(input_path):
        print(f"File {input_path} not found. Run 'make run-population' first.")
        return

    df = pl.read_parquet(input_path)
    
    # 1. Prepare data for Modal Shift Bar Chart
    modal_counts = df.group_by(["policy", "mode"]).len().to_pandas()
    
    plt.figure(figsize=(12, 6))
    sns.set_style("whitegrid")
    
    # Chart 1: Modal Distribution per Policy
    ax1 = sns.barplot(data=modal_counts, x="policy", y="len", hue="mode", palette="viridis")
    plt.title("Montreal Winter Modal Shift: Standard vs. Priority Snow Clearing", fontsize=16)
    plt.ylabel("Number of Citizens", fontsize=12)
    plt.xlabel("Policy Scenario", fontsize=12)
    plt.legend(title="Transport Mode")
    
    # Add values on top of bars
    for p in ax1.patches:
        ax1.annotate(f'{int(p.get_height())}', (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha = 'center', va = 'center', xytext = (0, 9), textcoords = 'offset points')

    plt.tight_layout()
    plt.savefig("data/modal_shift_comparison.png")
    print("Chart saved: data/modal_shift_comparison.png")

    # Chart 2: Correlation between Protected Path % and Biking Decision
    # We look at the 'Standard' scenario to see where the risk is highest
    std_df = df.filter(pl.col("policy") == "Standard").to_pandas()
    
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=std_df, x="mode", y="protected_%", palette="magma")
    plt.title("Impact of Protected Infrastructure on Commute Choice (Standard Clearing)", fontsize=14)
    plt.ylabel("Percentage of Route on Protected Path", fontsize=12)
    plt.xlabel("Chosen Mode", fontsize=12)
    
    plt.tight_layout()
    plt.savefig("data/infrastructure_impact.png")
    print("Chart saved: data/infrastructure_impact.png")

if __name__ == "__main__":
    visualize()
