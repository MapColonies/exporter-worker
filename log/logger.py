import logging
from sys import stdout
from src.config import read_config


class Logger:
    def __init__(self):
        self.__config = read_config()

        logging.basicConfig(level=self.__config['logger']['level'],
                            filename=self.__config['logger']['filename'],
                            datefmt=self.__config['logger']['date_format'],
                            format=self.__config['logger']['format'])
        self.log = logging.getLogger(__name__)
        self._create_file_handler()

    def _create_file_handler(self):
        if self.log.handlers:
            self.log.handlers = []
        file_handle = logging.FileHandler(self.__config['logger']['filename'])
        file_handle.setStream(stdout)
        file_handle.setFormatter(logging.Formatter(self.__config['logger']['format']))
        self.log.addHandler(file_handle)

    def warning(self, msg):
        self.log.warning(msg)

    def info(self, msg):
        self.log.info(msg)

    def error(self, error):
        self.log.error(error)

    def debug(self, msg):
        self.log.debug(msg)
