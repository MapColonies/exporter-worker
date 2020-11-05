from os import mkdir, path
import json
from src.config import read_config
from log.logger import Logger
import requests
from datetime import datetime


class Helper:
    def __init__(self):
        self.__config = read_config()
        self.logger = Logger()
        self.url = self.__config["commonstorage"]["url"]

    def load_json(self, task):
        parsed_json = json.loads(task)
        return parsed_json

    def json_fields_validate(self, json_obj):
        try:
            task_fields = self.__config['mandatory_task_fields']
            for field in task_fields:
                if field not in json_obj:
                    raise ValueError(f'Missing field "{field}"')
        except Exception as e:
            raise ValueError(f"Json validation failed: {e}")

    def save_update(self, taskId, status, fileName, progress=None, fullPath=None):
        updated_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        url = f'{self.url}/statuses'
        
        doc = {
            "taskId": taskId,
            "status": status,
            "updatedTime": updated_time,
            "fileName": fileName
        }
        if progress is not None:
            doc["progress"] = progress
        if fullPath is not None:
            file_size = path.getsize(fullPath)
            actual_size = self._convert_and_round_filesize(file_size)
            doc["fileURI"] = fullPath
            doc["realFileSize"] = actual_size
        try:
            headers = {"Content-Type": "application/json"}
            self.logger.info(f'Task Id "{taskId}" Updating database: {doc}')

            requests.put(url=url, data=json.dumps(doc), headers=headers)
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

    def create_folder_if_not_exists(self, dirPath):
        try:
            if path.isdir(dirPath) is False:
                mkdir(dirPath)
                self.logger.info(f'Successfully created the directory {dirPath}')
        except OSError as e:
            self.logger.error(f'Failed to create the directory {dirPath}: {e}')

    def _convert_and_round_filesize(self, filesize):
        # convert the real filesize from bytes to mb
        actual_size_mb = filesize / (1 << 20)
        # round up the converted number
        rounded_size = round(actual_size_mb + 0.005, 2)
        return rounded_size
