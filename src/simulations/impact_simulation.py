from __future__ import annotations

import json
from pathlib import Path

import networkx as nx


# ==========================================================
# SIMULAÇÃO DE IMPACTO
# ==========================================================
#
# Este módulo mede o que acontece com a estrutura da rede
# quando uma squad é removida.
#
# A ideia aqui não é sugerir remoção literal de time, mas
# estimar criticidade estrutural.
# ==========================================================


def measure_graph_structure(dependency_graph: nx.DiGraph) -> dict:
    """
    Mede propriedades estruturais básicas da rede direcionada.
    """
    return {
        "number_of_nodes": dependency_graph.number_of_nodes(),
        "number_of_edges": dependency_graph.number_of_edges(),
        "density": nx.density(dependency_graph),
        "number_of_weakly_connected_components": nx.number_weakly_connected_components(
            dependency_graph
        ),
    }


def measure_global_connectivity_metrics(dependency_graph: nx.DiGraph) -> dict:
    """
    Mede propriedades globais adicionais da rede, convertendo para
    grafo não direcionado para avaliar conectividade estrutural.
    """
    undirected_graph = dependency_graph.to_undirected()

    if undirected_graph.number_of_nodes() == 0:
        return {
            "number_of_connected_components": 0,
            "largest_connected_component_size": 0,
            "average_betweenness_centrality": 0.0,
        }

    connected_components = list(nx.connected_components(undirected_graph))
    largest_connected_component_size = len(max(connected_components, key=len))

    betweenness = nx.betweenness_centrality(undirected_graph)
    average_betweenness = (
        sum(betweenness.values()) / len(betweenness)
        if betweenness
        else 0.0
    )

    return {
        "number_of_connected_components": nx.number_connected_components(
            undirected_graph
        ),
        "largest_connected_component_size": largest_connected_component_size,
        "average_betweenness_centrality": average_betweenness,
    }


def calculate_impact_score(
    original_graph: nx.DiGraph,
    simulated_graph: nx.DiGraph,
) -> float:
    """
    Calcula impacto sistêmico com base em:
    - variação no número de componentes conectados
    - variação no tamanho do maior componente
    - variação da betweenness centrality média

    Quanto maior o score, maior a disrupção estrutural causada
    pela remoção da squad.
    """
    original_connectivity = measure_global_connectivity_metrics(original_graph)
    simulated_connectivity = measure_global_connectivity_metrics(simulated_graph)

    connected_components_delta = abs(
        simulated_connectivity["number_of_connected_components"]
        - original_connectivity["number_of_connected_components"]
    )

    largest_component_delta = abs(
        original_connectivity["largest_connected_component_size"]
        - simulated_connectivity["largest_connected_component_size"]
    )

    average_betweenness_delta = abs(
        original_connectivity["average_betweenness_centrality"]
        - simulated_connectivity["average_betweenness_centrality"]
    )

    impact_score = (
        connected_components_delta * 2.0
        + largest_component_delta * 0.5
        + average_betweenness_delta * 5.0
    )

    return round(impact_score, 4)


def simulate_squad_removal_impact(
    dependency_graph: nx.DiGraph,
    squad_to_remove: str,
) -> dict:
    """
    Simula o impacto estrutural da remoção de uma squad.
    """
    original_graph = dependency_graph.copy()
    simulated_graph = dependency_graph.copy()

    original_metrics = measure_graph_structure(original_graph)
    original_connectivity_metrics = measure_global_connectivity_metrics(
        original_graph
    )

    if simulated_graph.has_node(squad_to_remove):
        simulated_graph.remove_node(squad_to_remove)

    simulated_metrics = measure_graph_structure(simulated_graph)
    simulated_connectivity_metrics = measure_global_connectivity_metrics(
        simulated_graph
    )

    impact_score = calculate_impact_score(
        original_graph=original_graph,
        simulated_graph=simulated_graph,
    )

    impact = {
        "removed_squad": squad_to_remove,
        "impact_score": impact_score,
        "original_metrics": original_metrics,
        "original_connectivity_metrics": original_connectivity_metrics,
        "simulated_metrics": simulated_metrics,
        "simulated_connectivity_metrics": simulated_connectivity_metrics,
        "delta": {
            "nodes": simulated_metrics["number_of_nodes"]
            - original_metrics["number_of_nodes"],
            "edges": simulated_metrics["number_of_edges"]
            - original_metrics["number_of_edges"],
            "density": simulated_metrics["density"]
            - original_metrics["density"],
            "weakly_connected_components": (
                simulated_metrics["number_of_weakly_connected_components"]
                - original_metrics["number_of_weakly_connected_components"]
            ),
            "connected_components": (
                simulated_connectivity_metrics["number_of_connected_components"]
                - original_connectivity_metrics["number_of_connected_components"]
            ),
            "largest_connected_component_size": (
                simulated_connectivity_metrics["largest_connected_component_size"]
                - original_connectivity_metrics["largest_connected_component_size"]
            ),
            "average_betweenness_centrality": (
                simulated_connectivity_metrics["average_betweenness_centrality"]
                - original_connectivity_metrics["average_betweenness_centrality"]
            ),
        },
    }

    return impact


def export_simulation_result(
    simulation_result: dict,
    output_file: str | Path,
) -> Path:
    """
    Exporta o resultado da simulação para JSON.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(simulation_result, file, ensure_ascii=False, indent=2)

    return output_path