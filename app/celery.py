from celery import Celery
import os


celery_app = Celery(__name__, include=['tasks.csv_tasks'])

celery_app.conf.update(
    # --- Connectivity (Broker) ---
    broker_url = (
        f"pyamqp://"
        f"{os.getenv('RABBITMQ_DEFAULT_USER')}:"
        f"{os.getenv('RABBITMQ_DEFAULT_PASS')}"
        f"@rabbitmq:5672//"
    ),
    
    # --- Timezone ---
    timezone='America/Sao_Paulo',
    enable_utc=True,

    # --- Performance and Concurrency ---
    worker_concurrency=1,
    worker_prefetch_multiplier=2,
    
    # --- Security and Serialization ---
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],

    # --- Failure Handling ---
    task_acks_late=True,
    worker_max_tasks_per_child=100,
    
    # --- Time Limits (Timeouts) ---
    task_time_limit=300,
    task_soft_time_limit=150,
)
