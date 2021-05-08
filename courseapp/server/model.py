import logging as log
from json import loads

from itertools import combinations
from sqlalchemy import func
import courseapp.server.orm as orm
from courseapp.protocol import send, receive, GOOD, ERROR, BREAK
from courseapp.utils import bar_chart, count_sold
from tabulate import tabulate
from courseapp.config import table_format
from courseapp.models import ManageData, ManageUsers, ManageOrder, ManageProblems
from courseapp.server.enums import Status
from courseapp.server.utils import find_competence_assessment


class AuthenticationFail(Exception):
    def __str__(self):
        return "Wrong login or password"


class User:
    def __init__(self, socket, session):
        log.debug("User.__init__")
        self.socket = socket
        self.session = session
        self.user = orm.User
        log.debug("User.__init__ END")

    def login(self, obj):
        log.debug("User.login")
        obj = loads(obj)
        log.debug(f"Got dict {obj}")
        user = (
            self.session.query(orm.User)
            .filter(
                orm.User.login == obj["login"],
                orm.User.password == obj["password"],
                orm.User.permissions == obj["permissions"],
            )
            .first()
        )
        log.debug(f"Got user {user}")
        if user:
            log.debug("Found user")
            self.user = user
        else:
            log.debug("User not found")
            raise AuthenticationFail

    def main_menu(self):
        log.debug("User.main_menu")
        while True:
            obj = receive(socket=self.socket)
            if obj == BREAK:
                log.debug("User.main_menu BREAK")
                break
            try:
                self.login(obj=obj)
                send(socket=self.socket, data=GOOD)
                log.debug(f"Logged in as {self.user.permissions}")
                if self.user.permissions == "admin":
                    self.admin_menu()
                elif self.user.permissions == "default":
                    self.default_menu()
                elif self.user.permissions == "expert":
                    self.expert_menu()
            except AuthenticationFail:
                log.debug("Auth fail")
                send(socket=self.socket, data=ERROR)

    def admin_menu(self):
        log.debug("User.admin_menu")
        while True:
            choice = receive(socket=self.socket)
            log.debug(f"Choice {choice}")
            if choice == "1":
                log.debug("Services menu")
                Service.menu(socket=self.socket, session=self.session)
            elif choice == "2":
                log.debug("Orders menu")
                Order.menu(socket=self.socket, session=self.session, user=self.user)
            elif choice == "3":
                log.debug("Users menu")
                Users.menu(socket=self.socket, session=self.session, user=self.user)
            elif choice == "4":
                log.debug("Companies menu")
                Company.menu(
                    socket=self.socket,
                    session=self.session,
                )
            elif choice == "5":
                log.debug("Problems menu")
                Problems.menu(socket=self.socket, session=self.session, user=self.user)
            elif choice == BREAK:
                log.debug("admin_menu BREAK")
                break

    def default_menu(self):
        log.debug("User.default_menu")
        while True:
            choice = receive(socket=self.socket)
            log.debug(f"Choice {choice}")
            if choice == "1":
                Order.add(socket=self.socket, session=self.session, user=self.user)
            elif choice == "2":
                Order.print_for_user(
                    socket=self.socket, session=self.session, user=self.user
                )
            elif choice == "3":
                Users.change_password(
                    socket=self.socket, session=self.session, user=self.user
                )
            elif choice == BREAK:
                log.debug("User.default_menu BREAK")
                break

    def expert_menu(self):
        log.debug("User.expert_menu")
        while True:
            choice = receive(socket=self.socket)
            log.debug(f"Choice {choice}")
            if choice == "1":
                Problems.vote(socket=self.socket, session=self.session, user=self.user)
            elif choice == "2":
                Problems.print_voted(
                    socket=self.socket, session=self.session, user=self.user
                )
            elif choice == BREAK:
                log.debug("User.expert_menu BREAK")
                break


class Service(ManageData):
    @classmethod
    def choose(cls, **kwargs):
        choice = receive(socket=kwargs["socket"])
        return choice

    @classmethod
    def add(cls, socket, session):
        log.debug("Service.add")
        name = receive(socket=socket)
        service = session.query(orm.Service).filter(orm.Service.name == name)
        if service.first():
            log.debug("Service name already taken")
            send(socket=socket, data=ERROR)
        else:
            log.debug("Service name is new")
            send(socket=socket, data=GOOD)
            company_name = receive(socket=socket)
            company = (
                session.query(orm.Company)
                .filter(orm.Company.name == company_name)
                .first()
            )
            if not company:
                log.debug("Company does not exist")
                send(socket=socket, data=ERROR)
            else:
                send(socket=socket, data=GOOD)
                content = receive(socket=socket)
                send(socket=socket, data=GOOD)
                price = receive(socket=socket)
                log.debug(f"Service={name}, {price}")
                session.add(
                    orm.Service(
                        name=name,
                        price=price,
                        company=company,
                    )
                )
                session.commit()
                log.debug("Service.add END")

    @classmethod
    def delete(cls, socket, session):
        log.debug("Service.delete")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        service = session.query(orm.Service).get(id_)
        if service:
            send(socket=socket, data=GOOD)
            session.delete(service)
            session.commit()
            log.debug(f"Found and deleted ID={id_}")
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def edit(cls, socket, session):
        log.debug("Service.edit")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        service = session.query(orm.Service).get(id_)
        if service:
            send(socket=socket, data=GOOD)
            log.debug(f"ID={id_} found")
            while True:
                choice = receive(socket=socket)
                if choice == "1":
                    change_ = receive(socket=socket)
                    log.debug(f"Changing name to {change_}")
                    service.name = change_
                elif choice == "2":
                    change_ = receive(socket=socket)
                    log.debug(f"Changing price to {change_}")
                    service.price = int(change_)
                elif choice == BREAK:
                    log.debug("Service.edit BREAK")
                    session.commit()
                    break
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def print(cls, socket, session):
        log.debug("Service.print")
        services = session.query(orm.Service)
        table_services = []
        for service in services:
            sold = count_sold(service.orders)
            table_services.append(
                [
                    service.id,
                    service.name,
                    service.company,
                    f"${service.price}",
                    f"{sold} шт.",
                ]
            )
        log.debug(f"Table services {table_services}")
        table = tabulate(
            headers=["ID", "Название", "Компания", "Цена", "Заказано"],
            tabular_data=table_services,
            tablefmt=table_format,
        )
        table += "\n\n\t\tЗаказы\n\n"
        bar_chart_serveces = []
        for service in services:
            money_made = count_sold(service.orders) * service.price
            bar_chart_serveces.append((service.name, money_made))
        print(bar_chart_serveces)
        table += bar_chart(bar_chart_serveces, service=True)
        send(socket=socket, data=table)
        log.debug("Service.print END")
    
    @classmethod
    def order_print(cls, socket, session):
        log.debug("Service.order_print")
        services = session.query(orm.Service)
        table_services = []
        for service in services:
            table_services.append(
                [
                    service.id,
                    service.name,
                    service.company,
                    f"${service.price}",
                ]
            )
        log.debug(f"Table services {table_services}")
        table = tabulate(
            headers=["ID", "Название", "Компания", "Цена"],
            tabular_data=table_services,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        log.debug("Service.order_print END")

    @classmethod
    def filter(cls, socket, session):
        log.debug("Service.filter")
        id_ = False
        id_max = False
        name = False
        price = False
        price_max = False
        company = False
        while True:
            choice = receive(socket=socket)
            log.debug(f"Choice {choice}")
            if choice == "1":
                filter_ = receive(socket=socket)
                obj = loads(filter_)
                id_ = obj["min"]
                id_max = obj["max"]
                log.debug(f"id_ {id_} id_max {id_max}")
            elif choice == "2":
                name = receive(socket=socket)
                log.debug(f"name {name}")
            elif choice == "3":
                filter_ = receive(socket=socket)
                obj = loads(filter_)
                price = obj["min"]
                price_max = obj["max"]
                log.debug(f"price {price} price_max {price_max}")
            elif choice == "4":
                company_name = receive(socket=socket)
                company = (
                    session.query(orm.Company)
                    .filter(orm.Company.name == company_name.lower())
                    .first()
                )
                log.debug(f"company {company}")
            elif choice == "5":
                services = session.query(orm.Service)
                if id_ is not False:
                    services = services.filter(
                        orm.Service.id >= id_, orm.Service.id <= id_max
                    )
                    services = services.order_by(orm.Service.id.asc())
                if name is not False:
                    services = services.filter(orm.Service.name.ilike(f"%{name}%"))
                if price is not False:
                    services = services.filter(
                        orm.Service.price >= price, orm.Service.price <= price_max
                    )
                    services = services.order_by(orm.Service.price.asc())
                if company is not False:
                    services = services.filter(orm.Service.company == company)
                table_services = []
                for service in services:
                    sold = count_sold(service.orders)
                    table_services.append(
                        [
                            service.id,
                            service.name,
                            service.company,
                            f"${service.price}",
                            f"{sold} шт.",
                        ]
                    )
                table = tabulate(
                    headers=["ID", "Название", "Компания", "Цена", "Заказано"],
                    tabular_data=table_services,
                    tablefmt=table_format,
                )
                send(socket=socket, data=table)
                log.debug("Filter sent")
            elif choice == BREAK:
                log.debug("Service.filter BREAK")
                break

    @classmethod
    def sort(cls, socket, session):
        log.debug("Services.sort")
        while True:
            choice = receive(socket=socket)
            services = []
            if choice == "1":
                services = session.query(orm.Service).order_by(orm.Service.id)
            elif choice == "2":
                services = session.query(orm.Service).order_by(orm.Service.name)
            elif choice == "3":
                services = session.query(orm.Service).order_by(orm.Service.price)
            elif choice == "4":
                companies = session.query(orm.Company).filter(orm.Company.services)
                for company in companies:
                    services += company.services
            elif choice == BREAK:
                log.debug("Services.sort BREAK")
                break
            table_services = []
            for service in services:
                quantity = 0
                for order in service.orders:
                    quantity += order.quantity
                table_services.append(
                    [
                        service.id,
                        service.name,
                        service.company,
                        f"${service.price}",
                        f"{quantity} шт.",
                    ]
                )
            table = tabulate(
                headers=["ID", "Название", "Компания", "Цена", "Заказано"],
                tabular_data=table_services,
                tablefmt=table_format,
            )
            send(socket=socket, data=table)
            log.debug("Sort sent")


class Order(ManageOrder):
    @classmethod
    def print_for_user(cls, socket, session, user, **kwargs):
        log.debug("Order.print_for_user")
        orders = (
            session.query(orm.Order).join(orm.User).filter(orm.Order.customer == user)
        )
        table_orders = [
            [
                order.id,
                str(order.service),
                order.customer,
                order.quantity,
                f"${order.service.price * order.quantity}",
            ]
            for order in orders
        ]
        table = tabulate(
            headers=["ID", "Услуга", "Покупатель", "Количество", "Стоимость"],
            tabular_data=table_orders,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        log.debug("Order.print_for_user END")

    @classmethod
    def choose(cls, **kwargs):
        choice = receive(socket=kwargs["socket"])
        return choice

    @classmethod
    def add(cls, socket, session, user, **kwargs):
        log.debug("Order.add")
        Service.order_print(socket=socket, session=session)
        service_id = receive(socket=socket)
        service = session.query(orm.Service).get(service_id)
        if service:
            send(socket=socket, data=GOOD)
            log.debug("Right id")
            quantity = receive(socket=socket)
            quantity = int(quantity)
            log.debug(f"Quantity {quantity}")
            session.add(orm.Order(customer=user, service=service, quantity=quantity))
            session.commit()
            log.debug("Order.add END")
        else:
            send(socket=socket, data=ERROR)
            log.debug("Wrong id")

    @classmethod
    def delete(cls, socket, session, **kwargs):
        log.debug("Order.delete")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        order = session.query(orm.Order).get(id_)
        if order:
            send(socket=socket, data=GOOD)
            session.delete(order)
            session.commit()
            log.debug(f"Found and deleted ID={id_}")
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def print(cls, socket, session, **kwargs):
        log.debug("Order.print")
        orders = session.query(orm.Order).join(orm.User).join(orm.Service).all()
        table_orders = [
            [
                order.id,
                str(order.service),
                order.customer,
                order.quantity,
                f"${order.service.price * order.quantity}",
            ]
            for order in orders
        ]
        table = tabulate(
            headers=["ID", "Услуга", "Покупатель", "Количество", "Стоимость"],
            tabular_data=table_orders,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        log.debug("Order.print END")

    @classmethod
    def filter(cls, socket, session, **kwargs):
        log.debug("Order.filter")
        id_ = False
        id_max = False
        service = False
        customer = False
        quantity = False
        quantity_max = False
        while True:
            choice = receive(socket=socket)
            log.debug(f"Choice {choice}")
            if choice == "1":
                filter_ = receive(socket=socket)
                obj = loads(filter_)
                id_ = obj["min"]
                id_max = obj["max"]
                log.debug(f"id_ {id_} id_max {id_max}")
            elif choice == "2":
                Service.print(socket=socket, session=session)
                service_id = receive(socket=socket)
                service = session.query(orm.Service).get(service_id)
                log.debug(f"Service {service}")
            elif choice == "3":
                Users.print(socket=socket, session=session)
                customer_id = receive(socket=socket)
                customer = session.query(orm.User).get(customer_id)
                log.debug(f"Customer {customer}")
            elif choice == "4":
                filter_ = receive(socket=socket)
                obj = loads(filter_)
                quantity = obj["min"]
                quantity_max = obj["max"]
                log.debug(f"quantity {quantity} quantity_max {quantity_max}")
            elif choice == "5":
                orders = session.query(orm.Order).join(orm.Service)
                if id_ is not False:
                    print(id_, id_max)
                    orders = orders.filter(orm.Order.id >= id_, orm.Order.id <= id_max)
                    orders = orders.order_by(orm.Order.id.asc())
                if service is not False:
                    orders = orders.filter(orm.Order.service == service)
                if customer is not False:
                    orders = orders.filter(orm.Order.customer == customer)
                if quantity is not False:
                    orders = orders.filter(
                        orm.Order.quantity >= quantity,
                        orm.Order.quantity <= quantity_max,
                    )
                    orders = orders.order_by(orm.Order.quantity.asc())
                table_orders = []
                for order in orders:
                    table_orders.append(
                        [
                            order.id,
                            str(order.service),
                            order.customer,
                            order.quantity,
                            f"${order.service.price * order.quantity}",
                        ]
                    )
                table = tabulate(
                    headers=["ID", "Услуга", "Покупатель", "Количество", "Стоимость"],
                    tabular_data=table_orders,
                    tablefmt=table_format,
                )
                send(socket=socket, data=table)
                log.debug("Filter sent")
            elif choice == BREAK:
                log.debug("Order.filter BREAK")
                break

    @classmethod
    def sort(cls, socket, session, **kwargs):
        log.debug("Order.sort")
        while True:
            choice = receive(socket=socket)
            log.debug(f"Choice {choice}")
            orders = []
            if choice == "1":
                orders = session.query(orm.Order).order_by(orm.Order.id)
            elif choice == "2":
                orders = (
                    session.query(orm.Order)
                    .join(orm.Service)
                    .order_by(orm.Service.name)
                )
            elif choice == "3":
                orders = (
                    session.query(orm.Order).join(orm.User).order_by(orm.User.login)
                )
            elif choice == "4":
                orders = session.query(orm.Order).order_by(orm.Order.quantity)
            elif choice == BREAK:
                log.debug("Order.sort BREAK")
                break
            table_orders = [
                [
                    order.id,
                    str(order.service),
                    order.customer,
                    order.quantity,
                    f"${order.service.price * order.quantity}",
                ]
                for order in orders
            ]
            table = tabulate(
                headers=["ID", "Услуга", "Покупатель", "Количество", "Стоимость"],
                tabular_data=table_orders,
                tablefmt=table_format,
            )
            send(socket=socket, data=table)
            log.debug("Sort sent")


class Users(ManageUsers):
    @classmethod
    def choose(cls, **kwargs):
        choice = receive(socket=kwargs["socket"])
        return choice

    @classmethod
    def add(cls, socket, session, **kwargs):
        log.debug("Users.add")
        while True:
            choice = receive(socket=socket)
            log.debug(f"choice {choice}")
            if choice == BREAK:
                log.debug("Users.add BREAK")
                break
            login = receive(socket=socket)
            user = session.query(orm.User).filter(orm.User.login == login).first()
            if user:
                log.debug("Login already taken")
                send(socket=socket, data=ERROR)
            else:
                log.debug("Login is new")
                send(socket=socket, data=GOOD)
                if choice == "3":
                    position = receive(socket=socket)
                    send(socket=socket, data=GOOD)
                    log.debug(f"Position is {position}")
                    academic_degree = receive(socket=socket)
                    log.debug(f"Academic Degree is {academic_degree}")
                    send(socket=socket, data=GOOD)
                    obj = receive(socket=socket)
                    obj = loads(obj)
                    session.add(
                        orm.User(
                            login=obj["login"],
                            password=obj["password"],
                            permissions=obj["permissions"],
                            position=position,
                            academic_degree=academic_degree,
                        )
                    )
                    session.commit()
                    log.debug("Users.add END")
                    return
                obj = receive(socket=socket)
                obj = loads(obj)
                session.add(
                    orm.User(
                        login=obj["login"],
                        password=obj["password"],
                        permissions=obj["permissions"],
                    )
                )
                session.commit()
                log.debug("Users.add END")

    @classmethod
    def delete(cls, socket, session, **kwargs):
        log.debug("Users.delete")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        user = session.query(orm.User).get(id_)
        if user:
            send(socket=socket, data=GOOD)
            session.delete(user)
            session.commit()
            log.debug(f"Found and deleted ID={id_}")
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def change_password(cls, socket, session, user):
        log.debug("Users.change_password")
        new_password = receive(socket=socket)
        if new_password == user.password:
            send(socket=socket, data=ERROR)
            log.debug("Same password")
        else:
            send(socket=socket, data=GOOD)
            user.password = new_password
            session.commit()
            log.debug("Users.change_password END")

    @classmethod
    def print(cls, socket, session, **kwargs):
        log.debug("Users.print")
        users = session.query(orm.User).all()
        table_users = []
        for user in users:
            permissions = ""
            if user.permissions == "admin":
                permissions = "Администратор"
            elif user.permissions == "expert":
                permissions = "Эксперт"
            elif user.permissions == "default":
                permissions = "Покупатель"
            table_users.append([user.id, permissions, user.login, user.password])
        table = tabulate(
            headers=["ID", "Права", "Логин", "Пароль"],
            tabular_data=table_users,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        log.debug("Users.print END")


class Company(ManageData):
    @classmethod
    def menu(cls, **kwargs):
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
        choice = receive(socket=kwargs["socket"])
        return choice

    @classmethod
    def add(cls, socket, session):
        log.debug("Company.add")
        name = receive(socket=socket)
        company = session.query(orm.Company).filter(orm.Company.name == name)
        if company.first():
            log.debug("company name already taken")
            send(socket=socket, data=ERROR)
        else:
            log.debug("company name is new")
            send(socket=socket, data=GOOD)
            session.add(orm.Company(name=name))
            session.commit()
            log.debug("Company.add END")

    @classmethod
    def delete(cls, socket, session):
        log.debug("Company.delete")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        company = session.query(orm.Company).get(id_)
        if company:
            send(socket=socket, data=GOOD)
            session.delete(company)
            session.commit()
            log.debug(f"Found and deleted ID={id_}")
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def edit(cls, socket, session):
        log.debug("Company.edit")
        cls.print(socket=socket, session=session)
        id_ = receive(socket=socket)
        company = session.query(orm.Company).get(id_)
        if company:
            send(socket=socket, data=GOOD)
            log.debug(f"ID={id_} found")
            while True:
                choice = receive(socket=socket)
                if choice == "1":
                    change_ = receive(socket=socket)
                    log.debug(f"Changing name to {change_}")
                    company.name = change_
                    session.commit()
                elif choice == BREAK:
                    log.debug("Company.edit BREAK")
                    session.commit()
                    break
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def print(cls, socket, session):
        log.debug("Company.print")
        companies = session.query(orm.Company)
        table_companies = []
        for company in companies:
            services_quantity = len(company.services)
            table_companies.append([company.id, company.name, services_quantity])
        log.debug(f"Table companies {table_companies}")
        table = tabulate(
            headers=["ID", "Название", "Количество услуг"],
            tabular_data=table_companies,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        log.debug("Company.print END")

    @classmethod
    def sort(cls, socket, session):
        log.debug("Company.sort")
        while True:
            choice = receive(socket=socket)
            companies = []
            if choice == "1":
                companies = session.query(orm.Company).order_by(orm.Company.id)
            elif choice == "2":
                companies = session.query(orm.Company).order_by(orm.Company.name)
            elif choice == "3":
                companies = session.query(orm.Company)
                companies = sorted(
                    companies, key=lambda company: len(company.services), reverse=True
                )
            elif choice == BREAK:
                log.debug("Services.sort BREAK")
                break
            table_companies = []
            for company in companies:
                services_quantity = len(company.services)
                table_companies.append([company.id, company.name, services_quantity])
            table = tabulate(
                headers=["ID", "Название", "Количество услуг"],
                tabular_data=table_companies,
                tablefmt=table_format,
            )
            send(socket=socket, data=table)
            log.debug("Sort sent")


class Problems(ManageProblems):
    @classmethod
    def choose(cls, **kwargs):
        choice = receive(socket=kwargs["socket"])
        return choice

    @classmethod
    def add(cls, socket, session, user, **kwargs):
        log.debug("Problems.add")
        experts = session.query(orm.User).filter(orm.User.permissions == "expert")
        if not experts.all():
            send(socket=socket, data=ERROR)
            log.debug("No experts")
            return
        else:
            send(socket=socket, data=GOOD)
            log.debug("Experts found")
        obj = receive(socket=socket)
        obj = loads(obj)
        log.debug(f"Got obj {obj}")
        problem = orm.Problem(description=obj["description"], creator=user)
        for decision in obj["decisions"]:
            decision_ = orm.Decision(description=decision, problem=problem)
            session.add(decision_)
        log.debug("Created decisions")
        for expert in experts:
            left_to_vote = orm.LeftToVote(problem=problem, voter=expert)
            session.add(left_to_vote)
        log.debug(f"Created leftToVotes")
        session.add(problem)
        session.commit()
        log.debug("Problems.add END")

    @classmethod
    def print(cls, socket, session, user, **kwargs):
        log.debug("Problems.print")
        choice = receive(socket=socket)
        table_problems = []
        if choice == "1":
            problems = (
                session.query(orm.Problem)
                .filter(
                    orm.Problem.creator == user,
                    orm.Problem.status == Status.waiting.value,
                )
                .all()
            )
            table_problems = []
            for problem in problems:
                table_problems.append(
                    [
                        problem.id,
                        problem.creator.login,
                        problem.description,
                        problem.status,
                    ]
                )
            table = tabulate(
                headers=["ID", "Автор", "Описание", "Статус"],
                tabular_data=table_problems,
                tablefmt=table_format,
            )
            send(socket=socket, data=table)
            log.debug("Problems.print END")
        elif choice == "2":
            problems = (
                session.query(orm.Problem)
                .filter(
                    orm.Problem.creator == user,
                    orm.Problem.status == Status.decided.value,
                )
                .all()
            )
            table_problems = []
            for problem in problems:
                table_problems.append(
                    [
                        problem.id,
                        problem.creator.login,
                        problem.description,
                        problem.status,
                    ]
                )
            table = tabulate(
                headers=["ID", "Автор", "Описание", "Статус"],
                tabular_data=table_problems,
                tablefmt=table_format,
            )
            send(socket=socket, data=table)
            log.debug("Problems.print END")
            problem_id = receive(socket=socket)
            problem = (
                session.query(orm.Problem)
                .filter(
                    orm.Problem.creator == user,
                    orm.Problem.status == Status.decided.value,
                    orm.Problem.id == problem_id,
                )
                .first()
            )
            if not problem:
                log.debug("Problem not fount")
                send(socket=socket, data=ERROR)
                return
            send(socket=socket, data=GOOD)
            decisions = problem.decisions
            experts = session.query(orm.User).filter(orm.User.permissions == "expert")
            headers = ["Эксперты"] + [decision.description for decision in decisions]
            competence_sum = sum(
                [find_competence_assessment(expert) for expert in experts]
            )
            lines = []

            for expert in experts:
                line = [expert.login]
                for decision in decisions:
                    vote = (
                        session.query(orm.Vote)
                        .filter(orm.Vote.decision == decision, orm.Vote.voter == expert)
                        .first()
                    )
                    line.append(vote.decision_weigth)
                lines.append(line)
            final_line = ["Веса решений"]
            for decision in decisions:
                result_weight = 0
                votes = (
                    session.query(orm.Vote).filter(orm.Vote.decision == decision).all()
                )
                for vote in votes:
                    weight = (
                        vote.voter.get_relative_competence(competence_sum)
                        * vote.decision_weigth
                    )
                    result_weight += weight
                    final_line.append(result_weight)
            lines.append(final_line)

            table = tabulate(headers=headers, tabular_data=lines, tablefmt=table_format)
            send(socket=socket, data=table)

    @classmethod
    def delete(cls, socket, session, user, **kwargs):
        log.debug("Problems.delete")
        cls.print(socket=socket, session=session, user=user)
        id_ = receive(socket=socket)
        problem = session.query(orm.Problem).get(id_)
        if problem:
            send(socket=socket, data=GOOD)
            session.delete(problem)
            session.commit()
            log.debug(f"Found and deleted ID={id_}")
        else:
            send(socket=socket, data=ERROR)
            log.debug("ID not found")

    @classmethod
    def vote(cls, socket, session, user):
        pass
        log.debug("Problems.vote")
        problems = session.query(orm.Problem).join(orm.LeftToVote).join(orm.User)
        problems = problems.filter(orm.LeftToVote.voter == user)
        table_problems = []
        for problem in problems:
            table_problems.append(
                [problem.id, problem.creator.login, problem.description, problem.status]
            )
        table = tabulate(
            headers=["ID", "Автор", "Описание", "Статус"],
            tabular_data=table_problems,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
        problem_id = receive(socket=socket)
        problem = problems.filter(orm.Problem.id == int(problem_id)).first()
        if not problem:
            send(socket=socket, data=ERROR)
            log.debug("Problem is not exist")
            return
        decisions = problem.decisions
        send(socket=socket, data=cls.parse_decisions(decisions))
        assessments = loads(receive(socket=socket))
        sum_om_assessments = sum(assessments.values())
        for id in assessments:
            decision_weigth = round(assessments[id] / sum_om_assessments, 2)
            decision = (
                session.query(orm.Decision).filter(orm.Decision.id == int(id)).first()
            )
            vote = orm.Vote(
                voter=user,
                decision_weigth=decision_weigth,
                decision=decision,
                decision_assessment=assessments[id],
            )

            session.add(vote)
        left_to_vote = (
            session.query(orm.LeftToVote)
            .filter(orm.LeftToVote.voter == user, orm.LeftToVote.problem == problem)
            .first()
        )
        exist_left_to_vote = (
            session.query(orm.LeftToVote)
            .filter(orm.LeftToVote.problem == problem)
            .all()
        )
        if len(exist_left_to_vote) <= 1:
            log.debug("Left to vote dont exist")
            problem.status = Status.decided.value
            session.add(problem)
        session.delete(left_to_vote)
        session.commit()

    @classmethod
    def parse_decisions(cls, decisions):
        obj = {}
        for decision in decisions:
            obj[decision.id] = decision.description
        return obj

    @classmethod
    def print_voted(cls, socket, session, user):
        votes = session.query(orm.Vote).filter(orm.Vote.voter == user)
        problems = []
        for vote in votes:
            problem = vote.decision.problem
            if problem not in problems:
                problems.append(problem)
        table_problems = []
        for problem in problems:
            problem_decisions = problem.decisions
            votes_string = ""
            for problem_decision in problem_decisions:
                vote = (
                    session.query(orm.Vote)
                    .filter(
                        orm.Vote.decision == problem_decision, orm.Vote.voter == user
                    )
                    .first()
                )
                if vote:
                    votes_string += (
                        str(problem_decision.id) + f": {vote.decision_assessment}\n"
                    )
            table_problems.append(
                [
                    problem.id,
                    problem.creator.login,
                    problem.description,
                    votes_string,
                    problem.status,
                ]
            )

        table = tabulate(
            headers=["ID", "Автор", "Описание", "Оценка решениям", "Статус"],
            tabular_data=table_problems,
            tablefmt=table_format,
        )
        send(socket=socket, data=table)
