from __future__ import annotations

import networkx as nx

from src.simulations.impact_simulation import (
    measure_graph_structure,
    simulate_squad_removal_impact,
)


# ==========================================================
# TESTES DE SIMULAÇÃO DE IMPACTO
# ==========================================================
#
# Objetivo:
# Garantir que a remoção de uma squad:
# - altere corretamente a estrutura da rede
# - produza deltas consistentes
# ==========================================================


def build_sample_graph() -> nx.DiGraph:
    """
    Constrói um grafo simples:

    Squad A -> Squad B
    Squad C -> Squad B
    Squad B -> Squad D
    """
    graph = nx.DiGraph()
    graph.add_edge("Squad A", "Squad B")
    graph.add_edge("Squad C", "Squad B")
    graph.add_edge("Squad B", "Squad D")
    return graph


def test_measure_graph_structure_should_return_expected_keys() -> None:
    """
    Deve retornar o conjunto básico de propriedades da rede.
    """
    dependency_graph = build_sample_graph()

    result = measure_graph_structure(dependency_graph)

    expected_keys = {
        "number_of_nodes",
        "number_of_edges",
        "density",
        "number_of_weakly_connected_components",
    }

    assert expected_keys.issubset(set(result.keys()))
    assert result["number_of_nodes"] == 4
    assert result["number_of_edges"] == 3


def test_simulate_squad_removal_impact_should_reduce_nodes_and_edges() -> None:
    """
    Deve reduzir nós e arestas ao remover uma squad existente.
    """
    dependency_graph = build_sample_graph()

    result = simulate_squad_removal_impact(
        dependency_graph=dependency_graph,
        squad_to_remove="Squad B",
    )

    assert result["removed_squad"] == "Squad B"

    original_metrics = result["original_metrics"]
    simulated_metrics = result["simulated_metrics"]
    delta = result["delta"]

    assert original_metrics["number_of_nodes"] == 4
    assert simulated_metrics["number_of_nodes"] == 3
    assert delta["nodes"] == -1

    assert original_metrics["number_of_edges"] == 3
    assert simulated_metrics["number_of_edges"] == 0
    assert delta["edges"] == -3


def test_simulate_squad_removal_impact_should_not_break_if_node_does_not_exist() -> None:
    """
    Deve se comportar de forma estável mesmo se a squad não existir.
    """
    dependency_graph = build_sample_graph()

    result = simulate_squad_removal_impact(
        dependency_graph=dependency_graph,
        squad_to_remove="Squad Inexistente",
    )

    assert result["removed_squad"] == "Squad Inexistente"
    assert result["delta"]["nodes"] == 0
    assert result["delta"]["edges"] == 0