from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
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
from src.visualizations.dependency_heatmap import (
    build_dependency_matrix,
    generate_dependency_heatmap,
)
from src.simulations.impact_simulation import (
    simulate_squad_removal_impact,
    export_simulation_result,
)


# ==========================================================
# FLOWRADAR - ENTRY POINT
# ==========================================================
#
# Este é o ponto único de execução do FlowRadar.
#
# Exemplos de uso:
#
# 1) Rodar com dados de exemplo:
#    python run_flowradar.py --mode example
#
# 2) Rodar com dados reais:
#    python run_flowradar.py --mode prod
#
# 3) Rodar apontando um diretório manualmente:
#    python run_flowradar.py --input ./data/raw/example
#
# 4) Rodar com simulação de impacto:
#    python run_flowradar.py --mode example --simulate-squad "Squad B"
#
# ==========================================================


def resolve_input_directory(
    input_dir: str | None,
    mode: str | None,
) -> Path:
    """
    Resolve o diretório de entrada.

    Prioridade:
    1. --input
    2. --mode
    3. fallback para example
    """
    if input_dir:
        return Path(input_dir)

    if mode == "prod":
        return Path("data/raw/prod")

    return Path("data/raw/example")


def expected_file_names_for_directory(input_path: Path) -> dict[str, str]:
    """
    Define os nomes de arquivos esperados para o diretório informado.

    Convenção:
    - pasta example  -> arquivos com prefixo example_
    - pasta prod     -> arquivos sem prefixo
    """
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
    """
    Garante que o diretório de entrada exista e seja realmente uma pasta.
    """
    if not input_path.exists():
        raise FileNotFoundError(
            f"Diretório de entrada não encontrado: {input_path}"
        )

    if not input_path.is_dir():
        raise NotADirectoryError(
            f"O caminho informado não é um diretório: {input_path}"
        )


def validate_required_input_files(input_path: Path) -> dict[str, Path]:
    """
    Garante que os arquivos obrigatórios existam no diretório de entrada.
    """
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
    """
    Carrega os arquivos CSV de entrada do FlowRadar.
    """
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
    """
    Gera um resumo executivo simples da execução.
    """
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
    """
    Salva o summary executivo em JSON.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(summary_data, file, ensure_ascii=False, indent=2)


def print_execution_header(input_path: Path, output_path: Path) -> None:
    """
    Imprime o cabeçalho de execução.
    """
    print("\n[FlowRadar] Iniciando processamento...\n")
    print(f"[FlowRadar] Diretório de entrada : {input_path.resolve()}")
    print(f"[FlowRadar] Diretório de outputs : {output_path.resolve()}\n")


def print_execution_success(output_path: Path) -> None:
    """
    Imprime mensagem final de sucesso.
    """
    print("\n[FlowRadar] 🚀 Processamento concluído com sucesso")
    print(f"[FlowRadar] Outputs gerados em: {output_path.resolve()}\n")


def print_top_structural_ranking(
    structural_metrics_table: pd.DataFrame,
    top_n: int = 5,
) -> None:
    """
    Imprime no terminal o ranking das squads por criticidade estrutural.
    """
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


def generate_criticality_ranking_chart(
    structural_metrics_table: pd.DataFrame,
    output_file: Path,
    top_n: int = 10,
) -> None:
    """
    Gera gráfico horizontal com ranking de criticidade estrutural.
    """
    if structural_metrics_table.empty:
        return

    ranking_table = structural_metrics_table.sort_values(
        by="structural_criticality_score",
        ascending=False,
    ).head(top_n)

    plt.figure(figsize=(10, 6))
    plt.barh(
        ranking_table["squad"],
        ranking_table["structural_criticality_score"],
    )
    plt.gca().invert_yaxis()
    plt.title("Structural Criticality Ranking")
    plt.xlabel("Structural Criticality Score")
    plt.ylabel("Squad")
    plt.tight_layout()
    plt.savefig(output_file, dpi=150)
    plt.close()


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

    # ------------------------------------------------------
    # 1. VALIDAÇÃO DO DIRETÓRIO DE ENTRADA
    # ------------------------------------------------------
    try:
        validate_input_directory_exists(input_path)
        print("[FlowRadar] ✔ Diretório de entrada validado")
    except (FileNotFoundError, NotADirectoryError) as error:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {error}")
        return

    # ------------------------------------------------------
    # 2. LEITURA DOS DADOS
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # 3. VALIDAÇÃO MÍNIMA
    # ------------------------------------------------------
    minimum_validation = validate_minimum_data(raw_data)

    if not minimum_validation["is_valid"]:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {minimum_validation['reason']}")
        return

    print("[FlowRadar] ✔ Dados mínimos validados")

    # ------------------------------------------------------
    # 4. VALIDAÇÃO DO CONTRATO CANÔNICO
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # 5. TABELA DE RELAÇÕES ENTRE SQUADS
    # ------------------------------------------------------
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

    # ------------------------------------------------------
    # 6. CONSTRUÇÃO DO GRAFO DE DEPENDÊNCIAS
    # ------------------------------------------------------
    dependency_graph = build_dependency_graph(
        squad_relationships_table=squad_relationships
    )

    print("[FlowRadar] ✔ Grafo organizacional construído")

    export_dependency_graph_visual(
        dependency_graph=dependency_graph,
        output_file=output_path / "dependency_graph.png",
    )

    print("[FlowRadar] ✔ Grafo visual gerado")

    # ------------------------------------------------------
    # 7. MÉTRICAS ESTRUTURAIS
    # ------------------------------------------------------
    structural_metrics = calculate_and_export_structural_metrics(
        dependency_graph=dependency_graph,
        output_file=output_path / "structural_metrics.csv",
    )

    print("[FlowRadar] ✔ Métricas estruturais calculadas")

    print_top_structural_ranking(
        structural_metrics_table=structural_metrics,
        top_n=5,
    )

    generate_criticality_ranking_chart(
        structural_metrics_table=structural_metrics,
        output_file=output_path / "criticality_ranking.png",
        top_n=10,
    )

    print("[FlowRadar] ✔ Ranking de criticidade gerado")

    # ------------------------------------------------------
    # 8. MATRIZ DE DEPENDÊNCIAS + HEATMAP
    # ------------------------------------------------------
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
        title="Heatmap of Dependencies Between Squads",
    )

    print("[FlowRadar] ✔ Heatmap gerado")

    # ------------------------------------------------------
    # 9. SUMMARY EXECUTIVO
    # ------------------------------------------------------
    summary = generate_summary(
        structural_metrics_table=structural_metrics,
        squad_relationships_table=squad_relationships,
    )

    save_summary(
        summary_data=summary,
        output_file=output_path / "summary.json",
    )

    print("[FlowRadar] ✔ Summary gerado")

    # ------------------------------------------------------
    # 10. SIMULAÇÃO OPCIONAL DE IMPACTO
    # ------------------------------------------------------
    if simulate_squad:
        simulation_result = simulate_squad_removal_impact(
            dependency_graph=dependency_graph,
            squad_to_remove=simulate_squad,
        )

        export_simulation_result(
            simulation_result=simulation_result,
            output_file=output_path / "impact_simulation.json",
        )

        print(
            f"[FlowRadar] ✔ Simulação de impacto executada para a squad: {simulate_squad}"
        )

    # ------------------------------------------------------
    # 11. FINALIZAÇÃO
    # ------------------------------------------------------
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