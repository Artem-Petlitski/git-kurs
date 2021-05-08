"""Client's main module"""
import socket

from courseapp.client.models import User


class Client:
    def __init__(self):
        self.server = ("localhost", 1270)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect(self.server)

    def start(self):
        User.login(self.socket)
