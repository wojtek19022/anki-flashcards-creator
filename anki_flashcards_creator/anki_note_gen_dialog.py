from anki_note_gen_dialog_struct import AnkiNoteGenUI

class AnkiNoteGenUX:
    def __init__(self, parent=None):
        super().__init__(parent)
        AnkiNoteGenUI().setup_ui(self)
    def run(self):
        pass
    def onClose(self):
        pass