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
        self.connectSignals()

    def connectSignals(self):
        self.plugin_dlg.searchLineEdit.textChanged.connect(self.inputFileChanged)
        self.plugin_dlg.okPushButton.clicked.connect(self.prepareInputs)
        self.plugin_dlg.searchPushButton.clicked.connect(self.openFilesWindow)
        self.plugin_dlg.closePushButton.clicked.connect(self.closePlugin)
        self.plugin_dlg.settingsPushButton.clicked.connect(self.openSettings)
        self.plugin_dlg.rejected.connect(self.onClose)

    def inputFileChanged(self):
        input_file = self.plugin_dlg.searchLineEdit.text()
        if input_file and os.path.exists(input_file):
            # TODO tutaj trzeba dodać fragment do odczytywania w locie zawartości pliku XLSX (headerów i wpisać w comboboxy)
            self.plugin_dlg.settingsPushButton.setEnabled(True)
            self.plugin_dlg.okPushButton.setEnabled(False)
        else:
            self.plugin_dlg.settingsPushButton.setEnabled(False)
            self.plugin_dlg.okPushButton.setEnabled(False)

    def prepareInputs(self):
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

    def openFilesWindow(self):
        file_dlg = QtWidgets.QFileDialog
        file_name = file_dlg.getOpenFileName(self, caption="Select an excel file",filter="XLSX (*.xlsx);;XLS (*.xls)")
        
        if isinstance(file_name,str) and file_name:
            if os.path.exists(str(file_name)):
                self.plugin_dlg.searchLineEdit.setText(str(file_name))
        elif isinstance(file_name,tuple) and file_name:
            file = str(list(file_name)[0])
            if os.path.exists(file):
                self.plugin_dlg.searchLineEdit.setText(file)

    def openSettings(self):
        self.settings_dlg.run()

    def run(self):
        self.plugin_dlg.show()

    def closePlugin(self):
        self.plugin_dlg.hide()
    
    def onClose(self):
        self.settings_dlg.selected_native_lang_text = ""
        self.settings_dlg.selected_foreign_lang_text = ""
        self.settings_dlg.selected_example_field = ""
        self.settings_dlg.selected_deck_name = ""
        self.settings_dlg.selected_model_name = ""
        self.input_path = ""
        self.plugin_dlg.searchLineEdit.setText("")


class AnkiNoteGenSettingsDialog(QtWidgets.QDialog, SETTINGS_DLG_FORM):
    def __init__(self, parent):
        super(AnkiNoteGenSettingsDialog, self).__init__(parent)
        self.settings_dlg = self
        self.setupUi(self)
        self.parent = parent
        self.plugin_dlg = self.parent.plugin_dlg
        self.mw = self.parent.mw
        self.logger = self.parent.logger
        self.input_path = self.parent.input_path
        self.selected_native_lang_text = ""
        self.selected_foreign_lang_text = ""
        self.selected_example_field = ""
        self.selected_deck_name = ""
        self.selected_model_name = ""
        self.encoder = Encoder()
        self.excel_worker = ExcelWorker(self)
        self.connectSignals()

    def connectSignals(self):
        self.settings_dlg.nativeLangTextCbx.currentTextChanged.connect(self.assignNewNativeLang)
        self.settings_dlg.foreignLangTextCbx.currentTextChanged.connect(self.assignNewForeignLang)
        self.settings_dlg.examplesCbx.currentTextChanged.connect(self.assignNewExampleField)
        self.settings_dlg.deckNameTextCbx.currentTextChanged.connect(self.assignNewDeckName)
        self.settings_dlg.modelNameTextCbx.currentTextChanged.connect(self.assignNewModelName)
        self.settings_dlg.rejected.connect(self.onClose)

    def assignNewNativeLang(self) -> None:
        self.selected_native_lang_text = self.settings_dlg.nativeLangTextCbx.currentText()
        self.logger.info(
            f"No data had been detected for variable {self.selected_native_lang_text.encode('utf-8')}. Below data had been added: {self.settings_dlg.nativeLangTextCbx.currentText().encode('utf-8')}"
        )

    def assignNewForeignLang(self) -> None:
        self.selected_foreign_lang_text = self.settings_dlg.foreignLangTextCbx.currentText()
        self.logger.info(
            f"No data had been detected for variable {self.selected_foreign_lang_text.encode('utf-8')}. Below data had been added: {self.settings_dlg.foreignLangTextCbx.currentText().encode('utf-8')}"
        )

    def assignNewExampleField(self) -> None:
        self.selected_example_field = self.settings_dlg.examplesCbx.currentText()
        self.logger.info(
            f"No data had been detected for variable {self.selected_example_field.encode('utf-8')}. Below data had been added: {self.settings_dlg.examplesCbx.currentText().encode('utf-8')}"
        )

    def assignNewDeckName(self) -> None:
        self.selected_deck_name = self.settings_dlg.deckNameTextCbx.currentText()
        self.logger.info(
            f"No data had been detected for variable {self.selected_deck_name.encode('utf-8')}. Below data had been added: {self.settings_dlg.deckNameTextCbx.currentText().encode('utf-8')}"
        )

    def assignNewModelName(self) -> None:
        self.selected_model_name = self.settings_dlg.modelNameTextCbx.currentText()
        self.logger.info(
            f"No data had been detected for variable {self.selected_model_name.encode('utf-8')}. Below data had been added: {self.settings_dlg.modelNameTextCbx.currentText().encode('utf-8')}"
        )

    # def setVariableForItemData(self, variable, data) -> None:
    #     self.logger.info(
    #         f"No data had been detected for variable {variable.encode('utf-8')}. Below data had been added: {data.encode('utf-8')}"
    #     )
    #     variable = data
    
    def checkEmptySettingsData(self):
        """
        Funkcja sprawdza czy w settingsach nie ma danych.
        Jeżeli nie ma żadnych danych, funkcja zwraca True.
        Jeżeli coś jest w settingsach, funkcja zwraca False
        """
        if not self.selected_native_lang_text and \
            not self.selected_foreign_lang_text and \
            not self.selected_example_field and \
            not self.selected_deck_name and \
            not self.selected_model_name: 
            self.logger.info("No data had been previously added to settings. Initializing")
            return True
        else:
            return False
    
    def fillValues(self, headers):
        self.anki_client_desktop = AnkiClientDesktop(self)

        self.settings_dlg.nativeLangTextCbx.addItems(headers)
        self.settings_dlg.foreignLangTextCbx.addItems(headers)
        self.settings_dlg.examplesCbx.addItems(headers)
        self.orderItemsInSettingsFields()

        self.settings_dlg.deckNameTextCbx.addItems(self.anki_client_desktop.getDecksAndID().keys()) 
        self.settings_dlg.modelNameTextCbx.addItems(self.anki_client_desktop.getModelsAndID().keys())

    def orderItemsInSettingsFields(self):
        self.settings_dlg.nativeLangTextCbx.setCurrentIndex(0)
        self.settings_dlg.foreignLangTextCbx.setCurrentIndex(1)
        self.settings_dlg.examplesCbx.setCurrentIndex(2)

    def run(self):
        self.excel_df = self.excel_worker.regularExcelToDf(str(self.parent.plugin_dlg.searchLineEdit.text()))
        headers = self.excel_worker.readHeaders(self.excel_df)
        if self.checkEmptySettingsData():
            self.fillValues(headers)
        self.settings_dlg.show()

    def onClose(self):
        self.plugin_dlg.okPushButton.setEnabled(True)
        # self.selected_native_lang_text = ""
        # self.selected_foreign_lang_text = ""
        # self.selected_example_field = ""
        # self.selected_deck_name = ""
        # self.selected_model_name = ""
        # self.settings_dlg.nativeLangTextCbx.clear()
        # self.settings_dlg.foreignLangTextCbx.clear()
        # self.settings_dlg.examplesCbx.clear()
        # self.settings_dlg.deckNameTextCbx.clear()
        # self.settings_dlg.modelNameTextCbx.clear()

