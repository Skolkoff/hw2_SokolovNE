"""Функции для чтения и сохранения файлов базы данных."""

import json
from pathlib import Path

from primitive_db.constants import DATA_DIR, META_FILE, TABLE_FILE_SUFFIX


def load_metadata(filepath: str = META_FILE) -> dict:
    """Загружает метаданные или возвращает пустой словарь."""
    try:
        with Path(filepath).open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with Path(filepath).open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def get_table_path(table_name: str) -> Path:
    """Возвращает путь к файлу таблицы."""
    return Path(DATA_DIR) / f"{table_name}{TABLE_FILE_SUFFIX}"


def load_table_data(table_name: str) -> list:
    """Загружает строки таблицы или возвращает пустой список."""
    try:
        with get_table_path(table_name).open(encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list) -> None:
    """Сохраняет строки таблицы в отдельный JSON-файл."""
    table_path = get_table_path(table_name)
    table_path.parent.mkdir(parents=True, exist_ok=True)
    with table_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def delete_table_data(table_name: str) -> None:
    """Удаляет файл данных таблицы, если он существует."""
    get_table_path(table_name).unlink(missing_ok=True)
