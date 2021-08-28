import os

backed_server = os.getenv('backend', f'172.22.32.1')
backed_db = os.getenv('backend_db', '2')

broker_server = os.getenv('broker', '172.22.32.1')
broker_db = os.getenv("broker_db", "1")

CELERY_BACKEND = f'redis://{backed_server}:6379/{backed_db}'
CELERY_BROKER = f'redis://{broker_server}:6379/{broker_db}'

print(CELERY_BROKER)
print(CELERY_BROKER)