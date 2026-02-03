import os
from dotenv import load_dotenv
from celery import Celery

load_dotenv()

celery_app = Celery(
    "judge",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.autodiscover_tasks(["app.tasks"])
