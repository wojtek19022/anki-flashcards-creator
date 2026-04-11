import os
import logging
import asyncio

from concurrent.futures import ThreadPoolExecutor
from aqt.qt import QMessageBox

from .constants import __name__ as plugin_name, \
                        SYSTEM_ENCODING, \
                        CONSOLE_USED, CURR_LANG, DEFAULT_NUM_PROC, \
                        MODEL_NAME, FIELDS_EXCEL, FIELDS, DICT_LANG_SEARCH_URLS


from .utils import clear_string, get_dict_link_for_lang, Logger, Encoder
from .modules import AnkiClientConsole, AnkiClientDesktop, \
                    AnkiModulesValidator, \
                    ExcelWorker, WebsiteScrapper

# import anki plugin GUI components
if CONSOLE_USED:    
    import psutil

class AnkiNoteGenerator:
    def __init__(self, parent):
        self.parent = parent
        self.mw = self.parent.mw
        self.logging_client = Logger(name = plugin_name)
        self.logger = self.logging_client.logger
        self.logger.debug(f"NOTE GENERATOR: {self.mw}")
        self.encoder = Encoder()
        self.selected_model_name = ""
        self.selected_deck_name = ""
        self.selected_native_lang_text = ""
        self.selected_foreign_lang_text = ""
        self.selected_example_field = ""
        self.anki_modules_validator = AnkiModulesValidator(self)
        self.anki_client_console = AnkiClientConsole(self)

        if not CONSOLE_USED:
            self.settings_dlg = self.parent.settings_dlg
            self.anki_client_desktop = AnkiClientDesktop(self)

        self.excel_worker = ExcelWorker(self)
        self.website_scrapper = WebsiteScrapper() 
        self.data = ""
        self.data_cols = []
        self.max_threads = max(1, int(psutil.cpu_count() * 0.8)) if CONSOLE_USED else DEFAULT_NUM_PROC# Calculate the number of threads to use (80% of available CPU cores)
        self.logger.info("Program został prawidłowo zainicjalizowany")

    async def main(self, input_path):
        self.data = input_path

        self.cards_in_deck = self.anki_client_console.getAllCardsInDeck() if CONSOLE_USED \
                                else self.anki_client_desktop.getAllCardsInDeck()
        if not CONSOLE_USED:
            self.selected_model_name = self.settings_dlg.selected_model_name
            self.selected_deck_name = self.settings_dlg.selected_deck_name
            self.selected_native_lang_text = self.settings_dlg.selected_native_lang_text
            self.selected_foreign_lang_text = self.settings_dlg.selected_foreign_lang_text
            self.selected_example_field = self.settings_dlg.selected_example_field

        self.fields = self.anki_client_console.getFieldsByModelName(MODEL_NAME) if CONSOLE_USED \
                        else self.anki_client_desktop.getFieldsByModelName(self.selected_model_name)

        is_valid_struct = self.anki_modules_validator.validateStructure(
            input_structure=self.fields,
            dest_structure=FIELDS
        )

        if not is_valid_struct:
            if not CONSOLE_USED:
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Structure of fields in model is not correct. Look at logs"
                )   
            encoded_input_fields = [field.encode('utf-8') for field in self.fields]
            encoded_dest_fields = [field.encode('utf-8') for field in FIELDS.values()]
            self.logger.warning(f"Structure of fields in model is not correct: {encoded_input_fields}. It should be: {encoded_dest_fields}")
            return 

        self.logger.info("Creating of cards was started")

        if CONSOLE_USED:
            if not MODEL_NAME in self.anki_client_console.getModelsNames():
                self.logger.error(f'Model with name: {MODEL_NAME} is not on ANKI. Try with different name')
                return 
            
            if CURR_LANG not in self.anki_client_console.getDecksAndID().keys():
                self.logger.error(f'Cannot find deck with name: {CURR_LANG} try again with different name')
                return 
        else:
            if not self.selected_model_name in self.anki_client_desktop.getModelsNames():
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Model with name: {self.selected_model_name} is not on ANKI. <br>Try with different name"
                )
                self.logger.critical(f'Model with name: {self.selected_model_name} is not on ANKI. Try with different name'.encode(SYSTEM_ENCODING, errors="replace"))
                return 

            if self.selected_deck_name not in self.anki_client_desktop.getDecksAndID().keys():
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Cannot find deck with name: {self.selected_deck_name}. <br>Try again with different name"
                )
                self.logger.critical(f'Cannot find deck with name: {self.selected_deck_name}. Try again with different name'.encode(SYSTEM_ENCODING, errors="replace"))
                return 

        self.logger.info("Initial parameters are correct, starder processing excel")
        self.data = self.excel_worker.excelToDf(self.data, self.selected_foreign_lang_text)

        if not self.data:
            QMessageBox.warning(
                self.mw,
                'Anki notes creator',
                f"No data found in excel file. In order to create anki notes, input some data into excel"
            )
            self.logger.warning("No data found in excel file. In order to create anki notes, input some data into excel")
            return
        
        num_cards = range(1, len(self.data))  # Define the range based on the GeoDataFrame
        await self.threadedBuildTasks()
    
    async def threadedBuildTasks(self):
        """Execute buildTasks across multiple threads with proper async integration"""
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(executor, self.runCoroutine, row)
                for row in self.data
            ]
            results = await asyncio.gather(*futures)
            return results

    async def buildTasks(self, search_num):
        tasks = [self.noteCreator(obj) for obj in search_num]
        return await asyncio.gather(*tasks)

    async def noteCreator(self, row):
        front = clear_string(row[FIELDS_EXCEL.get("front_text") if CONSOLE_USED else self.selected_native_lang_text])
        back = clear_string(row[FIELDS_EXCEL.get("back_text") if CONSOLE_USED else self.selected_foreign_lang_text])
        example = clear_string(row[FIELDS_EXCEL.get("example") if CONSOLE_USED else self.selected_example_field])

        if (front not in [note["fields"][FIELDS.get("front_text")]["value"].rstrip() for note in self.cards_in_deck if front == note["fields"][FIELDS.get("front_text")]["value"].rstrip()]
            and back not in [note["fields"][FIELDS.get("back_text")]["value"].rstrip() for note in self.cards_in_deck if back == note["fields"][FIELDS.get("back_text")]["value"].rstrip()]):
            
            audio_upl = ""
            image_upl = ""
            audio_file_name = ""
            image_file_name = ""
            audio_url = ""
            image_url = ""
            upl_audio_file = ""
            upl_image_file = ""

            soup = self.website_scrapper.requestWebsite(
                get_dict_link_for_lang(DICT_LANG_SEARCH_URLS, CURR_LANG)+f"?q={back}"
            )
            if soup:
                image_url = self.website_scrapper.scrapeFirstImage(soup)
                audio_url = self.website_scrapper.scrapeFirstAudio(soup)
            
            if audio_url:
                audio_file_name = os.path.basename(audio_url)
            if image_url:
                image_file_name = os.path.basename(image_url)

            if audio_file_name:
                upl_audio_file = self.anki_client_console.retrieveUploadedFile(audio_file_name) if CONSOLE_USED \
                                    else self.anki_client_desktop.retrieveUploadedFile(audio_file_name)
            if image_file_name:
                upl_image_file = self.anki_client_console.retrieveUploadedFile(image_file_name) if CONSOLE_USED \
                                    else self.anki_client_desktop.retrieveUploadedFile(image_file_name)

            self.logger.debug(f"Image file: {upl_image_file}, audio file: {upl_audio_file}")
            
            if audio_url and upl_audio_file is False:
                audio_upl = self.anki_client_console.storeFileInAnki(audio_file_name, audio_url) if CONSOLE_USED \
                                    else self.anki_client_desktop.storeFileInAnki(audio_file_name, audio_url)
                self.logger.info(f"Uploaded new audio: {audio_upl}")
            elif upl_audio_file:
                audio_upl = audio_file_name

            if image_url and upl_image_file is False:
                image_upl = self.anki_client_console.storeFileInAnki(image_file_name, image_url) if CONSOLE_USED \
                                    else self.anki_client_desktop.storeFileInAnki(image_file_name, image_url)
                self.logger.info(f"Uploaded new image: {image_upl}")
            elif upl_image_file:
                image_upl = image_file_name

            row.update({"image": f"<div><img src='{image_upl}'></div>" if image_upl else ""})
            row.update({"audio": f"[sound:{audio_upl}]" if audio_upl else ""})

            if CONSOLE_USED:
                try:
                    result = self.anki_client_console.addNote(
                        deck_name = CURR_LANG,
                        fields = self.fields,
                        front_text = front, 
                        back_text = back,
                        example = example,
                        image = row.get("image"),
                        audio = row.get("audio")
                    )
                    self.logger.info(f'Created ANKI card with ID: {result}\nData: {row}')
                
                except FileExistsError:
                    self.logger.error(f"Word '{back}' is already used for some card in Anki")
                except Exception as ex:
                    self.logger.error(f"Unknown error occured: {ex}")
            else:
                try:
                    result = self.anki_client_desktop.addNote(
                        deck_name = self.selected_deck_name,
                        fields = self.fields,
                        front_text = front, 
                        back_text = back,
                        example = example,
                        image = row.get("image"),
                        audio = row.get("audio")
                    )
                    self.logger.info(f'Created ANKI card with ID: {result}\nData: {row}')
                
                except FileExistsError:
                    self.logger.error(f"Word '{back}' is already used for some card in Anki")
                except Exception as ex:
                    self.logger.error(f"Unknown error occured: {ex}")
        else:
            self.logger.error(f"Word '{back}' is already used for some card in Anki")
    
    def runCoroutine(self, row):
        """Run the coroutine in an event loop"""
        return asyncio.run(self.noteCreator(row))


if CONSOLE_USED:
    while True:
        data = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        generator = AnkiNoteGenerator(data)
        if os.path.exists(data):
            asyncio.run(generator.main())
            break