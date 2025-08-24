from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
import os

class WebsiteScrapper:
    def __init__(self, parent):
        self.diki_main_url = parent.diki_main_url

    def request_website(self, url):
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup

    def scrape_first_image(self, soup):
        dictionary_record = soup.find("div", {"class": "dictionaryEntity"})
        if dictionary_record:
            # Find the first image and its annotation
            first_image = dictionary_record.find('img')
            if first_image:
                image_url = first_image['src']
                return urljoin(self.diki_main_url, image_url) if 'transcription' not in image_url else "" #not ot return image of transcriptions
            else:
                return None

    def scrape_first_audio(self, soup):
        dictionary_record = soup.find("span", {"class": "recordingsAndTranscriptions"})
        if dictionary_record:
            test = dictionary_record.find("span", {"class": "audioIcon"})
            if not test:
                return None
            data_url = test['data-audio-url']
            if data_url:
                return urljoin(self.diki_main_url, data_url)
            else:
                return None

# # Example usage
# url = "https://www.diki.pl/slownik-angielskiego?q=rozmowa"
# image_url, annotation = scrape_first_image_and_annotation(url)

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