#!/bin/bash
cd /home/apps/rag
source env/bin/activate
pkill -f "gunicorn.*rag:app"
gunicorn -c gunicorn.rag.py rag:app &
