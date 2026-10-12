from app.celery import celery_app
from app.services.historic_report_service import generate_user_historic_reports
from celery import Celery
from celery.schedules import crontab


@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0, day_of_month=1), 
        close_month.s(), 
        name='close_month_task'
    )


@celery_app.task
def close_month():
    return generate_user_historic_reports()

