import json
from src.config import read_config


class Helper:
    def __init__(self):
        self.__config = read_config()

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
