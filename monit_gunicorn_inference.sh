#!/bin/bash
cd /home/apps/inference
source env/bin/activate
pkill -f "gunicorn.*inference:app"
gunicorn -c gunicorn.inference.py inference:app &
