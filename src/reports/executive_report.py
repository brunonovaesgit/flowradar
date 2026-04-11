from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


def _read_json(file_path: Path) -> dict:
    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _read_csv(file_path: Path) -> pd.DataFrame:
    if not file_path.exists():
        return pd.DataFrame()

    return pd.read_csv(file_path, encoding="utf-8-sig")


def _build_table_html(df: pd.DataFrame, max_rows: int = 10) -> str:
    if df.empty:
        return "<p class='empty'>No data available.</p>"

    safe_df = df.head(max_rows).copy()
    return safe_df.to_html(
        index=False,
        classes="flowradar-table",
        border=0,
        justify="left",
    )


def _image_block(title: str, image_name: str, subtitle: str = "") -> str:
    return f"""
    <section class="card">
        <h2>{title}</h2>
        <p class="section-subtitle">{subtitle}</p>
        <img src="{image_name}" alt="{title}" class="chart-image" />
    </section>
    """


def generate_executive_report(output_dir: str | Path) -> Path:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    summary = _read_json(output_path / "summary.json")
    structural_metrics = _read_csv(output_path / "structural_metrics.csv")
    risk_analysis = _read_csv(output_path / "risk_analysis.csv")

    top_structural = (
        structural_metrics.sort_values(
            by="structural_criticality_score",
            ascending=False,
        ).head(5)
        if not structural_metrics.empty
        else pd.DataFrame()
    )

    top_risks = (
        risk_analysis.sort_values(
            by="risk_score",
            ascending=False,
        ).head(5)
        if not risk_analysis.empty
        else pd.DataFrame()
    )

    total_squads = summary.get("total_squads", "-")
    total_dependencies = summary.get("total_dependencies", "-")
    top_bottleneck = summary.get("top_bottleneck", "-")
    top_bottleneck_score = summary.get("top_bottleneck_score", "-")

    impact_graph_exists = (output_path / "dependency_graph_impact.png").exists()

    impact_block = ""
    if impact_graph_exists:
        impact_block = _image_block(
            title="Impact Simulation",
            image_name="dependency_graph_impact.png",
            subtitle="Simulation of structural impact after removing a selected squad.",
        )

    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>FlowRadar Executive Report</title>
    <style>
        :root {{
            --blue: #4C78A8;
            --orange: #F28E2B;
            --red: #D62728;
            --dark-gray: #2F2F2F;
            --mid-gray: #666666;
            --light-gray: #EAEAEA;
            --white: #FFFFFF;
            --bg: #F7F8FA;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            background: var(--bg);
            color: var(--dark-gray);
        }}

        .container {{
            width: min(1200px, 92%);
            margin: 32px auto 48px;
        }}

        .hero {{
            background: var(--white);
            border-radius: 18px;
            padding: 28px 32px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
            margin-bottom: 24px;
        }}

        .hero h1 {{
            margin: 0 0 8px;
            font-size: 32px;
        }}

        .hero p {{
            margin: 0;
            color: var(--mid-gray);
            font-size: 16px;
        }}

        .kpis {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 16px;
            margin-top: 24px;
        }}

        .kpi {{
            background: var(--white);
            border-radius: 16px;
            padding: 20px;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.05);
        }}

        .kpi-label {{
            font-size: 13px;
            color: var(--mid-gray);
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-size: 28px;
            font-weight: bold;
        }}

        .grid-2 {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 20px;
            margin-top: 24px;
        }}

        .card {{
            background: var(--white);
            border-radius: 18px;
            padding: 22px 24px;
            box-shadow: 0 6px 18px rgba(0, 0, 0, 0.06);
            overflow: hidden;
        }}

        .card h2 {{
            margin: 0 0 8px;
            font-size: 22px;
        }}

        .section-subtitle {{
            margin: 0 0 16px;
            color: var(--mid-gray);
            font-size: 14px;
        }}

        .chart-image {{
            width: 100%;
            height: auto;
            border-radius: 12px;
            border: 1px solid var(--light-gray);
            background: var(--white);
        }}

        .flowradar-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        .flowradar-table th {{
            text-align: left;
            background: #F1F4F8;
            padding: 10px 12px;
        }}

        .flowradar-table td {{
            padding: 10px 12px;
            border-top: 1px solid #ECEFF3;
        }}

        .empty {{
            color: var(--mid-gray);
            font-style: italic;
        }}

        .footer {{
            margin-top: 24px;
            text-align: center;
            color: var(--mid-gray);
            font-size: 13px;
        }}

        @media (max-width: 900px) {{
            .grid-2 {{
                grid-template-columns: 1fr;
            }}

            .kpis {{
                grid-template-columns: repeat(2, minmax(0, 1fr));
            }}
        }}

        @media (max-width: 560px) {{
            .kpis {{
                grid-template-columns: 1fr;
            }}

            .hero h1 {{
                font-size: 26px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <section class="hero">
            <h1>FlowRadar — Executive Report</h1>
            <p>
                Systemic analysis of organizational dependencies, structural criticality, and operational risk.
            </p>

            <div class="kpis">
                <div class="kpi">
                    <div class="kpi-label">Total squads</div>
                    <div class="kpi-value">{total_squads}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-label">Total dependencies</div>
                    <div class="kpi-value">{total_dependencies}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-label">Top bottleneck</div>
                    <div class="kpi-value">{top_bottleneck}</div>
                </div>
                <div class="kpi">
                    <div class="kpi-label">Bottleneck score</div>
                    <div class="kpi-value">{top_bottleneck_score}</div>
                </div>
            </div>
        </section>

        <div class="grid-2">
            <section class="card">
                <h2>Top Structural Criticality</h2>
                <p class="section-subtitle">
                    Highest structural criticality scores in the dependency network.
                </p>
                {_build_table_html(top_structural)}
            </section>

            <section class="card">
                <h2>Top Organizational Risks</h2>
                <p class="section-subtitle">
                    Highest risk scores based on structural criticality and dependency concentration.
                </p>
                {_build_table_html(top_risks)}
            </section>
        </div>

        <div class="grid-2">
            {_image_block(
                title="Criticality Ranking",
                image_name="criticality_ranking.png",
                subtitle="Relative structural importance of squads in the dependency network.",
            )}

            {_image_block(
                title="Dependency Heatmap",
                image_name="dependency_heatmap.png",
                subtitle="Rows represent dependent squads; columns represent providers.",
            )}
        </div>

        <div class="grid-2">
            {_image_block(
                title="Executive Dependency Graph",
                image_name="dependency_graph.png",
                subtitle="Node size reflects structural criticality; edge width reflects dependency volume.",
            )}

            {impact_block}
        </div>

        <div class="footer">
            Generated automatically by FlowRadar
        </div>
    </div>
</body>
</html>
"""

    report_file = output_path / "flowradar_report.html"
    report_file.write_text(html, encoding="utf-8")

    return report_file