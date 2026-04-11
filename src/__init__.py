# import importlib
# anki_flashcards_creator = importlib.import_module("anki-flashcards-creator")

import os
import asyncio
from pathlib import Path
from .utils import Packages

Packages().install(os.path.join(os.path.dirname(Path(__file__)),"requirements.txt"))

from .constants import __name__, CONSOLE_USED

class AnkiNotesGeneratorPlugin:
    def __init__(self) -> None:
        if not CONSOLE_USED:
            from aqt import mw
            from aqt.qt import QAction, qconnect

            from .dialog.anki_note_gen_dialog import AnkiNoteGenDialog

            dialog = AnkiNoteGenDialog(mw=mw)
            action = QAction(__name__, mw)
            # set it to call testFunction when it's clicked
            qconnect(action.triggered, dialog.run)
            # and add it to the tools menu
            mw.form.menuTools.addAction(action)

        else:
            from .anki_note_gen import AnkiNoteGenerator
            while True:
                self.input_path = str(input("Type in a directory to excel data with words to ANKI integrator: "))
                generator = AnkiNoteGenerator(self)
                if os.path.exists(self.input_path):
                    asyncio.run(generator.main(self.input_path))
                    break

AnkiNotesGeneratorPlugin()