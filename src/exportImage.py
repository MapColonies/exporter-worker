from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
from src.model.enum.status_enum import Status
from datetime import datetime
from src.helper import Helper


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__helper = Helper()
        self.__config = read_config()

    def export(self, bbox, filename, url, taskid):
        gdal.UseExceptions()
        try:
            es_obj = {"taskId": taskid, "filename": filename}
            self.logger.info(f'Task Id "{taskid}" in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                      'format': self.__config['input_output']['output_format'],
                      'outputBounds': bbox,
                      'callback': self.progress_callback,
                      'callback_data': es_obj}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)

            if result is not None:
                link = f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg'
                doc = {
                    "taskId": taskid,
                    "status": Status.COMPLETED.value,
                    "progress": 100,
                    "lastUpdateTime": datetime.now(),
                    "link": link
                }

                self.__helper.update_db(doc)
                self.logger.info(f'Task Id "{taskid}" is done.')
            return result
        except Exception as e:
            doc = {
                "taskId": taskid,
                "status": Status.FAILED.value,
                "lastUpdateTime": datetime.now(),
                "fileName": filename
            }
            self.__helper.update_db(doc)
            raise e

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete * 100)
        doc = {
            "taskId": unknown["taskId"],
            "status": Status.IN_PROGRESS.value,
            "progress": percent,
            "lastUpdateTime": datetime.now(),
            "fileName": unknown["filename"]
        }
        self.__helper.update_db(doc)

