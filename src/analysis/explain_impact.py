from __future__ import annotations

import networkx as nx


def explain_squad_impact(graph: nx.DiGraph, squad: str) -> dict:
    """
    Explica por que uma squad é estruturalmente crítica.
    """

    if squad not in graph:
        return {"error": f"{squad} not found in graph"}

    # Quem depende dessa squad (arestas entrando)
    dependents = list(graph.predecessors(squad))

    # Quem essa squad depende (arestas saindo)
    dependencies = list(graph.successors(squad))

    # Grau
    in_degree = graph.in_degree(squad)
    out_degree = graph.out_degree(squad)

    # Betweenness (influência no fluxo)
    betweenness = nx.betweenness_centrality(graph.to_undirected())
    betweenness_score = betweenness.get(squad, 0)

    # Dependência de nível 2 (efeito cascata)
    cascade = set()
    for dep in dependents:
        cascade.update(list(graph.predecessors(dep)))

    cascade.discard(squad)

    explanation = {
        "squad": squad,
        "direct_dependents": dependents,
        "direct_dependencies": dependencies,
        "in_degree": in_degree,
        "out_degree": out_degree,
        "betweenness_centrality": round(betweenness_score, 4),
        "cascade_impact": list(cascade),
        "summary": build_summary(
            squad,
            dependents,
            dependencies,
            in_degree,
            out_degree,
            betweenness_score,
        ),
    }

    return explanation


def build_summary(
    squad,
    dependents,
    dependencies,
    in_degree,
    out_degree,
    betweenness,
) -> str:
    """
    Gera explicação executiva.
    """

    return (
        f"{squad} has {in_degree} incoming dependencies "
        f"(other squads depend on it) and {out_degree} outgoing dependencies. "
        f"It influences system flow with a betweenness centrality of {round(betweenness, 3)}. "
        f"The squad directly impacts {len(dependents)} squads."
    )