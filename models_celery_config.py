from celery import Celery

celery_app = Celery('models_tasks',  # Cambiado el nombre
                    broker='redis://localhost:6379/1',  # Usando diferente DB de Redis
                    backend='redis://localhost:6379/1')

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=300,  # 5 minutos debería ser suficiente para predicciones
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True
)