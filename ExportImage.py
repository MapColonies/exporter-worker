from osgeo import gdal
import configparser
import random

config = configparser.ConfigParser()
config.read('config.ini')
outputSRS = config['io']['outputSRS']
outputFormat = config['io']['outputFormat']

def export():
    kwargs = {'dstSRS': outputSRS, 'format': outputFormat, 'outputBounds': [34.812883, 31.907806, 34.814606, 31.909520]}
    gdal.Warp(f'{random.randint(1,5555555)}.gpkg', "WMS:http://localhost:8080/geoserver/cite/wms?service=WMS&version=1.1.0&request=GetMap&layers=cite:wizzman", **kwargs)
    print('done')




