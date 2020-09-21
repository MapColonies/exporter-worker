from src.TaskHandler import TaskHandler
from src.log.logger import Logger
from os import path
import json


class App:
    def __init__(self):
        self.__taskHandler = TaskHandler()
        self.logger = Logger()

        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../confd/config/default.json')
        with open(config_path, encoding='utf-8') as config_file:
            self.__config = json.loads(config_file.read())

    def _start_service(self):
        self.logger.info(f'Service is listening to broker: {self.__config["kafka"]["host_ip"]},'f' topic: {self.__config["kafka"]["topic"]}')
        try:
            self.__taskHandler.handle_tasks()
        except Exception as e:
            self.logger.error(f'Error occurred during running service: {e}')


App()._start_service()
