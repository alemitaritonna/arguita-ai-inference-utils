#!/bin/bash
cd /home/apps/inference
source env/bin/activate
pkill -f "celery.*rag_celery_worker"
celery -A rag_celery_worker worker --loglevel=info --concurrency=1 &
