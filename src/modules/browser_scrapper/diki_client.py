from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os

from ...constants import DIKI_MAIN_URL

class WebsiteScrapper:

    def requestWebsite(self, url):
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup

    def scrapeFirstImage(self, soup):
        dictionary_record = soup.find("div", {"class": "dictionaryEntity"})
        if dictionary_record:
            # Find the first image and its annotation
            first_image = dictionary_record.find('img')
            if first_image:
                image_url = first_image['src']
                return urljoin(DIKI_MAIN_URL, image_url) if 'transcription' not in image_url else "" #not ot return image of transcriptions
            else:
                return ""

    def scrapeFirstAudio(self, soup):
        dictionary_record = soup.find("span", {"class": "recordingsAndTranscriptions"})
        if dictionary_record:

            audio = dictionary_record.find_all("span", {"class": "audioIcon"})
            if not audio:
                return ""

            if len(audio) > 1:
                audio = audio[1]
            else:
                audio = audio[0]

            data_url = audio['data-audio-url']
            if data_url:
                return urljoin(DIKI_MAIN_URL, data_url)
            else:
                return ""

# # Example usage
# url = "https://www.diki.pl/slownik-angielskiego?q=rozmowa"
# image_url, annotation = scrapeFirstImage_and_annotation(url)

# print("Image URL:", image_url)
# print("Annotation:", annotation)

    # def downloadimages(self, query):
    #     arguments = {
    #         "keywords": query,
    #         "format": "jpg",
    #         "limit":1,
    #         "print_urls":True,
    #         "size": "medium",
    #         "aspect_ratio":"panoramic"}
    #     try:
    #         self.client.download(arguments)
        
    #     # Handling File NotFound Error    
    #     except FileNotFoundError: 
    #         arguments = {
    #             "keywords": query,
    #             "format": "jpg",
    #             "limit":1,
    #             "print_urls":True, 
    #             "size": "medium"}
    #         # Providing arguments for the searched query
    #         try:
    #             # Downloading the photos based
    #             # on the given arguments
    #             self.client.download(arguments) 
    #         except:
    #             pass