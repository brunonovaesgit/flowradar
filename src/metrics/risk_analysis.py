from __future__ import annotations

from pathlib import Path

import networkx as nx
import pandas as pd


# ==========================================================
# MÓDULO: RISK ANALYSIS
# ==========================================================
#
# Este módulo consolida a leitura de risco organizacional
# no FlowRadar.
#
# Objetivos:
# - preservar compatibilidade com o modelo atual
# - incorporar melhor a lógica das métricas oficiais
# - manter leitura simples e código fácil de evoluir
#
# Saídas principais:
# - risk_score
# - risk_category
# - flow_bottleneck_probability
# ==========================================================


def _normalize_series(series: pd.Series) -> pd.Series:
    """
    Normaliza uma série no intervalo entre 0 e 1.

    Quando todos os valores são iguais, retorna zeros
    para evitar divisão por zero e manter previsibilidade.
    """
    minimum_value = series.min()
    maximum_value = series.max()

    if maximum_value == minimum_value:
        return pd.Series([0.0] * len(series), index=series.index)

    return (series - minimum_value) / (maximum_value - minimum_value)


def _resolve_system_impact_column(
    structural_metrics_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Garante que a tabela tenha uma coluna única de impacto sistêmico.

    Regras:
    - se já existir system_impact_score, usa essa
    - caso contrário, tenta usar structural_criticality_score
    - se nenhuma existir, cria valor zerado
    """
    result = structural_metrics_table.copy()

    if "system_impact_score" not in result.columns:
        if "structural_criticality_score" in result.columns:
            result["system_impact_score"] = result[
                "structural_criticality_score"
            ]
        else:
            result["system_impact_score"] = 0.0

    if "structural_criticality_score" not in result.columns:
        result["structural_criticality_score"] = result[
            "system_impact_score"
        ]

    return result


def _ensure_dependency_load_score(
    risk_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Garante que a tabela tenha dependency_load_score.

    Se a coluna já vier pronta da tabela estrutural, ela é preservada.
    Caso contrário, é calculada a partir de in_degree e out_degree.
    """
    result = risk_table.copy()

    if "dependency_load_score" in result.columns:
        result["dependency_load_score"] = result[
            "dependency_load_score"
        ].fillna(0.0)
        return result

    result["dependency_load_score_raw"] = (
        0.60 * result["in_degree"] +
        0.40 * result["out_degree"]
    )

    result["dependency_load_score"] = _normalize_series(
        result["dependency_load_score_raw"]
    )

    return result


def classify_squad(
    risk_score: float,
    flow_bottleneck_probability: float,
    system_impact_score: float,
    dependency_load_score: float,
) -> str:
    """
    Classifica a squad em categorias de risco organizacional.

    Lógica:
    - bottleneck -> impacto sistêmico muito alto + alta chance de gargalo
    - hub        -> alta influência estrutural
    - fragile    -> alta carga relacional / exposição
    - peripheral -> menor relevância estrutural relativa
    """
    if risk_score >= 0.80 or flow_bottleneck_probability >= 0.80:
        return "bottleneck"

    if system_impact_score >= 0.60:
        return "hub"

    if dependency_load_score >= 0.60:
        return "fragile"

    return "peripheral"


def calculate_risk_analysis(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula análise de risco organizacional baseada no grafo
    e nas métricas estruturais já produzidas pelo FlowRadar.

    A tabela final inclui:
    - in_degree / out_degree
    - normalizações
    - structural_criticality_score
    - system_impact_score
    - dependency_load_score
    - risk_score
    - flow_bottleneck_probability
    - risk_category
    """
    resolved_structural_metrics = _resolve_system_impact_column(
        structural_metrics_table
    )

    in_degree_by_squad = dict(dependency_graph.in_degree())
    out_degree_by_squad = dict(dependency_graph.out_degree())

    risk_table = pd.DataFrame(
        {
            "squad": list(dependency_graph.nodes()),
            "in_degree": [
                in_degree_by_squad.get(node_name, 0)
                for node_name in dependency_graph.nodes()
            ],
            "out_degree": [
                out_degree_by_squad.get(node_name, 0)
                for node_name in dependency_graph.nodes()
            ],
        }
    )

    columns_to_merge = [
        "squad",
        "structural_criticality_score",
        "system_impact_score",
    ]

    if "dependency_load_score" in resolved_structural_metrics.columns:
        columns_to_merge.append("dependency_load_score")

    risk_table = risk_table.merge(
        resolved_structural_metrics[columns_to_merge],
        on="squad",
        how="left",
    )

    risk_table["structural_criticality_score"] = risk_table[
        "structural_criticality_score"
    ].fillna(0.0)

    risk_table["system_impact_score"] = risk_table[
        "system_impact_score"
    ].fillna(0.0)

    risk_table = _ensure_dependency_load_score(risk_table)

    # ------------------------------------------------------
    # Normalizações auxiliares
    # ------------------------------------------------------
    risk_table["in_degree_norm"] = _normalize_series(risk_table["in_degree"])
    risk_table["out_degree_norm"] = _normalize_series(risk_table["out_degree"])
    risk_table["criticality_norm"] = _normalize_series(
        risk_table["structural_criticality_score"]
    )
    risk_table["system_impact_norm"] = _normalize_series(
        risk_table["system_impact_score"]
    )

    if "dependency_load_score" in risk_table.columns:
        risk_table["dependency_load_norm"] = _normalize_series(
            risk_table["dependency_load_score"]
        )
    else:
        risk_table["dependency_load_norm"] = 0.0

    # ------------------------------------------------------
    # Risk Score
    # ------------------------------------------------------
    #
    # Mantemos a lógica histórica do projeto, mas agora
    # incorporando também a leitura de carga relacional.
    #
    # Fórmula:
    #   0.45 * criticidade estrutural
    # + 0.25 * dependências recebidas
    # + 0.15 * dependências geradas
    # + 0.15 * carga de dependência
    #
    risk_table["risk_score"] = (
        0.45 * risk_table["criticality_norm"]
        + 0.25 * risk_table["in_degree_norm"]
        + 0.15 * risk_table["out_degree_norm"]
        + 0.15 * risk_table["dependency_load_norm"]
    )

    # ------------------------------------------------------
    # Flow Bottleneck Probability
    # ------------------------------------------------------
    #
    # Essa é a métrica oficial sugerida para estimar o risco
    # de um nó se comportar como gargalo no fluxo.
    #
    risk_table["flow_bottleneck_probability"] = (
        0.55 * risk_table["system_impact_norm"]
        + 0.45 * risk_table["dependency_load_norm"]
    )

    # ------------------------------------------------------
    # Classificação qualitativa
    # ------------------------------------------------------
    risk_table["risk_category"] = risk_table.apply(
        lambda row: classify_squad(
            risk_score=row["risk_score"],
            flow_bottleneck_probability=row["flow_bottleneck_probability"],
            system_impact_score=row["system_impact_norm"],
            dependency_load_score=row["dependency_load_norm"],
        ),
        axis=1,
    )

    # ------------------------------------------------------
    # Ordenação final
    # ------------------------------------------------------
    risk_table = risk_table.sort_values(
        by=["risk_score", "flow_bottleneck_probability"],
        ascending=False,
    ).reset_index(drop=True)

    return risk_table


def export_risk_analysis(
    risk_table: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    """
    Exporta a análise de risco para CSV.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    risk_table.to_csv(
        output_path,
        index=False,
        encoding="utf-8-sig",
    )

    return output_path