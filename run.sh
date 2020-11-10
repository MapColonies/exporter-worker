#!/bin/bash
docker run -d --name exporter-worker -v /home/ubuntu/outputs:/app/outputs exporter_worker:latest
