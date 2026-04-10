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


def _build_node_color_map(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame | None = None,
) -> dict[str, str]:
    """
    Define cores dos nós com foco executivo:
    - top 1: vermelho
    - top 2 e top 3: laranja
    - demais: azul
    """
    default_color = "#4C78A8"
    top_1_color = "#D62728"
    top_2_3_color = "#F28E2B"

    color_map = {node: default_color for node in dependency_graph.nodes()}

    if (
        structural_metrics_table is None
        or structural_metrics_table.empty
        or "squad" not in structural_metrics_table.columns
        or "structural_criticality_score" not in structural_metrics_table.columns
    ):
        return color_map

    ranking = structural_metrics_table.sort_values(
        by="structural_criticality_score",
        ascending=False,
    )["squad"].tolist()

    if len(ranking) >= 1:
        color_map[ranking[0]] = top_1_color

    for squad in ranking[1:3]:
        color_map[squad] = top_2_3_color

    return color_map


def _filter_graph_for_executive_view(
    dependency_graph: nx.DiGraph,
    structural_metrics_table: pd.DataFrame | None = None,
    min_edge_weight: int = 2,
    keep_top_n_squads: int = 5,
) -> nx.DiGraph:
    """
    Cria uma visão executiva do grafo:
    - remove self-loops
    - mantém arestas com peso >= min_edge_weight
    - preserva conexões das squads mais críticas, mesmo se a aresta for menor
    """
    graph_for_plot = dependency_graph.copy()

    self_loops = list(nx.selfloop_edges(graph_for_plot))
    graph_for_plot.remove_edges_from(self_loops)

    top_squads: set[str] = set()

    if (
        structural_metrics_table is not None
        and not structural_metrics_table.empty
        and "squad" in structural_metrics_table.columns
        and "structural_criticality_score" in structural_metrics_table.columns
    ):
        top_squads = set(
            structural_metrics_table.sort_values(
                by="structural_criticality_score",
                ascending=False,
            )["squad"].head(keep_top_n_squads).tolist()
        )

    filtered_graph = nx.DiGraph()
    filtered_graph.add_nodes_from(graph_for_plot.nodes(data=True))

    for source, target, data in graph_for_plot.edges(data=True):
        weight = int(data.get("weight", 1))

        should_keep = (
            weight >= min_edge_weight
            or source in top_squads
            or target in top_squads
        )

        if should_keep:
            filtered_graph.add_edge(source, target, **data)

    isolated_nodes = list(nx.isolates(filtered_graph))
    filtered_graph.remove_nodes_from(isolated_nodes)

    return filtered_graph


def export_dependency_graph_visual(
    dependency_graph: nx.DiGraph,
    output_file: str,
    structural_metrics_table: pd.DataFrame | None = None,
) -> None:
    """
    Gera visual executivo do grafo de dependências entre squads.

    Melhorias visuais:
    - tamanho dos nós pela criticidade estrutural
    - destaque automático do top 3
    - remoção de self-loops da visualização principal
    - filtro de arestas para reduzir ruído
    - layout mais legível
    """
    executive_graph = _filter_graph_for_executive_view(
        dependency_graph=dependency_graph,
        structural_metrics_table=structural_metrics_table,
        min_edge_weight=2,
        keep_top_n_squads=5,
    )

    plt.figure(figsize=(14, 10))

    if len(executive_graph.nodes()) == 0:
        plt.title("Squad Dependency Graph - Executive View")
        plt.axis("off")
        plt.tight_layout()
        plt.savefig(output_file, dpi=150)
        plt.close()
        return

    pos = nx.kamada_kawai_layout(executive_graph)

    edge_weights = [
        executive_graph[u][v].get("weight", 1)
        for u, v in executive_graph.edges()
    ]

    max_weight = max(edge_weights) if edge_weights else 1
    edge_widths = [
        1.4 + (weight / max_weight) * 5.5
        for weight in edge_weights
    ]

    node_size_map = _build_node_size_map(
        dependency_graph=executive_graph,
        structural_metrics_table=structural_metrics_table,
    )
    node_sizes = [
        node_size_map.get(node, 1800)
        for node in executive_graph.nodes()
    ]

    node_color_map = _build_node_color_map(
        dependency_graph=executive_graph,
        structural_metrics_table=structural_metrics_table,
    )
    node_colors = [
        node_color_map.get(node, "#4C78A8")
        for node in executive_graph.nodes()
    ]

    nx.draw_networkx_nodes(
        executive_graph,
        pos,
        node_size=node_sizes,
        node_color=node_colors,
        alpha=0.95,
        edgecolors="white",
        linewidths=1.5,
    )

    nx.draw_networkx_edges(
        executive_graph,
        pos,
        width=edge_widths,
        arrows=True,
        arrowstyle="->",
        arrowsize=22,
        alpha=0.55,
        edge_color="#2F2F2F",
        connectionstyle="arc3,rad=0.08",
        min_source_margin=15,
        min_target_margin=15,
    )

    nx.draw_networkx_labels(
        executive_graph,
        pos,
        font_size=10,
        font_weight="bold",
    )

    plt.title("Squad Dependency Graph - Executive View")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()