
#gunicorn --config gunicorn.inference_models.py inference_models:app

# gunicorn.inference_models.py
bind = "0.0.0.0:5003"
workers = 1  # Reducido a 1 ya que usamos Celery para el procesamiento paralelo
threads = 2
timeout = 360  # 6 minutos, suficiente para predicciones
worker_class = 'gevent'
max_requests = 100
max_requests_jitter = 20