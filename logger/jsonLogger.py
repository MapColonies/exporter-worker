from jsonlogger.logger import JSONLogger


class Logger:
    instance = None

    @staticmethod
    def __get_instance():
        return JSONLogger('main-info', config={'handlers': {'file': {'filename': 'logger/logs.log'}}},
                   additional_fields={'service': 'exporter-worker'})

    @staticmethod
    def get_logger_instance():
        if Logger.instance is None:
            Logger.instance = Logger.__get_instance()
        return Logger.instance
