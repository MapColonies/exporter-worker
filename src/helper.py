import json
from jsonschema import validate
from src.model.schema.taskSchema import schema


class Helper:
    def load_json(self, task):
        parsed_json = json.loads(task.value)
        return parsed_json

    def json_fields_validate(self, json_obj):
        try:
            validate(json_obj, schema)
        except Exception as e:
            raise ValueError(f"Json validation failed: {e}")
