from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
from src.model.enum.status_enum import Status
import requests
from datetime import datetime
import json


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__config = read_config()
        self.index = self.__config["es"]["index"]
        self.hostip = self.__config["es"]["host_ip"]
        self.port = self.__config["es"]["port"]

    def export(self, offset, bbox, filename, url, taskid):
        try:
            es_obj = { "taskId": taskid, "filename": filename}
            self.logger.info(f'Task Id "{taskid}" in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                      'format': self.__config['input_output']['output_format'],
                      'outputBounds': bbox,
                      'callback': self.progress_callback,
                      'callback_data': es_obj}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)
            if result is not None:
                self.logger.info(f'Task Id "{taskid}" is done.')
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')
            doc = {
                "params": {
                    "taskId": taskid,
                    "status": Status.FAILED.value,
                    "lastUpdateDate": str(datetime.now()),
                    "fileName": filename
                }
            }
            self.update_db(doc, taskid)
            raise e

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete * 100)
        doc = {
            "params": {
                "taskId": unknown["taskId"],
                "status": Status.IN_PROGRESS.value,
                "progress": percent,
                "lastUpdateTime": str(datetime.now()),
                "fileName": unknown["filename"]
            }
        }

        if percent == 100:
            link = f'{self.__config["input_output"]["folder_path"]}/{unknown["filename"]}.gpkg'
            doc["params"]["status"] = Status.COMPLETED.value
            doc["params"]["link"] = link

        self.update_db(doc, unknown["taskId"])

    def update_db(self, doc, taskId):
        url = f'http://{self.hostip}:{self.port}/indexes/{self.index}/document?taskId={taskId}'
        try:
            headers = {"Content-Type": "application/json"}

            self.logger.info(f'Task Id "{taskId}" Updating database')
            requests.post(url=url, data=json.dumps(doc), headers=headers)
        except ConnectionError as ce:
            self.logger.error(f'Database connection failed: {ce}')
        except Exception as e:
            self.logger.error(f'Task Id "{taskId}" Failed to update database: {e}')

