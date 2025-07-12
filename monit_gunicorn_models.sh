#!/bin/bash
cd /home/apps/inference
source env_models/bin/activate
pkill -f "gunicorn.*inference_models:app"
gunicorn -c gunicorn.inference_models.py inference_models:app &
