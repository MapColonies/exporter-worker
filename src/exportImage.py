from osgeo import gdal
from math import floor
from log.logger import Logger
from src.config import read_config


class ExportImage:
    def __init__(self):
        self.logger = Logger()
        self.__config = read_config()

    def export(self, offset, bbox, filename, url):
        try:
            self.logger.info(f'Task no.{offset} in progress.')
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'], 'format': self.__config['input_output']['output_format'], 'outputBounds': bbox, 'callback': self.progress_callback}
            result = gdal.Warp(f'./outputs/{filename}.gpkg', url, **kwargs)
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


