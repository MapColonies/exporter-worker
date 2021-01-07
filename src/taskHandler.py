from os import path
from kafka import KafkaConsumer, BrokerConnection
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from src.exportImage import ExportImage
from src.helper import Helper
from logger.jsonLogger import Logger
from src.config import read_json


class TaskHandler:
    def __init__(self):
        self.__helper = Helper()
        self.__exportImage = ExportImage()
        self.log = Logger.get_logger_instance()

        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)

    def handle_tasks(self):
        consumer = KafkaConsumer(bootstrap_servers=self.__config['kafka']['host_ip'],
                                 enable_auto_commit=False,
                                 max_poll_interval_ms=self.__config['kafka']['poll_timeout_milliseconds'],
                                 max_poll_records=self.__config['kafka']['poll_records'],
                                 auto_offset_reset=self.__config['kafka']['offset_reset'],
                                 group_id=self.__config['kafka']['group_id'],
                                 partition_assignment_strategy=[RoundRobinPartitionAssignor])
        try:
            consumer.subscribe([self.__config['kafka']['topic']])
            for task in consumer:
                task_values = self.__helper.load_json(task.value)
                result = self.execute_task(task_values)
                if result:
                    self.log.info(f'commitng task "{task_values["taskId"]}" to kafka')
                    consumer.commit()
        except Exception as e:
            self.log.error(f'Error occurred: {e}.')
            raise e
        finally:
            consumer.close()

    def execute_task(self, task_values):
        try:
            self.__helper.json_fields_validate(task_values)
            self.log.info(f'Task Id "{task_values["taskId"]}" received.')
            return self.__exportImage.export(task_values['bbox'], task_values['fileName'], task_values['url'], task_values['taskId'], task_values['directoryName'], task_values['maxZoom'])
        except Exception as e:
            self.log.error(f'Error occurred while exporting: {e}.')
