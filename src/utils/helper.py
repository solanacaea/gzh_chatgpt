import socket
import os

SERVER_FORMAT = "{}://{}:{}"
PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_PATH_NAME = os.path.dirname(os.path.dirname(PROJECT_PATH))


def get_hostname():
    return socket.gethostname()


def get_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        if s is not None:
            s.close()
    return ip
