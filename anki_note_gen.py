import genanki
import os

from constants import LANGUAGES_DECKS, CURR_LANG, CARD_TMPLT

from utils import invoke

from modules import AnkiClient

class AnkiNoteGenerator:
    def __init__(self):
        self.current_lang = CURR_LANG
        self.card_template = CARD_TMPLT
        self.anki_client = AnkiClient(self)

    def main(self):
        result = self.anki_client.add_note(
            front_text = '111', 
            back_text = '111'
        )
        print(f'Created a card with ID: {result}')

# result = invoke("findCards",query="deck:*")
# result = invoke('getDecks',cards=result)
# for res in result:
#     print(res)

if __name__ == "__main__":
    AnkiNoteGenerator().main()