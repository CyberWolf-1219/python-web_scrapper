from tokenize import String
from bs4 import BeautifulSoup as BS
import requests as R

# CONSTANTS =====================================================================================
URL = "https://store.steampowered.com/search?query&start={}&count={}&sort_by=Released_DESC&force_infinite=1&category1=998&infinite=1"
EXTRACTED_LINKS = []

TEMPLATE = {
    "NAME": None,
    "GENRES": [],
    "TAGS": [],
    "RELEASE_YEAR": None,
    "DEVELOPER": None,
    "STEAM_LINK": None,
    "SYSTEM_REQUIREMENTS":{
        "PROCESSORS":[],
        "GRAPHIC_CARDS": [],
        "MEMORY": None,
        "STORAGE": None,
    }
}
#================================================================================================

#================================================================================================
# REQUEST A LINK LIST FROM STEAM
#================================================================================================
def pull_links():
    print("[*] REQUESTING LINKS FROM THE STEAM...")
    steamResponse = R.get(URL.format(0, 10))
    print("[+] RESPONSE RECIEVED...")

    steamResponse.encoding = 'UTF-8'
    extract_links(steamResponse.json()['results_html'])

#================================================================================================
# EXTRACT & STORE LINKS FROM THE RESPONSE
#================================================================================================
def extract_links(htmlBuffer):
    encodedHTML = BS(htmlBuffer, 'lxml')

    print("[*] SERACHING FOR LINKS...")
    anchorElements = encodedHTML.find_all('a')

    for anchor in anchorElements:
        link = anchor['href']
        print("[+] NEW LINK FOUND: {}".format(link))
        EXTRACTED_LINKS.append(link)

#================================================================================================
# FOLLOW EACH LINK AND GET THE APP PAGE
#================================================================================================
def crawl_links():
    for link in EXTRACTED_LINKS:
        appPageResponse = R.get(link)
        appPageResponse.encoding = 'UTF-8'

        extract_data(appPageResponse.text)

#================================================================================================
# EXTRACT THE DATA FROM THE APP PAGE AND FILL THE TEMPLATE
#================================================================================================
def extract_data(htmlBuffer):
    dataCapsul = TEMPLATE
    appPage = BS(htmlBuffer, 'lxml')

    detailBlock = BS.find('div', id="genresAndManufacturer")
    
#================================================================================================
# WRITE THE FILLED TEMPLATE TO THE DB.JSON FILE
#================================================================================================
def write_data():
    pass


pull_links()