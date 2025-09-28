import os
import asyncio

from aqt.qt import *
from PyQt6 import QtWidgets, uic
from pathlib import Path

from .anki_note_creator_ui import Ui_Dialog
from ..anki_note_gen import AnkiNoteGenerator

FORM, _ = uic.load_ui.loadUiType(os.path.join(os.path.dirname(__file__), 'anki_note_creator_ui.ui'))

class AnkiNoteGenDialog(QtWidgets.QDialog, FORM):
    def __init__(self, mw, parent=None):
        super(AnkiNoteGenDialog, self).__init__(parent)
        self.plugin_dlg = self
        self.setupUi(self)
        self.mw = mw
        self.note_generator = AnkiNoteGenerator(self.mw)
        self.connect_signals()

    def connect_signals(self):
        self.plugin_dlg.okPushButton.clicked.connect(self.prepare_inputs)
        self.plugin_dlg.searchPushButton.clicked.connect(self.open_files_window)
        self.plugin_dlg.closePushButton.clicked.connect(self.close_plugin)

    def prepare_inputs(self):
        if not self.note_generator.console_used:
            input_path = self.plugin_dlg.searchLineEdit.text()
            if input_path == 0 or not input_path:
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Please select existing XLSX file"
                )
                return
        else:
            input_path = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        
        if os.path.exists(input_path):
            asyncio.run(self.note_generator.main(input_path))

    def open_files_window(self):
        file_dlg = QtWidgets.QFileDialog
        file_name = file_dlg.getOpenFileName(self, caption="Select an XLSX file",filter="XLSX (*.xlsx);;XLS (*.xls)")
        
        if isinstance(file_name,str) and file_name:
            if os.path.exists(str(file_name)):
                self.plugin_dlg.searchLineEdit.setText(str(file_name))
        elif isinstance(file_name,tuple) and file_name:
            file = str(list(file_name)[0])
            if os.path.exists(file):
                self.plugin_dlg.searchLineEdit.setText(file)

    def run(self):
        self.plugin_dlg.show()

    def close_plugin(self):
        self.plugin_dlg.hide()
    
    def onClose(self):
        pass