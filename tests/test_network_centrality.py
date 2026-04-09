from __future__ import annotations

import networkx as nx
import pandas as pd

from src.metrics.network_centrality import (
    build_structural_metrics_table,
    calculate_in_out_degree,
    calculate_pagerank,
    calculate_betweenness_centrality,
)


# ==========================================================
# TESTES DE MÉTRICAS ESTRUTURAIS
# ==========================================================
#
# Objetivo:
# Garantir que as métricas principais sejam calculadas
# corretamente em um cenário pequeno, controlado e previsível.
# ==========================================================


def build_sample_graph() -> nx.DiGraph:
    """
    Constrói um grafo simples para teste:

    Squad A -> Squad B
    Squad C -> Squad B
    Squad B -> Squad D

    Nesse cenário:
    - Squad B recebe 2 dependências
    - Squad B tende a ser ponte
    """
    graph = nx.DiGraph()
    graph.add_edge("Squad A", "Squad B")
    graph.add_edge("Squad C", "Squad B")
    graph.add_edge("Squad B", "Squad D")
    return graph


def test_calculate_in_out_degree_should_return_expected_values() -> None:
    """
    Deve calcular corretamente dependências recebidas e geradas.
    """
    dependency_graph = build_sample_graph()

    result = calculate_in_out_degree(dependency_graph)

    squad_b_row = result[result["squad"] == "Squad B"].iloc[0]
    squad_a_row = result[result["squad"] == "Squad A"].iloc[0]

    assert squad_b_row["dependencies_received_in_degree"] == 2
    assert squad_b_row["dependencies_generated_out_degree"] == 1

    assert squad_a_row["dependencies_received_in_degree"] == 0
    assert squad_a_row["dependencies_generated_out_degree"] == 1


def test_calculate_betweenness_centrality_should_identify_bridge_node() -> None:
    """
    Deve identificar Squad B como nó mais central em intermediação.
    """
    dependency_graph = build_sample_graph()

    result = calculate_betweenness_centrality(dependency_graph)

    squad_b_value = result[result["squad"] == "Squad B"].iloc[0]["betweenness_centrality"]
    squad_a_value = result[result["squad"] == "Squad A"].iloc[0]["betweenness_centrality"]

    assert squad_b_value > squad_a_value


def test_calculate_pagerank_should_return_non_empty_result() -> None:
    """
    Deve retornar uma tabela não vazia com PageRank para todos os nós.
    """
    dependency_graph = build_sample_graph()

    result = calculate_pagerank(dependency_graph)

    assert not result.empty
    assert set(result["squad"]) == {"Squad A", "Squad B", "Squad C", "Squad D"}


def test_build_structural_metrics_table_should_include_final_score() -> None:
    """
    Deve gerar tabela consolidada com score composto e ordenação.
    """
    dependency_graph = build_sample_graph()

    result = build_structural_metrics_table(dependency_graph)

    expected_columns = {
        "squad",
        "dependencies_received_in_degree",
        "dependencies_generated_out_degree",
        "betweenness_centrality",
        "pagerank",
        "in_degree_normalized",
        "betweenness_normalized",
        "pagerank_normalized",
        "structural_criticality_score",
    }

    assert expected_columns.issubset(set(result.columns))
    assert not result.empty

    # Em geral, Squad B deve aparecer como uma das mais críticas
    top_squad = result.iloc[0]["squad"]
    assert top_squad == "Squad B"