from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from src.ExportImage import ExportImage
from src.Helper import Helper
from os import path
import json


class TaskHandler:
    def __init__(self):
        self.__helper = Helper()
        self.__exportImage = ExportImage()
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../confd/config/default.json')
        with open(config_path, encoding='utf-8') as config_file:
            self.__config = json.loads(config_file.read())

    def handle_tasks(self):
        consumer = KafkaConsumer(bootstrap_servers=[self.__config['kafka']['host_ip']], enable_auto_commit=self.__config['kafka']['auto_commit'],
                                 auto_offset_reset=self.__config['kafka']['offset_reset'], group_id=self.__config['kafka']['group_id'],
                                 partition_assignment_strategy=[RoundRobinPartitionAssignor])
        try:
            consumer.subscribe([self.__config['kafka']['topic']])
            for task in consumer:
                result = self.execute_task(task)
                print(result)
                if result is not None:
                    consumer.commit()
                    print('Task done.')
        except ValueError as e:
            print(f'Error: {e}')
            return 1
        finally:
            consumer.close()

    def execute_task(self, task):
        try:
            task_values = self.__helper.load_json(task)
            print('Task received, Offset: ', task.offset)
            return self.__exportImage.export(task_values['bbox'], task_values['filename'], task_values['url'])
        except Exception as e:
            print(f'Error while execute task, Info: {e}')









