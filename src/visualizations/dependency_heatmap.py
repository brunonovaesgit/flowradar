from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from src.visualizations.visual_style import (
    LAYOUT,
    PALETTE,
    TYPOGRAPHY,
    build_standard_subtitle,
    build_standard_title,
)


# ==========================================================
# VISUALIZAÇÃO: DEPENDENCY HEATMAP
# ==========================================================


def build_dependency_matrix(
    squad_relationships_table: pd.DataFrame,
) -> pd.DataFrame:
    dependency_matrix = pd.crosstab(
        squad_relationships_table["source_squad"],
        squad_relationships_table["target_squad"],
    )

    return dependency_matrix


def generate_dependency_heatmap(
    dependency_matrix: pd.DataFrame,
    output_file: str | Path,
) -> Path:
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(LAYOUT.figure_width, LAYOUT.figure_height))

    # 🔥 heatmap com identidade visual (gradiente azul)
    plt.imshow(dependency_matrix, cmap="Blues")

    plt.xticks(
        range(len(dependency_matrix.columns)),
        dependency_matrix.columns,
        rotation=45,
        ha="right",
        fontsize=TYPOGRAPHY.label_size,
    )

    plt.yticks(
        range(len(dependency_matrix.index)),
        dependency_matrix.index,
        fontsize=TYPOGRAPHY.label_size,
    )

    cbar = plt.colorbar()
    cbar.set_label("Dependency volume", fontsize=TYPOGRAPHY.legend_size)

    # 🔥 título padrão
    plt.title(
        build_standard_title("Dependency Heatmap"),
        fontsize=TYPOGRAPHY.title_size,
        fontweight=TYPOGRAPHY.title_weight,
    )

    # 🔥 subtítulo explicativo (ESSENCIAL)
    plt.figtext(
        0.5,
        0.92,
        build_standard_subtitle(
            "Rows represent dependent squads; columns represent providers"
        ),
        ha="center",
        fontsize=TYPOGRAPHY.subtitle_size,
        color=PALETTE.mid_gray,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=LAYOUT.dpi, bbox_inches="tight")
    plt.close()

    return output_path