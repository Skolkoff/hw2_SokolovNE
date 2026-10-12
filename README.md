# Примитивная база данных

Консольная база данных на Python. Схемы таблиц хранятся в `db_meta.json`, а
записи каждой таблицы — в отдельном JSON-файле в `data/`.

## Команды

Строковые значения нужно заключать в одинарные или двойные кавычки. Поддерживаются
типы `int`, `str` и `bool`; логические значения вводятся как `true` или `false`.
Столбец `ID:int` создаётся автоматически, все остальные поля обязательны.

### Управление таблицами

```text
create_table users name:str age:int is_active:bool
list_tables
info users
drop_table users
```

Перед удалением таблицы программа запрашивает подтверждение. Введите `y`, чтобы
продолжить, или любой другой ответ, чтобы отменить действие.

### Операции с данными

```text
insert into users values ("Sergei", 28, true)
select from users
select from users where age = 28
select from users order by age
select from users where is_active = true order by age desc
update users set age = 29 where name = "Sergei"
delete from users where ID = 1
```

`select` выводит результат в виде таблицы. Для `update` и `delete` обязательно
условие `where`. Сортировка задаётся необязательной частью `order by <столбец>`;
по умолчанию порядок возрастающий, для убывающего укажите `desc`. Удаление записи
также требует подтверждения.

### Общие команды

```text
help
exit
```

## Демонстрация

[![Демонстрация работы базы данных](https://asciinema.org/a/Q5FgswVcBGOO4JFP.svg)](https://asciinema.org/a/Q5FgswVcBGOO4JFP)
