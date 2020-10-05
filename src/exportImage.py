from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config
from datetime import datetime
from src.services import es
from threading import Timer


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__config = read_config()

    def export(self, offset, bbox, filename, url):
        try:
            self.logger.info(f'Task no.{offset} in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'], 'format': self.__config['input_output']['output_format'], 'outputBounds': bbox, 'callback': self.progress_callback}
            result = gdal.Warp(f'{self.__config["input_output"]["folder_path"]}/{filename}.gpkg', url, **kwargs)
            print("DONE DATABASE UPDATE")
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')
            raise e

    def progress_callback(self, complete, message, unknown):
        try:
            percent = floor(complete*100)
            doc = {
                'status': 'in-progress',
                'percent': percent,
                'timestamp': datetime.now(),
            }
            if percent == 100:
                doc['status'] = 'completed'

            es.update(doc)
            self.logger.info(f'Updated database with progress: {percent}')
        except Exception as e:
            self.logger.error(f'Database Error: {e}')
            doc['status'] = 'stopped'
            es.update(doc)
            raise e
