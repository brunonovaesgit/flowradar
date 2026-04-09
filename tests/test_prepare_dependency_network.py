from __future__ import annotations

import pandas as pd

from src.graph_builder.prepare_dependency_network import (
    build_dependency_graph,
    build_squad_relationships_table,
)


# ==========================================================
# TESTES DE CONSTRUÇÃO DA REDE
# ==========================================================
#
# Objetivo:
# Garantir que:
# - itens sejam corretamente traduzidos em relações entre squads
# - o grafo seja construído com os nós e arestas esperados
# ==========================================================


def test_build_squad_relationships_table_should_map_items_to_squads() -> None:
    """
    Deve transformar relações entre itens em relações entre squads.
    """
    work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": "F2", "team": "Squad B"},
            {"item_id": "F3", "team": "Squad C"},
        ]
    )

    relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
            {"source_item": "F2", "target_item": "F3"},
        ]
    )

    result = build_squad_relationships_table(
        work_items=work_items,
        relationships=relationships,
    )

    assert len(result) == 2
    assert list(result.columns) == [
        "source_item",
        "target_item",
        "source_squad",
        "target_squad",
    ]

    first_row = result.iloc[0]
    assert first_row["source_squad"] == "Squad A"
    assert first_row["target_squad"] == "Squad B"


def test_build_dependency_graph_should_create_expected_nodes_and_edges() -> None:
    """
    Deve criar um grafo com as squads corretas e arestas corretas.
    """
    squad_relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2", "source_squad": "Squad A", "target_squad": "Squad B"},
            {"source_item": "F2", "target_item": "F3", "source_squad": "Squad B", "target_squad": "Squad C"},
            {"source_item": "F3", "target_item": "F1", "source_squad": "Squad C", "target_squad": "Squad A"},
        ]
    )

    dependency_graph = build_dependency_graph(
        squad_relationships_table=squad_relationships
    )

    assert dependency_graph.number_of_nodes() == 3
    assert dependency_graph.number_of_edges() == 3

    assert dependency_graph.has_edge("Squad A", "Squad B")
    assert dependency_graph.has_edge("Squad B", "Squad C")
    assert dependency_graph.has_edge("Squad C", "Squad A")