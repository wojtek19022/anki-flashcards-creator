# import importlib
# anki_flashcards_creator = importlib.import_module("anki-flashcards-creator")

import aqt
from aqt.qt import *
import os
import sys

sys.path.append(os.path.dirname(__file__))

from . import constants
from .dialog.anki_note_gen_dialog import AnkiNoteGenDialog
from . import utils

dialog = AnkiNoteGenDialog(mw=aqt.mw)
action = QAction(constants.__name__, aqt.mw)
# set it to call testFunction when it's clicked
qconnect(action.triggered, dialog.run)
# and add it to the tools menu
aqt.mw.form.menuTools.addAction(action)