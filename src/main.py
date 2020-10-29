from src.taskHandler import TaskHandler
from log.logger import Logger
from src.helper import Helper
from src.config import read_config
import src.probe as probe
import threading


class Main:
    def __init__(self):
        self.__config = read_config()
        self.logger = Logger()
        self.__helper = Helper()
        self.__taskHandler = TaskHandler()
        probe.readiness = True
        probe.liveness = True


    def _start_service(self):
        self.logger.info(f'Service is listening to broker: {self.__config["kafka"]["host_ip"]},'f' topic: {self.__config["kafka"]["topic"]}')
        try:
            keys = ("input_output", "shared_folder")
            self.__helper.valid_configuration(keys)
            self.__taskHandler.handle_tasks()
        except Exception as e:
            self.logger.error(f'Error occurred during running service: {e}')
            probe.liveness = False


service_thread = threading.Thread(target=Main()._start_service)
service_thread.start()
probe.start()


