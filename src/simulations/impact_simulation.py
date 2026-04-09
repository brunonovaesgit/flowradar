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
    Mede propriedades estruturais básicas da rede.
    """
    return {
        "number_of_nodes": dependency_graph.number_of_nodes(),
        "number_of_edges": dependency_graph.number_of_edges(),
        "density": nx.density(dependency_graph),
        "number_of_weakly_connected_components": nx.number_weakly_connected_components(
            dependency_graph
        ),
    }


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

    if simulated_graph.has_node(squad_to_remove):
        simulated_graph.remove_node(squad_to_remove)

    simulated_metrics = measure_graph_structure(simulated_graph)

    impact = {
        "removed_squad": squad_to_remove,
        "original_metrics": original_metrics,
        "simulated_metrics": simulated_metrics,
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