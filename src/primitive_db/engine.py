"""Цикл взаимодействия с пользователем."""

from prompt import string

from primitive_db.constants import COMMANDS, INPUT_PROMPT, META_FILE
from primitive_db.core import create_table, drop_table, list_tables
from primitive_db.parser import parse_command
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    save_metadata,
)


def print_help() -> None:
    """Показывает команды текущего этапа."""
    print("***База данных***")
    print("create_table <имя> <столбец:тип> ... — создать таблицу")
    print("drop_table <имя> — удалить таблицу")
    print("list_tables — показать таблицы")
    print("help — справка")
    print("exit — выход")


def run() -> None:
    """Запускает цикл обработки команд."""
    print_help()
    while True:
        user_input = string(INPUT_PROMPT)
        try:
            command_parts = parse_command(user_input)
            if not command_parts:
                continue
            command, *arguments = command_parts
            if command not in COMMANDS:
                print(f"Функции {command} нет. Попробуйте снова.")
                continue

            metadata = load_metadata()
            if command == "create_table":
                if len(arguments) < 2:
                    raise ValueError("Укажите имя таблицы и столбцы.")
                table_name, *columns = arguments
                create_table(metadata, table_name, columns)
                save_metadata(META_FILE, metadata)
                column_list = ", ".join(
                    f"{name}:{kind}" for name, kind in metadata[table_name].items()
                )
                print(
                    f'Таблица "{table_name}" успешно создана со столбцами: '
                    f"{column_list}"
                )
            elif command == "drop_table":
                if len(arguments) != 1:
                    raise ValueError("Укажите имя одной таблицы.")
                table_name = arguments[0]
                drop_table(metadata, table_name)
                save_metadata(META_FILE, metadata)
                delete_table_data(table_name)
                print(f'Таблица "{table_name}" успешно удалена.')
            elif command == "list_tables":
                if arguments:
                    raise ValueError("Команда list_tables не принимает аргументы.")
                tables = list_tables(metadata)
                print("\n".join(f"- {table}" for table in tables) or "Таблиц нет.")
            elif command == "help":
                print_help()
            elif command == "exit":
                break
        except (KeyError, ValueError) as error:
            print(f"Ошибка: {error}")
