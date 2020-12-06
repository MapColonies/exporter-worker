#!/bin/bash
docker run -d \
-e CONFIGURATION_EXPORTER_WORKER_KAFKA_TOPIC=topic-dev-9 \
-e CONFIGURATION_EXPORTER_WORKER_INPUT_OUTPUT_EXTERNAL_PHYSICAL_PATH=http://$(ipad):8082/downloads \
-e CONFIGURATION_EXPORTER_WORKER_EXPORTSTORAGE_URL=http://$(ipad):8081 \
--name exporter-worker -v /home/ubuntu/outputs:/app/outputs exporter-worker:latest
