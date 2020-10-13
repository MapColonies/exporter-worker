from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
import datetime
import requests
import json


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__config = read_config()

    def export(self, offset, bbox, filename, url, taskid):
        try:
            self.logger.info(f'Task no.{offset} in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                      'format': self.__config['input_output']['output_format'],
                      'outputBounds': bbox,
                      'callback': self.progress_callback,
                      'callback_data': taskid}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')
            raise e

    def progress_callback(self, complete, message, unknown):
        host_ip = self.__config["elasticsearch"]["host_ip"]
        port = self.__config["elasticsearch"]["port"]
        index = self.__config["elasticsearch"]["index"]
        url = f'http://{host_ip}:{port}/indexes/{index}/document'

        try:
            percent = floor(complete * 100)
            headers = {"Content-Type": "application/json"}
            doc = {
                "body": {
                    "taskId": unknown,
                    "status": "in-progress",
                    "percent": percent,
                    "timestamp": datetime.now()
                }
            }
            requests.post(url=url, data=json.dumps(doc), headers=headers)

            if percent == 100:
                doc['status'] = 'completed'
            self.logger.info(f'Task Id "{unknown}" Updated database with progress: {percent}')
            return percent
        except requests.ConnectionError as ce:
            self.logger.error(f'Database connection error: {ce}')
            raise ce

        except Exception as e:
            doc['status'] = 'failed'
            requests.post(url=url, data=json.dumps(doc), headers=headers)
            self.logger.error(f'Error occurred while update taskId: {unknown}: {e}')
            raise e
