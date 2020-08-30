from osgeo import gdal

kwargs = {'dstSRS': 'EPSG:4326', 'format': 'gpkg', 'outputBounds': [34.812883, 31.907806, 34.814606, 31.909520]}
ds = gdal.Warp('warp_test.gpkg', "WMS:http://localhost:8080/geoserver/cite/wms?service=WMS&version=1.1.0&request=GetMap&layers=cite:wizzman", **kwargs)
ds = None
print('done')