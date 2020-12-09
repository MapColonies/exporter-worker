import json
from os import path


def read_json(json_path):
    try:
        if path.exists(json_path):
            with open(json_path, encoding='utf-8') as json_file:
                _json = json.loads(json_file.read())
                return _json
        else:
            raise FileNotFoundError(f"Configure file not found: {json_path}")
    except Exception as e:
        raise e
