"""Декораторы и замыкание для повторно используемых операций."""

import time
from functools import wraps

from prompt import string

from primitive_db.constants import CONFIRM_PROMPT, TIME_MESSAGE


def handle_db_errors(func):
    """Перехватывает ошибки операций с базой данных."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: файл данных не найден.")
        except KeyError as error:
            print(f"Ошибка: таблица или столбец {error} не найден.")
        except ValueError as error:
            print(f"Ошибка валидации: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    return wrapper


def confirm_action(action_name: str):
    """Запрашивает подтверждение перед опасной операцией."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            answer = string(CONFIRM_PROMPT.format(action_name=action_name))
            if answer.lower() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Печатает время выполнения функции."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        started_at = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - started_at
            print(TIME_MESSAGE.format(name=func.__name__, seconds=elapsed))

    return wrapper


def create_cacher():
    """Создаёт функцию кэширования результатов по ключу."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает сохранённое значение или вычисляет его."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
