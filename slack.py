import requests
import json 
import os

class slack_webhook():
    def __init__(self,message):
        url = os.environ["SLACK_WEBHOOK"]
        payload = {"text": message}
        headers = {'Content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(payload), headers=headers)