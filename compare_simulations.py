from pathlib import Path

from src.simulations.simulation_comparator import (
    calculate_simulation_comparison,
    export_simulation_comparison_chart,
    export_simulation_comparison_summary,
    export_simulation_comparison_table,
    build_simulation_insights,
)

output_dir = Path("data/outputs")

comparison = calculate_simulation_comparison(output_dir)

export_simulation_comparison_table(
    comparison,
    output_dir / "simulation_comparison.csv",
)

export_simulation_comparison_summary(
    comparison,
    output_dir / "simulation_comparison_summary.json",
)

export_simulation_comparison_chart(
    comparison,
    output_dir / "simulation_comparison.png",
)

print("\n[FlowRadar] Simulation comparison generated.\n")
for insight in build_simulation_insights(comparison):
    print(f"- {insight}")