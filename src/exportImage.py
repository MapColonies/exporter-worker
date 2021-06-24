from osgeo import gdal, ogr
from os import path
import boto3
from shutil import rmtree
from enum import Enum
from math import floor
from logger.jsonLogger import Logger
from src.config import read_json
from src.model.enum.status_enum import Status
from src.model.enum.storage_provider_enum import StorageProvider
from src.helper import Helper
from pyority_queue.task_handler import *
from src.model.errors.invalid_data import InvalidDataError
import asyncio
import concurrent.futures


def is_valid_zoom_for_area(resolution, bbox):
    """
    Return true if bbox is at least 1 pixle at the wanted resolution, false otherwise.
    """
    top_right_lat = bbox[3]
    top_right_lon = bbox[2]
    bottom_left_lat = bbox[1]
    bottom_left_lon = bbox[0]

    # Check if bbox width and height are at least at the resolution of a pixle at the wanted zoom level
    return (top_right_lon - bottom_left_lon) > float(resolution) and (top_right_lat - bottom_left_lat) > float(resolution)


def is_valid_overview_factor(dataset, ov_factor):
    """
    Check if a given overview factor is valid for the dataset.
    """
    # Use gdal Dataset attributes (https://gdal.org/python/osgeo.gdal.Dataset-class.html)
    return dataset.RasterXSize / ov_factor >= 8 and dataset.RasterYSize / ov_factor >= 8


def calculate_overviews(dataframe, max_zoom):
    """
    Calculate overview factors for the given dataframe.

    return an array of valid overview factors (2 ^ i) for the dataset
    """
    overview_factors = [
        2 ** i for i in range(1, max_zoom + 1) if is_valid_overview_factor(dataframe, 2 ** i)]
    return overview_factors


class GDALBuildOverviewsResponse(Enum):
    CE_None = 0
    CE_Debug = 1
    CE_Warning = 2
    CE_Failure = 3
    CE_Fatal = 4


class ExportImage:
    def __init__(self, queue_handler, asyncio_eventloop):
        self.log = Logger.get_logger_instance()
        self.__helper = Helper()
        self.warp_percent = 70
        self.upload_percent = 1
        self.overview_percent = 100 - self.upload_percent - self.warp_percent
        self.queue_handler = queue_handler
        self.loop = asyncio_eventloop
        # Get current files path
        current_dir_path = path.dirname(__file__)

        # Get config path
        config_path = path.join(current_dir_path, '../config/production.json')
        self.__config = read_json(config_path)

        # Get path for "zoom level to resolution" json
        zoom_resolution_mapping_path = path.join(
            current_dir_path, 'constant/zoomLevelToResolution.json')
        self.__zoom_to_resolution = read_json(zoom_resolution_mapping_path)

    async def export(self, bbox, filename, url, task_id, job_id, directory_name, max_zoom, status, attempts):
        # retry while not done or reached max attempts
        while True:
            is_executable = await self.runPreperation(task_id, job_id, filename, status, attempts)
            if is_executable:
                gdal.UseExceptions()
                output_format = self.__config["gdal"]["output_format"]
                full_path = f'{path.join(self.__config["fs"]["internal_outputs_path"], directory_name, filename)}.{output_format}'
                try:
                    resolution = self.get_zoom_resolution(max_zoom)
                    if not is_valid_zoom_for_area(resolution, bbox):
                        raise InvalidDataError(
                            'Invalid zoom level for exported area (exported area too small)')
                    self.__helper.create_folder_if_not_exists(
                        f'{self.__config["fs"]["internal_outputs_path"]}/{directory_name}')
                    result = self.create_geopackage(
                        bbox, filename, url, task_id, job_id, full_path, max_zoom, resolution)

                    if result:
                        file_size = path.getsize(full_path)

                        # Check wanted storage provider
                        storage_provider = self.__config["storage_provider"].upper(
                        )
                        if (storage_provider == StorageProvider.S3.value):
                            # Try to upload export to s3
                            try:
                                self.log.info(f'Uploading task "{task_id}" to s3.')
                                self.upload_to_s3(
                                    filename, directory_name, output_format, full_path)
                                key = '{0}/{1}'.format(directory_name, filename)
                                s3_download_url = '{0}/{1}.{2}'.format(self.__config["s3"]["download_proxy"],
                                                                        key, self.__config['gdal']['output_format'])
                            except Exception as e:
                                self.log.info(
                                    f'Failed uploading task "{task_id}" to s3.')
                                raise e
                            finally:
                                # Delete local files
                                self.delete_local_directory(directory_name)
                                await self.queue_handler.ack(job_id, task_id)
                        else:
                            await asyncio.sleep(self.__config["update_delay_seconds"])
                            await self.queue_handler.ack(job_id, task_id)
                            self.log.info(f'Task Id "{task_id}" is done.')
                        return True
                except InvalidDataError as e:
                    await self.queue_handler.reject(job_id, task_id, False, str(e))
                    self.log.error(
                        f'Error occurred while exporting. taskID: {task_id}, error: {e}.')
                except Exception as e:
                    is_recoverable_task = True if attempts < self.__config['max_attempts'] else False
                    await self.queue_handler.reject(job_id, task_id, is_recoverable_task, str(e))
                    self.log.error(
                        f'Error occurred while exporting. taskID: {task_id}, error: {e}.')
            return True  # if task shouldn't run it should be removed from queue

    def warp_progress_callback(self, complete, message, unknown):
        """
        Callback for updating export progress according to geopackage creation process.
        """
        # Calculate warp percent of the whole process

        percent = floor(complete * self.warp_percent)
        asyncio.run_coroutine_threadsafe(
            self.queue_handler.update_progress(unknown['job_id'], unknown['task_id'], percent), loop=self.loop)


    def overviews_progress_callback(self, complete, message, unknown):
        """
        Callback for updating export progress according to geopackage overview build.
        """
        # Calculate build overview percent of the whole process
        percent = floor(complete * (self.overview_percent))
        asyncio.run_coroutine_threadsafe(
            self.queue_handler.update_progress(unknown['job_id'], unknown['task_id'], self.warp_percent + percent), self.loop)
        # Final percent = warp percent + build overviews percent

    def upload_to_s3(self, file_name, directory_name, output_format, full_path):
        """
        Upload a file to s3.
        """
        s3_client = boto3.client('s3', endpoint_url=self.__config["s3"]["endpoint_url"],
                                 aws_access_key_id=self.__config["s3"]["access_key_id"],
                                 aws_secret_access_key=self.__config["s3"]["secret_access_key"],
                                 verify=self.__config["s3"]["ssl_enabled"])
        bucket = self.__config["s3"]["bucket"]
        object_key = f'{directory_name}/{file_name}.{output_format}'

        s3_client.upload_file(
            full_path, bucket, object_key)
        self.log.info(
            f'File "{file_name}.{output_format}" was uploaded to bucket "{bucket}" succesfully')

    def delete_local_directory(self, directoryName):
        """
        Delete a directory on the file system.
        """
        directory_path = path.join(
            self.__config["fs"]["internal_outputs_path"], directoryName)
        rmtree(directory_path)
        self.log.info(
            f'Folder "{directoryName}" in path: "{directory_path}" removed successfully')

    def create_geopackage(self, bbox, file_name, url, task_id, job_id, full_path, max_zoom, resolution):
        """
        Create a geopackage with a maximum zoom level from a given BBOX.
        """
        warp_result = self.create_geopackage_base(
            bbox, file_name, url, task_id, job_id, full_path, resolution)

        if not warp_result:
            self.log.error(f'gdal return empty response for task: "{task_id}"')
            return False

        # Clear cache (for closing process)
        warp_result.FlushCache()
        warp_result = None

        overviews_result = self.create_geopackage_overview(
            file_name, task_id, job_id, full_path, max_zoom)

        # Check for overview build errors
        if overviews_result == GDALBuildOverviewsResponse.CE_Failure or overviews_result == GDALBuildOverviewsResponse.CE_Fatal:
            self.log.error(
                f'Error occured whild building overviews for task: "{task_id}", Error: {overviews_result}')
            return False

        # Create indexes
        self.log.info(f'Creating indexes for task "{task_id}".')
        self.create_index(file_name, full_path)
        self.log.info(
            f'Done creating indexes for task "{task_id}".')

        return True

    def create_geopackage_base(self, bbox, file_name, url, task_id, job_id, full_path, resolution):
        """
        Create a new geopackage with only the base zoom level.
        """
        output_format = self.__config["gdal"]["output_format"]
        es_obj = {"task_id": task_id, "job_id": job_id, "filename": file_name}
        self.log.info(f'Task Id "{task_id}" in progress.')
        thread_count = self.__config['gdal']['thread_count'] if int(self.__config['gdal']['thread_count']) > 0 \
            else 'val/ALL_CPUS'
        thread_count = f'NUM_THREADS={thread_count}'
        kwargs = {
            'dstSRS': self.__config['gdal']['output_srs'],
            'format': output_format,
            'outputBounds': bbox,
            'callback': self.warp_progress_callback,
            'callback_data': es_obj,
            'xRes': resolution,
            'yRes': resolution,
            'creationOptions': ['TILING_SCHEME=InspireCrs84Quad'],
            'multithread': self.__config['gdal']['multithread'],
            'warpOptions': [thread_count]
        }

        result = gdal.Warp(full_path, url, **kwargs)
        self.log.info(f'Base overview built for task: "{task_id}".')
        return result

    def create_geopackage_overview(self, file_name, task_id, job_id, full_path, max_zoom):
        """
        Add overviews to an existing geopackage.
        Added overviews are calculated according to the base size (geopackage x and y pixle size).
        """
        Image = gdal.Open(full_path, 1)
        resolution_multipliers = calculate_overviews(Image, max_zoom)
        gdal.SetConfigOption('COMPRESS_OVERVIEW', 'DEFLATE')

        # Build overviews
        self.log.info(f'Creating overviews for task {task_id}')
        es_obj = {"task_id": task_id, "job_id": job_id, "filename": file_name}
        kwargs = {
            'callback': self.overviews_progress_callback,
            'callback_data': es_obj
        }
        overviews_result = Image.BuildOverviews(
            "BILINEAR", resolution_multipliers, **kwargs)
        self.log.info(f'Finished creating overviews for task {task_id}')
        del Image
        return overviews_result

    def create_index(self, file_name, full_path):
        """
        Create index for an existing DB (geopackage).
        """
        driver = ogr.GetDriverByName("GPKG")
        data_source = driver.Open(full_path, update=True)
        sql = f'CREATE unique INDEX tiles_index on {file_name}(zoom_level, tile_column, tile_row)'
        data_source.ExecuteSQL(sql)

    async def runPreperation(self, task_id, job_id, filename, status, attempts):
        if status is None or status == Status.COMPLETED.value:
            return False
        attempts = int(attempts)
        if attempts >= self.__config["max_attempts"]:
            self.log.error(f'max attempts limit reached for task: "{task_id}"')
            await self.queue_handler.reject(job_id, task_id, False, 'max attempts limit reached')
            return False
        return True

    def get_zoom_resolution(self, zoom_level):
        if f'{zoom_level}' in self.__zoom_to_resolution:
            resolution = self.__zoom_to_resolution[f'{zoom_level}']
            return resolution
        else:
            raise InvalidDataError(f'No such zoom level: {zoom_level}')
