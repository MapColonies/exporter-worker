from osgeo import gdal
from math import floor
from os import path
import json


class ExportImage:
    def __init__(self):
        current_dir_path = path.dirname(__file__)
        config_path = path.join(current_dir_path, '../confd/config/default.json')
        with open(config_path, encoding='utf-8') as config_file:
            self.__config = json.loads(config_file.read())

    def export(self, bbox, filename, url):
        try:
            kwargs = {'dstSRS': self.__config['input_output']['output_srs'], 'format': self.__config['input_output']['output_format'], 'outputBounds': bbox, 'callback': self.progress_callback}
            result = gdal.Warp(f'{filename}.gpkg', url, **kwargs)
            return result
        except Exception as e:
            print(f'Failed export image: {e}')

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete*100)
        print('progress: {}, message: "{}", unknown {}'.format(percent, message, unknown))
        return percent

