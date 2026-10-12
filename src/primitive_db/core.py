"""Основные операции с таблицами и данными."""

import json
import re

from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES
from primitive_db.decorators import (
    confirm_action,
    create_cacher,
    handle_db_errors,
    log_time,
)
from primitive_db.utils import load_table_data

_select_cache = create_cacher()


@handle_db_errors
def create_table(metadata: dict, table_name: str, columns: list[str]) -> dict:
    """Создаёт таблицу и добавляет её схему в метаданные."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", table_name):
        raise ValueError(f"Некорректное имя таблицы: {table_name}.")
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')
    if not columns:
        raise ValueError("Нужно указать хотя бы один столбец.")

    schema = {ID_COLUMN: ID_TYPE}
    for column in columns:
        parts = column.split(":", maxsplit=1)
        if len(parts) != 2:
            raise ValueError(f"Некорректное описание столбца: {column}.")
        column_name, column_type = parts
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", column_name):
            raise ValueError(f"Некорректное имя столбца: {column_name}.")
        if column_name == ID_COLUMN or column_name in schema:
            raise ValueError(f"Столбец {column_name} уже существует.")
        if column_type not in VALID_TYPES:
            raise ValueError(f"Некорректный тип данных: {column_type}.")
        schema[column_name] = column_type

    metadata[table_name] = schema
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет схему таблицы из метаданных."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    return metadata


def list_tables(metadata: dict) -> list[str]:
    """Возвращает отсортированный список таблиц."""
    return sorted(metadata)


@handle_db_errors
@log_time
def insert(
    metadata: dict,
    table_name: str,
    values: list,
    table_data: list | None = None,
) -> list:
    """Добавляет запись с автоматически сгенерированным ID."""
    if table_name not in metadata:
        raise KeyError(table_name)
    schema = metadata[table_name]
    columns = [name for name in schema if name != ID_COLUMN]
    if len(values) != len(columns):
        raise ValueError(f"Ожидалось значений: {len(columns)}.")
    for column_name, value in zip(columns, values, strict=True):
        expected_type = VALID_TYPES[schema[column_name]]
        if type(value) is not expected_type:
            raise ValueError(
                f"Для столбца {column_name} требуется тип {schema[column_name]}."
            )

    if table_data is None:
        table_data = load_table_data(table_name)
    next_id = max((row[ID_COLUMN] for row in table_data), default=0) + 1
    row = {ID_COLUMN: next_id}
    row.update(zip(columns, values, strict=True))
    table_data.append(row)
    return table_data


@handle_db_errors
@log_time
def select(
    table_data: list,
    where_clause: dict | None = None,
    order_by: str | None = None,
    descending: bool = False,
) -> list:
    """Возвращает записи с фильтрацией и необязательной сортировкой."""
    cache_key = json.dumps(
        [table_data, where_clause, order_by, descending],
        ensure_ascii=False,
        sort_keys=True,
    )

    def get_rows():
        rows = [
            row
            for row in table_data
            if where_clause is None
            or all(row.get(key) == value for key, value in where_clause.items())
        ]
        if order_by is not None:
            rows.sort(key=lambda row: row[order_by], reverse=descending)
        return rows

    return _select_cache(
        cache_key,
        get_rows,
    )


@handle_db_errors
def update(table_data: list, set_clause: dict, where_clause: dict) -> list:
    """Обновляет все записи, подходящие под условие."""
    if not set_clause or not where_clause:
        raise ValueError("Для update нужны условия set и where.")
    for row in table_data:
        if all(row.get(key) == value for key, value in where_clause.items()):
            row.update(set_clause)
    return table_data


@handle_db_errors
@confirm_action("удаление записи")
def delete(table_data: list, where_clause: dict) -> list:
    """Удаляет записи, подходящие под условие."""
    if not where_clause:
        raise ValueError("Для delete нужно условие where.")
    return [
        row
        for row in table_data
        if not all(row.get(key) == value for key, value in where_clause.items())
    ]
