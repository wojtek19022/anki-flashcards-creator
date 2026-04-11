import logging

__name__ = "Anki notes creator"
__version = "2.0.0"
__author__ = "Wojciech Sołyga"

CONSOLE_USED = False
DEFAULT_NUM_PROC = 3
DEFAULT_TIMEOUT = 10
MIN_LOGS_LEVEL = logging.INFO

SYSTEM_ENCODING = "cp1250"
CURR_LANG = "🇬🇧 Angielski" #"English" #"English" #'🇬🇧 Angielski'#'🇪🇸 Hiszpański'
LANGUAGES_DECKS = ""
MODEL_NAME = 'Słownictwo z odwrotną kartą i multimediami'

CARD_TMPLT = {
  "deckName": CURR_LANG,
  "modelName": MODEL_NAME,
  "fields": {},
  "options": {
    "allowDuplicate": False
  },
  "tags": []
}

DIKI_MAIN_URL = "https://www.diki.pl/"

#link do słownika dicki z którego będziemy brać słówka z danego języka
DICT_LANG_SEARCH_URLS = {
  "🇪🇸  Español": "https://www.diki.pl/slownik-hiszpanskiego",
  "🇪🇸 Hiszpański": "https://www.diki.pl/slownik-hiszpanskiego",
  "🇬🇧 Angielski": "https://www.diki.pl/slownik-angielskiego",
  "English": "https://www.diki.pl/slownik-angielskiego",
  "test": "https://www.diki.pl/slownik-hiszpanskiego"
  # "test": "https://www.diki.pl/slownik-angielskiego"
}

#Do dostosowania jeżeli będzie potrzeba zmiana nazw pól do wypełnienia dla karty
FIELDS = {
  "front_text": "Słowo PL",
  # "front_audio": "FrontAudio",
  "back_text": "Słowo EN",
  # "back_audio": "BackAudio",
  "image": "Obrazek",
  "audio": "Audio",
  "example": "Przykład EN"
}

FIELDS_EXCEL = {
  "back_text":"word",
  "front_text":"definition",
  "example":"example"
}