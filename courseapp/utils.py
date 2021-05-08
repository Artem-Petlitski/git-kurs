"""Basic utils"""
import logging
from os import system
import hashlib
from courseapp.protocol import receive
from functools import reduce as reduce_
from getpass import getpass
from courseapp.server.enums import AcademicDegree, Position


def create_logger():
    logger_ = logging.getLogger()
    logger_.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(funcName)s] = %(message)s"
    )
    s_handler = logging.StreamHandler()
    s_handler.setFormatter(formatter)
    logger_.addHandler(s_handler)
    return logger_


def count_sold(iterable: list, default=0):
    function = (
        lambda a, b: a + b.quantity if type(a) is int else a.quantity + b.quantity
    )
    if not iterable:
        return default
    elif len(iterable) == 1:
        return iterable[0].quantity
    else:
        return reduce_(function, iterable)


def string_input(prompt: str) -> str:
    return input(prompt + "\n")


def login_input(prompt: str = "Введите логин") -> str:
    string = input(prompt + "\n")
    while not string.isalpha():
        print("В логине должны быть только буквы")
        string = input(prompt + "\n")
    return string


def password_input(prompt: str = "Введите пароль") -> str:
    password = getpass(prompt + " (ввод символов не будет отображен)\n")
    hash_ = hashlib.sha1(bytes(password, encoding="utf8"))
    return hash_.hexdigest()


def integer_input(prompt: str) -> str:
    integer = input(prompt + "\n")
    while not integer.isnumeric():
        print("В строке должны быть только цифры")
        integer = input(prompt + "\n")
    return integer


def select_position(prompt: str) -> str:
    integer = input(prompt + "\n")
    while not integer in ["1", "2", "3", "4"]:
        print("В строке должны быть только цифры от 1 до 4")
        integer = input(prompt + "\n")

    choices = {
        "1": Position.engineer.value,
        "2": Position.head_laboratory.value,
        "3": Position.complex_manager.value,
        "4": Position.director.value,
    }
    return choices[integer]


def select_academic_degree(prompt: str) -> str:
    integer = input(prompt + "\n")
    while not integer in ["1", "2", "3", "4"]:
        print("В строке должны быть только цифры от 1 до 4")
        integer = input(prompt + "\n")

    choices = {
        "1": AcademicDegree.no_degree.value,
        "2": AcademicDegree.candidate.value,
        "3": AcademicDegree.phd.value,
        "4": AcademicDegree.academic.value,
    }
    return choices[integer]


def type_of_output_input(prompt: str) -> str:
    integer = input(prompt + "\n")
    while not integer in ["1", "2"]:
        print("В строке должны быть только цифры от 1 до 2")
        integer = input(prompt + "\n")
    return integer


def max_min_10_input(prompt: str) -> str:
    integer = input(prompt + "\n")
    while not (integer.isnumeric() and int(integer) <= 10 and int(integer) >= 1):
        print("В строке должны быть только цифры от 1 до 10")
        integer = input(prompt + "\n")
    return integer


def get_or_create(session_, model, **kwargs):
    instance = session_.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session_.add(instance)
        session_.commit()
        return instance


def receive_and_print(socket) -> None:
    data = receive(socket=socket)
    print(data)


def pause() -> None:
    print("Нажмите Enter для продолжения")
    # system("pause")


def clear() -> None:
    print()
    # system("clear")


def enter_to_continue() -> None:
    input()


def menu(title: str, options: list, exit_option="Назад") -> str:
    while True:
        clear()
        counter = 1
        print(f"\t{title}")
        for option in options:
            print(f"{counter}. {option}")
            counter += 1
        print(f"{counter}. {exit_option}")
        choice = input()
        if "1" <= choice <= str(counter):
            return choice


def bar_chart(data: list, **kwargs) -> str:
    if not data:
        return ""
    max_value = max(count for _, count in data)
    increment = max_value / 25
    longest_label_length = max(len(label) for label, _ in data)
    string_bar_chart = ""
    counter = 1
    for label, count in data:
        if count == 0:
            bar = ""
        else:
            bar_chunks, remainder = divmod(int(count * 8 / increment), 8)
            bar = "█" * bar_chunks
            if remainder > 0:
                bar += chr(ord("█") + (8 - remainder))
        if "service" in kwargs:
            string_bar_chart += (
                f"{label.rjust(longest_label_length)} | {bar} ${count}\n"
            )
        elif "rating" in kwargs:
            string_bar_chart += (
                f"{counter}. {label.rjust(longest_label_length)} | {bar} {count}%\n"
            )
            counter += 1
        else:
            string_bar_chart += f"{label.rjust(longest_label_length)} | {bar} {count}\n"
    return string_bar_chart
