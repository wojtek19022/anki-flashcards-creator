# import importlib
# anki_flashcards_creator = importlib.import_module("anki-flashcards-creator")

import aqt
from aqt.qt import *

from .constants import __name__
from .utils import Packages

from pathlib import Path

Packages().install(os.path.join(os.path.dirname(Path(__file__)),"requirements.txt"))

from .dialog.anki_note_gen_dialog import AnkiNoteGenDialog

dialog = AnkiNoteGenDialog(mw=aqt.mw)
action = QAction(__name__, aqt.mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, dialog.run)
# and add it to the tools menu
aqt.mw.form.menuTools.addAction(action)