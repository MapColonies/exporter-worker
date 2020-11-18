from jsonlogger.logger import JSONLogger
from src.config import read_config
config = read_config()



class Logger:
    instance = None

    @staticmethod
    def __get_instance():
        return JSONLogger('main-info', config={'handlers': {'file': {'filename': config['logger']['filename'],
                                                                     'backupCount': config['logger']['backup_count'],
                                                                     'maxBytes': config['logger']['max_bytes']}}},
                          additional_fields={'service': 'exporter-worker'})

    @staticmethod
    def get_logger_instance():
        if Logger.instance is None:
            Logger.instance = Logger.__get_instance()
        return Logger.instance
