import celery
from config import CELERY_BACKEND, CELERY_BROKER
import time

celery_app = celery.Celery(
    'task',
    backend=CELERY_BACKEND,
    broker=CELERY_BROKER
)


# делаем какую-то тяжелую работу по рассылке сообщений
@celery_app.task()
def send_mail(address_list):
    for address in address_list:
        time.sleep(2)
    return True

