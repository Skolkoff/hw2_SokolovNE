"""Основные операции с таблицами и данными."""

import re

from primitive_db.constants import ID_COLUMN, ID_TYPE, VALID_TYPES


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


def drop_table(metadata: dict, table_name: str) -> dict:
    """Удаляет схему таблицы из метаданных."""
    if table_name not in metadata:
        raise KeyError(f'Таблица "{table_name}" не существует.')
    del metadata[table_name]
    return metadata


def list_tables(metadata: dict) -> list[str]:
    """Возвращает отсортированный список таблиц."""
    return sorted(metadata)
