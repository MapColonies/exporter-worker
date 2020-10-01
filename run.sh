#!/bin/bash
docker run -d --name exporter-worker -v /home/ubuntu/exporter-worker/src/outputs:/app/src/outputs exporter_worker:latest
