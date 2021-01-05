# **Exporter-Worker**

Worker is using Gdal operations to generate tiles into GeoPackage.

Based on Kafka-Queue, the worker is listening into specific Topic partitioner, consumes 
messages and processing them one by one.

**Installation`

git clone repository `master` branch 
* `git clone <master>`

# Run as localhost

  **from root`

generate config file
* `python3 confd/generate-config.py  --environment production`

set PYTHONPATH env into current repository - python will look for costum modules in application dir
* `export PYTHONPATH=.`
* `python3 src/main.py`

**_Important:_**

- **check the 'production.tmpl' variables values** (i.e. ports, topics, etc.) inside the 'confd' dir to declare the right values BEFORE you run 'generate-config.py'.
- **run the 'generate-config.py' from root application**, so the production.json config file will be generated on root application.  
- remember! if you wish to test worker, only one instance of worker can be 'on-air' (unless the kafka-topic has more than one partitioner) other, only one instance of worker will consume a message and will processing it.
  **if there is more then one instance of worker on air (includes running containers in Docker) that listening on the same topic, you may not receive messages because other worker is already consumed it.**
  
# Run in Docker

Build image:

* run the 'install.sh' from root application or run:
  
   `docker build --no-cache -t exporter-worker:latest .`

* run the 'run.sh' from root application or run:
  
  `docker run -d --name exporter-worker -v /your/external/mount/directory:/app/outputs exporter-worker:latest`

this will run container with the default config values as in the 'generate-config.tmpl',
you can declare environment variables **before** you are running the container OR pass the envs **while** you are running it

_**example`_

`docker run -d --name exporter-worker -e KAFKA_TOPIC=my-topic -v /your/external/mount/directory:/app/outputs exporter-worker:latest`


this will run container with your kafka topic declared topic value , in this case 'my-topic', you can see more configuration below

**_Important:_**

* when running in production on FS, you must provide config value: `FS_EXTERNAL_PHYSICAL_PATH` (see below on configurations section) as full path, to declare the creation of the packages location,
in dev mode you can just provide some random path (package will be created at the mount directory that provided in 'run.sh' script in dev mode)

* if you want to use S3 object storage, read the following configurations to allow the worker connect your S3 bucket

**_Configurations:_**

Make sure to append `CONFIGURATION_EXPORTER_WORKER` before each of the environment variables below:


- `KAFKA_HOST_IP`   an array of host ips and ports of kafka brokers *can be multiple*
- `KAFKA_TOPIC`     the topic's name that the worker will be listening to
- `KAFKA_GROUP_ID`       the group's name that the consumer will be join to
- `KAFKA_OFFSET_RESET`   can be 'earliest' or 'latest', will decide whether to start from the beginning of the topic (earliest) or from the end of the topic (latest)
  `KAFKA_POLL_TIMEOUT_MILLISECONDS`    limits the time from consuming the message to the commit if its not failed **by milliseconds** 
- `KAFKA_POLL_RECORDS`    limits the number of messages that will be consumed at once by the worker default to 1
- `LOGGER_LEVEL`    select the level of logs, default to 'INFO'
- `LOGGER_FILENAME`    select the log's file name
- `EXPORTSTORAGE_URL`    define the protocol, ip and port of the exported storage service, default to http://127.0.0.1:8080 , change if run on other port or on Docker.
- `STORAGE_PROVIDER` the storage service we are using, currently S3 or file-system are supported, default to FS
- `GDAL_MULTITHREAD`    boolean to enable [gdal mutlithread](https://gdal.org/programs/gdalwarp.html#cmdoption-gdalwarp-multi) option 
- `GDAL_THREAD_COUNT`    [gdal wrap options - NUM_THREADS option](https://gdal.org/api/gdalwarp_cpp.html#_CPPv4N15GDALWarpOptions16papszWarpOptionsE) negative number will be converted to "ALL_CPUS"  
- `GDAL_OUTPUT_SRS`   set target spatial reference default to 'EPSG:4326'
- `GDAL_OUTPUT_FORMAT`   select the output format, use the short format name, default to 'GPKG'
- `FS_EXTERNAL_PHYSICAL_PATH`   select the directory name by full path that wil be mounted to outputs directory **mandatory when using FS storage provider** 
- `FS_INTERNAL_OUTPUTS_PATH`    select the directory name by full path that the worker will be generate the package to, deafult to '/repository/root/location/outputs', in docker: "/app/outputs"
- `S3_ENDPOINT_URL` the url endpoint for the S3 service
- `ACCESS_KEY_ID` the access key id ("username") credential for the S3 service
- `SECRET_ACCESS_KEY` the secret access key ("password") credential for the S3 service
- `BUCKET` the bucket we will be using within the S3 service
- `SSL_VERIFY` (if https) choose whether to verify certificates or not, default is false