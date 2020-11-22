from osgeo import gdal, ogr
from os import path
from math import floor
from logger.jsonLogger import Logger
from src.config import read_config
from src.model.enum.status_enum import Status
from src.helper import Helper


class ExportImage:
    def __init__(self):
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.__config = read_config()

    def export(self, bbox, filename, url, taskid, directoryName):
        while self.runPreperation(taskid, filename):  # retry while not done or reached max attempts
            gdal.UseExceptions()
            output_format = self.__config["input_output"]["output_format"]
            full_path = f'{path.join(self.__config["input_output"]["internal_outputs_path"], directoryName, filename)}.{output_format}'
            try:
                self.__helper.create_folder_if_not_exists(f'{self.__config["input_output"]["internal_outputs_path"]}/{directoryName}')
                result = self.create_geopackage(bbox, filename, url, taskid, full_path)

                if result is not None:
                    self.create_index(filename, full_path)
                    self.__helper.save_update(taskid, Status.COMPLETED.value, filename, 100, full_path, directoryName)
                    self.log.info(f'Task Id "{taskid}" is done.')
                return result
            except Exception as e:
                self.__helper.save_update(taskid, Status.FAILED.value, filename)
                self.log.error(f'Error occurred while exporting: {e}.')
        return True  # if task shouldn't run it should be removed from queue

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete * 100)
        self.__helper.save_update(unknown["taskId"], Status.IN_PROGRESS.value, unknown["filename"], percent)

    def create_geopackage(self, bbox, filename, url, taskid, fullPath):
        output_format = self.__config["input_output"]["output_format"]
        es_obj = {"taskId": taskid, "filename": filename}
        self.log.info(f'Task Id "{taskid}" in progress.')
        thered_count = self.__config['gdal']['thread_count'] if int(self.__config['gdal']['thread_count']) > 0 \
            else 'val/ALL_CPUS'
        thered_count = f'NUM_THREADS={thered_count}'
        kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                  'format': output_format,
                  'outputBounds': bbox,
                  'callback': self.progress_callback,
                  'callback_data': es_obj,
                  'xRes': 1.67638063430786e-07,
                  'yRes': 1.67638063430786e-07,
                  'creationOptions': ['TILING_SCHEME=InspireCrs84Quad'],
                  'multithread': self.__config['gdal']['multithread'],
                  'warpOptions': [thered_count]}
        result = gdal.Warp(fullPath, url, **kwargs)
        return result

    def create_index(self, filename, fullPath):
        driver = ogr.GetDriverByName("GPKG")
        data_source = driver.Open(fullPath, update=True)
        sql = f'CREATE unique INDEX tiles_index on {filename}(zoom_level, tile_column, tile_row)'
        data_source.ExecuteSQL(sql)

    def runPreperation(self, taskId, filename):
        status = self.__helper.get_status(taskId)
        if status is None or status["status"] == Status.COMPLETED.value:
            return False
        attempts = int(status["workerAttempts"])
        if attempts >= self.__config["max_attempts"]:
            self.log.error(f'max attempts limit reached for task: "{taskId}"')
            self.__helper.save_update(taskId, Status.FAILED.value, filename)
            return False
        self.__helper.save_update(taskId, Status.IN_PROGRESS.value, filename, 0, None, None, attempts+1)
        return True
