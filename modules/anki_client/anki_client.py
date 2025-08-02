from utils import invoke

class NoteGenerator:
    def __init__(self, parent):
        self.card_template = parent.card_template

    def card_from_txt(
        self,
        deck: str,
        input_test: str, 
        output_str: str
    ) -> int:
        self.card_template['fields']['Przód'] = input_test
        self.card_template['fields']['Tył'] = output_str
        self.card_template['deckName'] = deck    
    
        return self.card_template

    def on_finish(self):
        self.card_template = None


class AnkiClient:
    def __init__(self, parent):
        self.language = parent.current_lang
        self.card_template = parent.card_template
        self.note_generator = NoteGenerator(self)

    def get_decks_and_id(self) -> dict:
        result = invoke('deckNamesAndIds')
        return result

    def add_note(self, front_text, back_text) -> int:
        result = invoke(
            'addNote', 
            note = self.note_generator.card_from_txt(
                self.language,
                front_text,
                back_text
            )
        )
        self.note_generator.on_finish()
        return result
