import sys

from osgeo import gdal
from math import floor
from os import path
import json
from src.log.logger import Logger


class ExportImage:
    def __init__(self):
        self.logger = Logger()

        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../confd/config/default.json')
        with open(config_path, encoding='utf-8') as config_file:
            self.__config = json.loads(config_file.read())

    def export(self, offset, bbox, filename, url):
        try:
            self.logger.info(f'Task no.{offset} in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'], 'format': self.__config['input_output']['output_format'], 'outputBounds': bbox, 'callback': self.progress_callback}
            result = gdal.Warp(f'{filename}.gpkg', url, **kwargs)
            return result
        except Exception as e:
            self.logger.error(f'Error occurred while exporting: {e}.')
            raise e

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete*100)
        #TODO:
        # Add database connection to update with progress
        self.logger.info(f'Updated database with progress: {percent}')
        return percent


