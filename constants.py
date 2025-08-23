import logging
from utils import invoke

LOGGER = logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

LANGUAGES_DECKS = ""
MODEL_NAME = 'Basic Quizlet Extended'

CARD_TMPLT = {
  "deckName": "",
  "modelName": MODEL_NAME,
  "fields": {},
  "options": {
    "allowDuplicate": False
  },
  "tags": []
}

#Do dostosowania jeżeli będzie potrzeba zmiana nazw pól do wypełnienia dla karty
FIELDS = {
  "front_text": "FrontText",
  "front_audio": "FrontAudio",
  "back_test": "BackText",
  "back_audio": "BackAudio",
  "image": "Image",
  "example": "Example"
}

FIELDS_EXCEL = {
  "back_text":"word",
  "front_text":"definition",
  "example":"example"
}

CURR_LANG = '🇬🇧 Angielski'#'🇪🇸 Hiszpański'