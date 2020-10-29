from os import mkdir
import json
from src.config import read_config
from log.logger import Logger
import requests
from datetime import datetime


class Helper:
    def __init__(self):
        self.__config = read_config()
        self.logger = Logger()
        self.index = self.__config["es"]["index"]
        self.hostip = self.__config["es"]["host_ip"]
        self.port = self.__config["es"]["port"]

    def load_json(self, task):
        parsed_json = json.loads(task)
        return parsed_json

    def json_fields_validate(self, json_obj):
        try:
            task_fields = self.__config['task_fields']
            for field in task_fields:
                if field not in json_obj:
                    raise ValueError(f'Missing field "{field}"')
        except Exception as e:
            raise ValueError(f"Json validation failed: {e}")

    def save_update(self, taskId, status, lastUpdateTime, fileName, progress=None, link=None):
        url = f'http://{self.hostip}:{self.port}/indexes/{self.index}/document?taskId={taskId}'
        doc = {
            "taskId": taskId,
            "status": status,
            "lastUpdateTime": lastUpdateTime,
            "fileName": fileName
        }
        if progress is not None:
            doc["progress"] = progress
        if link is not None:
            doc["link"] = link

        try:
            headers = {"Content-Type": "application/json"}

            self.logger.info(f'Task Id "{taskId}" Updating database')

            requests.post(url=url, data=json.dumps(doc, default=self.json_converter), headers=headers)
        except ConnectionError as ce:
            self.logger.error(f'Database connection failed: {ce}')
        except Exception as e:
            self.logger.error(f'Task Id "{taskId}" Failed to update database: {e}')

    def json_converter(self, field):
        if isinstance(field, datetime):
            return field.isoformat()


    def valid_configuration(self, keys):
        value = self.__config[keys[0]][keys[1]]
        if value:
            self.logger.info(f'{keys[1]} is set to {value}')
        else:
            raise ValueError(f'Bad Configuration - no value for {keys[1]} variable.')

    def create_folder_if_not_exists(self, path):
        try:
            mkdir(path)
        except OSError as e:
            self.logger.error(f'Creation of the directory {path} failed: {e}')
        else:
            self.logger.info(f'Successfully created the directory {path}')

