from osgeo import gdal
import configparser
from math import floor
from uuid import uuid4

config = configparser.ConfigParser()
config.read('config.ini')
outputSRS = config['io']['outputSRS']
outputFormat = config['io']['outputFormat']
wmsBaseUrl = config['WMS']['wmsBaseUrl']
version = config['WMS']['version']

def export(bbox, layer):
    try:
        kwargs = {'dstSRS': outputSRS, 'format': outputFormat, 'outputBounds': bbox, 'callback': progress_callback}
        result = gdal.Warp(f'{uuid4()}.gpkg', f'{wmsBaseUrl}&version={version}&request=GetMap&layers={layer}', **kwargs)
        return result
    except ValueError as e:
        print(e)


def progress_callback(complete, message, unknown):
    precent = floor(complete*100)
    print('progress: {}, message: "{}", unknown {}'.format(precent, message, unknown))
    return precent