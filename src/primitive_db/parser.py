"""Разбор ввода командной строки."""

import shlex


def parse_command(user_input: str) -> list[str]:
    """Разбирает команду на имя и аргументы."""
    return shlex.split(user_input)
