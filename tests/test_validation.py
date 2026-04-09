from __future__ import annotations

import pandas as pd

from src.pipeline.validation import validate_minimum_data


# ==========================================================
# TESTES DE VALIDAÇÃO DE DADOS
# ==========================================================
#
# Objetivo:
# Garantir que o FlowRadar:
# - aceite dados mínimos válidos
# - rejeite entradas insuficientes
# - explique claramente o motivo da rejeição
# ==========================================================


def test_validate_minimum_data_should_accept_valid_input() -> None:
    """
    Deve aceitar dados quando todos os arquivos mínimos existem
    e possuem as colunas obrigatórias.
    """
    work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": "F2", "team": "Squad B"},
        ]
    )

    relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
        ]
    )

    team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad B", "cluster": "Cluster 1", "tribe": "Tribo X"},
        ]
    )

    result = validate_minimum_data(
        {
            "work_items": work_items,
            "relationships": relationships,
            "team_mapping": team_mapping,
        }
    )

    assert result["is_valid"] is True
    assert result["reason"] == ""


def test_validate_minimum_data_should_reject_missing_work_items() -> None:
    """
    Deve rejeitar quando não houver work_items.
    """
    relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
        ]
    )

    team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
        ]
    )

    result = validate_minimum_data(
        {
            "work_items": pd.DataFrame(),
            "relationships": relationships,
            "team_mapping": team_mapping,
        }
    )

    assert result["is_valid"] is False
    assert "Nenhum work item encontrado" in result["reason"]


def test_validate_minimum_data_should_reject_missing_relationships() -> None:
    """
    Deve rejeitar quando não houver relações entre itens.
    """
    work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
        ]
    )

    team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
        ]
    )

    result = validate_minimum_data(
        {
            "work_items": work_items,
            "relationships": pd.DataFrame(),
            "team_mapping": team_mapping,
        }
    )

    assert result["is_valid"] is False
    assert "Nenhuma relação encontrada" in result["reason"]


def test_validate_minimum_data_should_reject_missing_team_mapping() -> None:
    """
    Deve rejeitar quando não houver mapeamento organizacional mínimo.
    """
    work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
        ]
    )

    relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F1"},
        ]
    )

    result = validate_minimum_data(
        {
            "work_items": work_items,
            "relationships": relationships,
            "team_mapping": pd.DataFrame(),
        }
    )

    assert result["is_valid"] is False
    assert "Nenhum mapeamento de time encontrado" in result["reason"]


def test_validate_minimum_data_should_reject_missing_required_columns() -> None:
    """
    Deve rejeitar quando work_items não possuir as colunas mínimas esperadas.
    """
    work_items = pd.DataFrame(
        [
            {"id_errado": "F1", "equipe": "Squad A"},
        ]
    )

    relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
        ]
    )

    team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
        ]
    )

    result = validate_minimum_data(
        {
            "work_items": work_items,
            "relationships": relationships,
            "team_mapping": team_mapping,
        }
    )

    assert result["is_valid"] is False
    assert "example_work_items.csv não contém as colunas mínimas esperadas" in result["reason"]