"""Main project module"""
import argparse

from courseapp.client.client import Client
from courseapp.config import version
from courseapp.server.server import Server
from courseapp.utils import create_logger

log = create_logger()


class App:
    def __init__(self):
        self.parser = App.init_parser()
        self.args = self.parser.parse_args()

    @staticmethod
    def init_parser():
        parser = argparse.ArgumentParser(
            add_help=False,
        )
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=argparse.SUPPRESS,
            help="Вывод справки по аргументам",
        )
        parser.add_argument(
            "--version",
            help="Вывод версии приложения",
            action="version",
            version=f"client-server v{version}",
        )
        parser.add_argument(
            "-s", "--server", help="Запуск сервера", action="store_true"
        )
        parser.add_argument(
            "-c", "--client", help="Запуск клиента", action="store_true"
        )
        return parser

    def start(self):
        log.debug("App.start")
        if self.args.server:
            log.debug("Starting server")
            server = Server()
            server.start()
        elif self.args.client:
            try:
                log.debug("Starting client")
                client = Client()
                client.start()
            except Exception as e:
                print(f"Ошибка подключения {e}")
        else:
            print("Недостаточно аргументов")
            self.parser.print_help()


def main():
    app = App()
    app.start()


if __name__ == "__main__":
    main()
