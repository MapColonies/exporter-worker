from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
from datetime import datetime
from src.services import es as esClient


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__config = read_config()

    def export(self, offset, bbox, filename, url, taskid):
        try:
            self.logger.info(f'Task Id: "{taskid}" in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'], 'format': self.__config['input_output']['output_format'], 'outputBounds': bbox, 'callback': self.progress_callback, 'callback_data': taskid}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting Task Id "{taskid}": {e}.')
            raise e

    def progress_callback(self, complete, message, unknown):
        try:
            percent = floor(complete*100)
            doc = {
                'taskId': unknown,
                'status': 'in-progress',
                'percent': percent,
                'timestamp': datetime.now(),
            }
            if percent == 100:
                doc['status'] = 'completed'

            esClient.update(doc)
            self.logger.info(f'Task Id: "{unknown}" updated database with progress: {percent}')
        except Exception as e:
            self.logger.error(f'Database Error: {e}')
            doc['status'] = 'stopped'
            esClient.update(doc)
            raise e
