"""Константы приложения."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
TABLE_FILE_SUFFIX = ".json"
ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
COMMANDS = {"create_table", "drop_table", "list_tables", "help", "exit"}
INPUT_PROMPT = "Введите команду: "
