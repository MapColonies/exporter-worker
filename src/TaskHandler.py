from pathlib import Path
from kafka import KafkaConsumer
from kafka.coordinator.assignors.roundrobin import RoundRobinPartitionAssignor
from src import ExportImage
from src.Helper import Helper


class TaskHandler():
    def __init__(self):
        self.__helper = Helper()

    #def _filename_exist(filename):
    #    file = Path(f'{filename}.gpkg')
    #    return file.exists()

    def handle_tasks(self):
        consumer = KafkaConsumer(bootstrap_servers=['10.28.11.49:9092'], enable_auto_commit=False,
                                 auto_offset_reset='latest', group_id='task_group_1',
                                 partition_assignment_strategy=[RoundRobinPartitionAssignor])
        try:
            consumer.subscribe(['topic-test-5'])
            for task in consumer:
                result = self.execute_task(task)
                if result is not None:
                    consumer.commit()
                    print('Task done.')
        except ValueError as e:
            print(f'Error: {e}')
            return 1
        finally:
            consumer.close()

    def execute_task(self, task):
        task_values = self.__helper.load_json(task)
        print('Task received, Offset: ', task.offset)

        return ExportImage.export(task_values['bbox'], task_values['filename'], task_values['url'])








