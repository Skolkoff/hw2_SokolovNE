"""Разбор команд и значений базы данных."""

import re
import shlex

from primitive_db.constants import FALSE_VALUES, TRUE_VALUES, VALID_TYPES


def parse_command(user_input: str) -> list[str]:
    """Разбирает команду на имя и аргументы."""
    return shlex.split(user_input)


def split_values(raw_values: str) -> list[str]:
    """Разделяет значения по запятым вне кавычек."""
    values = []
    current = []
    quote = None
    escaped = False

    for character in raw_values:
        if escaped:
            current.append(character)
            escaped = False
            continue
        if character == "\\" and quote:
            current.append(character)
            escaped = True
            continue
        if character in {"'", '"'}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
            current.append(character)
            continue
        if character == "," and quote is None:
            values.append("".join(current).strip())
            current = []
        else:
            current.append(character)

    if quote:
        raise ValueError("Не закрыты кавычки в значениях.")
    if current or raw_values.strip():
        values.append("".join(current).strip())
    if any(not value for value in values):
        raise ValueError("Пустые значения не допускаются.")
    return values


def parse_value(raw_value: str) -> tuple[object, bool]:
    """Преобразует литерал и возвращает признак строковых кавычек."""
    value = raw_value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        text = value[1:-1]
        text = text.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")
        return text, True
    if value.lower() in TRUE_VALUES:
        return True, False
    if value.lower() in FALSE_VALUES:
        return False, False
    try:
        return int(value), False
    except ValueError as error:
        raise ValueError(f"Некорректное значение: {value}.") from error


def parse_values(raw_values: str) -> list[object]:
    """Преобразует значения из команды insert в Python-типы."""
    return [parse_value(value)[0] for value in split_values(raw_values)]


def parse_clause(clause: str, schema: dict) -> dict:
    """Преобразует условие или список присваиваний в словарь."""
    result = {}
    for assignment in split_values(clause):
        column_name, raw_value = _split_assignment(assignment)
        if column_name not in schema:
            raise KeyError(column_name)
        if column_name in result:
            raise ValueError(f"Столбец {column_name} указан несколько раз.")
        value, quoted = parse_value(raw_value)
        column_type = schema[column_name]
        expected_type = VALID_TYPES.get(column_type)
        if expected_type is str and not quoted:
            raise ValueError(
                f"Строковое значение для {column_name} нужно взять в кавычки."
            )
        if expected_type is None or type(value) is not expected_type:
            raise ValueError(f"Для столбца {column_name} требуется тип {column_type}.")
        result[column_name] = value
    if not result:
        raise ValueError("Условие не должно быть пустым.")
    return result


def _split_assignment(assignment: str) -> tuple[str, str]:
    """Разделяет присваивание по знаку равенства вне кавычек."""
    quote = None
    escaped = False
    equal_index = -1
    for index, character in enumerate(assignment):
        if escaped:
            escaped = False
        elif character == "\\" and quote:
            escaped = True
        elif character in {"'", '"'}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        elif character == "=" and quote is None:
            if equal_index >= 0:
                raise ValueError(f"Некорректное условие: {assignment}.")
            equal_index = index
    if equal_index < 0:
        raise ValueError(f"Некорректное условие: {assignment}.")
    column_name = assignment[:equal_index].strip()
    raw_value = assignment[equal_index + 1 :].strip()
    if not column_name or not raw_value:
        raise ValueError(f"Некорректное условие: {assignment}.")
    return column_name, raw_value


def _find_keyword(text: str, keyword: str) -> int:
    """Находит ключевое слово вне строковых кавычек."""
    quote = None
    escaped = False
    index = 0
    lowered = text.lower()
    while index < len(text):
        character = text[index]
        if escaped:
            escaped = False
        elif character == "\\" and quote:
            escaped = True
        elif character in {"'", '"'}:
            if quote == character:
                quote = None
            elif quote is None:
                quote = character
        elif quote is None and re.match(r"\b" + keyword + r"\b", lowered[index:]):
            return index
        index += 1
    return -1


def parse_insert_command(user_input: str) -> tuple[str, list[object]]:
    """Разбирает команду добавления записи."""
    match = re.fullmatch(
        r"\s*insert\s+into\s+([A-Za-z_][A-Za-z0-9_]*)\s+values\s*\((.*)\)\s*",
        user_input,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("Формат команды insert: insert into <таблица> values (...).")
    table_name, raw_values = match.groups()
    return table_name, parse_values(raw_values)


def parse_select_command(
    user_input: str,
) -> tuple[str, str | None, str | None, bool]:
    """Разбирает select с необязательными where и order by."""
    match = re.fullmatch(
        r"\s*select\s+from\s+([A-Za-z_][A-Za-z0-9_]*)(.*)",
        user_input,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("Формат команды select: select from <таблица> [where ...].")
    table_name, remainder = match.groups()
    remainder = remainder.strip()
    if not remainder:
        return table_name, None, None, False

    order_index = _find_keyword(remainder, r"order\s+by")
    order_by = None
    descending = False
    if order_index >= 0:
        order_match = re.match(r"order\s+by\b", remainder[order_index:], re.I)
        order_start = order_index + order_match.end()
        order_clause = remainder[order_start:].strip()
        order_match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_]*)(?:\s+(asc|desc))?",
            order_clause,
            flags=re.IGNORECASE,
        )
        if not order_match:
            raise ValueError("Формат сортировки: order by <столбец> [asc|desc].")
        order_by, direction = order_match.groups()
        descending = direction is not None and direction.lower() == "desc"
        remainder = remainder[:order_index].strip()

    if not remainder:
        return table_name, None, order_by, descending
    if not remainder.lower().startswith("where "):
        raise ValueError("После имени таблицы ожидается условие where или order by.")
    return table_name, remainder[6:].strip(), order_by, descending


def parse_update_command(user_input: str) -> tuple[str, str, str]:
    """Разбирает команду update на таблицу, set и where."""
    match = re.match(
        r"\s*update\s+([A-Za-z_][A-Za-z0-9_]*)\s+set\b",
        user_input,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("Формат команды update: update <таблица> set ... where ....")
    where_index = _find_keyword(user_input[match.end() :], "where")
    if where_index < 0:
        raise ValueError("В команде update требуется условие where.")
    set_start = match.end()
    split_at = set_start + where_index
    set_clause = user_input[set_start:split_at].strip()
    where_clause = user_input[split_at + len("where") :].strip()
    if not set_clause or not where_clause:
        raise ValueError("Укажите условия set и where.")
    return match.group(1), set_clause, where_clause


def parse_delete_command(user_input: str) -> tuple[str, str]:
    """Разбирает команду delete и возвращает имя таблицы и where."""
    match = re.fullmatch(
        r"\s*delete\s+from\s+([A-Za-z_][A-Za-z0-9_]*)\s+where\s+(.+?)\s*",
        user_input,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        raise ValueError("Формат команды delete: delete from <таблица> where ....")
    return match.group(1), match.group(2)
