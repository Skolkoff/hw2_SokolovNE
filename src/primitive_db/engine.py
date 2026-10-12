"""Цикл взаимодействия с пользователем."""

from prettytable import PrettyTable
from prompt import string

from primitive_db.constants import COMMANDS, INPUT_PROMPT, META_FILE
from primitive_db.core import (
    create_table,
    delete,
    drop_table,
    insert,
    list_tables,
    select,
    update,
)
from primitive_db.parser import (
    parse_clause,
    parse_command,
    parse_delete_command,
    parse_insert_command,
    parse_select_command,
    parse_update_command,
)
from primitive_db.utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help() -> None:
    """Показывает список команд."""
    print("***База данных***")
    print("create_table <имя> <столбец:тип> ...")
    print("drop_table <имя>")
    print("list_tables")
    print("insert into <имя> values (<значение>, ...)")
    print("select from <имя> [where <столбец> = <значение>] [order by <столбец>]")
    print("update <имя> set <столбец> = <значение> where <столбец> = <значение>")
    print("delete from <имя> where <столбец> = <значение>")
    print("info <имя>")
    print("help")
    print("exit")
    print('Строковые значения указывайте в кавычках, например "Sergei".')


def _get_schema(metadata: dict, table_name: str) -> dict:
    """Возвращает схему таблицы или сообщает об ошибке."""
    if table_name not in metadata:
        raise KeyError(table_name)
    return metadata[table_name]


def _print_rows(rows: list, schema: dict) -> None:
    """Выводит записи в виде таблицы."""
    table = PrettyTable()
    table.field_names = list(schema)
    table.add_rows([[row.get(column) for column in schema] for row in rows])
    print(table)


def _handle_table_command(command: str, arguments: list[str]) -> None:
    """Обрабатывает команды создания и удаления таблиц."""
    metadata = load_metadata()
    if command == "create_table":
        if len(arguments) < 2:
            raise ValueError("Укажите имя таблицы и столбцы.")
        table_name, *columns = arguments
        updated_metadata = create_table(metadata, table_name, columns)
        if updated_metadata is None:
            return
        save_metadata(META_FILE, updated_metadata)
        column_list = ", ".join(
            f"{name}:{kind}" for name, kind in updated_metadata[table_name].items()
        )
        print(f'Таблица "{table_name}" успешно создана со столбцами: {column_list}')
    elif command == "drop_table":
        if len(arguments) != 1:
            raise ValueError("Укажите имя одной таблицы.")
        table_name = arguments[0]
        updated_metadata = drop_table(metadata, table_name)
        if updated_metadata is None:
            return
        save_metadata(META_FILE, updated_metadata)
        delete_table_data(table_name)
        print(f'Таблица "{table_name}" успешно удалена.')


def _handle_insert(user_input: str) -> None:
    """Добавляет строку в таблицу и сохраняет её."""
    table_name, values = parse_insert_command(user_input)
    metadata = load_metadata()
    _get_schema(metadata, table_name)
    table_data = load_table_data(table_name)
    updated_data = insert(metadata, table_name, values, table_data)
    if updated_data is None:
        return
    save_table_data(table_name, updated_data)
    record_id = updated_data[-1]["ID"]
    print(f'Запись с ID={record_id} успешно добавлена в таблицу "{table_name}".')


def _handle_select(user_input: str) -> None:
    """Выбирает строки и выводит их в табличном виде."""
    table_name, raw_where, order_by, descending = parse_select_command(user_input)
    metadata = load_metadata()
    schema = _get_schema(metadata, table_name)
    if order_by is not None and order_by not in schema:
        raise KeyError(order_by)
    where_clause = parse_clause(raw_where, schema) if raw_where else None
    table_data = load_table_data(table_name)
    rows = select(table_data, where_clause, order_by, descending)
    if rows is not None:
        _print_rows(rows, schema)


def _handle_update(user_input: str) -> None:
    """Обновляет подходящие строки и сохраняет результат."""
    table_name, raw_set, raw_where = parse_update_command(user_input)
    metadata = load_metadata()
    schema = _get_schema(metadata, table_name)
    set_clause = parse_clause(raw_set, schema)
    where_clause = parse_clause(raw_where, schema)
    if "ID" in set_clause:
        raise ValueError("Идентификатор ID изменять нельзя.")
    table_data = load_table_data(table_name)
    updated_ids = [
        row["ID"]
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]
    updated_data = update(table_data, set_clause, where_clause)
    if updated_data is None:
        return
    save_table_data(table_name, updated_data)
    if updated_ids:
        for record_id in updated_ids:
            print(
                f'Запись с ID={record_id} в таблице "{table_name}" успешно обновлена.'
            )
    else:
        print("Записи для обновления не найдены.")


def _handle_delete(user_input: str) -> None:
    """Удаляет подходящие строки после подтверждения."""
    table_name, raw_where = parse_delete_command(user_input)
    metadata = load_metadata()
    schema = _get_schema(metadata, table_name)
    where_clause = parse_clause(raw_where, schema)
    table_data = load_table_data(table_name)
    removed_ids = [
        row["ID"]
        for row in table_data
        if all(row.get(key) == value for key, value in where_clause.items())
    ]
    updated_data = delete(table_data, where_clause)
    if updated_data is None:
        return
    save_table_data(table_name, updated_data)
    if removed_ids:
        for record_id in removed_ids:
            print(f'Запись с ID={record_id} успешно удалена из таблицы "{table_name}".')
    else:
        print("Записи для удаления не найдены.")


def _handle_info(arguments: list[str]) -> None:
    """Печатает схему таблицы и количество записей."""
    if len(arguments) != 1:
        raise ValueError("Укажите имя одной таблицы.")
    table_name = arguments[0]
    metadata = load_metadata()
    schema = _get_schema(metadata, table_name)
    table_data = load_table_data(table_name)
    columns = ", ".join(f"{name}:{kind}" for name, kind in schema.items())
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {columns}")
    print(f"Количество записей: {len(table_data)}")


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
            if command == "exit":
                break
            if command == "help":
                print_help()
            elif command == "list_tables":
                if arguments:
                    raise ValueError("Команда list_tables не принимает аргументы.")
                tables = list_tables(load_metadata())
                table_list = "\n".join(f"- {table}" for table in tables)
                print(table_list or "Таблиц нет.")
            elif command in {"create_table", "drop_table"}:
                _handle_table_command(command, arguments)
            elif command == "insert":
                _handle_insert(user_input)
            elif command == "select":
                _handle_select(user_input)
            elif command == "update":
                _handle_update(user_input)
            elif command == "delete":
                _handle_delete(user_input)
            elif command == "info":
                _handle_info(arguments)
        except (KeyError, ValueError) as error:
            print(f"Ошибка: {error}")
