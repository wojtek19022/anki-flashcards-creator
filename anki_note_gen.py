import os
import logging

from constants import LOGGER, MODEL_NAME, LANGUAGES_DECKS, CURR_LANG, CARD_TMPLT

from utils import invoke

from modules import AnkiClient

class AnkiNoteGenerator:
    def __init__(self):
        self.current_lang = CURR_LANG
        self.card_template = CARD_TMPLT
        self.model_name = MODEL_NAME
        self.anki_client = AnkiClient(self)

    def main(self):
        logging.info("Creating of cards was started")
        if not self.model_name in self.anki_client.get_models_names():
            logging.error(f'Model with name: {self.model_name} is not on ANKI. Try with different name')
            return 
        
        if self.current_lang not in self.anki_client.get_decks_and_id().keys():
            logging.error(f'Cannot find deck with name: {self.current_lang} try again with different name')
            return 

        fields = self.anki_client.get_fields_by_model_name(self.model_name)
        
        result = self.anki_client.add_note(
            fields = fields,
            front_text = '111', 
            back_text = '111'
        )

        logging.info(f'Created ANKI card with ID: {result}')

if __name__ == "__main__":
    AnkiNoteGenerator().main()