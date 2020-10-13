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
            es_obj = { "taskId": taskid, "filename": filename, "link": "/test/link"}
            self.logger.info(f'Task no.{offset} in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                      'format': self.__config['input_output']['output_format'],
                      'outputBounds': bbox,
                      'callback': self.progress_callback,
                      'callback_data': es_obj}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')
            raise e

    def progress_callback(self, complete, message, unknown):
        index = self.__config["es"]["index"]
        hostip = self.__config["es"]["host_ip"]
        port = self.__config["es"]["port"]

        url = f'http://{hostip}:{port}/indexes/{index}/document'

        try:
            percent = floor(complete * 100)
            headers = {"Content-Type": "application/json"}
            doc = {
                "body": {
                    "taskId": unknown["taskId"],
                    "status": "in-progress",
                    "progress": percent,
                    "datetime": str(datetime.now()),
                    "filename": unknown["filename"],
                    "link": unknown["link"]
                }
            }
            if percent == 100:
                doc["body"]["status"] = 'completed'

            requests.post(url=url, data=json.dumps(doc), headers=headers)
            self.logger.info(f'Task Id "{unknown["taskId"]}" Updated database with progress: {percent}')
            return percent
        except ConnectionError as ce:
            self.logger.error(f'Database connection failed: {ce}')
            raise ce
        except Exception as e:
            doc["body"]["status"] = 'failed'
            requests.post(url=url, data=json.dumps(doc), headers=headers)
            self.logger.error(f'Task Id "{unknown["taskId"]}" Failed Update database: {e}')
            raise e
