from kafka import KafkaConsumer
import ExportImage

consumer = KafkaConsumer(bootstrap_servers=['10.28.11.49:9092'], enable_auto_commit=False, auto_offset_reset='latest', group_id='taskGroup1')


def handle_task():
    currentlyRunning = 0
    while True:
        try:
            print('Looking for task.')
            consumer.subscribe(['topic-test-1'])
            if (currentlyRunning < 1):
                currentlyRunning += 1
                task = consumer.poll(timeout_ms=5000, max_records=1)
                if (len(task.values()) > 0):
                    values = list(task.values())
                    print('Task received, Offset: ', values[0][0].offset)
                    result = ExportImage.export([-122.459473, 37.734669, -122.456367, 37.738146],
                                                'GS_Workspace:i3SF15-meter')
                    if (result is not None):
                        consumer.commit()
                        consumer.unsubscribe()
                        print('Task done.')
                currentlyRunning -= 1
        except ValueError as e:
            print('Something went wrong:', e)






