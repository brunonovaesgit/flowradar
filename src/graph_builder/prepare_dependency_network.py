from __future__ import annotations

import networkx as nx
import pandas as pd


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

    for _, row in squad_relationships_table.iterrows():
        source_squad = row["source_squad"]
        target_squad = row["target_squad"]

        dependency_graph.add_edge(source_squad, target_squad)

    return dependency_graph