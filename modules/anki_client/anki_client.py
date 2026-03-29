from ...utils import invoke, set_up_fields_for_model

from ...constants import CURR_LANG, CARD_TMPLT, \
                        FIELDS_EXCEL

class NoteGenerator:

    def card_from_txt(
        self,
        deck: str,
        fields: list,
        input_str: str, 
        output_str: str,
        image: str,
        audio: str,
        example: str
    ) -> dict:   
        """
        Function prepares ANKI Note to be send to a database - assigns attributes to correct columns
        """
        CARD_TMPLT['fields'] = set_up_fields_for_model(fields)
        CARD_TMPLT['fields'][FIELDS_EXCEL.get("front_text")] = input_str
        CARD_TMPLT['fields'][FIELDS_EXCEL.get("back_text")] = output_str
        CARD_TMPLT['fields'][FIELDS_EXCEL.get("example")] = example
        CARD_TMPLT['fields'][FIELDS_EXCEL.get("image")] = image
        CARD_TMPLT['fields'][FIELDS_EXCEL.get("audio")] = audio
        CARD_TMPLT['deckName'] = deck    
    
        return CARD_TMPLT


class AnkiClientConsole:
    def __init__(self, parent):
        self.parent = parent
        self.note_generator = NoteGenerator()

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
            deck=f"'{CURR_LANG}'"
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
                CURR_LANG,
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


class AnkiClientDesktop:
    def __init__(self, parent):
        self.parent = parent
        self.mw = self.parent.mw
        self.logger = self.parent.logger
        self.anki_backend = AnkiBackend(self)

    def get_all_models(self) -> list:
        return self.mw.col.models.all()

    def get_models_names(self) -> list:
        """
        Get available models (cards views)
        """
        result = [model["name"] for model in self.mw.col.models.all()]
        return result

    def get_cards_details(self, cards_list: list) -> list:
        """
        Function returns ANKI card information
        """
        result = self.anki_backend.cardsInfo(cards_list)
        return result
    
    def find_all_notes(self) -> list:
        """
        Function returns all available cards in all decks
        """
        self.parent.logger.info(f"find_all_notes: {self.mw}")
        result = self.mw.col.find_cards('deck:*')
        return result

    def get_fields_by_model_name(self, model_name) -> list:
        models = self.get_all_models()
        fields = [model.get("flds") for model in models if model["name"]==model_name]
        fields_names = list(map(lambda d: d["name"], fields[0]))
        return fields_names



class AnkiBackend:
    def __init__(self, parent):
        self.parent = parent
        self.mw = self.parent.mw

    def cardsInfo(self, cards) -> list:
        result = []
        for cid in cards:
            try:
                card = self.mw.col.getCard(cid)
                model = card.note_type()
                note = card.note()
                fields = {}
                for info in model['flds']:
                    order = info['ord']
                    name = info['name']
                    fields[name] = {'value': note.fields[order], 'order': order}
                states = self.mw.col._backend.get_scheduling_states(card.id)
                nextReviews = self.mw.col._backend.describe_next_states(states)

                result.append({
                    'cardId': card.id,
                    'fields': fields,
                    'fieldOrder': card.ord,
                    'question': self.cardQuestion(card),
                    'answer': self.cardAnswer(card),
                    'modelName': model['name'],
                    'ord': card.ord,
                    'deckName': self.deckNameFromId(card.did),
                    'css': model['css'],
                    'factor': card.factor,
                    #This factor is 10 times the ease percentage,
                    # so an ease of 310% would be reported as 3100
                    'interval': card.ivl,
                    'note': card.nid,
                    'type': card.type,
                    'queue': card.queue,
                    'due': card.due,
                    'reps': card.reps,
                    'lapses': card.lapses,
                    'left': card.left,
                    'mod': card.mod,
                    'nextReviews': list(nextReviews),
                    'flags': card.flags,
                })
            except NotFoundError:
                # Anki will give a NotFoundError if the card ID does not exist.
                # Best behavior is probably to add an 'empty card' to the
                # returned result, so that the items of the input and return
                # lists correspond.
                result.append({})

        return result

    def cardQuestion(self, card):
        if getattr(card, 'question', None) is None:
            return card._getQA()['q']

        return card.question()

    def cardAnswer(self, card):
        if getattr(card, 'answer', None) is None:
            return card._getQA()['a']

        return card.answer()
    
    def deckNameFromId(self, deckId):
        deck = self.collection().decks.get(deckId)
        if deck is None:
            raise Exception('deck was not found: {}'.format(deckId))

        return deck['name']