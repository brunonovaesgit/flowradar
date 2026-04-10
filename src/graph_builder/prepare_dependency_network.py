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
    """
    Constrói uma tabela de dependências entre squads a partir de:
    - work items
    - relationships entre itens

    Entrada esperada:
    work_items:
    - item_id
    - team

    relationships:
    - source_item
    - target_item

    Returns
    -------
    pd.DataFrame
        Tabela com:
        - source_item
        - target_item
        - source_squad
        - target_squad
    """
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
    """
    Constrói um grafo direcionado entre squads.

    Parameters
    ----------
    squad_relationships_table : pd.DataFrame
        Tabela contendo:
        - source_squad
        - target_squad

    Returns
    -------
    nx.DiGraph
        Grafo direcionado de dependências.
    """
    dependency_graph = nx.DiGraph()

    grouped = (
        squad_relationships_table
        .groupby(["source_squad", "target_squad"])
        .size()
        .reset_index(name="weight")
    )

    for _, row in grouped.iterrows():
        source_squad = row["source_squad"]
        target_squad = row["target_squad"]
        weight = int(row["weight"])

        dependency_graph.add_edge(
            source_squad,
            target_squad,
            weight=weight,
        )

    return dependency_graph


def _build_node_size_map(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame | None = None,
) -> dict[str, float]:
    """
    Cria mapa de tamanho dos nós.

    Prioridade:
    1. structural_criticality_score, se disponível
    2. fallback para degree centrality simples
    """
    node_size_map: dict[str, float] = {}

    if (
        structural_metrics_table is not None
        and not structural_metrics_table.empty
        and "squad" in structural_metrics_table.columns
        and "structural_criticality_score" in structural_metrics_table.columns
    ):
        metrics_indexed = structural_metrics_table.set_index("squad")

        for node in dependency_graph.nodes():
            if node in metrics_indexed.index:
                score = float(
                    metrics_indexed.loc[node, "structural_criticality_score"]
                )
            else:
                score = 0.0

            # base + escala visual
            node_size_map[node] = 1800 + (score * 4200)

        return node_size_map

    degree_map = dict(dependency_graph.degree())

    if not degree_map:
        return node_size_map

    max_degree = max(degree_map.values()) or 1

    for node, degree in degree_map.items():
        normalized_degree = degree / max_degree
        node_size_map[node] = 1800 + (normalized_degree * 4200)

    return node_size_map


def export_dependency_graph_visual(
    dependency_graph: nx.DiGraph,
    output_file: str,
    structural_metrics_table: pd.DataFrame | None = None,
) -> None:
    """
    Gera visual do grafo de dependências entre squads.

    Melhorias visuais:
    - tamanho dos nós pela criticidade estrutural
    - espessura das arestas pelo volume
    - remoção de self-loops da visualização principal
    - layout mais legível
    """
    plt.figure(figsize=(14, 10))

    # remover self-loops do desenho principal para reduzir ruído visual
    graph_for_plot = dependency_graph.copy()
    self_loops = list(nx.selfloop_edges(graph_for_plot))
    graph_for_plot.remove_edges_from(self_loops)

    if len(graph_for_plot.nodes()) == 0:
        plt.title("Squad Dependency Graph")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_file, dpi=150)
        plt.close()
        return

    # layout mais estável e legível
    pos = nx.kamada_kawai_layout(graph_for_plot)

    # pesos das arestas
    edge_weights = [
        graph_for_plot[u][v].get("weight", 1)
        for u, v in graph_for_plot.edges()
    ]

    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [
        1.2 + (weight / max_weight) * 5.0
        for weight in edge_weights
    ]

    # tamanho dos nós
    node_size_map = _build_node_size_map(
        dependency_graph=graph_for_plot,
        structural_metrics_table=structural_metrics_table,
    )
    node_sizes = [node_size_map.get(node, 1800) for node in graph_for_plot.nodes()]

    # desenhar nós
    nx.draw_networkx_nodes(
        graph_for_plot,
        pos,
        node_size=node_sizes,
        alpha=0.95,
    )

    # desenhar arestas
    nx.draw_networkx_edges(
        graph_for_plot,
        pos,
        width=edge_widths,
        arrows=True,
        arrowstyle="->",
        arrowsize=22,
        alpha=0.80,
        connectionstyle="arc3,rad=0.08",
    )

    # labels
    nx.draw_networkx_labels(
        graph_for_plot,
        pos,
        font_size=10,
        font_weight="bold",
    )

    plt.title("Squad Dependency Graph")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()