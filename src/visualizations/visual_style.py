from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FlowRadarPalette:
    blue: str = "#4C78A8"
    orange: str = "#F28E2B"
    red: str = "#D62728"
    dark_gray: str = "#2F2F2F"
    mid_gray: str = "#666666"
    light_gray: str = "#B0B0B0"
    white: str = "#FFFFFF"


@dataclass(frozen=True)
class FlowRadarTypography:
    title_size: int = 14
    subtitle_size: int = 10
    label_size: int = 10
    legend_size: int = 10
    title_weight: str = "bold"
    label_weight: str = "bold"


@dataclass(frozen=True)
class FlowRadarLayout:
    figure_width: int = 14
    figure_height: int = 10
    dpi: int = 150
    edge_alpha: float = 0.50
    node_alpha: float = 0.95
    edge_linewidth_base: float = 1.2
    edge_linewidth_scale: float = 5.0
    node_border_width: float = 1.5
    arrow_size: int = 20
    connection_style: str = "arc3,rad=0.08"


PALETTE = FlowRadarPalette()
TYPOGRAPHY = FlowRadarTypography()
LAYOUT = FlowRadarLayout()


def build_standard_title(main_title: str, subtitle_context: str | None = None) -> str:
    if subtitle_context:
        return f"FlowRadar — {main_title}\n{subtitle_context}"
    return f"FlowRadar — {main_title}"


def build_standard_subtitle(text: str) -> str:
    return text