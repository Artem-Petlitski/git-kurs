"""Server's main module"""
import logging as log
import socket
import threading

from courseapp.server.model import User
from courseapp.server.orm import Session_maker


class ConnectionHandler:
    def __init__(self, connection, address):
        self.socket = connection
        self.address = address
        self.session = Session_maker()

    def __del__(self):
        self.session.close()

    def handle(self):
        user = User(self.socket, self.session)
        user.main_menu()


class Server:
    def __init__(self):
        self.address = ("localhost", 1270)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(self.address)

    @staticmethod
    def new_connection(connection, address):
        handler = ConnectionHandler(connection, address)
        handler.handle()
        log.debug(f"{address} connection ended")

    def start(self):
        log.debug("Listening")
        self.socket.listen(10)
        while True:
            connection, address = self.socket.accept()
            log.debug(f"New connection from {address}")
            thread = threading.Thread(
                target=self.new_connection, args=(connection, address)
            )
            thread.daemon = True
            thread.start()
