from utils.helper import PROJECT_PATH_NAME
from logging import config
import logging
import yaml
import time


TRACE_LOG = "tracelogger"
ERROR_LOG = "errorlogger"


def load_logger():
    with open(f"{PROJECT_PATH_NAME}/config/logger.yml", 'r', encoding="utf-8")as f:
        logging_yaml = yaml.load(stream=f, Loader=yaml.FullLoader)
        config.dictConfig(config=logging_yaml)
        return logging_yaml


def get_trace_logger():
    return logging.getLogger(TRACE_LOG)


def get_error_logger():
    return logging.getLogger(ERROR_LOG)


def get_out_logger():
    return logging.getLogger()


class TraceLogger:
    def __init__(self, name, request, doc):
        self.name = name
        self.req = request
        self.start_time = 0
        self.end_time = 0
        self.gap = 0
        self.doc = doc

    def start(self):
        self.start_time = time.time()

    def end(self):
        self.end_time = time.time()
        self.gap = self.end_time - self.start_time

    def end_log(self):
        self.end()
        self.log()

    def log(self):
        get_trace_logger()\
            .info(f"{self.name}, cost: {self.gap}, from: {self.req.ip}, "
                  f"args: {self.req.args}, data: {self.doc}, "
                  f"agent: {self.req.headers}")

