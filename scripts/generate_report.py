"""
Generate a Markdown post-simulation report from temporal simulation results.

Reads data/temporal_results.parquet and writes data/simulation_report.md
with a summary of policy effectiveness, modal splits, weather impact,
and agent frustration analysis.
"""

import os
from datetime import datetime

import polars as pl


def _pct(count: int, total: int) -> float:
    return round((count / total) * 100, 1) if total else 0.0


def generate_report() -> None:
    input_path = "data/temporal_results.parquet"
    output_path = "data/simulation_report.md"

    if not os.path.exists(input_path):
        print(f"File {input_path} not found. Run 'make run-temporal' first.")
        return

    df = pl.read_parquet(input_path)

    policies = sorted(df["policy"].unique().to_list())
    day_names = df.sort("day").select("day", "day_name").unique().sort("day")
    num_agents = df.filter((pl.col("policy") == policies[0]) & (pl.col("day") == 1))["agent_id"].n_unique()
    num_days = df["day"].n_unique()

    lines: list[str] = []

    def w(line: str = "") -> None:
        lines.append(line)

    # ── Header ───────────────────────────────────────────────────────────
    w("# VeloSim-MTL — Post-Simulation Report")
    w()
    w(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    w(f"**Population size:** {num_agents} agents")
    w(f"**Simulation length:** {num_days} days")
    w(f"**Policy scenarios:** {', '.join(policies)}")
    w()

    # ── Executive Summary ────────────────────────────────────────────────
    w("## Executive Summary")
    w()

    bike_by_policy: dict[str, int] = {}
    total_by_policy: dict[str, int] = {}
    for policy in policies:
        pdf = df.filter(pl.col("policy") == policy)
        total_by_policy[policy] = len(pdf)
        bike_by_policy[policy] = len(pdf.filter(pl.col("mode") == "bike"))

    for policy in policies:
        pct = _pct(bike_by_policy[policy], total_by_policy[policy])
        w(f"- **{policy}** clearing: **{pct}%** overall bike adoption "
          f"({bike_by_policy[policy]}/{total_by_policy[policy]} decisions)")

    if len(policies) == 2:
        pct_std = _pct(bike_by_policy[policies[0]], total_by_policy[policies[0]])
        pct_pri = _pct(bike_by_policy[policies[1]], total_by_policy[policies[1]])
        diff = round(pct_pri - pct_std, 1)
        direction = "increase" if diff > 0 else "decrease" if diff < 0 else "no change"
        w()
        w(f"Priority snow clearing resulted in a **{abs(diff)} percentage-point "
          f"{direction}** in bike adoption compared to standard clearing.")
    w()

    # ── Daily Breakdown ──────────────────────────────────────────────────
    w("## Daily Breakdown")
    w()

    for policy in policies:
        w(f"### {policy} Clearing")
        w()
        pdf = df.filter(pl.col("policy") == policy)

        for row in day_names.iter_rows(named=True):
            day_num = row["day"]
            day_name = row["day_name"]
            ddf = pdf.filter(pl.col("day") == day_num)
            total = len(ddf)
            snow = ddf["snow"].first() if len(ddf) > 0 else 0

            mode_counts = ddf.group_by("mode").len().sort("len", descending=True)
            mode_parts = [
                f"{r['mode']} {_pct(r['len'], total)}%"
                for r in mode_counts.iter_rows(named=True)
            ]

            avg_frust = round(ddf["frustration"].mean(), 3) if len(ddf) > 0 else 0
            w(f"- **{day_name}** (Day {day_num}, snow: {snow} cm) — "
              f"{', '.join(mode_parts)} | avg frustration: {avg_frust}")

        w()

    # ── Modal Split Comparison ───────────────────────────────────────────
    w("## Modal Split Comparison")
    w()

    for policy in policies:
        w(f"### {policy}")
        w()
        pdf = df.filter(pl.col("policy") == policy)
        total = len(pdf)
        mode_counts = pdf.group_by("mode").len().sort("len", descending=True)
        for r in mode_counts.iter_rows(named=True):
            pct = _pct(r["len"], total)
            bar_len = int(round(pct / 2))
            bar = "█" * bar_len + "░" * (50 - bar_len)
            w(f"- `{r['mode']:<6}` {bar} {pct}% ({r['len']})")
        w()

    # ── Frustration Analysis ─────────────────────────────────────────────
    w("## Frustration Analysis")
    w()

    for policy in policies:
        pdf = df.filter(pl.col("policy") == policy)
        # Frustration on the last day gives the cumulative picture
        last_day = pdf["day"].max()
        last_df = pdf.filter(pl.col("day") == last_day)
        avg = round(last_df["frustration"].mean(), 3) if len(last_df) > 0 else 0
        max_f = round(last_df["frustration"].max(), 3) if len(last_df) > 0 else 0
        w(f"- **{policy}** — End-of-week avg frustration: **{avg}**, peak: **{max_f}**")

    w()

    # ── Weather Impact ───────────────────────────────────────────────────
    w("## Weather Impact on Cycling")
    w()
    w("Bike adoption rate by snow depth across all policies:")
    w()

    snow_groups = (
        df.with_columns(
            snow_bracket=pl.when(pl.col("snow") == 0).then(pl.lit("0 cm"))
            .when(pl.col("snow") <= 5).then(pl.lit("1-5 cm"))
            .when(pl.col("snow") <= 10).then(pl.lit("6-10 cm"))
            .otherwise(pl.lit("10+ cm"))
        )
        .group_by("snow_bracket")
        .agg(
            total=pl.len(),
            bike=pl.col("mode").filter(pl.col("mode") == "bike").len(),
        )
        .with_columns(pct=(pl.col("bike") / pl.col("total") * 100).round(1))
        .sort("pct", descending=True)
    )

    for r in snow_groups.iter_rows(named=True):
        w(f"- **{r['snow_bracket']}**: {r['pct']}% bike adoption ({r['bike']}/{r['total']})")

    w()

    # ── Methodology ──────────────────────────────────────────────────────
    w("## Methodology")
    w()
    w("- Each agent's commute decision is produced by an LLM (Ollama llama3.2) "
      "given their persona, route analysis, weather conditions, and policy state.")
    w("- Agents accumulate \"bad day\" memory when biking in >5 cm snow or <-7°C, "
      "increasing frustration and discouraging future cycling.")
    w("- Two policy scenarios are compared: Standard (no priority bike path clearing) "
      "and Priority (bike paths cleared first after snowfall).")
    w()
    w("---")
    w("*Report generated by VeloSim-MTL*")

    report = "\n".join(lines)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(report)

    print(f"Report saved to {output_path}")
    print()
    print(report)


if __name__ == "__main__":
    generate_report()
