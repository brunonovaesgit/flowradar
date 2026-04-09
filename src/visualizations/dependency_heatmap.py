from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ==========================================================
# VISUALIZAÇÃO: DEPENDENCY HEATMAP
# ==========================================================
#
# Este módulo gera:
# 1. a matriz de dependências entre squads
# 2. o heatmap salvo em arquivo
# ==========================================================


def build_dependency_matrix(
    squad_relationships_table: pd.DataFrame,
) -> pd.DataFrame:
    """
    Constrói uma matriz de dependências entre squads.

    Linhas:
    - source_squad

    Colunas:
    - target_squad

    Valores:
    - volume de dependências
    """
    dependency_matrix = pd.crosstab(
        squad_relationships_table["source_squad"],
        squad_relationships_table["target_squad"],
    )

    return dependency_matrix


def generate_dependency_heatmap(
    dependency_matrix: pd.DataFrame,
    output_file: str | Path,
    title: str = "Dependency Heatmap",
) -> Path:
    """
    Gera um heatmap a partir de uma matriz de dependências.
    """
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 7))
    plt.imshow(dependency_matrix)

    plt.xticks(
        range(len(dependency_matrix.columns)),
        dependency_matrix.columns,
        rotation=45,
        ha="right",
    )
    plt.yticks(
        range(len(dependency_matrix.index)),
        dependency_matrix.index,
    )

    plt.colorbar(label="Dependency Volume")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    return output_path