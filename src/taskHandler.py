from kafka import KafkaConsumer, BrokerConnection
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from src.exportImage import ExportImage
from src.helper import Helper
from log.logger import Logger
from src.config import read_config


class TaskHandler:
    def __init__(self):
        self.__helper = Helper()
        self.__exportImage = ExportImage()
        self.logger = Logger()
        self.__config = read_config()

    def handle_tasks(self):
        consumer = KafkaConsumer(bootstrap_servers=[self.__config['kafka']['host_ip']], enable_auto_commit=self.__config['kafka']['auto_commit'],
                                 max_poll_interval_ms=self.__config['kafka']['poll_timeout_milliseconds'], max_poll_records=self.__config['kafka']['poll_records'],
                                 auto_offset_reset=self.__config['kafka']['offset_reset'], group_id=self.__config['kafka']['group_id'],
                                 partition_assignment_strategy=[RoundRobinPartitionAssignor])
        try:
            consumer.subscribe([self.__config['kafka']['topic']])
            for task in consumer:
                result = self.execute_task(task)
                if result is not None:
                    consumer.commit()
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e
        finally:
            consumer.close()

    def execute_task(self, task):
        try:
            task_values = self.__helper.load_json(task.value)
            self.__helper.json_fields_validate(task_values)
            self.logger.info(f'Task Id "{task.offset}" received.')
            return self.__exportImage.export(task.offset, task_values['bbox'], task_values['fileName'], task_values['url'], task_values["taskId"])
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')




