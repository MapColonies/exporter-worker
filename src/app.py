from src.taskHandler import TaskHandler
from log.logger import Logger
from src.config import read_config


class App:
    def __init__(self):
        self.__config = read_config()
        self.logger = Logger()
        self.__taskHandler = TaskHandler()

    def _start_service(self):
        self.logger.info(f'Service is listening to broker: {self.__config["kafka"]["host_ip"]},'f' topic: {self.__config["kafka"]["topic"]}')
        try:
            self.__taskHandler.handle_tasks()
        except Exception as e:
            self.logger.error(f'Error occurred during running service: {e}')


App()._start_service()
