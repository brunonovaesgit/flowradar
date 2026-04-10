from __future__ import annotations

import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt


# ==========================================================
# CONSTRUÇÃO DA REDE DE DEPENDÊNCIAS
# ==========================================================
#
# Convenção adotada:
# Se Squad A -> Squad B
# significa:
# Squad A depende de Squad B
# ==========================================================


def build_squad_relationships_table(
    work_items: pd.DataFrame,
    relationships: pd.DataFrame,
) -> pd.DataFrame:
    source_side = relationships.merge(
        work_items[["item_id", "team"]],
        left_on="source_item",
        right_on="item_id",
        how="left",
    ).rename(columns={"team": "source_squad"})

    full_table = source_side.merge(
        work_items[["item_id", "team"]],
        left_on="target_item",
        right_on="item_id",
        how="left",
        suffixes=("_source", "_target"),
    ).rename(columns={"team": "target_squad"})

    result = full_table[
        ["source_item", "target_item", "source_squad", "target_squad"]
    ].copy()

    result = result.dropna(subset=["source_squad", "target_squad"])

    return result


def build_dependency_graph(
    squad_relationships_table: pd.DataFrame,
) -> nx.DiGraph:
    dependency_graph = nx.DiGraph()

    # contar volume de dependências entre squads
    grouped = (
        squad_relationships_table
        .groupby(["source_squad", "target_squad"])
        .size()
        .reset_index(name="weight")
    )

    for _, row in grouped.iterrows():
        source = row["source_squad"]
        target = row["target_squad"]
        weight = row["weight"]

        dependency_graph.add_edge(source, target, weight=weight)

    return dependency_graph


def export_dependency_graph_visual(
    dependency_graph: nx.DiGraph,
    output_file: str,
) -> None:
    """
    Gera visual do grafo de dependências entre squads.
    """

    plt.figure(figsize=(12, 10))

    pos = nx.spring_layout(dependency_graph, seed=42, k=1)

    # pesos das arestas
    weights = [
        dependency_graph[u][v]["weight"]
        for u, v in dependency_graph.edges()
    ]

    # normalizar espessura
    max_weight = max(weights) if weights else 1
    widths = [1 + (w / max_weight) * 4 for w in weights]

    # desenhar nós
    nx.draw_networkx_nodes(
        dependency_graph,
        pos,
        node_size=2000,
    )

    # desenhar arestas
    nx.draw_networkx_edges(
        dependency_graph,
        pos,
        width=widths,
        arrows=True,
        arrowstyle="->",
        arrowsize=20,
    )

    # labels
    nx.draw_networkx_labels(
        dependency_graph,
        pos,
        font_size=9,
        font_weight="bold",
    )

    plt.title("Squad Dependency Graph")
    plt.axis("off")
    plt.tight_layout()

    plt.savefig(output_file, dpi=150)
    plt.close()