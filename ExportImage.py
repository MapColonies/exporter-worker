from osgeo import gdal
import configparser
from math import floor
from uuid import uuid4

config = configparser.ConfigParser()
config.read('config.ini')
outputSRS = config['io']['outputSRS']
outputFormat = config['io']['outputFormat']

def export(bbox, filename ,url):
    try:
        kwargs = {'dstSRS': outputSRS, 'format': outputFormat, 'outputBounds': bbox, 'callback': progress_callback}
        result = gdal.Warp(f'{filename}.gpkg', url, **kwargs)
        return result
    except ValueError as e:
        print(e)


def progress_callback(complete, message, unknown):
    precent = floor(complete*100)
    print('progress: {}, message: "{}", unknown {}'.format(precent, message, unknown))
    return precent