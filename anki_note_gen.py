import os
import logging

from constants import LOGGER, MODEL_NAME, LANGUAGES_DECKS, FIELDS, FIELDS_EXCEL, CURR_LANG, CARD_TMPLT

from utils import invoke

from modules import AnkiClient, ExcelWorker

class AnkiNoteGenerator:
    def __init__(self, data):
        self.current_lang = CURR_LANG
        self.card_template = CARD_TMPLT
        self.model_name = MODEL_NAME
        self.fields_anki = FIELDS
        self.fields_data = FIELDS_EXCEL
        self.anki_client = AnkiClient(self)
        self.cards_in_deck = [
            card for card in self.anki_client.get_cards_details(self.anki_client.find_all_notes()) \
            if card["deckName"] == self.current_lang and card["modelName"] == self.model_name
        ]
        self.data = data
        self.data_cols = []

    def main(self):
        logging.info("Creating of cards was started")
        if not self.model_name in self.anki_client.get_models_names():
            logging.error(f'Model with name: {self.model_name} is not on ANKI. Try with different name')
            return 
        
        if self.current_lang not in self.anki_client.get_decks_and_id().keys():
            logging.error(f'Cannot find deck with name: {self.current_lang} try again with different name')
            return 

        fields = self.anki_client.get_fields_by_model_name(self.model_name)
        self.data = ExcelWorker.excel_to_df(self.data)

        if not self.data:
            return
        
        for row in self.data:
            if row["definition"] not in [note["fields"][self.fields_anki.get("front_text")]["value"] for note in self.cards_in_deck]:
                result = self.anki_client.add_note(
                    fields = fields,
                    front_text = row[self.fields_data.get("front_text")], 
                    back_text = row[self.fields_data.get("back_text")],
                    example = row[self.fields_data.get("example")]
                )
                logging.info(f'Created ANKI card with ID: {result}')
            else:
                logging.error("Word is already used for some card in in Anki")
            break

if __name__ == "__main__":
    while True:
        data = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        generator = AnkiNoteGenerator(data)
        if os.path.exists(data):
            generator.main()
            break