from __future__ import annotations

import pandas as pd


# ==========================================================
# VALIDAÇÃO DE DADOS MÍNIMOS
# ==========================================================
#
# Este módulo valida apenas o mínimo necessário para que o
# FlowRadar rode de forma previsível e profissional.
#
# A ideia não é "quebrar", mas explicar claramente o que falta.
# ==========================================================


def _is_missing_or_empty(dataframe: pd.DataFrame | None) -> bool:
    """
    Retorna True se o dataframe não existir ou estiver vazio.
    """
    return dataframe is None or dataframe.empty


def validate_minimum_data(data: dict) -> dict[str, str | bool]:
    """
    Valida se os dados mínimos necessários estão presentes.

    Esperado:
    - work_items
    - relationships
    - team_mapping

    Returns
    -------
    dict
        Exemplo:
        {
            "is_valid": False,
            "reason": "Nenhum work item encontrado"
        }
    """
    work_items = data.get("work_items")
    relationships = data.get("relationships")
    team_mapping = data.get("team_mapping")

    if _is_missing_or_empty(work_items):
        return {
            "is_valid": False,
            "reason": (
                "Nenhum work item encontrado. "
                "Requisito mínimo: arquivo example_work_items.csv com pelo menos 1 linha."
            ),
        }

    if _is_missing_or_empty(relationships):
        return {
            "is_valid": False,
            "reason": (
                "Nenhuma relação encontrada. "
                "Requisito mínimo: arquivo example_relationships.csv com pelo menos 1 linha."
            ),
        }

    if _is_missing_or_empty(team_mapping):
        return {
            "is_valid": False,
            "reason": (
                "Nenhum mapeamento de time encontrado. "
                "Requisito mínimo: arquivo example_team_mapping.csv com pelo menos 1 linha."
            ),
        }

    required_work_items_columns = {"item_id", "team"}
    missing_work_items_columns = required_work_items_columns - set(work_items.columns)
    if missing_work_items_columns:
        return {
            "is_valid": False,
            "reason": (
                "O arquivo example_work_items.csv não contém as colunas mínimas esperadas: "
                f"{sorted(required_work_items_columns)}. "
                f"Faltando: {sorted(missing_work_items_columns)}"
            ),
        }

    required_relationships_columns = {"source_item", "target_item"}
    missing_relationships_columns = required_relationships_columns - set(
        relationships.columns
    )
    if missing_relationships_columns:
        return {
            "is_valid": False,
            "reason": (
                "O arquivo example_relationships.csv não contém as colunas mínimas esperadas: "
                f"{sorted(required_relationships_columns)}. "
                f"Faltando: {sorted(missing_relationships_columns)}"
            ),
        }

    required_team_mapping_columns = {"team", "cluster", "tribe"}
    missing_team_mapping_columns = required_team_mapping_columns - set(
        team_mapping.columns
    )
    if missing_team_mapping_columns:
        return {
            "is_valid": False,
            "reason": (
                "O arquivo example_team_mapping.csv não contém as colunas mínimas esperadas: "
                f"{sorted(required_team_mapping_columns)}. "
                f"Faltando: {sorted(missing_team_mapping_columns)}"
            ),
        }

    return {
        "is_valid": True,
        "reason": "",
    }