from osgeo import gdal
import configparser
from math import floor

config = configparser.ConfigParser()
config.read('config.ini')
outputSRS = config['io']['outputSRS']
outputFormat = config['io']['outputFormat']


def export(bbox, filename, url):
    try:
        kwargs = {'dstSRS': outputSRS, 'format': outputFormat, 'outputBounds': bbox, 'callback': progress_callback}
        result = gdal.Warp(f'{filename}.gpkg', url, **kwargs)
        return result
    except Exception as e:
        print(f'Failed export image: {e}')


def progress_callback(complete, message, unknown):
    percent = floor(complete*100)
    print('progress: {}, message: "{}", unknown {}'.format(precent, message, unknown))
    return percent
