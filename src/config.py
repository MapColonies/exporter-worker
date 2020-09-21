import json
from os import path


def read_config():
    try:
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../confd/config/default.json')
        if path.exists(config_path):
            with open(config_path, encoding='utf-8') as config_file:
                _config = json.loads(config_file.read())
                return _config
        else:
            raise FileNotFoundError(f"Configure file not found: {config_path}")
    except Exception as e:
        raise e
