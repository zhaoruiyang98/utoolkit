from __future__ import annotations
import logging
from logging import Formatter
from logging import Logger


class LoggedError(Exception):
    def __init__(self, logger: str | Logger, *args, **kwargs) -> None:
        if isinstance(logger, str):
            logger = get_logger(logger)
        if not isinstance(logger, Logger):
            raise TypeError("logger must be a Logger instance or a string")
        if args:
            logger.error(*args, **kwargs)
        msg = args[0] if args else ""
        if msg and len(args) > 1:
            msg = msg % args[1:]
        super().__init__(msg)


class CustomFormatter(Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629"""

    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt: str = "%(levelname)-8s: %(message)s"):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.blue + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(name: str) -> Logger:
    if name.startswith('utoolkit.'):
        name = name.split('.')[-1]
    return logging.getLogger(name)


def setup_logging(level: int = logging.WARNING) -> None:
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(CustomFormatter())
    stdout_handler.setLevel(level)
    logging.basicConfig(level=level, handlers=[stdout_handler])


class HasLogger:
    def set_logger(self, name: str | None = None) -> None:
        if name is None:
            name = self.__class__.__name__
        self.log = get_logger(name)
