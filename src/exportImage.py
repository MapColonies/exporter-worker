from osgeo import gdal, ogr
from os import path
from math import floor
from logger.jsonLogger import Logger
from src.config import read_json
from src.model.enum.status_enum import Status
from src.helper import Helper


def get_zoom_resolution(zoom_to_resolution_dict, zoom_level):
    if f'{zoom_level}' in zoom_to_resolution_dict:
        resolution = zoom_to_resolution_dict[f'{zoom_level}']
        return resolution
    else:
        raise Exception(f'No such zoom level. got: {zoom_level}')


def is_valid_zoom_for_area(resolution, tile_size, bbox):
    top_right_lat = bbox[3]
    top_right_lon = bbox[2]
    bottom_left_lat = bbox[1]
    bottom_left_lon = bbox[0]

    # Check if bbox width and height are at least at the resolution of a pixle at the wanted zoom level
    return (top_right_lon - bottom_left_lon) >= float(resolution) and (top_right_lat - bottom_left_lat) >= float(resolution)


class ExportImage:
    def __init__(self):
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()

        # Get current files path
        current_dir_path = path.dirname(__file__)

        # Get config path
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)

        # Get path for "zoom level to resolution" json
        zoom_resolution_mapping_path = path.join(
            current_dir_path, 'constant/zoomLevelToResolution.json')
        self.__zoom_to_resolution = read_json(zoom_resolution_mapping_path)

    def export(self, bbox, filename, url, taskid, directoryName, max_zoom):
        # retry while not done or reached max attempts
        while self.runPreperation(taskid, filename):
            gdal.UseExceptions()
            output_format = self.__config["input_output"]["output_format"]
            full_path = f'{path.join(self.__config["input_output"]["internal_outputs_path"], directoryName, filename)}.{output_format}'
            try:
                resolution = get_zoom_resolution(
                    self.__zoom_to_resolution, max_zoom)
                if not is_valid_zoom_for_area(resolution, 256, bbox):
                    raise Exception(
                        'Invalid zoom level for exported area (exported area too small)')
                self.__helper.create_folder_if_not_exists(
                    f'{self.__config["input_output"]["internal_outputs_path"]}/{directoryName}')
                result = self.create_geopackage(
                    bbox, filename, url, taskid, full_path, resolution)

                if result is not None:
                    self.create_index(filename, full_path)
                    self.__helper.save_update(
                        taskid, Status.COMPLETED.value, filename, 100, full_path, directoryName)
                    self.log.info(f'Task Id "{taskid}" is done.')
                return result
            except Exception as e:
                self.__helper.save_update(
                    taskid, Status.FAILED.value, filename)
                self.log.error(
                    f'Error occurred while exporting. taskID: {taskid}, error: {e}.')
        return True  # if task shouldn't run it should be removed from queue

    def progress_callback(self, complete, message, unknown):
        percent = floor(complete * 100)
        self.__helper.save_update(
            unknown["taskId"], Status.IN_PROGRESS.value, unknown["filename"], percent)

    def create_geopackage(self, bbox, filename, url, taskid, fullPath, resolution):
        output_format = self.__config["input_output"]["output_format"]
        es_obj = {"taskId": taskid, "filename": filename}
        self.log.info(f'Task Id "{taskid}" in progress.')
        thread_count = self.__config['gdal']['thread_count'] if int(self.__config['gdal']['thread_count']) > 0 \
            else 'val/ALL_CPUS'
        thread_count = f'NUM_THREADS={thread_count}'
        kwargs = {
            'dstSRS': self.__config['input_output']['output_srs'],
            'format': output_format,
            'outputBounds': bbox,
            'callback': self.progress_callback,
            'callback_data': es_obj,
            'xRes': resolution,
            'yRes': resolution,
            'creationOptions': ['TILING_SCHEME=InspireCrs84Quad'],
            'multithread': self.__config['gdal']['multithread'],
            'warpOptions': [thread_count]
        }
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
        self.__helper.save_update(
            taskId, Status.IN_PROGRESS.value, filename, 0, None, None, attempts+1)
        return True
