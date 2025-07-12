from celery import Celery

celery_app = Celery('inference_tasks',
                    broker='redis://localhost:6379/0',
                    backend='redis://localhost:6379/0')

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_time_limit=900,
    task_soft_time_limit=600,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True
)