
#gunicorn --config gunicorn.inference.py inference:app

bind = "0.0.0.0:5001"
workers = 1  # Reducido ya que usamos Celery con concurrency=1
threads = 4
worker_class = 'gevent'
timeout = 900  # Aumentado a 15 minutos para coincidir con Celery
max_requests = 100
max_requests_jitter = 20