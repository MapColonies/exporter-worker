from src.TaskHandler import TaskHandler

class App():
    def __init__(self):
        self.__taskHandler = TaskHandler()

    def _start_service(self):
        print('Service is listening to queue.')
        try:
            self.__taskHandler.handle_tasks()
        except Exception as e:
            print(f'Error occurred during service. Info: {e}')


App()._start_service()
