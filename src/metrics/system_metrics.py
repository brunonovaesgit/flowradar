from __future__ import annotations

from pathlib import Path
import json

import networkx as nx
import pandas as pd


# ==========================================================
# MÓDULO: SYSTEM METRICS
# ==========================================================
#
# Este módulo calcula métricas sistêmicas do FlowRadar,
# olhando para a rede como um todo — e não apenas para
# squads individualmente.
#
# Métricas atuais:
# - Flow Fragility Index (FFI)
# - Coordination Cost Index (CCI)
# - total_squads
# - total_dependencies
# - top_bottleneck
# - top_bottleneck_score
# ==========================================================


def compute_flow_fragility_index(
    structural_metrics_table: pd.DataFrame,
    top_ratio: float = 0.20,
) -> float:
    """
    Mede o quanto a criticidade estrutural está concentrada
    em poucos nós da rede.

    Fórmula:
        FFI = soma dos SIS dos top N% nós
              --------------------------------
              soma total dos SIS da rede
    """
    if structural_metrics_table.empty:
        return 0.0

    if "system_impact_score" in structural_metrics_table.columns:
        score_column = "system_impact_score"
    elif "structural_criticality_score" in structural_metrics_table.columns:
        score_column = "structural_criticality_score"
    else:
        return 0.0

    ranked_table = structural_metrics_table.sort_values(
        by=score_column,
        ascending=False,
    ).reset_index(drop=True)

    top_n = max(1, int(len(ranked_table) * top_ratio))

    top_score_sum = ranked_table.head(top_n)[score_column].sum()
    total_score_sum = ranked_table[score_column].sum()

    if total_score_sum == 0:
        return 0.0

    return float(top_score_sum / total_score_sum)


def compute_coordination_cost_index(
    dependency_graph: nx.DiGraph,
) -> float:
    """
    Mede o custo estrutural médio de coordenação do sistema.

    Fórmula:
        CCI = número de arestas / número de nós
    """
    total_nodes = dependency_graph.number_of_nodes()
    total_edges = dependency_graph.number_of_edges()

    if total_nodes == 0:
        return 0.0

    return float(total_edges / total_nodes)


def build_system_summary(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame,
    top_ratio: float = 0.20,
) -> dict:
    """
    Consolida um resumo sistêmico do FlowRadar.
    """
    total_squads = int(dependency_graph.number_of_nodes())
    total_dependencies = int(dependency_graph.number_of_edges())

    flow_fragility_index = compute_flow_fragility_index(
        structural_metrics_table=structural_metrics_table,
        top_ratio=top_ratio,
    )

    coordination_cost_index = compute_coordination_cost_index(
        dependency_graph=dependency_graph
    )

    if structural_metrics_table.empty:
        top_bottleneck = None
        top_bottleneck_score = 0.0
    else:
        if "system_impact_score" in structural_metrics_table.columns:
            score_column = "system_impact_score"
        else:
            score_column = "structural_criticality_score"

        top_row = structural_metrics_table.sort_values(
            by=score_column,
            ascending=False,
        ).iloc[0]

        top_bottleneck = top_row["squad"]
        top_bottleneck_score = float(top_row[score_column])

    summary = {
        "total_squads": total_squads,
        "total_dependencies": total_dependencies,
        "flow_fragility_index": round(flow_fragility_index, 4),
        "coordination_cost_index": round(coordination_cost_index, 4),
        "top_bottleneck": top_bottleneck,
        "top_bottleneck_score": round(top_bottleneck_score, 4),
    }

    return summary


def export_system_summary(
    system_summary: dict,
    output_file: str | Path,
) -> Path:
    """
    Exporta o resumo sistêmico para JSON.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(system_summary, file, ensure_ascii=False, indent=2)

    return output_path