import os
import logging
import asyncio

from concurrent.futures import ThreadPoolExecutor
from aqt.qt import QMessageBox

from .constants import __name__ as plugin_name, \
                        SYSTEM_ENCODING, \
                        CONSOLE_USED, CURR_LANG, DEFAULT_NUM_PROC, \
                        MODEL_NAME, LANGUAGES_DECKS, FIELDS_EXCEL, FIELDS, DICT_LANG_SEARCH_URLS, \
                        DIKI_MAIN_URL


from .utils import invoke, clear_string, get_dict_link_for_lang, Logger, Encoder
from .modules import AnkiClientConsole, AnkiClientDesktop, ExcelWorker, WebsiteScrapper

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
        self.anki_client_console = AnkiClientConsole(self)
        if not CONSOLE_USED:
            self.anki_client_desktop = AnkiClientDesktop(self)
        self.excel_worker = ExcelWorker(self)
        self.website_scrapper = WebsiteScrapper() 
        self.data = ""
        self.data_cols = []
        self.max_threads = max(1, int(psutil.cpu_count() * 0.8)) if CONSOLE_USED else DEFAULT_NUM_PROC# Calculate the number of threads to use (80% of available CPU cores)
        self.logger.info("Program został prawidłowo zainicjalizowany")

    async def main(self, input_path):
        self.data = input_path
        self.fields = self.anki_client_console.get_fields_by_model_name(MODEL_NAME) if CONSOLE_USED \
                        else self.anki_client_desktop.get_fields_by_model_name(MODEL_NAME)
        self.cards_in_deck = self.anki_client_console.get_all_cards_in_deck() if CONSOLE_USED \
                                else self.anki_client_desktop.get_all_cards_in_deck()
        self.logger.info("Creating of cards was started")

        if CONSOLE_USED:
            if not MODEL_NAME in self.anki_client_console.get_models_names():
                self.logger.error(f'Model with name: {MODEL_NAME} is not on ANKI. Try with different name')
                return 
            
            if CURR_LANG not in self.anki_client_console.get_decks_and_id().keys():
                self.logger.error(f'Cannot find deck with name: {CURR_LANG} try again with different name')
                return 
        else:
            if not MODEL_NAME in self.anki_client_desktop.get_models_names():
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Model with name: {MODEL_NAME} is not on ANKI. <br>Try with different name"
                )
                self.logger.critical(f'Model with name: {MODEL_NAME} is not on ANKI. Try with different name'.encode(SYSTEM_ENCODING, errors="replace"))
                return 

            if CURR_LANG not in self.anki_client_desktop.get_decks_and_id().keys():
                QMessageBox.critical(
                    self.mw,
                    'Anki notes creator',
                    f"Cannot find deck with name: {CURR_LANG}. <br>Try again with different name"
                )
                self.logger.critical(f'Cannot find deck with name: {CURR_LANG}. Try again with different name'.encode(SYSTEM_ENCODING, errors="replace"))
                return 

        self.logger.info("Initial parameters are correct, starder processing excel")
        self.data = self.excel_worker.excel_to_df(self.data, FIELDS_EXCEL.get('back_text'))

        if not self.data:
            QMessageBox.warning(
                self.mw,
                'Anki notes creator',
                f"No data found in excel file. In order to create anki notes, input some data into excel"
            )
            self.logger.warning("No data found in excel file. In order to create anki notes, input some data into excel")
            return
        
        num_cards = range(1, len(self.data))  # Define the range based on the GeoDataFrame
        await self.threaded_build_tasks()
    
    async def threaded_build_tasks(self):
        """Execute build_tasks across multiple threads with proper async integration"""
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            loop = asyncio.get_event_loop()
            futures = [
                loop.run_in_executor(executor, self.run_coroutine, row)
                for row in self.data
            ]
            results = await asyncio.gather(*futures)
            return results

    async def build_tasks(self, search_num):
        tasks = [self.note_creator(obj) for obj in search_num]
        return await asyncio.gather(*tasks)

    async def note_creator(self, row):
        front = clear_string(row[FIELDS_EXCEL.get("front_text")])
        back = clear_string(row[FIELDS_EXCEL.get("back_text")])
        example = clear_string(row[FIELDS_EXCEL.get("example")])
        
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

            soup = self.website_scrapper.request_website(
                get_dict_link_for_lang(DICT_LANG_SEARCH_URLS, CURR_LANG)+f"?q={back}"
            )
            if soup:
                image_url = self.website_scrapper.scrape_first_image(soup)
                audio_url = self.website_scrapper.scrape_first_audio(soup)
            
            if audio_url:
                audio_file_name = os.path.basename(audio_url)
            if image_url:
                image_file_name = os.path.basename(image_url)

            if audio_file_name:
                upl_audio_file = self.anki_client_console.retrieve_uploaded_file(audio_file_name) if CONSOLE_USED \
                                    else self.anki_client_desktop.retrieve_uploaded_file(audio_file_name)
            if image_file_name:
                upl_image_file = self.anki_client_console.retrieve_uploaded_file(image_file_name) if CONSOLE_USED \
                                    else self.anki_client_desktop.retrieve_uploaded_file(image_file_name)

            self.logger.debug(f"Image file: {upl_image_file}, audio file: {upl_audio_file}")
            
            if audio_url and upl_audio_file is False:
                audio_upl = self.anki_client_console.store_file_in_anki(audio_file_name, audio_url) if CONSOLE_USED \
                                    else self.anki_client_desktop.store_file_in_anki(audio_file_name, audio_url)
                self.logger.info(f"Uploaded new audio: {audio_upl}")
            elif upl_audio_file:
                audio_upl = audio_file_name

            if image_url and upl_image_file is False:
                image_upl = self.anki_client_console.store_file_in_anki(image_file_name, image_url) if CONSOLE_USED \
                                    else self.anki_client_desktop.store_file_in_anki(image_file_name, image_url)
                self.logger.info(f"Uploaded new image: {image_upl}")
            elif upl_image_file:
                image_upl = image_file_name

            row.update({"image": f"<div><img src='{image_upl}'></div>" if image_upl else ""})
            row.update({"audio": f"[sound:{audio_upl}]" if audio_upl else ""})

            if CONSOLE_USED:
                try:
                    result = self.anki_client_console.add_note(
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
                    result = self.anki_client_desktop.add_note(
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
    
    def run_coroutine(self, row):
        """Run the coroutine in an event loop"""
        return asyncio.run(self.note_creator(row))


# if __name__ == "__main__":
#     while True:
        # data = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        # generator = AnkiNoteGenerator(data)
        # if os.path.exists(data):
        #     asyncio.run(generator.main())
        #     break