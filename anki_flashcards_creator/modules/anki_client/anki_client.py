from utils import invoke, set_up_fields_for_model
from dataclasses import dataclass

class NoteGenerator:
    def __init__(self, parent):
        self.card_template = parent.card_template
        self.fields = parent.fields_anki

    def card_from_txt(
        self,
        deck: str,
        fields: list,
        input_str: str, 
        output_str: str,
        image: str,
        audio: str,
        example: str
    ) -> int:   
        """
        Function prepares ANKI Note to be send to a database - assigns attributes to correct columns
        """
        self.card_template['fields'] = set_up_fields_for_model(fields)
        self.card_template['fields'][self.fields.get("front_text")] = input_str
        self.card_template['fields'][self.fields.get("back_text")] = output_str
        self.card_template['fields'][self.fields.get("example")] = example
        self.card_template['fields'][self.fields.get("image")] = image
        self.card_template['fields'][self.fields.get("audio")] = audio
        self.card_template['deckName'] = deck    
    
        return self.card_template


class AnkiClient:
    def __init__(self, parent):
        self.language = parent.current_lang
        self.card_template = parent.card_template
        self.fields_anki = parent.fields_anki
        self.note_generator = NoteGenerator(self)

    @staticmethod
    def get_fields_by_model_name(model_name: str) -> list:
        """
        Get fields of a card view
        """
        result = invoke(
            'modelFieldNames', 
            modelName=model_name
        )
        return result

    @staticmethod
    def get_models_names() -> list:
        """
        Get available models (cards views)
        """
        result = invoke('modelNames')
        return result

    @staticmethod
    def get_decks_and_id() -> dict:
        """
        Get all decks with assigned ids
        """
        result = invoke('deckNamesAndIds')
        return result

    @staticmethod
    def get_fields_for_deck():
        """
        Get selected deck config
        """
        result = invoke(
            'getDeckConfig',
            deck=f"'{self.language}'"
        )

    def add_note(
        self, 
        fields: list, 
        front_text: str, 
        back_text: str, 
        example: str, 
        image: str, 
        audio: str
    ) -> int:
        """
        Function adds an ANKI card from input card view
        """
        result = invoke(
            'addNote', 
            note = self.note_generator.card_from_txt(
                self.language,
                fields = fields,
                input_str = front_text,
                output_str = back_text,
                example = example,
                image = image,
                audio = audio
            )
        )

        return result

    def find_all_notes(self) -> list:
        """
        Function returns all available cards in all decks
        """
        result = invoke(
            'findCards',
            query = f"deck:*" 
        )
        return result

    def get_cards_details(self, cards_list: list) -> dict:
        """
        Function returns ANKI card information
        """
        result = invoke(
            'cardsInfo',
            cards = cards_list 
        )
        return result

    def store_file_in_anki(self, filename: str, url: str) -> str:
        """
        Function stores any kind of a file from URL
        """
        result = invoke(
            'storeMediaFile',
            filename= filename,
            url= url
        )
        return result

    def retrieve_uploaded_file(self, filename: str) -> str:
        """
        Function returns a file that was added into ANKI files repository
        """
        result = invoke(
            'retrieveMediaFile',
            filename= filename
        )
        return result
        