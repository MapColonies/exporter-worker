import json
from src.config import read_config
from log.logger import Logger
import requests


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

    def update_db(self, doc):
        url = f'http://{self.hostip}:{self.port}/indexes/{self.index}/document?taskId={doc["params"]["taskId"]}'
        try:
            headers = {"Content-Type": "application/json"}

            self.logger.info(f'Task Id "{doc["params"]["taskId"]}" Updating database')
            requests.post(url=url, data=json.dumps(doc), headers=headers)
        except ConnectionError as ce:
            self.logger.error(f'Database connection failed: {ce}')
        except Exception as e:
            self.logger.error(f'Task Id "{doc["params"]["taskId"]}" Failed to update database: {e}')
