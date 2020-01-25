import json
import requests

api_url = 'http://127.0.0.1:8000/webhooks/webharvest/'

payload = {'name': 'andre',
           'payload': 'noobs only 1-5 please',
           'dog': 'Dante'
           }

r = requests.post(api_url, data=payload)