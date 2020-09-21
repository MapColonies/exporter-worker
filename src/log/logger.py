import logging
from os import path
import json
from sys import stdout


class Logger:
    def __init__(self):
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../../confd/config/default.json')
        with open(config_path, encoding='utf-8') as config_file:
            self.__config = json.loads(config_file.read())

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
