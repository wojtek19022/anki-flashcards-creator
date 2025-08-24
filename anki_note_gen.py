import os
import logging
import asyncio
import psutil

from concurrent.futures import ThreadPoolExecutor

from constants import LOGGER, MODEL_NAME, LANGUAGES_DECKS, FIELDS, FIELDS_EXCEL, CURR_LANG, CARD_TMPLT, DICT_LANG_SEARCH_URLS, \
                        DIKI_MAIN_URL


from utils import invoke, get_dict_link_for_lang
from modules import AnkiClient, ExcelWorker, WebsiteScrapper

class AnkiNoteGenerator:
    def __init__(self, data):
        self.dict_langs_links = DICT_LANG_SEARCH_URLS
        self.current_lang = CURR_LANG
        self.card_template = CARD_TMPLT
        self.model_name = MODEL_NAME
        self.diki_main_url = DIKI_MAIN_URL
        self.fields_anki = FIELDS
        self.fields_data = FIELDS_EXCEL
        self.anki_client = AnkiClient(self)
        self.excel_worker = ExcelWorker(self)
        self.website_scrapper = WebsiteScrapper(self)
        self.cards_in_deck = [
            card for card in self.anki_client.get_cards_details(self.anki_client.find_all_notes()) \
            if card["deckName"] == self.current_lang and card["modelName"] == self.model_name
        ]
        self.fields = self.anki_client.get_fields_by_model_name(self.model_name)
        self.data = data
        self.data_cols = []
        self.max_threads = max(1, int(psutil.cpu_count() * 0.8)) # Calculate the number of threads to use (80% of available CPU cores)

    async def main(self):
        logging.info("Creating of cards was started")
        if not self.model_name in self.anki_client.get_models_names():
            logging.error(f'Model with name: {self.model_name} is not on ANKI. Try with different name')
            return 
        
        if self.current_lang not in self.anki_client.get_decks_and_id().keys():
            logging.error(f'Cannot find deck with name: {self.current_lang} try again with different name')
            return 

        self.data = self.excel_worker.excel_to_df(self.data, self.fields_data.get('back_text'))

        if not self.data:
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
        if row[self.fields_data.get("front_text")] not in [note["fields"][self.fields_anki.get("front_text")]["value"] for note in self.cards_in_deck]:
            audio_upl = ""
            image_upl = ""
            audio_file_name = ""
            image_file_name = ""
            upl_audio_file = ""
            upl_image_file = ""

            soup = self.website_scrapper.request_website(
                get_dict_link_for_lang(self.dict_langs_links, self.current_lang)+f"?q={row[self.fields_data.get('back_text')]}"
            )
            if soup:
                image_url = self.website_scrapper.scrape_first_image(soup)
                audio_url = self.website_scrapper.scrape_first_audio(soup)
            
                audio_file_name = os.path.basename(audio_url)
                image_file_name = os.path.basename(image_url)

            if audio_file_name:
                upl_audio_file = self.anki_client.retrieve_uploaded_file(audio_file_name)
            if image_file_name:
                upl_image_file = self.anki_client.retrieve_uploaded_file(image_file_name)
            
            if not upl_audio_file and audio_file_name:
                audio_upl = self.anki_client.store_file_in_anki(audio_file_name, audio_url)
            if not image_file_name and image_file_name:
                image_upl = self.anki_client.store_file_in_anki(image_file_name, image_url)
            
            try:
                result = self.anki_client.add_note(
                    fields = self.fields,
                    front_text = row[self.fields_data.get("front_text")], 
                    back_text = row[self.fields_data.get("back_text")],
                    example = row[self.fields_data.get("example")],
                    image = f"<div><img src='{image_file_name}'></div>" if image_file_name else "",
                    audio = f"[sound:{audio_file_name}]" if audio_file_name else ""
                )
                logging.info(f'Created ANKI card with ID: {result}\nData: {row}')
            except Exception as ex:
                logging.error(f"Word '{row[self.fields_data.get('back_text')]}' is already used for some card in Anki")
        else:
            logging.error(f"Word '{row[self.fields_data.get('back_text')]}' is already used for some card in Anki")
    
    def run_coroutine(self, row):
        """Run the coroutine in an event loop"""
        return asyncio.run(self.note_creator(row))


if __name__ == "__main__":
    while True:
        data = str(input("Type in a directory to excel data with words to ANKI integrator: "))
        generator = AnkiNoteGenerator(data)
        if os.path.exists(data):
            asyncio.run(generator.main())
            break