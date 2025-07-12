
#gunicorn --config gunicorn.rag.py rag:app

bind = "0.0.0.0:5002"
workers = 3  # Reducido para mejor gestión de recursos
threads = 2
timeout = 900  # Aumentado a 15 minutos
worker_class = 'gevent'  # Añadido para mejor manejo de conexiones asíncronas