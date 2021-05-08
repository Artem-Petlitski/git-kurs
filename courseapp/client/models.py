"""Client's models"""
from json import loads

from courseapp.models import ManageData, ManageUsers, ManageOrder, ManageProblems
from courseapp.protocol import send, receive, GOOD, ERROR, BREAK
from courseapp.utils import (
    string_input,
    integer_input,
    login_input,
    password_input,
    enter_to_continue,
    receive_and_print,
    max_min_10_input,
    type_of_output_input,
    menu,
    clear,
    select_academic_degree,
    select_position,
)
from functools import reduce
from courseapp.server.enums import AcademicDegree, Position


class User:
    @staticmethod
    def login(socket):
        while True:
            choice = menu(
                title="Главное меню",
                exit_option="Выход",
                options=[
                    "Вход как администратор",
                    "Вход как пользователь",
                    "Вход как эксперт",
                ],
            )
            if choice == "1":
                obj = {
                    "login": login_input(),
                    "password": password_input(),
                    "permissions": "admin",
                }
                send(socket=socket, data=obj)
                response = receive(socket=socket)
                if response == GOOD:
                    User.admin_menu(socket=socket)
                else:
                    print("Неверный логин или пароль")
                    enter_to_continue()
            elif choice == "2":
                obj = {
                    "login": login_input(),
                    "password": password_input(),
                    "permissions": "default",
                }

                send(socket=socket, data=obj)
                response = receive(socket=socket)
                if response == GOOD:
                    User.default_menu(socket=socket)
                else:
                    print("Неверный логин или пароль")
                    enter_to_continue()
            elif choice == "3":
                obj = {
                    "login": login_input(),
                    "password": password_input(),
                    "permissions": "expert",
                }
                send(socket=socket, data=obj)
                response = receive(socket=socket)
                if response == GOOD:
                    User.expert_menu(socket=socket)
                else:
                    print("Неверный логин или пароль")
                    enter_to_continue()
            elif choice == "4":
                send(socket=socket, data=BREAK)
                break

    @staticmethod
    def admin_menu(socket):
        while True:
            choice = menu(
                title="Меню администратора",
                options=[
                    "Услуги",
                    "Заказы",
                    "Пользователи",
                    "Компании",
                    "Принятие решений",
                ],
            )
            if choice == "1":
                send(socket=socket, data=choice)
                Service.menu(socket=socket)
            elif choice == "2":
                send(socket=socket, data=choice)
                Order.menu(socket=socket)
            elif choice == "3":
                send(socket=socket, data=choice)
                Users.menu(socket=socket)
            elif choice == "4":
                send(socket=socket, data=choice)
                Company.menu(socket=socket)
            elif choice == "5":
                send(socket=socket, data=choice)
                Problems.menu(socket=socket)
            elif choice == "6":
                send(socket=socket, data=BREAK)
                break

    @staticmethod
    def default_menu(socket):
        while True:
            choice = menu(
                title="Меню компании",
                options=[
                    "Купить услугу",
                    "Просмотр заказанных услуг",
                    "Сменить пароль",
                ],
            )
            if choice == "1":
                send(socket=socket, data=choice)
                Order.add(socket=socket)
            elif choice == "2":
                send(socket=socket, data=choice)
                Order.print_for_user(socket=socket)
            elif choice == "3":
                send(socket=socket, data=choice)
                Users.change_password(socket=socket)
            elif choice == "4":
                send(socket=socket, data=BREAK)
                break

    @staticmethod
    def expert_menu(socket):
        while True:
            choice = menu(
                title="Меню эксперта",
                options=["Проголосовать", "Просмотреть принятые решения"],
            )
            if choice == "1":
                send(socket=socket, data=choice)
                Problems.vote(socket=socket)
            elif choice == "2":
                send(socket=socket, data=choice)
                Problems.print_voted(socket=socket)
            elif choice == "3":
                send(socket=socket, data=BREAK)
                break


class Users(ManageUsers):
    menu_title = "Меню пользователей"
    menu_options = ["Добавление", "Удаление", "Изменение пароля", "Вывод"]

    @classmethod
    def choose(cls, **kwargs):
        choice = menu(title=cls.menu_title, options=cls.menu_options)
        send(socket=kwargs["socket"], data=choice)
        return choice

    @classmethod
    def add(cls, socket):
        user = {}
        while True:
            role_choice = menu(
                title="Добавление пользователя",
                options=["Администратор", "Покупатель", "Эксперт"],
            )
            if role_choice == "1":
                send(socket=socket, data=role_choice)
                user["permissions"] = "admin"
                user["login"] = login_input()
                send(socket=socket, data=user["login"])
                response = receive(socket=socket)
                if response == GOOD:
                    user["password"] = password_input()
                    send(socket=socket, data=user)
                    print("Пользователь добавлен успешно")
                    enter_to_continue()
                else:
                    print("Такой логин уже существует")
                    enter_to_continue()
            elif role_choice == "2":
                send(socket=socket, data=role_choice)
                user["permissions"] = "default"
                user["login"] = login_input()
                send(socket=socket, data=user["login"])
                response = receive(socket=socket)
                if response == GOOD:
                    user["password"] = password_input()
                    send(socket=socket, data=user)
                    print("Пользователь добавлен успешно")
                    enter_to_continue()
                else:
                    print("Такой логин уже существует")
                    enter_to_continue()
            elif role_choice == "3":
                send(socket=socket, data=role_choice)
                user["permissions"] = "expert"
                user["login"] = login_input()
                send(socket=socket, data=user["login"])
                response = receive(socket=socket)
                if response == GOOD:
                    clear()
                    pos_mess = (
                        "Выберете должнсть\n"
                        f"1. {Position.engineer.value}\n"
                        f"2. {Position.head_laboratory.value}\n"
                        f"3. {Position.complex_manager.value}\n"
                        f"4. {Position.director.value}\n"
                    )

                    send(socket=socket, data=select_position(pos_mess))
                    receive(socket=socket)
                    clear()
                    academic_degree_mess = (
                        "Выберете ученую степень\n"
                        f"1. {AcademicDegree.no_degree.value}\n"
                        f"2. {AcademicDegree.candidate.value}\n"
                        f"3. {AcademicDegree.phd.value}\n"
                        f"4. {AcademicDegree.academic.value}\n"
                    )
                    send(
                        socket=socket, data=select_academic_degree(academic_degree_mess)
                    )
                    receive(socket=socket)

                    user["password"] = password_input()
                    send(socket=socket, data=user)
                    print("Пользователь добавлен успешно")
                    enter_to_continue()
                else:
                    print("Такой логин уже существует")
                    enter_to_continue()
            elif role_choice == "4":
                send(socket=socket, data=BREAK)
                break

    @classmethod
    def delete(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            print("Пользователь удален")
        else:
            print("Неверный id")
        enter_to_continue()

    @classmethod
    def change_password(cls, socket):
        new_password = password_input("Введите новый пароль")
        send(socket=socket, data=new_password)
        response = receive(socket=socket)
        if response == ERROR:
            print("Нельзя изменить пароль на текущий")
        else:
            print("Пароль изменен")
        enter_to_continue()

    @classmethod
    def print(cls, socket):
        clear()
        receive_and_print(socket=socket)
        enter_to_continue()


class Service(ManageData):
    menu_title = "Меню услуг"
    menu_options = [
        "Добавление",
        "Удаление",
        "Изменение",
        "Вывод",
        "Фильтрация",
        "Сортировка",
    ]

    @classmethod
    def choose(cls, **kwargs):
        choice = menu(title=cls.menu_title, options=cls.menu_options)
        send(socket=kwargs["socket"], data=choice)
        return choice

    @classmethod
    def add(cls, socket):
        clear()
        send(socket=socket, data=string_input("Введите название"))
        response = receive(socket=socket)
        if response == ERROR:
            print("Услуга с таким названием уже существует")
            enter_to_continue()
        else:
            clear()
            send(socket=socket, data=string_input("Введите название компании"))
            response = receive(socket=socket)
            if response == ERROR:
                print("Компании с таким именем не существует")
                enter_to_continue()
            else:
                clear()
                send(socket=socket, data=string_input("Введите описание услуги"))
                receive(socket=socket)
                send(socket=socket, data=integer_input("Введите цену"))
                print("Услуга добавлена успешно")
                enter_to_continue()

    @classmethod
    def edit(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            while True:
                choice = menu(title="Изменение услуги", options=["Название", "Цену"])
                if choice == "1":
                    send(socket=socket, data=choice)
                    name = string_input("Введите название")
                    send(socket=socket, data=name)
                    print("Успешно изменено")
                    enter_to_continue()
                elif choice == "2":
                    send(socket=socket, data=choice)
                    price = integer_input("Введите цену")
                    send(socket=socket, data=price)
                    print("Успешно изменено")
                    enter_to_continue()
                elif choice == "3":
                    send(socket=socket, data=BREAK)
                    break
        else:
            print("Неверный id")
            enter_to_continue()

    @classmethod
    def delete(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            print("Услуга удалена")
        else:
            print("Неверный id")
        enter_to_continue()

    @classmethod
    def print(cls, socket):
        clear()
        receive_and_print(socket=socket)
        enter_to_continue()

    @classmethod
    def filter(cls, socket):
        while True:
            choice = menu(
                title="Фильтрация по услугам",
                options=["По id", "По названию", "По цене", "По компании", "Вывод"],
            )

            if choice == "1":
                send(socket=socket, data=choice)
                obj = {
                    "min": integer_input("Введите минимальный id"),
                    "max": integer_input("Введите максимальный id"),
                }
                while int(obj["min"]) > int(obj["max"]):
                    print("Минимальное значение не должно быть больше максимального")
                    obj = {
                        "min": integer_input("Введите минимальный id"),
                        "max": integer_input("Введите максимальный id"),
                    }
                send(socket=socket, data=obj)
            elif choice == "2":
                send(socket=socket, data=choice)
                name = string_input("Введите название")
                send(socket=socket, data=name)
            elif choice == "3":
                send(socket=socket, data=choice)
                obj = {
                    "min": integer_input("Введите минимальную цену"),
                    "max": integer_input("Введите максимальную цену"),
                }
                while int(obj["min"]) > int(obj["max"]):
                    print("Минимальное значение не должно быть больше максимального")
                    obj = {
                        "min": integer_input("Введите минимальную цену"),
                        "max": integer_input("Введите максимальную цену"),
                    }
                send(socket=socket, data=obj)
            elif choice == "4":
                send(socket=socket, data=choice)
                send(socket=socket, data=string_input("Введите название компании"))
            elif choice == "5":
                send(socket=socket, data=choice)
                cls.print(socket=socket)
            elif choice == "6":
                send(socket=socket, data=BREAK)
                break

    @classmethod
    def sort(cls, socket):
        while True:
            choice = menu(
                title="Сортировка по услугам",
                options=["По id", "По названию", "По цене", "По компании"],
            )
            if choice in ("1", "2", "3", "4"):
                send(socket=socket, data=choice)
                cls.print(socket=socket)
            elif choice == "5":
                send(socket=socket, data=BREAK)
                break


class Order(ManageOrder):
    menu_title = "Меню заказов"
    menu_options = ["Вывод", "Удаление", "Фильтрация", "Сортировка"]

    @classmethod
    def print_for_user(cls, socket):
        cls.print(socket)

    @classmethod
    def choose(cls, **kwargs):
        choice = menu(title=cls.menu_title, options=cls.menu_options)
        send(socket=kwargs["socket"], data=choice)
        return choice

    @classmethod
    def add(cls, socket):
        clear()
        receive_and_print(socket=socket)
        service_id = integer_input("Введите id заказываемой услуги")
        send(socket=socket, data=service_id)
        response = receive(socket=socket)
        if response == ERROR:
            print("Неверный id")
        else:
            quantity = integer_input("Введите количество")
            send(socket=socket, data=quantity)
            print("Заказ добавлен успешно")
        enter_to_continue()

    @classmethod
    def delete(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            print("Заказ удален")
        else:
            print("Неверный id")
        enter_to_continue()

    @classmethod
    def print(cls, socket):
        clear()
        receive_and_print(socket=socket)
        enter_to_continue()

    @classmethod
    def filter(cls, socket):
        while True:
            choice = menu(
                title="Фильтрация по заказам",
                options=[
                    "По id",
                    "По услуге",
                    "По покупателю",
                    "По количеству",
                    "Вывод",
                ],
            )
            if choice == "1":
                send(socket=socket, data=choice)
                obj = {
                    "min": integer_input("Введите минимальный id"),
                    "max": integer_input("Введите максимальный id"),
                }
                while int(obj["min"]) > int(obj["max"]):
                    print("Минимальное значение не должно быть больше максимального")
                    obj = {
                        "min": integer_input("Введите минимальный id"),
                        "max": integer_input("Введите максимальный id"),
                    }
                send(socket=socket, data=obj)
            elif choice == "2":
                send(socket=socket, data=choice)
                clear()
                receive_and_print(socket=socket)
                send(socket=socket, data=integer_input("Введите id услуги"))
            elif choice == "3":
                send(socket=socket, data=choice)
                clear()
                receive_and_print(socket=socket)
                send(socket=socket, data=integer_input("Введите id покупателя"))
            elif choice == "4":
                send(socket=socket, data=choice)
                obj = {
                    "min": integer_input("Введите минимальное количество"),
                    "max": integer_input("Введите максимальное количество"),
                }
                while int(obj["min"]) > int(obj["max"]):
                    print("Минимальное значение не должно быть больше максимального")
                    obj = {
                        "min": integer_input("Введите минимальное количество"),
                        "max": integer_input("Введите максимальное количество"),
                    }
                send(socket=socket, data=obj)
            elif choice == "5":
                send(socket=socket, data=choice)
                cls.print(socket=socket)
            elif choice == "6":
                send(socket=socket, data=BREAK)
                break

    @classmethod
    def sort(cls, socket):
        while True:
            choice = menu(
                title="Сортировка по заказам",
                options=["По id", "По услугам", "По покупателю", "По количеству"],
            )
            if "1" <= choice <= "4":
                send(socket=socket, data=choice)
                cls.print(socket=socket)
            elif choice == "5":
                send(socket=socket, data=BREAK)
                break


class Company(ManageData):
    menu_title = "Меню компаний"
    menu_options = ["Добавление", "Удаление", "Изменение", "Вывод", "Сортировка"]

    @classmethod
    def menu(cls, **kwargs):
        """Шаблонный метод"""
        while True:
            choice = cls.choose(**kwargs)
            if choice == "1":
                cls.add(**kwargs)
            elif choice == "2":
                cls.delete(**kwargs)
            elif choice == "3":
                cls.edit(**kwargs)
            elif choice == "4":
                cls.print(**kwargs)
            elif choice == "5":
                cls.sort(**kwargs)
            elif choice == "6":
                break

    @classmethod
    def choose(cls, **kwargs):
        choice = menu(title=cls.menu_title, options=cls.menu_options)
        send(socket=kwargs["socket"], data=choice)
        return choice

    @classmethod
    def add(cls, socket):
        clear()
        send(socket=socket, data=string_input("Введите название"))
        response = receive(socket=socket)
        if response == ERROR:
            print("Компания с таким названием уже существует")
            enter_to_continue()
        else:
            print("Компания добавлен успешно")
            enter_to_continue()

    @classmethod
    def edit(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            while True:
                choice = menu(title="Изменение компании", options=["Название"])
                if choice == "1":
                    send(socket=socket, data=choice)
                    name = string_input("Введите название")
                    send(socket=socket, data=name)
                    print("Успешно изменено")
                    enter_to_continue()
                elif choice == "2":
                    send(socket=socket, data=BREAK)
                    break
        else:
            print("Неверный id")
            enter_to_continue()

    @classmethod
    def delete(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            print("Компания удалена")
        else:
            print("Неверный id")
        enter_to_continue()

    @classmethod
    def print(cls, socket):
        clear()
        receive_and_print(socket=socket)
        enter_to_continue()

    @classmethod
    def sort(cls, socket):
        while True:
            choice = menu(
                title="Сортировка компаний",
                options=["По id", "По названию", "По количеству услуг"],
            )
            if choice in ("1", "2", "3"):
                send(socket=socket, data=choice)
                cls.print(socket=socket)
            elif choice == "4":
                send(socket=socket, data=BREAK)
                break


class Problems(ManageProblems):
    menu_title = "Меню принятия решений"
    menu_options = ["Ввод проблемы", "Вывод", "Удаление"]

    @classmethod
    def choose(cls, **kwargs):
        choice = menu(title=cls.menu_title, options=cls.menu_options)
        send(socket=kwargs["socket"], data=choice)
        return choice

    @classmethod
    def add(cls, socket):
        response = receive(socket=socket)
        if response == ERROR:
            print("Среди пользователей нет экспертов")
            enter_to_continue()
            return
        obj = {"description": string_input("Введите описание проблемы")}
        num = 1
        obj["decisions"] = [string_input(f"Введите решение проблемы №{num}")]
        num += 1
        decision = string_input(f"Введите решение проблемы №{num}")
        while decision in obj["decisions"]:
            print("Решения одной проблемы должны быть уникальны")
            decision = string_input(f"Введите решение проблемы №{num}")
        obj["decisions"].append(decision)
        while True:
            choice = menu(title="Добавить ещё?", options=["Да"])
            if choice == "1":
                num += 1
                decision = string_input(f"Введите решение проблемы №{num}")
                while decision in obj["decisions"]:
                    print("Решения одной проблемы должны быть уникальны")
                    decision = string_input(f"Введите решение проблемы №{num}")
                obj["decisions"].append(decision)
            elif choice == "2":
                send(socket=socket, data=obj)
                print("Проблема добавлена успешно")
                enter_to_continue()
                break

    @classmethod
    def print(cls, socket):
        clear()
        choice = type_of_output_input(
            "1. Проблемы с неоконченным голосованием\n"
            "2. Проблемы с оконченным голосованием"
        )
        if choice == "1":
            send(socket=socket, data=choice)
            clear()
            receive_and_print(socket=socket)
            enter_to_continue()
        elif choice == "2":
            clear()
            send(socket=socket, data=choice)
            clear()
            receive_and_print(socket=socket)
            send(
                socket=socket,
                data=integer_input("Введите id проблемы для детального просмотра"),
            )
            response = receive(socket=socket)
            if response == ERROR:
                print("Неверный id")
                enter_to_continue()
                return
            receive_and_print(socket=socket)

            enter_to_continue()

    @classmethod
    def delete(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")
        send(socket=socket, data=id_)
        response = receive(socket=socket)
        if response == GOOD:
            print("Проблема удалена")
        else:
            print("Неверный id")
        enter_to_continue()

    @classmethod
    def vote(cls, socket):
        clear()
        receive_and_print(socket=socket)
        id_ = integer_input("Введите id")

        send(socket=socket, data=id_)
        decisions = receive(socket=socket)
        if decisions == ERROR:
            print("Неверный id")
            enter_to_continue()
            return
        clear()
        decisions = loads(decisions)
        for id in decisions:
            assessment = max_min_10_input(
                f"Введите оценку решению от одного до 10\n {decisions[id]}"
            )
            decisions[id] = int(assessment)
            clear()
        send(socket=socket, data=decisions)
        print("Спасибо, ваши голоса будут учитаны")
        enter_to_continue()

    @classmethod
    def print_voted(cls, socket):
        clear()
        receive_and_print(socket=socket)
        enter_to_continue()
