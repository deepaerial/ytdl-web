"""
Logging configuratio utiities
"""
import logging
from pathlib import Path
from typing import Union

import yaml


def setup_logging(config_path: Union[str, Path], log_level=logging.INFO):
    """
    Setup logging configuration.

    :param config_path: path to logging config file.
    :param log_level: log level for logger.
    """
    if isinstance(config_path, str):
        config_path = Path(config_path)
    if config_path.is_file():
        with config_path.open(mode="rt") as f:
            try:
                config = yaml.safe_load(f.read())
            except (IOError, OSError) as e:
                print(e)
        logging.config.dictConfig(config)
    else:
        logging.warning(
            f"Config {config_path.absolute()} not loaded...fallback to basic config..."
        )
        logging.basicConfig(level=log_level)


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
