#!/bin/bash
docker run -d --name exporter-worker -v /app/src/outputs:/home/ubuntu/exporter-worker/src/outputs exporter_worker:latest
