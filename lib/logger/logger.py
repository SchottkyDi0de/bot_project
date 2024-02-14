from os import mkdir, path

import logging

def get_logger(python_name: str, logger_name: str, file_name: str):
    """
    Creates and configures a logger with the specified name and settings.

    Args:
        python_name (str): The name of the Python module or script.
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
    _file_handler = logging.FileHandler(file_name)
    _console_handler.setLevel(logging.DEBUG)
    _file_handler.setLevel(logging.INFO)
    _log_format = f'~ [LINE:%(lineno)d]# |%(levelname)-8s| [%(asctime)s] in {python_name}:\n>>> %(message)s '
    _formatter = logging.Formatter(_log_format)
    _console_handler.setFormatter(_formatter)
    _file_handler.setFormatter(_formatter)
    logger.addHandler(_console_handler)
    logger.addHandler(_file_handler)
    return logger