import json
import os
import urllib.request
import pathlib
import base64
# std
import importlib
import sys
import subprocess
import logging
from pathlib import Path


from .constants import CONSOLE_USED

if CONSOLE_USED:
    from dotenv import load_dotenv

    env_path = os.path.join(Path(__file__).parent,'.env')
    load_dotenv(dotenv_path=env_path)
    ANKI_API_URL=os.getenv('ANKI_API_URL')
else:
    ANKI_API_URL = ""

def request(action, **params):
    return {
        'action': action, 
        'params': params, 
        'version': 6
    }

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
def clear_string(word: str) -> str:
    try:
        return word.rstrip()
    except AttributeError:
        return word if word else ""

@staticmethod
def set_up_fields_for_model(fields_list: list) -> dict:
    values = ['' for _ in range(len(fields_list))]
    fields = dict(zip(fields_list, values))
    return fields

@staticmethod
def check_excel_data(data: str) -> bool:
    allowed_formats = ["xlsx","xls"]

    if os.path.exists(data) and pathlib.Path.suffix(data) in allowed_formats:
        return True
    else:
        return False

@staticmethod
def get_dict_link_for_lang(lang_dict, select_lang):
    return lang_dict.get(select_lang)


class Encoder:
    @staticmethod
    def encode_string(filepath: str):
        return base64.b64encode(filepath.encode("utf-8"))


class Packages:

    def install(self, deps):
        import subprocess
        import sys
        # Install a package using pip via subprocess

        subprocess.run([sys.executable, "-m", "pip", "install", "-r", deps], check=True)

class Logger:
    """
    Logging client for unique logging system for client
    """
    def __init__(self, name: str, log_file: str = "flashcards_creator_log.log"):
        # Create logger
        self.logger = logging.getLogger(name)
        self.handler = logging.FileHandler(log_file)
        self.setLogsFormat()
        self.setLogsLevel()
        self.logger.addHandler(self.handler)

    def setLogsFormat(self) -> None:
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        self.handler.setFormatter(formatter)

    def setLogsLevel(self, log_level: logging.log = logging.INFO):
        self.logger.setLevel(log_level)

