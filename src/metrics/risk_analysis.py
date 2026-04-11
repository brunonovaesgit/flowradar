from __future__ import annotations

import pandas as pd
import networkx as nx


def _normalize_series(series: pd.Series) -> pd.Series:
    """
    Normaliza valores entre 0 e 1.
    """
    if series.max() == series.min():
        return pd.Series([0.0] * len(series), index=series.index)

    return (series - series.min()) / (series.max() - series.min())


def classify_squad(
    structural_score: float,
    in_degree: float,
    out_degree: float,
) -> str:
    """
    Classifica a squad em categorias de risco.
    """

    if structural_score >= 0.8:
        return "bottleneck"

    if in_degree >= 0.6:
        return "hub"

    if out_degree >= 0.6:
        return "fragile"

    return "peripheral"


def calculate_risk_analysis(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calcula análise de risco organizacional baseada no grafo.
    """

    # -----------------------------
    # Degree metrics
    # -----------------------------
    in_degree = dict(dependency_graph.in_degree())
    out_degree = dict(dependency_graph.out_degree())

    df = pd.DataFrame({
        "squad": list(dependency_graph.nodes()),
        "in_degree": [in_degree.get(n, 0) for n in dependency_graph.nodes()],
        "out_degree": [out_degree.get(n, 0) for n in dependency_graph.nodes()],
    })

    # -----------------------------
    # Merge com criticidade estrutural
    # -----------------------------
    df = df.merge(
        structural_metrics_table[["squad", "structural_criticality_score"]],
        on="squad",
        how="left",
    )

    df["structural_criticality_score"] = df[
        "structural_criticality_score"
    ].fillna(0)

    # -----------------------------
    # Normalização
    # -----------------------------
    df["in_degree_norm"] = _normalize_series(df["in_degree"])
    df["out_degree_norm"] = _normalize_series(df["out_degree"])
    df["criticality_norm"] = _normalize_series(
        df["structural_criticality_score"]
    )

    # -----------------------------
    # Risk Score (ponderado)
    # -----------------------------
    df["risk_score"] = (
        0.5 * df["criticality_norm"]
        + 0.3 * df["in_degree_norm"]
        + 0.2 * df["out_degree_norm"]
    )

    # -----------------------------
    # Classificação
    # -----------------------------
    df["risk_category"] = df.apply(
        lambda row: classify_squad(
            structural_score=row["criticality_norm"],
            in_degree=row["in_degree_norm"],
            out_degree=row["out_degree_norm"],
        ),
        axis=1,
    )

    # -----------------------------
    # Ordenação final
    # -----------------------------
    df = df.sort_values(
        by="risk_score",
        ascending=False,
    ).reset_index(drop=True)

    return df


def export_risk_analysis(
    risk_table: pd.DataFrame,
    output_file: str,
) -> None:
    """
    Exporta análise de risco para CSV.
    """
    risk_table.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig",
    )