#!/bin/bash
cd /home/apps/inference
source env_models/bin/activate
pkill -f "celery.*models_celery_worker"
celery -A models_celery_worker worker --loglevel=info --concurrency=1 &

