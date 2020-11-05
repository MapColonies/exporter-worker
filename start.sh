#!/bin/bash

python3 /app/confd/generate-config.py --environment production
python3 /app/src/main.py
