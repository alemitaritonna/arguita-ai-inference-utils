#!/bin/bash

# Matar el servidor tmux y procesos existentes
tmux kill-server
pkill -f celery
pkill -f gunicorn

# Matar procesos en puertos específicos
sudo kill -9 $(sudo lsof -t -i:5001) 2>/dev/null || true
sudo kill -9 $(sudo lsof -t -i:5003) 2>/dev/null || true

# Esperar un momento para asegurar que los puertos se liberen
sleep 2

# Crear una sesión principal
tmux new-session -d -s "RAG_SYSTEM"

# Dividir la ventana en 5 paneles
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v
tmux select-pane -t 2
tmux split-window -v

# Panel 0: RAG Celery Worker
tmux select-pane -t 0
tmux send-keys "cd /home/apps/inference" C-m
tmux rename-window -t 0 "RAG_CELERY"
tmux send-keys "source env/bin/activate" C-m
tmux send-keys "celery -A rag_celery_worker worker --loglevel=info --concurrency=1" C-m

# Panel 1: Servidor de inferencia
tmux select-pane -t 1
tmux rename-window -t 1 "INFERENCE"
tmux send-keys "cd /home/apps/inference" C-m
tmux send-keys "source env/bin/activate" C-m
tmux send-keys "gunicorn -c gunicorn.inference.py inference:app" C-m

# Panel 2: Servidor RAG
tmux select-pane -t 2
tmux rename-window -t 2 "RAG_SERVER"
tmux send-keys "cd /home/apps/rag" C-m
tmux send-keys "source env/bin/activate" C-m
tmux send-keys "gunicorn -c gunicorn.rag.py rag:app" C-m

# Panel 3: Models Celery Worker
tmux select-pane -t 3
tmux rename-window -t 3 "MODELS_CELERY"
tmux send-keys "cd /home/apps/inference" C-m
tmux send-keys "source env_models/bin/activate" C-m
tmux send-keys "celery -A models_celery_worker worker --loglevel=info --concurrency=1" C-m

# Panel 4: Servidor de inferencia de modelos
tmux select-pane -t 4
tmux rename-window -t 4 "MODELS_SERVER"
tmux send-keys "cd /home/apps/inference" C-m
tmux send-keys "source env_models/bin/activate" C-m
tmux send-keys "gunicorn -c gunicorn.inference_models.py inference_models:app" C-m

# Nombrar los paneles para mejor identificación
tmux select-pane -t 0 -T "RAG Celery"
tmux select-pane -t 1 -T "Inference"
tmux select-pane -t 2 -T "RAG Server"
tmux select-pane -t 3 -T "Models Celery"
tmux select-pane -t 4 -T "Models Server"

# Configurar barra de estado para mostrar nombres
tmux set -g pane-border-status top
tmux set -g pane-border-format "#{pane_index} #{pane_title}"

# Seleccionar el primer panel
tmux select-pane -t 0

# Adjuntar a la sesión
tmux attach-session -t RAG_SYSTEM