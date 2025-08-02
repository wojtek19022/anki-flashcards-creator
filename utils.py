import json
import os
import urllib.request

from dotenv import load_dotenv

load_dotenv()
ANKI_API_URL=os.getenv('ANKI_API_URL')

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_API_URL, requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

@staticmethod
def set_up_fields_for_model(fields_list: list) -> dict:
    values = ['' for el in range(len(fields_list))]
    fields = dict(zip(fields_list, values))
    return fields