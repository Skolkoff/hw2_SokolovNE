"""Константы приложения."""

META_FILE = "db_meta.json"
DATA_DIR = "data"
TABLE_FILE_SUFFIX = ".json"
ID_COLUMN = "ID"
ID_TYPE = "int"
VALID_TYPES = {"int": int, "str": str, "bool": bool}
COMMANDS = {
    "create_table",
    "drop_table",
    "list_tables",
    "insert",
    "select",
    "update",
    "delete",
    "info",
    "help",
    "exit",
}
INPUT_PROMPT = "Введите команду: "
CONFIRM_PROMPT = 'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
TIME_MESSAGE = "Функция {name} выполнилась за {seconds:.3f} секунд."
TRUE_VALUES = {"true"}
FALSE_VALUES = {"false"}
