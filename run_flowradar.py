from _future_ import annotations

import argparse
from pathlib import Path

import pandas as pd

from src.pipeline.validation import validate_minimum_data
from src.graph_builder.prepare_dependency_network import (
    build_dependency_graph,
    build_squad_relationships_table,
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
# Este é o ponto único de execução do projeto.
#
# Uso:
# python run_flowradar.py --input ./data/raw
#
# O objetivo deste arquivo é orquestrar:
# 1. leitura dos dados
# 2. validação mínima
# 3. construção da rede
# 4. cálculo das métricas estruturais
# 5. geração de visualizações
# 6. simulação opcional de impacto
# ==========================================================


def load_raw_input_data(input_dir: Path) -> dict[str, pd.DataFrame]:
    """
    Lê os arquivos CSV mínimos esperados para o FlowRadar.

    Esperado:
    - example_work_items.csv
    - example_relationships.csv
    - example_team_mapping.csv

    Returns
    -------
    dict[str, pd.DataFrame]
        Dicionário com os dataframes carregados.
    """
    work_items_file = input_dir / "example_work_items.csv"
    relationships_file = input_dir / "example_relationships.csv"
    team_mapping_file = input_dir / "example_team_mapping.csv"

    work_items = pd.read_csv(work_items_file, encoding="utf-8-sig")
    relationships = pd.read_csv(relationships_file, encoding="utf-8-sig")
    team_mapping = pd.read_csv(team_mapping_file, encoding="utf-8-sig")

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
    Gera um resumo executivo simples a partir dos resultados.

    Este summary é intencionalmente enxuto, para servir como
    ponto de partida. Você pode enriquecer depois.
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
    Salva um resumo executivo em JSON.
    """
    import json

    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(summary_data, file, ensure_ascii=False, indent=2)


def main(input_dir: str, simulate_squad: str | None = None) -> None:
    input_path = Path(input_dir)
    output_path = Path("data/outputs")
    output_path.mkdir(parents=True, exist_ok=True)

    print("\n[FlowRadar] Iniciando processamento...\n")

    # ------------------------------------------------------
    # 1. LEITURA DOS DADOS
    # ------------------------------------------------------
    try:
        raw_data = load_raw_input_data(input_path)
    except FileNotFoundError as error:
        print("[FlowRadar] ❌ Execução interrompida\n")
        print("Motivo: arquivo de entrada não encontrado.")
        print(f"Detalhe: {error}")
        print("\nArquivos esperados dentro do diretório informado:")
        print("- example_work_items.csv")
        print("- example_relationships.csv")
        print("- example_team_mapping.csv")
        return

    print("[FlowRadar] ✔ Dados carregados")

    # ------------------------------------------------------
    # 2. VALIDAÇÃO MÍNIMA
    # ------------------------------------------------------
    validation_result = validate_minimum_data(raw_data)

    if not validation_result["is_valid"]:
        print("\n[FlowRadar] ❌ Execução interrompida\n")
        print(f"Motivo: {validation_result['reason']}")
        return

    print("[FlowRadar] ✔ Dados mínimos validados")

    work_items = raw_data["work_items"]
    relationships = raw_data["relationships"]
    team_mapping = raw_data["team_mapping"]

    # ------------------------------------------------------
    # 3. TABELA DE RELAÇÕES ENTRE SQUADS
    # ------------------------------------------------------
    squad_relationships = build_squad_relationships_table(
        work_items=work_items,
        relationships=relationships,
    )

    print("[FlowRadar] ✔ Relações entre squads preparadas")

    # ------------------------------------------------------
    # 4. CONSTRUÇÃO DO GRAFO
    # ------------------------------------------------------
    dependency_graph = build_dependency_graph(
        squad_relationships_table=squad_relationships
    )

    print("[FlowRadar] ✔ Grafo organizacional construído")

    # ------------------------------------------------------
    # 5. MÉTRICAS ESTRUTURAIS
    # ------------------------------------------------------
    structural_metrics = calculate_and_export_structural_metrics(
        dependency_graph=dependency_graph,
        output_file=output_path / "structural_metrics.csv",
    )

    print("[FlowRadar] ✔ Métricas estruturais calculadas")

    # ------------------------------------------------------
    # 6. MATRIZ E HEATMAP DE DEPENDÊNCIAS
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
    # 7. RESUMO EXECUTIVO
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
    # 8. SIMULAÇÃO OPCIONAL DE IMPACTO
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
    # 9. SAÍDA FINAL
    # ------------------------------------------------------
    print("\n[FlowRadar] 🚀 Processamento concluído com sucesso")
    print(f"[FlowRadar] Outputs gerados em: {output_path.resolve()}\n")


if __name__ == "_main_":
    parser = argparse.ArgumentParser(
        description="FlowRadar - análise sistêmica de fluxo e dependências"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Diretório com os arquivos de entrada CSV",
    )
    parser.add_argument(
        "--simulate-squad",
        required=False,
        help="Nome da squad a remover na simulação de impacto",
    )

    args = parser.parse_args()

    main(
        input_dir=args.input,
        simulate_squad=args.simulate_squad,
    )