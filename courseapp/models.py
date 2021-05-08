"""Models for data management"""
from abc import ABC, abstractmethod


class ManageEvaluation:
    @classmethod
    def choose(cls, **kwargs):
        return True

    @classmethod
    def menu(cls, **kwargs):
        """Шаблонныйы метод"""
        while True:
            choice = cls.choose(**kwargs)
            if choice == "1":
                cls.evaluate(**kwargs)
            elif choice == "2":
                cls.print(**kwargs)
            elif choice == "3":
                cls.print_raiting(**kwargs)
            elif choice == "4":
                break


class ManageData(ABC):
    @classmethod
    def choose(cls, **kwargs):
        return True

    @classmethod
    def menu(cls, **kwargs):
        """Шаблонныйы метод"""
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
                cls.filter(**kwargs)
            elif choice == "6":
                cls.sort(**kwargs)
            elif choice == "7":
                break

    @classmethod
    @abstractmethod
    def add(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def edit(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def print(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def filter(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def sort(cls, **kwargs):
        pass


class ManageUsers(ABC):
    @classmethod
    @abstractmethod
    def choose(cls, **kwargs):
        return True

    @classmethod
    @abstractmethod
    def menu(cls, **kwargs):
        """Шаблонныйы метод"""
        while True:
            choice = cls.choose(**kwargs)
            if choice == "1":
                cls.add(**kwargs)
            elif choice == "2":
                cls.delete(**kwargs)
            elif choice == "3":
                cls.change_password(**kwargs)
            elif choice == "4":
                cls.print(**kwargs)
            elif choice == "5":
                break

    @classmethod
    @abstractmethod
    def add(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def change_password(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def print(cls, **kwargs):
        pass


class ManageOrder(ABC):
    @classmethod
    @abstractmethod
    def choose(cls, **kwargs):
        return True

    @classmethod
    @abstractmethod
    def menu(cls, **kwargs):
        """Шаблонныйы метод"""
        while True:
            choice = cls.choose(**kwargs)
            if choice == "1":
                cls.print(**kwargs)
            elif choice == "2":
                cls.delete(**kwargs)
            elif choice == "3":
                cls.filter(**kwargs)
            elif choice == "4":
                cls.sort(**kwargs)
            elif choice == "5":
                break

    @classmethod
    @abstractmethod
    def add(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def print(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def filter(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def sort(cls, **kwargs):
        pass


class ManageProblems(ABC):
    @classmethod
    @abstractmethod
    def choose(cls, **kwargs):
        return True

    @classmethod
    @abstractmethod
    def menu(cls, **kwargs):
        """Шаблонныйы метод"""
        while True:
            choice = cls.choose(**kwargs)
            if choice == "1":
                cls.add(**kwargs)
            elif choice == "2":
                cls.print(**kwargs)
            elif choice == "3":
                cls.delete(**kwargs)
            elif choice == "4":
                break

    @classmethod
    @abstractmethod
    def add(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def print(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def delete(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def vote(cls, **kwargs):
        pass

    @classmethod
    @abstractmethod
    def print_voted(cls, **kwargs):
        pass
