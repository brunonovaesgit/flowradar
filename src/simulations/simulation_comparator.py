from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.visualizations.visual_style import (
    LAYOUT,
    PALETTE,
    TYPOGRAPHY,
    build_standard_subtitle,
    build_standard_title,
)


def _read_json(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _extract_simulated_squad(file_path: Path) -> str:
    """
    Extrai o nome da squad a partir do padrão:
    impact_simulation_<SQUAD>.json
    """
    stem = file_path.stem
    prefix = "impact_simulation_"
    if stem.startswith(prefix):
        return stem[len(prefix):]
    return stem


def _safe_get(payload: dict, keys: list[str], default=None):
    """
    Tenta recuperar o primeiro campo disponível entre várias opções,
    para tolerar pequenas variações de schema.
    """
    for key in keys:
        if key in payload:
            return payload[key]
    return default


def classify_simulation_severity(impact_score: float) -> str:
    """
    Classificação executiva de severidade.
    """
    if impact_score >= 0.75:
        return "critical"
    if impact_score >= 0.50:
        return "high"
    if impact_score >= 0.25:
        return "medium"
    return "low"


def calculate_simulation_comparison(output_dir: str | Path) -> pd.DataFrame:
    """
    Lê todos os arquivos de simulação e consolida uma tabela comparativa.

    Espera arquivos com padrão:
    impact_simulation_<SQUAD>.json
    """
    output_path = Path(output_dir)

    simulation_files = sorted(
        output_path.glob("impact_simulation_*.json")
    )

    if not simulation_files:
        return pd.DataFrame(
            columns=[
                "removed_squad",
                "impact_score",
                "severity",
                "affected_nodes",
                "remaining_nodes",
                "notes",
            ]
        )

    rows: list[dict] = []

    for file_path in simulation_files:
        payload = _read_json(file_path)
        removed_squad = _extract_simulated_squad(file_path)

        # Campos tolerantes a variações do JSON
        impact_score = _safe_get(
            payload,
            [
                "impact_score",
                "network_impact_score",
                "systemic_impact_score",
                "disruption_score",
            ],
            0.0,
        )

        affected_nodes = _safe_get(
            payload,
            [
                "affected_nodes_count",
                "affected_nodes",
                "impacted_nodes_count",
                "impacted_nodes",
            ],
            0,
        )

        remaining_nodes = _safe_get(
            payload,
            [
                "remaining_nodes_count",
                "remaining_nodes",
                "surviving_nodes_count",
            ],
            0,
        )

        # Se vier lista em vez de contagem
        if isinstance(affected_nodes, list):
            affected_nodes = len(affected_nodes)

        if isinstance(remaining_nodes, list):
            remaining_nodes = len(remaining_nodes)

        severity = classify_simulation_severity(float(impact_score))

        note = (
            "High systemic disruption"
            if severity in {"critical", "high"}
            else "Moderate / localized disruption"
        )

        rows.append(
            {
                "removed_squad": removed_squad,
                "impact_score": float(impact_score),
                "severity": severity,
                "affected_nodes": int(affected_nodes),
                "remaining_nodes": int(remaining_nodes),
                "notes": note,
            }
        )

    comparison = pd.DataFrame(rows).sort_values(
        by="impact_score",
        ascending=False,
    ).reset_index(drop=True)

    return comparison


def export_simulation_comparison_table(
    comparison_table: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    comparison_table.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def export_simulation_comparison_summary(
    comparison_table: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if comparison_table.empty:
        summary = {
            "total_simulations": 0,
            "most_disruptive_squad": None,
            "highest_impact_score": None,
            "average_impact_score": None,
        }
    else:
        top_row = comparison_table.iloc[0]
        summary = {
            "total_simulations": int(len(comparison_table)),
            "most_disruptive_squad": top_row["removed_squad"],
            "highest_impact_score": float(top_row["impact_score"]),
            "average_impact_score": float(
                comparison_table["impact_score"].mean()
            ),
        }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(summary, file, ensure_ascii=False, indent=2)

    return output_path


def export_simulation_comparison_chart(
    comparison_table: pd.DataFrame,
    output_file: str | Path,
    top_n: int = 10,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if comparison_table.empty:
        plt.figure(figsize=(LAYOUT.figure_width, LAYOUT.figure_height))
        plt.title(
            build_standard_title("Simulation Comparison"),
            fontsize=TYPOGRAPHY.title_size,
            fontweight=TYPOGRAPHY.title_weight,
        )
        plt.figtext(
            0.5,
            0.92,
            build_standard_subtitle("No simulation files were found"),
            ha="center",
            fontsize=TYPOGRAPHY.subtitle_size,
            color=PALETTE.mid_gray,
        )
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_path, dpi=LAYOUT.dpi)
        plt.close()
        return output_path

    chart_df = comparison_table.head(top_n).copy()

    plt.figure(figsize=(LAYOUT.figure_width, LAYOUT.figure_height))

    bars = plt.barh(
        chart_df["removed_squad"],
        chart_df["impact_score"],
        color=PALETTE.blue,
        edgecolor=PALETTE.white,
    )

    for i, (_, row) in enumerate(chart_df.iterrows()):
        if row["severity"] == "critical":
            bars[i].set_color(PALETTE.red)
        elif row["severity"] == "high":
            bars[i].set_color(PALETTE.orange)
        elif row["severity"] == "medium":
            bars[i].set_color(PALETTE.dark_gray)
        else:
            bars[i].set_color(PALETTE.blue)

    plt.gca().invert_yaxis()

    plt.xlabel("Impact Score", fontsize=TYPOGRAPHY.label_size)

    plt.title(
        build_standard_title("Simulation Comparison"),
        fontsize=TYPOGRAPHY.title_size,
        fontweight=TYPOGRAPHY.title_weight,
    )

    plt.figtext(
        0.5,
        0.92,
        build_standard_subtitle(
            "Higher scores indicate greater systemic disruption after squad removal"
        ),
        ha="center",
        fontsize=TYPOGRAPHY.subtitle_size,
        color=PALETTE.mid_gray,
    )

    plt.scatter([], [], color=PALETTE.red, label="Critical")
    plt.scatter([], [], color=PALETTE.orange, label="High")
    plt.scatter([], [], color=PALETTE.dark_gray, label="Medium")
    plt.scatter([], [], color=PALETTE.blue, label="Low")

    plt.legend(loc="lower right", fontsize=TYPOGRAPHY.legend_size)

    plt.tight_layout()
    plt.savefig(output_path, dpi=LAYOUT.dpi)
    plt.close()

    return output_path


def build_simulation_insights(comparison_table: pd.DataFrame) -> list[str]:
    """
    Gera insights automáticos curtos para uso em relatório ou terminal.
    """
    if comparison_table.empty:
        return ["No simulation scenarios were found."]

    insights: list[str] = []

    top_row = comparison_table.iloc[0]
    insights.append(
        f"The most disruptive simulated removal is {top_row['removed_squad']}, "
        f"with impact score {top_row['impact_score']:.3f}."
    )

    avg_score = comparison_table["impact_score"].mean()
    insights.append(
        f"The average disruption across all simulations is {avg_score:.3f}."
    )

    critical_count = int((comparison_table["severity"] == "critical").sum())
    high_count = int((comparison_table["severity"] == "high").sum())

    insights.append(
        f"{critical_count} critical scenario(s) and {high_count} high-impact scenario(s) were identified."
    )

    if len(comparison_table) >= 2:
        second_row = comparison_table.iloc[1]
        insights.append(
            f"The second most disruptive scenario is {second_row['removed_squad']}, "
            f"with impact score {second_row['impact_score']:.3f}."
        )

    return insights