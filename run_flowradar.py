from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd

from src.pipeline.validation import validate_minimum_data
from src.pipeline.input_contract_validation import validate_input_contract
from src.graph_builder.prepare_dependency_network import (
    build_dependency_graph,
    build_squad_relationships_table,
    export_dependency_graph_visual,
)
from src.metrics.network_centrality import (
    calculate_and_export_structural_metrics,
)
from src.metrics.risk_analysis import (
    calculate_risk_analysis,
    export_risk_analysis,
)
from src.reports.executive_report import (
    generate_executive_report,
)
from src.visualizations.dependency_heatmap import (
    build_dependency_matrix,
    generate_dependency_heatmap,
)
from src.visualizations.visual_style import (
    LAYOUT,
    PALETTE,
    TYPOGRAPHY,
    build_standard_subtitle,
    build_standard_title,
)
from src.simulations.impact_simulation import (
    simulate_squad_removal_impact,
    export_simulation_result,
)


# ==========================================================
# FLOWRADAR - ENTRY POINT
# ==========================================================


def resolve_input_directory(
    input_dir: str | None,
    mode: str | None,
) -> Path:
    if input_dir:
        return Path(input_dir)

    if mode == "prod":
        return Path("data/raw/prod")

    return Path("data/raw/example")


def expected_file_names_for_directory(input_path: Path) -> dict[str, str]:
    if input_path.name == "example":
        return {
            "work_items": "example_work_items.csv",
            "relationships": "example_relationships.csv",
            "team_mapping": "example_team_mapping.csv",
        }

    return {
        "work_items": "work_items.csv",
        "relationships": "relationships.csv",
        "team_mapping": "team_mapping.csv",
    }


def validate_input_directory_exists(input_path: Path) -> None:
    if not input_path.exists():
        raise FileNotFoundError(
            f"Diretório de entrada não encontrado: {input_path}"
        )

    if not input_path.is_dir():
        raise NotADirectoryError(
            f"O caminho informado não é um diretório: {input_path}"
        )


def validate_required_input_files(input_path: Path) -> dict[str, Path]:
    expected_files = expected_file_names_for_directory(input_path)

    resolved_files = {
        logical_name: input_path / file_name
        for logical_name, file_name in expected_files.items()
    }

    missing_files = [
        file_path.name
        for file_path in resolved_files.values()
        if not file_path.exists()
    ]

    if missing_files:
        missing_list = ", ".join(sorted(missing_files))
        raise FileNotFoundError(
            "Arquivos obrigatórios não encontrados no diretório de entrada: "
            f"{missing_list}"
        )

    return resolved_files


def load_raw_input_data(input_path: Path) -> dict[str, pd.DataFrame]:
    resolved_files = validate_required_input_files(input_path)

    work_items = pd.read_csv(
        resolved_files["work_items"],
        encoding="utf-8-sig",
    )
    relationships = pd.read_csv(
        resolved_files["relationships"],
        encoding="utf-8-sig",
    )
    team_mapping = pd.read_csv(
        resolved_files["team_mapping"],
        encoding="utf-8-sig",
    )

    return {
        "work_items": work_items,
        "relationships": relationships,
        "team_mapping": team_mapping,
    }


def generate_summary(
    structural_metrics_table: pd.DataFrame,
    squad_relationships_table: pd.DataFrame,
) -> dict:
    if structural_metrics_table.empty:
        return {
            "total_squads": 0,
            "total_dependencies": 0,
            "top_bottleneck": None,
            "top_bottleneck_score": None,
        }

    top_row = structural_metrics_table.iloc[0]

    return {
        "total_squads": int(structural_metrics_table["squad"].nunique()),
        "total_dependencies": int(len(squad_relationships_table)),
        "top_bottleneck": top_row["squad"],
        "top_bottleneck_score": float(top_row["structural_criticality_score"]),
    }


def save_summary(summary_data: dict, output_file: Path) -> None:
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(summary_data, file, ensure_ascii=False, indent=2)


def print_execution_header(input_path: Path, output_path: Path) -> None:
    print("\n[FlowRadar] Iniciando processamento...\n")
    print(f"[FlowRadar] Diretório de entrada : {input_path.resolve()}")
    print(f"[FlowRadar] Diretório de outputs : {output_path.resolve()}\n")


def print_execution_success(output_path: Path) -> None:
    print("\n[FlowRadar] 🚀 Processamento concluído com sucesso")
    print(f"[FlowRadar] Outputs gerados em: {output_path.resolve()}\n")


def print_top_structural_ranking(
    structural_metrics_table: pd.DataFrame,
    top_n: int = 5,
) -> None:
    if structural_metrics_table.empty:
        print("[FlowRadar] ⚠ Nenhuma métrica estrutural disponível para ranking")
        return

    ranking_table = structural_metrics_table.sort_values(
        by="structural_criticality_score",
        ascending=False,
    ).head(top_n)

    print("[FlowRadar] 🔝 Top squads por criticidade estrutural:")
    for _, row in ranking_table.iterrows():
        squad = row["squad"]
        score = row["structural_criticality_score"]
        print(f"  - {squad}: {score:.4f}")
    print()


def print_top_risk_analysis(
    risk_analysis_table: pd.DataFrame,
    top_n: int = 5,
) -> None:
    if risk_analysis_table.empty:
        print("[FlowRadar] ⚠ Nenhuma análise de risco disponível")
        return

    print("[FlowRadar] ⚠ Top riscos organizacionais:")
    for _, row in risk_analysis_table.head(top_n).iterrows():
        squad = row["squad"]
        score = row["risk_score"]
        category = row["risk_category"]
        print(f"  - {squad} | score={score:.3f} | tipo={category}")
    print()


def export_criticality_ranking_visual(
    structural_metrics_table: pd.DataFrame,
    output_file: Path,
    top_n: int = 10,
) -> None:
    if structural_metrics_table.empty:
        return

    ranking_table = structural_metrics_table.sort_values(
        by="structural_criticality_score",
        ascending=False,
    ).head(top_n)

    squads = ranking_table["squad"]
    scores = ranking_table["structural_criticality_score"]

    plt.figure(figsize=(LAYOUT.figure_width, LAYOUT.figure_height))

    bars = plt.barh(
        squads,
        scores,
        color=PALETTE.blue,
        edgecolor=PALETTE.white,
    )

    for i, bar in enumerate(bars):
        if i == 0:
            bar.set_color(PALETTE.red)
        elif i < 3:
            bar.set_color(PALETTE.orange)

    plt.gca().invert_yaxis()
    plt.xlabel(
        "Structural Criticality Score",
        fontsize=TYPOGRAPHY.label_size,
    )

    plt.title(
        build_standard_title("Squad Criticality Ranking"),
        fontsize=TYPOGRAPHY.title_size,
        fontweight=TYPOGRAPHY.title_weight,
    )

    plt.figtext(
        0.5,
        0.92,
        build_standard_subtitle(
            "Higher scores indicate structurally critical squads in the dependency network"
        ),
        ha="center",
        fontsize=TYPOGRAPHY.subtitle_size,
        color=PALETTE.mid_gray,
    )

    plt.scatter([], [], color=PALETTE.red, label="Top bottleneck")
    plt.scatter([], [], color=PALETTE.orange, label="High criticality")
    plt.scatter([], [], color=PALETTE.blue, label="Other squads")

    plt.legend(loc="lower right", fontsize=TYPOGRAPHY.legend_size)

    plt.tight_layout()
    plt.savefig(output_file, dpi=LAYOUT.dpi)
    plt.close()


# ==========================================================
# EXPLAIN IMPACT ENGINE
# ==========================================================


def build_impact_summary(
    squad: str,
    direct_dependents: list[str],
    direct_dependencies: list[str],
    in_degree: int,
    out_degree: int,
    betweenness_score: float,
) -> str:
    return (
        f"{squad} has {in_degree} incoming dependencies "
        f"(other squads depend on it) and {out_degree} outgoing dependencies. "
        f"It directly impacts {len(direct_dependents)} squads and depends on "
        f"{len(direct_dependencies)} squads. "
        f"Its betweenness centrality is {betweenness_score:.4f}, indicating how much "
        f"it influences the overall flow of the network."
    )


def explain_squad_impact(
    dependency_graph: nx.DiGraph,
    squad: str,
) -> dict:
    """
    Explica por que uma squad é estruturalmente crítica.
    """
    if squad not in dependency_graph:
        return {
            "squad": squad,
            "error": "Squad not found in graph.",
        }

    direct_dependents = sorted(list(dependency_graph.predecessors(squad)))
    direct_dependencies = sorted(list(dependency_graph.successors(squad)))

    in_degree = dependency_graph.in_degree(squad)
    out_degree = dependency_graph.out_degree(squad)

    betweenness = nx.betweenness_centrality(dependency_graph.to_undirected())
    betweenness_score = float(betweenness.get(squad, 0.0))

    cascade_impact = set()
    for dependent in direct_dependents:
        cascade_impact.update(list(dependency_graph.predecessors(dependent)))

    cascade_impact.discard(squad)

    explanation = {
        "squad": squad,
        "direct_dependents": direct_dependents,
        "direct_dependencies": direct_dependencies,
        "in_degree": int(in_degree),
        "out_degree": int(out_degree),
        "betweenness_centrality": round(betweenness_score, 4),
        "cascade_impact": sorted(list(cascade_impact)),
        "summary": build_impact_summary(
            squad=squad,
            direct_dependents=direct_dependents,
            direct_dependencies=direct_dependencies,
            in_degree=in_degree,
            out_degree=out_degree,
            betweenness_score=betweenness_score,
        ),
    }

    return explanation


def export_impact_explanation(
    explanation: dict,
    output_file: str | Path,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(explanation, file, ensure_ascii=False, indent=2)

    return output_path


def main(
    input_dir: str | None = None,
    mode: str | None = None,
    simulate_squad: str | None = None,
) -> None:
    input_path = resolve_input_directory(
        input_dir=input_dir,
        mode=mode,
    )
    output_path = Path("data/outputs")
    output_path.mkdir(parents=True, exist_ok=True)

    print_execution_header(
        input_path=input_path,
        output_path=output_path,
    )

    # 1. VALIDAÇÃO DO DIRETÓRIO DE ENTRADA
    try:
        validate_input_directory_exists(input_path)
        print("[FlowRadar] ✔ Diretório de entrada validado")
    except (FileNotFoundError, NotADirectoryError) as error:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {error}")
        return

    # 2. LEITURA DOS DADOS
    try:
        raw_data = load_raw_input_data(input_path)
        print("[FlowRadar] ✔ Arquivos obrigatórios encontrados e carregados")
    except FileNotFoundError as error:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {error}\n")
        print("Estrutura esperada:")
        print("- example: example_work_items.csv, example_relationships.csv, example_team_mapping.csv")
        print("- prod   : work_items.csv, relationships.csv, team_mapping.csv")
        return
    except Exception as error:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print("Motivo: falha ao carregar os dados de entrada.")
        print(f"Detalhe: {error}")
        return

    work_items = raw_data["work_items"]
    relationships = raw_data["relationships"]
    team_mapping = raw_data["team_mapping"]

    # 3. VALIDAÇÃO MÍNIMA
    minimum_validation = validate_minimum_data(raw_data)

    if not minimum_validation["is_valid"]:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {minimum_validation['reason']}")
        return

    print("[FlowRadar] ✔ Dados mínimos validados")

    # 4. VALIDAÇÃO DO CONTRATO CANÔNICO
    contract_validation = validate_input_contract(
        work_items=work_items,
        relationships=relationships,
        team_mapping=team_mapping,
    )

    if not contract_validation.is_valid:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(contract_validation.build_human_readable_message())
        return

    print("[FlowRadar] ✔ Contrato canônico de entrada validado")

    if contract_validation.warnings:
        print("[FlowRadar] ⚠ Avisos encontrados na validação:")
        for warning in contract_validation.warnings:
            print(f"  - {warning}")
        print()

    # 5. TABELA DE RELAÇÕES ENTRE SQUADS
    squad_relationships = build_squad_relationships_table(
        work_items=work_items,
        relationships=relationships,
    )

    squad_relationships.to_csv(
        output_path / "squad_relationships.csv",
        index=False,
        encoding="utf-8-sig",
    )

    print("[FlowRadar] ✔ Relações entre squads preparadas")
    print("[FlowRadar] ✔ squad_relationships.csv gerado")

    # 6. CONSTRUÇÃO DO GRAFO DE DEPENDÊNCIAS
    dependency_graph = build_dependency_graph(
        squad_relationships_table=squad_relationships
    )

    print("[FlowRadar] ✔ Grafo organizacional construído")

    # 7. MÉTRICAS ESTRUTURAIS
    structural_metrics = calculate_and_export_structural_metrics(
        dependency_graph=dependency_graph,
        output_file=output_path / "structural_metrics.csv",
    )

    print("[FlowRadar] ✔ Métricas estruturais calculadas")

    print_top_structural_ranking(
        structural_metrics_table=structural_metrics,
        top_n=5,
    )

    export_criticality_ranking_visual(
        structural_metrics_table=structural_metrics,
        output_file=output_path / "criticality_ranking.png",
        top_n=10,
    )

    print("[FlowRadar] ✔ Ranking de criticidade gerado")

    # 8. ANÁLISE DE RISCO ORGANIZACIONAL
    risk_analysis = calculate_risk_analysis(
        dependency_graph=dependency_graph,
        structural_metrics_table=structural_metrics,
    )

    export_risk_analysis(
        risk_table=risk_analysis,
        output_file=output_path / "risk_analysis.csv",
    )

    print("[FlowRadar] ✔ Análise de risco gerada")

    print_top_risk_analysis(
        risk_analysis_table=risk_analysis,
        top_n=5,
    )

    # 9. GRAFO VISUAL
    export_dependency_graph_visual(
        dependency_graph=dependency_graph,
        output_file=output_path / "dependency_graph.png",
        structural_metrics_table=structural_metrics,
    )

    print("[FlowRadar] ✔ Grafo visual gerado")

    # 10. MATRIZ DE DEPENDÊNCIAS + HEATMAP
    dependency_matrix = build_dependency_matrix(
        squad_relationships_table=squad_relationships
    )

    dependency_matrix.to_csv(
        output_path / "dependency_matrix.csv",
        index=True,
        encoding="utf-8-sig",
    )

    generate_dependency_heatmap(
        dependency_matrix=dependency_matrix,
        output_file=output_path / "dependency_heatmap.png",
    )

    print("[FlowRadar] ✔ Heatmap gerado")

    # 11. SUMMARY EXECUTIVO
    summary = generate_summary(
        structural_metrics_table=structural_metrics,
        squad_relationships_table=squad_relationships,
    )

    save_summary(
        summary_data=summary,
        output_file=output_path / "summary.json",
    )

    print("[FlowRadar] ✔ Summary gerado")

    # 12. SIMULAÇÃO OPCIONAL DE IMPACTO
    report_filename = "flowradar_report.html"

    if simulate_squad:
        impact_json_file = output_path / f"impact_simulation_{simulate_squad}.json"
        impact_graph_file = output_path / f"dependency_graph_impact_{simulate_squad}.png"
        impact_explanation_file = output_path / f"impact_explanation_{simulate_squad}.json"
        report_filename = f"flowradar_report_simulation_{simulate_squad}.html"

        simulation_result = simulate_squad_removal_impact(
            dependency_graph=dependency_graph,
            squad_to_remove=simulate_squad,
        )

        export_simulation_result(
            simulation_result=simulation_result,
            output_file=impact_json_file,
        )

        from src.graph_builder.prepare_dependency_network import (
            export_impact_graph_visual,
        )

        export_impact_graph_visual(
            dependency_graph=dependency_graph,
            removed_squad=simulate_squad,
            output_file=impact_graph_file,
            structural_metrics_table=structural_metrics,
        )

        explanation = explain_squad_impact(
            dependency_graph=dependency_graph,
            squad=simulate_squad,
        )

        export_impact_explanation(
            explanation=explanation,
            output_file=impact_explanation_file,
        )

        print(
            f"[FlowRadar] ✔ Simulação de impacto executada para a squad: {simulate_squad}"
        )
        print("[FlowRadar] ✔ Grafo de impacto gerado")
        print("[FlowRadar] ✔ Explain Impact gerado")
        print("[FlowRadar] 🧠 Explain Impact:")
        print(f"  - {explanation['summary']}")
        print()

    # 13. RELATÓRIO EXECUTIVO HTML
    report_file = generate_executive_report(
        output_path,
        file_name=report_filename,
    )
    print(f"[FlowRadar] ✔ Relatório executivo gerado: {report_file.resolve()}")

    # 14. FINALIZAÇÃO
    print_execution_success(output_path=output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="FlowRadar - análise sistêmica de fluxo e dependências"
    )

    parser.add_argument(
        "--input",
        required=False,
        help=(
            "Diretório de entrada com os CSVs. "
            "Exemplo: ./data/raw/example ou ./data/raw/prod"
        ),
    )

    parser.add_argument(
        "--mode",
        required=False,
        choices=["example", "prod"],
        help=(
            "Modo de execução padronizado. "
            "Se usado, aponta automaticamente para data/raw/example ou data/raw/prod"
        ),
    )

    parser.add_argument(
        "--simulate-squad",
        required=False,
        help="Nome da squad a remover na simulação de impacto",
    )

    args = parser.parse_args()

    main(
        input_dir=args.input,
        mode=args.mode,
        simulate_squad=args.simulate_squad,
    )