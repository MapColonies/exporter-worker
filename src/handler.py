from os import path
from src.exportImage import ExportImage
from src.helper import Helper
from logger.jsonLogger import Logger
from src.config import read_json
from pyority_queue.task_handler import *


class Handler:
    def __init__(self, asyncio_event_loop):
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.loop = asyncio_event_loop
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)
        self.queue_handler = TaskHandler(self.__config["server"]["job_type"], self.__config["server"]["task_type"],
                                         self.__config["server"]["job_manager_url"], self.__config["server"]["heartbeat_manager_url"],
                                         self.__config["server"]["heartbeat_interval_ms"], self.log)
        self.__exportImage = ExportImage(self.queue_handler, self.loop)

    async def handle_tasks(self):
        try:
            while True:
                task = await self.queue_handler.dequeue(5)
                if task:
                    await self.execute_task(task)
        except Exception as e:
            self.log.error(f'Error occurred consuming: {e}.')

    async def execute_task(self, task_values):
        try:
            # get the job's and task's id/status/attempts from the consumed task
            job_id = task_values['jobId']
            task_id = task_values['id']
            status = task_values['status']
            attempts = task_values['attempts']

            self.log.info(f'Task Id "{task_id}" received.')

            # get and validate the export params from the consumed task
            parameters = task_values['parameters']
            self.__helper.json_fields_validate(parameters)
            bbox = parameters['bbox']
            filename = parameters['fileName']
            url = parameters['url']
            directory_name = parameters['directoryName']
            max_zoom = parameters['maxZoom']

            # send the consumed task to work
            return await self.__exportImage.export(bbox, filename, url, task_id,
                                                   job_id, directory_name, max_zoom, status, attempts)
        except Exception as e:
            self.log.error(f'Error occurred while exporting: {e}.')
