#!/bin/bash
#docker run -d --name exporter-worker -v /home/ubuntu/outputs:/app/outputs exporter-worker:latest
docker run -d \
-e CONFIGURATION_EXPORTER_WORKER_EXPORTSTORAGE_URL=http://192.168.49.1:8080 \
-e CONFIGURATION_EXPORTER_WORKER_KAFKA_TOPIC=topic-try-123 \
-e CONFIGURATION_EXPORTER_WORKER_MAX_ATTEMPTS=1 \
-e CONFIGURATION_EXPORTER_WORKER_S3_ENDPOINT_URL=http://192.168.49.1:9000 \
-e CONFIGURATION_EXPORTER_WORKER_INPUT_OUTPUT_EXTERNAL_PHYSICAL_PATH=http://192.168.49.1:8082/downloads \
--user root \
-v /home/ubuntu/outputs:/app/outputs \
--name exporter-worker exporter-worker:latest
