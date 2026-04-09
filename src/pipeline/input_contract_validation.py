from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import pandas as pd


# ==========================================================
# FLOWRADAR - INPUT CONTRACT VALIDATION
# ==========================================================
#
# Objetivo
# --------
# Validar o contrato canônico de entrada do FlowRadar:
# - work_items.csv
# - relationships.csv
# - team_mapping.csv
#
# Este módulo não carrega arquivos do disco.
# Ele recebe os DataFrames já carregados e valida:
#
# 1. Estrutura mínima
# 2. Colunas obrigatórias
# 3. Valores nulos
# 4. Duplicidades indevidas
# 5. Integridade referencial
#
# Filosofia
# ---------
# O objetivo não é apenas "dar erro".
# O objetivo é explicar de forma profissional e objetiva
# por que o processamento não pode continuar.
# ==========================================================


# ----------------------------------------------------------
# MODELO DE RESULTADO DA VALIDAÇÃO
# ----------------------------------------------------------

@dataclass
class ValidationResult:
    """
    Representa o resultado da validação do contrato de entrada.
    """
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def build_human_readable_message(self) -> str:
        """
        Monta uma mensagem amigável para terminal, log ou relatório.
        """
        if self.is_valid:
            message_lines = ["Validação concluída com sucesso."]
            if self.warnings:
                message_lines.append("")
                message_lines.append("Avisos:")
                for warning in self.warnings:
                    message_lines.append(f"- {warning}")
            return "\n".join(message_lines)

        message_lines = [
            "Validação interrompida: o contrato mínimo de entrada não foi atendido.",
            "",
            "Erros encontrados:",
        ]

        for error in self.errors:
            message_lines.append(f"- {error}")

        if self.warnings:
            message_lines.append("")
            message_lines.append("Avisos:")
            for warning in self.warnings:
                message_lines.append(f"- {warning}")

        return "\n".join(message_lines)


# ----------------------------------------------------------
# FUNÇÕES AUXILIARES
# ----------------------------------------------------------

def _is_missing_or_empty(dataframe: pd.DataFrame | None) -> bool:
    """
    Retorna True se o DataFrame estiver ausente ou vazio.
    """
    return dataframe is None or dataframe.empty


def _find_missing_columns(
    dataframe: pd.DataFrame,
    required_columns: set[str],
) -> list[str]:
    """
    Retorna as colunas obrigatórias que não estão presentes.
    """
    return sorted(required_columns - set(dataframe.columns))


def _count_null_rows(
    dataframe: pd.DataFrame,
    required_columns: list[str],
) -> int:
    """
    Conta quantas linhas possuem ao menos um valor nulo
    nas colunas obrigatórias informadas.
    """
    return int(dataframe[required_columns].isnull().any(axis=1).sum())


# ----------------------------------------------------------
# VALIDAÇÃO PRINCIPAL
# ----------------------------------------------------------

def validate_input_contract(
    work_items: pd.DataFrame,
    relationships: pd.DataFrame,
    team_mapping: pd.DataFrame,
) -> ValidationResult:
    """
    Valida o contrato canônico de entrada do FlowRadar.

    Parâmetros
    ----------
    work_items : pd.DataFrame
        Esperado:
        - item_id
        - team

    relationships : pd.DataFrame
        Esperado:
        - source_item
        - target_item

    team_mapping : pd.DataFrame
        Esperado:
        - team
        - cluster
        - tribe

    Retorno
    -------
    ValidationResult
        Resultado detalhado da validação.
    """
    errors: list[str] = []
    warnings: list[str] = []

    # ------------------------------------------------------
    # 1. EXISTÊNCIA / NÃO-VAZIO
    # ------------------------------------------------------
    if _is_missing_or_empty(work_items):
        errors.append(
            "work_items.csv está ausente ou vazio. "
            "Requisito mínimo: ao menos 1 linha com item_id e team."
        )

    if _is_missing_or_empty(relationships):
        errors.append(
            "relationships.csv está ausente ou vazio. "
            "Requisito mínimo: ao menos 1 linha com source_item e target_item."
        )

    if _is_missing_or_empty(team_mapping):
        errors.append(
            "team_mapping.csv está ausente ou vazio. "
            "Requisito mínimo: ao menos 1 linha com team, cluster e tribe."
        )

    # Se algum estiver vazio, não vale continuar validando estrutura.
    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # ------------------------------------------------------
    # 2. COLUNAS OBRIGATÓRIAS
    # ------------------------------------------------------
    required_work_items_columns = {"item_id", "team"}
    required_relationships_columns = {"source_item", "target_item"}
    required_team_mapping_columns = {"team", "cluster", "tribe"}

    missing_work_items_columns = _find_missing_columns(
        work_items,
        required_work_items_columns,
    )
    if missing_work_items_columns:
        errors.append(
            "work_items.csv não contém as colunas obrigatórias: "
            f"{missing_work_items_columns}"
        )

    missing_relationships_columns = _find_missing_columns(
        relationships,
        required_relationships_columns,
    )
    if missing_relationships_columns:
        errors.append(
            "relationships.csv não contém as colunas obrigatórias: "
            f"{missing_relationships_columns}"
        )

    missing_team_mapping_columns = _find_missing_columns(
        team_mapping,
        required_team_mapping_columns,
    )
    if missing_team_mapping_columns:
        errors.append(
            "team_mapping.csv não contém as colunas obrigatórias: "
            f"{missing_team_mapping_columns}"
        )

    if errors:
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

    # ------------------------------------------------------
    # 3. VALORES NULOS
    # ------------------------------------------------------
    work_items_null_count = _count_null_rows(work_items, ["item_id", "team"])
    if work_items_null_count > 0:
        errors.append(
            f"work_items.csv possui {work_items_null_count} linha(s) com valores nulos "
            "nas colunas obrigatórias item_id/team."
        )

    relationships_null_count = _count_null_rows(
        relationships,
        ["source_item", "target_item"],
    )
    if relationships_null_count > 0:
        errors.append(
            f"relationships.csv possui {relationships_null_count} linha(s) com valores nulos "
            "nas colunas obrigatórias source_item/target_item."
        )

    team_mapping_null_count = _count_null_rows(
        team_mapping,
        ["team", "cluster", "tribe"],
    )
    if team_mapping_null_count > 0:
        errors.append(
            f"team_mapping.csv possui {team_mapping_null_count} linha(s) com valores nulos "
            "nas colunas obrigatórias team/cluster/tribe."
        )

    # ------------------------------------------------------
    # 4. UNICIDADE
    # ------------------------------------------------------
    duplicated_item_ids = work_items["item_id"].duplicated().sum()
    if duplicated_item_ids > 0:
        errors.append(
            f"work_items.csv possui {duplicated_item_ids} item_id duplicado(s). "
            "A coluna item_id deve ser única."
        )

    duplicated_teams = team_mapping["team"].duplicated().sum()
    if duplicated_teams > 0:
        errors.append(
            f"team_mapping.csv possui {duplicated_teams} team duplicado(s). "
            "Cada team deve aparecer apenas uma vez."
        )

    duplicated_relationships = relationships.duplicated(
        subset=["source_item", "target_item"]
    ).sum()
    if duplicated_relationships > 0:
        warnings.append(
            f"relationships.csv possui {duplicated_relationships} relação(ões) duplicada(s) "
            "entre source_item e target_item."
        )

    # ------------------------------------------------------
    # 5. INTEGRIDADE REFERENCIAL
    # ------------------------------------------------------
    known_item_ids = set(work_items["item_id"].astype(str))
    known_teams = set(team_mapping["team"].astype(str))

    source_items = set(relationships["source_item"].astype(str))
    target_items = set(relationships["target_item"].astype(str))
    all_referenced_items = source_items.union(target_items)

    missing_items_in_work_items = sorted(all_referenced_items - known_item_ids)
    if missing_items_in_work_items:
        errors.append(
            "relationships.csv referencia item(s) inexistente(s) em work_items.csv: "
            f"{missing_items_in_work_items}"
        )

    teams_used_in_work_items = set(work_items["team"].astype(str))
    missing_teams_in_team_mapping = sorted(teams_used_in_work_items - known_teams)
    if missing_teams_in_team_mapping:
        errors.append(
            "work_items.csv contém team(s) não mapeado(s) em team_mapping.csv: "
            f"{missing_teams_in_team_mapping}"
        )

    # ------------------------------------------------------
    # 6. REGRAS DE CONSISTÊNCIA ADICIONAIS
    # ------------------------------------------------------
    self_relationship_count = (
        relationships["source_item"].astype(str)
        == relationships["target_item"].astype(str)
    ).sum()

    if self_relationship_count > 0:
        warnings.append(
            f"relationships.csv possui {self_relationship_count} auto-relação(ões) "
            "(source_item == target_item)."
        )

    teams_without_items = sorted(known_teams - teams_used_in_work_items)
    if teams_without_items:
        warnings.append(
            "team_mapping.csv contém team(s) que ainda não aparecem em work_items.csv: "
            f"{teams_without_items}"
        )

    # ------------------------------------------------------
    # 7. RESULTADO FINAL
    # ------------------------------------------------------
    return ValidationResult(
        is_valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
    )