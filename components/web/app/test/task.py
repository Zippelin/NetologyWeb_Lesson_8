import celery
from celery import worker
import time
import os

adr = os.getenv('hostip', '192.168.1.62')
POSTGRE_URI = f'postgresql://admin:admin@{adr}:5432/web_01'

app = celery.Celery(
    'task',
    backend='redis://172.22.32.1:6379/1',
    broker='redis://172.22.32.1:6379/2'
)


@app.task()
def test_task(sleep_time):
    time.sleep(sleep_time)
    return f'Awaken {sleep_time}'
