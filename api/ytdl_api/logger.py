"""
Logging configuratio utiities
"""
import logging
from pathlib import Path
from typing import Union


def get_logger(logger_name: str = "ytdl") -> logging.Logger:
    """
    Returns app's default logger.

    :param logger_name: name of the logger defined in
    configuration file.
    """
    return logging.getLogger(logger_name)


log = get_logger()


class YDLLogger:
    def debug(self, msg):
        log.debug(msg)

    def warning(self, msg):
        log.warning(msg)

    def error(self, msg):
        log.error(msg)
