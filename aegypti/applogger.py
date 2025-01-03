import logging

class Logger:
    """
    A wrapper class for a logger object.
    """

    def __init__(self, logger):
        """
        Initializes the SatLogger with a logger object.

        Args:
            logger (logging.Logger): The underlying logger object to be used.
        """
        self.logger = logger

    def info(self, msg, *args, **kwargs):
        """
        Logs an informational message using the underlying logger.

        Args:
            msg (str): The message to be logged.
            *args: Additional arguments to be passed to the underlying logger's info method.
            **kwargs: Additional keyword arguments to be passed to the underlying logger's info method.
        """
        self.logger.info(msg, *args, **kwargs)

class ConsoleLogger:
    """
    A simple logger class that logs to the console when enabled.
    """

    def __init__(self, log_enabled=True):
        """
        Initializes the ConsoleLogger with an optional flag for enabling logging.

        Args:
            log_enabled (bool, optional): Flag to enable or disable console logging. Defaults to True.
        """
        self.log_enabled = log_enabled

    def info(self, msg, *args, **kwargs):
        """
        Logs a message to the console if enabled.

        Args:
            msg (str): The message to be logged.
            *args: Additional arguments to be formatted with the message.
            **kwargs: Additional keyword arguments (ignored for console logging).
        """

        if self.log_enabled:
            print(msg.format(*args))  # Use f-strings or format method for cleaner formatting

class FileLogger:
    """
    A simple logger class that logs to a file.
    """

    def __init__(self, log_file="app.log", log_level=logging.INFO):
        """
        Initializes the FileLogger with an optional log file name and log level.

        Args:
            log_file (str, optional): The filename of the log file. Defaults to "app.log".
            log_level (int, optional): The logging level. Defaults to logging.INFO.
        """
        logging.basicConfig(filename=log_file, level=log_level, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def info(self, msg, *args, **kwargs):
        """
        Logs an informational message to the file.

        Args:
            msg (str): The message to be logged.
            *args: Additional arguments to be formatted with the message.
            **kwargs: Additional keyword arguments (ignored for file logging).
        """
        self.logger.info(msg.format(*args))