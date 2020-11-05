#!/bin/bash
docker run -d --name exporter-worker -v /home/ubuntu/exporter-worker/outputs:/app/outputs exporter-worker:latest
