from os import path
from src.taskHandler import TaskHandler
from logger.jsonLogger import Logger
from src.helper import Helper
from src.config import read_json
import src.probe as probe
import threading


class Main:
    def __init__(self):
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)

        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.__taskHandler = TaskHandler()
        probe.readiness = True
        probe.liveness = True

    def _start_service(self):
        self.log.info(
            f'Service is listening to broker: {self.__config["kafka"]["host_ip"]},'f' topic: {self.__config["kafka"]["topic"]}')
        try:
            self.__helper.create_folder_if_not_exists(
                self.__config["fs"]["internal_outputs_path"])
            keys = ("fs", "external_physical_path")
            self.__helper.valid_configuration(keys)
            self.__taskHandler.handle_tasks()
        except Exception as e:
            self.log.error(f'Error occurred during running service: {e}')
            probe.liveness = False


service_thread = threading.Thread(target=Main()._start_service)
service_thread.start()
probe.start()
