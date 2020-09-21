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
        self.__config = read_config(self)

    def handle_tasks(self):
        consumer = KafkaConsumer(bootstrap_servers=[self.__config['kafka']['host_ip']], enable_auto_commit=self.__config['kafka']['auto_commit'],
                                 auto_offset_reset=self.__config['kafka']['offset_reset'], group_id=self.__config['kafka']['group_id'],
                                 partition_assignment_strategy=[RoundRobinPartitionAssignor])
        try:
            consumer.subscribe([self.__config['kafka']['topic']])
            for task in consumer:
                result = self.execute_task(task)
                if result is not None:
                    consumer.commit()
                    self.logger.info(f'Task no.{task.offset} is done.')
        except Exception as e:
            self.logger.error(f'Error occurred: {e}.')
            raise e
        finally:
            consumer.close()

    def execute_task(self, task):
        try:
            task_values = self.__helper.load_json(task)
            self.logger.info(f'Task no.{task.offset} received.')
            return self.__exportImage.export(task.offset, task_values['bbox'], task_values['filename'], task_values['url'])
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')



