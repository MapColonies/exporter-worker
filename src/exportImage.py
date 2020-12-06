from osgeo import gdal, ogr
from os import path
from math import floor
from logger.jsonLogger import Logger
from src.config import read_config
from src.model.enum.status_enum import Status
from src.model.enum.storage_provider_enum import StorageProvider
from src.helper import Helper


class ExportImage:
    def __init__(self):
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.__config = read_config()
        if (self.__config["storage_provider"] == StorageProvider.S3.value):
            gdal.SetConfigOption(
                'AWS_SECRET_ACCESS_KEY', self.__config["gdal"]["aws"]["secret_access_key"])
            gdal.SetConfigOption('AWS_ACCESS_KEY_ID',
                                 self.__config["gdal"]["aws"]["access_key_id"])
            gdal.SetConfigOption(
                'AWS_HTTPS', self.__config["gdal"]["aws"]["https"])
            # prevent gdal for searching a subdomain bucket.localhost:9000
            gdal.SetConfigOption(
                'AWS_S3_ENDPOINT', self.__config["gdal"]["aws"]["s3_endpoint"])
            gdal.SetConfigOption(
                'AWS_VIRTUAL_HOSTING', self.__config["gdal"]["aws"]["virtual_hosting"])
            gdal.SetConfigOption(
                'CPL_VSIL_USE_TEMP_FILE_FOR_RANDOM_WRITE', 'YES')

    def export(self, bbox, filename, url, taskid, directoryName):
        # retry while not done or reached max attempts
        while self.runPreperation(taskid, filename):
            gdal.UseExceptions()
            output_format = self.__config["input_output"]["output_format"]
            if (self.__config["storage_provider"] == StorageProvider.S3.value):
                full_path = f'{directoryName}/{filename}.{output_format}'
            else:
                full_path = f'{path.join(self.__config["input_output"]["internal_outputs_path"], directoryName, filename)}.{output_format}'
            try:
                if (self.__config["storage_provider"] != StorageProvider.S3.value):
                    self.__helper.create_folder_if_not_exists(
                        f'{self.__config["input_output"]["internal_outputs_path"]}/{directoryName}')

                result = self.create_geopackage(
                    bbox, filename, url, taskid, full_path)

                if result:

                    # TODO: self.create_index(filename, full_path)
                    self.__helper.save_update(
                        taskid, Status.COMPLETED.value, filename, 100, full_path, directoryName)
                    self.log.info(f'Task Id "{taskid}" is done.')
                return result
            except Exception as e:
                self.__helper.save_update(
                    taskid, Status.FAILED.value, filename)
                self.log.error(f'Error occurred while exporting: {e}.')
        return True  # if task shouldn't run it should be removed from queue

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete * 100)
        self.__helper.save_update(
            unknown["taskId"], Status.IN_PROGRESS.value, unknown["filename"], percent)

    def create_geopackage(self, bbox, filename, url, taskid, full_path):
        self.log.info(f'Task Id "{taskid}" in progress.')
        output_format = self.__config["input_output"]["output_format"]
        es_obj = {"taskId": taskid, "filename": filename}
        thread_count = self.__config['gdal']['thread_count'] if int(self.__config['gdal']['thread_count']) > 0 \
            else 'val/ALL_CPUS'
        thread_count = f'NUM_THREADS={thread_count}'
        kwargs = {'dstSRS': self.__config['input_output']['output_srs'],
                  'format': output_format,
                  'outputBounds': bbox,
                  'callback': self.progress_callback,
                  'callback_data': es_obj,
                  'xRes': 1.67638063430786e-07,
                  'yRes': 1.67638063430786e-07,
                  'creationOptions': ['TILING_SCHEME=InspireCrs84Quad'],
                  'multithread': self.__config['gdal']['multithread'],
                  'warpOptions': [thread_count]}

        result = gdal.Warp(f'/vsis3/{self.__config["gdal"]["aws"]["s3_bucket"]}/{full_path}'
                           if self.__config["storage_provider"] == StorageProvider.S3.value else full_path,
                           url, **kwargs)
        if (result is not None):
            result.FlushCache()
            result = None
            return True
        else:
            return False

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
        self.__helper.save_update(
            taskId, Status.IN_PROGRESS.value, filename, 0, None, None, attempts+1)
        return True
