from __future__ import annotations

from pathlib import Path
from typing import Optional

import networkx as nx
import pandas as pd


# ==========================================================
# MÓDULO: NETWORK CENTRALITY
# ==========================================================
#
# Este módulo consolida as principais métricas estruturais
# da rede de dependências organizacionais.
# ==========================================================


def calculate_in_out_degree(dependency_graph: nx.DiGraph) -> pd.DataFrame:
    """
    Calcula o número de dependências recebidas e geradas por cada squad.
    """
    rows = []

    for squad_name in dependency_graph.nodes():
        dependencies_received = dependency_graph.in_degree(squad_name)
        dependencies_generated = dependency_graph.out_degree(squad_name)

        rows.append(
            {
                "squad": squad_name,
                "dependencies_received_in_degree": dependencies_received,
                "dependencies_generated_out_degree": dependencies_generated,
            }
        )

    return pd.DataFrame(rows)


def calculate_betweenness_centrality(
    dependency_graph: nx.DiGraph,
) -> pd.DataFrame:
    """
    Calcula betweenness centrality para cada squad.
    """
    betweenness_by_squad = nx.betweenness_centrality(
        dependency_graph,
        normalized=True,
    )

    return pd.DataFrame(
        [
            {
                "squad": squad_name,
                "betweenness_centrality": centrality_value,
            }
            for squad_name, centrality_value in betweenness_by_squad.items()
        ]
    )


def calculate_pagerank(dependency_graph: nx.DiGraph) -> pd.DataFrame:
    """
    Calcula PageRank para cada squad.
    """
    pagerank_by_squad = nx.pagerank(dependency_graph)

    return pd.DataFrame(
        [
            {
                "squad": squad_name,
                "pagerank": pagerank_value,
            }
            for squad_name, pagerank_value in pagerank_by_squad.items()
        ]
    )


def _normalize_series(values: pd.Series) -> pd.Series:
    """
    Normaliza uma série entre 0 e 1.
    """
    minimum_value = values.min()
    maximum_value = values.max()

    if maximum_value == minimum_value:
        return pd.Series([0.0] * len(values), index=values.index)

    return (values - minimum_value) / (maximum_value - minimum_value)


def calculate_structural_criticality_score(
    centrality_table: pd.DataFrame,
    in_degree_weight: float = 0.40,
    betweenness_weight: float = 0.35,
    pagerank_weight: float = 0.25,
) -> pd.DataFrame:
    """
    Calcula um score composto de criticidade estrutural.
    """
    required_columns = {
        "dependencies_received_in_degree",
        "betweenness_centrality",
        "pagerank",
    }

    missing_columns = required_columns - set(centrality_table.columns)
    if missing_columns:
        missing_str = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Centrality table is missing required columns: {missing_str}"
        )

    result = centrality_table.copy()

    result["in_degree_normalized"] = _normalize_series(
        result["dependencies_received_in_degree"]
    )
    result["betweenness_normalized"] = _normalize_series(
        result["betweenness_centrality"]
    )
    result["pagerank_normalized"] = _normalize_series(result["pagerank"])

    result["structural_criticality_score"] = (
        in_degree_weight * result["in_degree_normalized"]
        + betweenness_weight * result["betweenness_normalized"]
        + pagerank_weight * result["pagerank_normalized"]
    )

    return result


def build_structural_metrics_table(
    dependency_graph: nx.DiGraph,
    sort_descending: bool = True,
) -> pd.DataFrame:
    """
    Constrói a tabela consolidada de métricas estruturais.
    """
    degree_table = calculate_in_out_degree(dependency_graph)
    betweenness_table = calculate_betweenness_centrality(dependency_graph)
    pagerank_table = calculate_pagerank(dependency_graph)

    consolidated_table = (
        degree_table.merge(betweenness_table, on="squad", how="left")
        .merge(pagerank_table, on="squad", how="left")
        .fillna(0)
    )

    consolidated_table = calculate_structural_criticality_score(
        consolidated_table
    )

    if sort_descending:
        consolidated_table = consolidated_table.sort_values(
            by="structural_criticality_score",
            ascending=False,
        ).reset_index(drop=True)

    return consolidated_table


def export_structural_metrics_table(
    structural_metrics_table: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    """
    Exporta a tabela consolidada para CSV.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    structural_metrics_table.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path


def calculate_and_export_structural_metrics(
    dependency_graph: nx.DiGraph,
    output_file: Optional[str | Path] = None,
) -> pd.DataFrame:
    """
    Calcula todas as métricas estruturais e exporta opcionalmente.
    """
    structural_metrics_table = build_structural_metrics_table(
        dependency_graph=dependency_graph
    )

    if output_file is not None:
        export_structural_metrics_table(
            structural_metrics_table=structural_metrics_table,
            output_file=output_file,
        )

    return structural_metrics_table