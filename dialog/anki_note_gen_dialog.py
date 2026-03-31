import os
import asyncio
import subprocess

from aqt.qt import *
from PyQt6 import QtWidgets, uic
from pathlib import Path

from ..utils import Logger, Encoder
from ..constants import __name__ as plugin_name, \
                        CARD_TMPLT, CONSOLE_USED

from .anki_note_creator_ui import Ui_Dialog
from ..anki_note_gen import AnkiNoteGenerator
from ..modules import ExcelWorker, AnkiClientDesktop

MAIN_DLG_FORM, _ = uic.load_ui.loadUiType(os.path.join(os.path.dirname(__file__), 'anki_note_creator_ui.ui'))
SETTINGS_DLG_FORM, _ = uic.load_ui.loadUiType(os.path.join(os.path.dirname(__file__), 'anki_note_settings_ui.ui'))

class AnkiNoteGenDialog(QtWidgets.QDialog, MAIN_DLG_FORM):
    def __init__(self, mw, parent=None):
        super(AnkiNoteGenDialog, self).__init__(parent)
        self.plugin_dlg = self
        self.setupUi(self)
        self.mw = mw
        self.input_path = ""
        self.logging_client = Logger(name = plugin_name)
        self.logger = self.logging_client.logger
        self.settings_dlg = AnkiNoteGenSettingsDialog(self)
        self.note_generator = AnkiNoteGenerator(self)
        self.connect_signals()

    def connect_signals(self):
        self.plugin_dlg.searchLineEdit.textChanged.connect(self.input_file_changed)
        self.plugin_dlg.okPushButton.clicked.connect(self.prepare_inputs)
        self.plugin_dlg.searchPushButton.clicked.connect(self.open_files_window)
        self.plugin_dlg.closePushButton.clicked.connect(self.close_plugin)
        self.plugin_dlg.settingsPushButton.clicked.connect(self.open_settings)

    def input_file_changed(self):
        input_file = self.plugin_dlg.searchLineEdit.text()
        if input_file and os.path.exists(input_file):
            # TODO tutaj trzeba dodać fragment do odczytywania w locie zawartości pliku XLSX (headerów i wpisać w comboboxy)
            self.plugin_dlg.settingsPushButton.setEnabled(True)
            self.plugin_dlg.okPushButton.setEnabled(True)
        else:
            self.plugin_dlg.settingsPushButton.setEnabled(False)
            self.plugin_dlg.okPushButton.setEnabled(False)

    def prepare_inputs(self):
        if not CONSOLE_USED:
            self.input_path = self.plugin_dlg.searchLineEdit.text()
            if self.input_path == 0 or not self.input_path:
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Please select existing excel file"
                )
                return
        else:
            self.input_path = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        
        if os.path.exists(self.input_path):
            asyncio.run(self.note_generator.main(self.input_path))

    def open_files_window(self):
        file_dlg = QtWidgets.QFileDialog
        file_name = file_dlg.getOpenFileName(self, caption="Select an excel file",filter="XLSX (*.xlsx);;XLS (*.xls)")
        
        if isinstance(file_name,str) and file_name:
            if os.path.exists(str(file_name)):
                self.plugin_dlg.searchLineEdit.setText(str(file_name))
        elif isinstance(file_name,tuple) and file_name:
            file = str(list(file_name)[0])
            if os.path.exists(file):
                self.plugin_dlg.searchLineEdit.setText(file)

    def open_settings(self):
        self.settings_dlg.run()

    def run(self):
        self.plugin_dlg.show()

    def close_plugin(self):
        self.plugin_dlg.hide()
    
    def onClose(self):
        pass

class AnkiNoteGenSettingsDialog(QtWidgets.QDialog, SETTINGS_DLG_FORM):
    def __init__(self, parent):
        super(AnkiNoteGenSettingsDialog, self).__init__(parent)
        self.settings_dlg = self
        self.setupUi(self)
        self.parent = parent
        self.mw = self.parent.mw
        self.logger = self.parent.logger
        self.input_path = self.parent.input_path
        self.encoder = Encoder()
        self.excel_worker = ExcelWorker(self)
        self.connect_signals()

    def connect_signals(self):
        pass
    
    def fill_values(self, headers):
        if (
            self.settings_dlg.nativeLangTextCbx.currentText() or \
            self.settings_dlg.foreignLangTextCbx.currentText() or \
            self.settings_dlg.examplesCbx.currentText() or \
            self.settings_dlg.deckNameTextCbx.currentText() or \
            self.settings_dlg.modelNameTextCbx.currentText()
        ):
            self.settings_dlg.nativeLangTextCbx.clear()
            self.settings_dlg.foreignLangTextCbx.clear()
            self.settings_dlg.examplesCbx.clear()
            self.settings_dlg.deckNameTextCbx.clear()
            self.settings_dlg.modelNameTextCbx.clear()

        self.anki_client_desktop = AnkiClientDesktop(self)

        self.settings_dlg.nativeLangTextCbx.addItems(headers)
        self.settings_dlg.foreignLangTextCbx.addItems(headers)
        self.settings_dlg.examplesCbx.addItems(headers)
        self.order_items_in_settings_fields()

        self.settings_dlg.deckNameTextCbx.addItems(self.anki_client_desktop.get_decks_and_id().keys()) 
        self.settings_dlg.modelNameTextCbx.addItems(self.anki_client_desktop.get_models_and_id().keys())

    def order_items_in_settings_fields(self):
        self.settings_dlg.nativeLangTextCbx.setCurrentIndex(0)
        self.settings_dlg.foreignLangTextCbx.setCurrentIndex(1)
        self.settings_dlg.examplesCbx.setCurrentIndex(2)

    def run(self):
        self.excel_df = self.excel_worker.regular_excel_to_df(str(self.parent.plugin_dlg.searchLineEdit.text()))
        headers = self.excel_worker.read_headers(self.excel_df)
        self.fill_values(headers)
        self.settings_dlg.show()

    def onClose(self):
        pass