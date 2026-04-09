from __future__ import annotations

import pandas as pd

from src.pipeline.input_contract_validation import validate_input_contract


# ==========================================================
# TESTES DO CONTRATO CANÔNICO DE ENTRADA
# ==========================================================
#
# Objetivo:
# Garantir que o FlowRadar valide corretamente o formato
# mínimo esperado de entrada antes de processar os dados.
#
# O foco aqui é validar:
# - estrutura
# - integridade referencial
# - warnings úteis
# ==========================================================


def build_valid_work_items() -> pd.DataFrame:
    """
    Cria um conjunto mínimo e válido de work_items.
    """
    return pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": "F2", "team": "Squad B"},
            {"item_id": "F3", "team": "Squad C"},
        ]
    )


def build_valid_relationships() -> pd.DataFrame:
    """
    Cria um conjunto mínimo e válido de relationships.
    """
    return pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
            {"source_item": "F3", "target_item": "F2"},
        ]
    )


def build_valid_team_mapping() -> pd.DataFrame:
    """
    Cria um conjunto mínimo e válido de team_mapping.
    """
    return pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad B", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad C", "cluster": "Cluster 2", "tribe": "Tribo X"},
        ]
    )


def test_validate_input_contract_should_accept_valid_input() -> None:
    """
    Deve aceitar o contrato quando os três arquivos estiverem válidos.
    """
    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is True
    assert result.errors == []


def test_validate_input_contract_should_reject_empty_work_items() -> None:
    """
    Deve rejeitar quando work_items estiver vazio.
    """
    result = validate_input_contract(
        work_items=pd.DataFrame(),
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any("work_items.csv está ausente ou vazio" in error for error in result.errors)


def test_validate_input_contract_should_reject_missing_required_columns() -> None:
    """
    Deve rejeitar quando faltar coluna obrigatória em work_items.
    """
    invalid_work_items = pd.DataFrame(
        [
            {"id_errado": "F1", "team_errado": "Squad A"},
        ]
    )

    result = validate_input_contract(
        work_items=invalid_work_items,
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any(
        "work_items.csv não contém as colunas obrigatórias" in error
        for error in result.errors
    )


def test_validate_input_contract_should_reject_null_values_in_required_columns() -> None:
    """
    Deve rejeitar quando houver nulos nas colunas obrigatórias.
    """
    invalid_work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": None, "team": "Squad B"},
        ]
    )

    result = validate_input_contract(
        work_items=invalid_work_items,
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any(
        "work_items.csv possui" in error and "valores nulos" in error
        for error in result.errors
    )


def test_validate_input_contract_should_reject_duplicated_item_id() -> None:
    """
    Deve rejeitar quando item_id estiver duplicado em work_items.
    """
    invalid_work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": "F1", "team": "Squad B"},
        ]
    )

    result = validate_input_contract(
        work_items=invalid_work_items,
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any(
        "item_id duplicado" in error
        for error in result.errors
    )


def test_validate_input_contract_should_reject_duplicated_team_in_mapping() -> None:
    """
    Deve rejeitar quando o mesmo team aparecer duas vezes em team_mapping.
    """
    invalid_team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad A", "cluster": "Cluster 2", "tribe": "Tribo X"},
        ]
    )

    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=build_valid_relationships(),
        team_mapping=invalid_team_mapping,
    )

    assert result.is_valid is False
    assert any(
        "team duplicado" in error
        for error in result.errors
    )


def test_validate_input_contract_should_reject_relationships_with_unknown_items() -> None:
    """
    Deve rejeitar quando relationships referenciar item inexistente.
    """
    invalid_relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "ITEM_INEXISTENTE"},
        ]
    )

    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=invalid_relationships,
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any(
        "referencia item(s) inexistente(s) em work_items.csv" in error
        for error in result.errors
    )


def test_validate_input_contract_should_reject_work_items_with_unknown_team() -> None:
    """
    Deve rejeitar quando work_items contiver team inexistente em team_mapping.
    """
    invalid_work_items = pd.DataFrame(
        [
            {"item_id": "F1", "team": "Squad A"},
            {"item_id": "F2", "team": "Squad Inexistente"},
        ]
    )

    result = validate_input_contract(
        work_items=invalid_work_items,
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is False
    assert any(
        "work_items.csv contém team(s) não mapeado(s)" in error
        for error in result.errors
    )


def test_validate_input_contract_should_raise_warning_for_duplicated_relationships() -> None:
    """
    Deve aceitar o contrato, mas emitir warning para relações duplicadas.
    """
    duplicated_relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F2"},
            {"source_item": "F1", "target_item": "F2"},
        ]
    )

    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=duplicated_relationships,
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is True
    assert any(
        "relação(ões) duplicada(s)" in warning
        for warning in result.warnings
    )


def test_validate_input_contract_should_raise_warning_for_self_relationship() -> None:
    """
    Deve aceitar o contrato, mas avisar quando houver auto-relação.
    """
    self_relationships = pd.DataFrame(
        [
            {"source_item": "F1", "target_item": "F1"},
        ]
    )

    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=self_relationships,
        team_mapping=build_valid_team_mapping(),
    )

    assert result.is_valid is True
    assert any(
        "auto-relação" in warning
        for warning in result.warnings
    )


def test_validate_input_contract_should_raise_warning_for_unused_team_mapping() -> None:
    """
    Deve aceitar o contrato, mas avisar quando houver team mapeado
    que ainda não aparece em work_items.
    """
    extended_team_mapping = pd.DataFrame(
        [
            {"team": "Squad A", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad B", "cluster": "Cluster 1", "tribe": "Tribo X"},
            {"team": "Squad C", "cluster": "Cluster 2", "tribe": "Tribo X"},
            {"team": "Squad D", "cluster": "Cluster 2", "tribe": "Tribo X"},
        ]
    )

    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=build_valid_relationships(),
        team_mapping=extended_team_mapping,
    )

    assert result.is_valid is True
    assert any(
        "ainda não aparecem em work_items.csv" in warning
        for warning in result.warnings
    )


def test_build_human_readable_message_should_return_success_text_for_valid_case() -> None:
    """
    Deve retornar mensagem de sucesso quando a validação for válida.
    """
    result = validate_input_contract(
        work_items=build_valid_work_items(),
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    message = result.build_human_readable_message()

    assert "Validação concluída com sucesso" in message


def test_build_human_readable_message_should_list_errors_for_invalid_case() -> None:
    """
    Deve retornar mensagem detalhada contendo os erros encontrados.
    """
    invalid_work_items = pd.DataFrame()

    result = validate_input_contract(
        work_items=invalid_work_items,
        relationships=build_valid_relationships(),
        team_mapping=build_valid_team_mapping(),
    )

    message = result.build_human_readable_message()

    assert "Validação interrompida" in message
    assert "Erros encontrados" in message
    assert "work_items.csv está ausente ou vazio" in message