import logging

__name__ = "Anki notes creator"
LOGGER = logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

CONSOLE_USED = False
DEFAULT_NUM_PROC = 3

LANGUAGES_DECKS = ""
MODEL_NAME = 'Słownictwo z odwrotną kartą i multimediami'

CARD_TMPLT = {
  "deckName": "",
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
  "🇪🇸 Hiszpański": "https://www.diki.pl/slownik-hiszpanskiego",
  "🇬🇧 Angielski": "https://www.diki.pl/slownik-angielskiego",
  "English": "https://www.diki.pl/slownik-angielskiego",
  "test": "https://www.diki.pl/slownik-hiszpanskiego"
  # "test": "https://www.diki.pl/slownik-angielskiego"
}

#Do dostosowania jeżeli będzie potrzeba zmiana nazw pól do wypełnienia dla karty
FIELDS = {
  "front_text": "Słowo PL",
  "front_audio": "FrontAudio",
  "back_text": "Słowo EN",
  "back_audio": "BackAudio",
  "image": "Obrazek",
  "audio": "Audio",
  "example": "Przykład EN"
}

FIELDS_EXCEL = {
  "back_text":"word",
  "front_text":"definition",
  "example":"example"
}

CURR_LANG = "English" #"English" #'🇬🇧 Angielski'#'🇪🇸 Hiszpański'