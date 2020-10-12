from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
import requests
from datetime import datetime
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
        try:
            percent = floor(complete * 100)
            headers = {"Content-Type": "application/json"}
            doc = {
                "body": {
                    "taskId": unknown,
                    "status": "in-progress",
                    "percent": percent
                }
            }
            json.dumps(doc)
            r = requests.post(url='http://10.28.11.49:8080/indexes/es/document', data=json.dumps(doc), headers=headers)
            res = r.text
            print(res)

            if percent == 100:
                doc['status'] = 'completed'
            self.logger.info(f'Task Id "{unknown}" Updated database with progress: {percent}')
            return percent
        except Exception as e:
            print(e)
            raise e


