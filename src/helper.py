import json


class Helper:
    def load_json(self, task):
        parsed_json = json.loads(task.value)
        return parsed_json
