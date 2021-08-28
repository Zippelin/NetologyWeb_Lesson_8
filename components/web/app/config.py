import os

adr = os.getenv('hostip', '192.168.1.62')
POSTGRE_URI = f'postgresql://admin:admin@{adr}:5432/web_01'