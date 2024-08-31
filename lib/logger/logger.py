import logging
from os import mkdir, path

import yaml

with open ('settings/logger_config.yaml', 'r') as f:
    _config = yaml.safe_load(f)

def get_logger(module_path: str, logger_name: str, file_path: str):
    """
    Creates and configures a logger with the specified name and settings.

    Args:
        module_path (str): __file__ attribute of the module.
        logger_name (str): The name of the logger.
        file_name (str): The name of the log file.

    Returns:
        logging.Logger: The configured logger object.
    """
    if not path.exists('logs'):
        mkdir('logs')

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    _console_handler = logging.StreamHandler()
    _file_handler = logging.FileHandler(file_path)
    _console_handler.setLevel(getattr(logging, _config['log_levels']['console']))
    _file_handler.setLevel(getattr(logging, _config['log_levels']['file']))
    _log_format = f'~ |%(levelname)-8s| [%(asctime)s] in {module_path}:%(lineno)d\n>>> %(message)s '
    _formatter = logging.Formatter(_log_format)
    _console_handler.setFormatter(_formatter)
    _file_handler.setFormatter(_formatter)
    logger.addHandler(_console_handler)
    logger.addHandler(_file_handler)
    return logger