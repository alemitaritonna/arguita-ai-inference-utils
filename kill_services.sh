#!/bin/bash

# Matar todas las sesiones de tmux
echo "Cerrando todas las sesiones tmux..."
tmux kill-server

# Matar procesos específicos
echo "Matando procesos de celery y gunicorn..."
pkill -f celery
pkill -f gunicorn

# Matar procesos en puertos específicos
echo "Liberando puertos..."
sudo kill -9 $(sudo lsof -t -i:5001) 2>/dev/null || true
sudo kill -9 $(sudo lsof -t -i:5003) 2>/dev/null || true

# Verificar procesos de Python que puedan quedar
echo "Verificando procesos de Python restantes..."
pkill -f python

# Esperar un momento para asegurar que todo se cierre
sleep 2

# Verificar que todo se haya cerrado correctamente
if pgrep -f celery > /dev/null || pgrep -f gunicorn > /dev/null; then
    echo "¡Advertencia! Algunos procesos siguen activos"
    echo "Procesos restantes:"
    ps aux | grep -E 'celery|gunicorn|python' | grep -v grep
else
    echo "Todos los procesos han sido terminados exitosamente"
fi

# Verificar puertos
echo "Verificando puertos..."
if lsof -i:5001 > /dev/null || lsof -i:5003 > /dev/null; then
    echo "¡Advertencia! Algunos puertos siguen ocupados"
    echo "Estado de los puertos:"
    sudo lsof -i:5001,5003
else
    echo "Todos los puertos han sido liberados exitosamente"
fi