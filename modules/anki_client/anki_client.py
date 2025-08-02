from utils import invoke, set_up_fields_for_model
from dataclasses import dataclass

from constants import FIELDS

class NoteGenerator:
    def __init__(self, parent):
        self.card_template = parent.card_template
        self.fields = FIELDS

    def card_from_txt(
        self,
        deck: str,
        fields: list,
        input_test: str, 
        output_str: str
    ) -> int:   
        self.card_template['fields'] = set_up_fields_for_model(fields)
        self.card_template['fields'][self.fields.get("front_text")] = input_test
        self.card_template['fields'][self.fields.get("back_text")] = output_str
        self.card_template['deckName'] = deck    
    
        return self.card_template

    def on_finish(self):
        self.card_template = None


class AnkiClient:
    def __init__(self, parent):
        self.language = parent.current_lang
        self.card_template = parent.card_template
        self.note_generator = NoteGenerator(self)

    @staticmethod
    def get_fields_by_model_name(model_name):
        result = invoke('modelFieldNames', modelName=model_name)
        return result

    @staticmethod
    def get_models_names():
        result = invoke('modelNames')
        return result

    @staticmethod
    def get_decks_and_id() -> dict:
        result = invoke('deckNamesAndIds')
        return result

    @staticmethod
    def get_fields_for_deck():
        result = invoke('getDeckConfig',deck=f"'{self.language}'")

    def set_up_fields(self):
        pass

    def add_note(self, fields, front_text, back_text) -> int:
        result = invoke(
            'addNote', 
            note = self.note_generator.card_from_txt(
                self.language,
                fields,
                front_text,
                back_text
            )
        )
        self.note_generator.on_finish()
        return result
