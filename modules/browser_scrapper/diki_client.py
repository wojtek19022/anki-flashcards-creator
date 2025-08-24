from bs4 import BeautifulSoup
import requests

class WebsiteScrapper:
    def __init__(self, parent):
        self.diki_main_url = parent.diki_main_url

    def scrape_first_image_and_annotation(url):
        # Send a GET request to the website
        response = requests.get(url)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content
            soup = BeautifulSoup(response.text, 'html.parser')
            dictionary_record = soup.find("div", { "class" : "dictionaryEntity" })
            if dictionary_record:
                print(dictionary_record)
                # Find the first image and its annotation
                first_image = soup.find_all('img')
                print(first_image)
                if first_image:
                    image_url = first_image['src']
                    # Find the annotation (title or alt text)
                    annotation = first_image.get('alt', 'No annotation available')
                    return image_url, annotation
                else:
                    return None, "No image found"
        else:
            return None, "Failed to retrieve the webpage"

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