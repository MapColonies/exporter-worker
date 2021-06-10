from os import path
from src.handler import Handler
from logger.jsonLogger import Logger
from src.helper import Helper
from src.config import read_json
import src.probe as probe
import threading
import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
import nest_asyncio
from multiprocessing import Process

class Main:
    def __init__(self):
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)
        self.loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self.loop)
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.__taskHandler = Handler(self.loop)
        probe.readiness = True
        probe.liveness = True

    def _start_service(self):
        self.log.info(f'Service is listening')
        try:
            self.__helper.create_folder_if_not_exists(
                self.__config["fs"]["internal_outputs_path"])
            keys = ("fs", "external_physical_path")
            self.__helper.valid_configuration(keys)
            self.loop.run_until_complete(self.__taskHandler.handle_tasks())
        except Exception as e:
            self.log.error(f'Error occurred during running service: {e}')
            probe.liveness = False
        finally:
            self.loop.close()

# create thread for app entrypoint
service_thread = threading.Thread(target=Main()._start_service)
service_thread.start()
# start worker probe (liveness & readiness)
probe.start()

