# Примитивная база данных

Консольное приложение для создания таблиц и управления записями. Данные и
схемы хранятся в JSON-файлах.

## Установка и запуск

```bash
uv sync
uv run database
```

## Управление таблицами

```text
create_table users name:str age:int is_active:bool
list_tables
drop_table users
help
exit
```

Столбец `ID:int` добавляется автоматически. Поддерживаются типы `int`, `str`
и `bool`.
