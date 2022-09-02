from os import system
from platform import processor
from bs4 import BeautifulSoup as BS
import requests as R
import json

# CONSTANTS =====================================================================================
URL = "https://store.steampowered.com/search?query&start={}&count={}&sort_by=Released_DESC&force_infinite=1&category1=998&infinite=1"
EXTRACTED_LINKS = []
OUTPUT_BUFFER = {}
#TEMPLATE = {
#    "NAME": None,
#    "GENRES": [],
#    "TAGS": [],
#    "RELEASE_YEAR": None,
#    "DEVELOPER": None,
#    "STEAM_LINK": None,
#    "SYSTEM_REQUIREMENTS":{
#        "PROCESSORS":[],
#        "GRAPHIC_CARDS": [],
#        "MEMORY": None,
#        "STORAGE": None,
#    }
#}
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

    print("=" * 100)
    for anchor in anchorElements:
        link = anchor['href']
        print("[+] NEW LINK FOUND: {}".format(link))
        EXTRACTED_LINKS.append(link)
    print("=" * 100)

    crawl_links()

#================================================================================================
# FOLLOW EACH LINK AND GET THE APP PAGE
#================================================================================================
def crawl_links():
    print("[*] CRAWLING LINKS...")

    for link in EXTRACTED_LINKS:
        print("[i] CURRENT LINK: {}".format(link))
        appPageResponse = R.get(link)
        appPageResponse.encoding = 'UTF-8'

        extract_data(appPageResponse.text, link)
    
    write_data()

#================================================================================================
# EXTRACT THE DATA FROM THE APP PAGE AND FILL THE TEMPLATE
#================================================================================================
def extract_data(htmlBuffer, appLink):
    print("[i] EXTRACTING DATA...")
    dataCapsul = {
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
    appPage = BS(htmlBuffer, 'lxml')

    #enter link to capsul
    dataCapsul["STEAM_LINK"] = appLink
    print("[+] WEBPAGE LINK ADDED: {}".format(appLink))

    #extract name
    appName = appPage.find('div', id="appHubAppName").text
    dataCapsul["NAME"] = appName
    print("[+] APP NAME ADDED: {}".format(appName))

    #extract genres + developer
    detailsElement = appPage.find('div', id="genresAndManufacturer")
    linksInElement = detailsElement.find_all('a')
    
    for link in linksInElement:
        href = link["href"]

        if("/genre/" in href):
            genre = link.text
            dataCapsul["GENRES"].append(genre)
            print("[+] NEW GENRE ADDED: {}".format(genre))
        elif("/?developer=" in href):
            dev = link.text
            dataCapsul["DEVELOPER"] = dev
            print("[+] APP DEVELOPER FOUND: {}".format(dev))

    #extract release year
    dateElement = appPage.find('div', class_='date')
    date = dateElement.text.split(',')[-1].strip()

    dataCapsul["RELEASE_YEAR"] = date
    print("[+] APP RELEASE DATE ADDED: {}".format(date))

    #extract tags
    appTagElements = appPage.find_all('a', class_="app_tag")
    
    for tagElement in appTagElements:
        tag = tagElement.text.replace("\t", "").replace("\r", "").replace("\n", "")
        dataCapsul["TAGS"].append(tag)
        print("[+] NEW TAG ADDED: {}".format(tag))

    # SYSTEM REQ EXTRACTION =============================================================
    print('=' * 100)
    
    sysReqElement = appPage.find('div', class_="game_area_sys_req_leftCol")
    if(sysReqElement == None):
        sysReqElement = appPage.find('div', class_="game_area_sys_req_full")



    listElements = sysReqElement.find_all('li')
    
    for listElement in listElements:
        try:
            dataName = listElement.find("strong").text

            if("Processor" in dataName):
                processor = listElement.text.replace("Processor:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["PROCESSORS"].append(processor)
                print("[+] COMPATIBLE PROESSOR ADDED: {}".format(processor))

            if("Memory" in dataName):
                memory = listElement.text.replace("Memroy:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["MEMORY"] = memory
                print("[+] COMPATIBLE PROESSOR ADDED: {}".format(memory))

            if("Graphics" in dataName):
                graphics = listElement.text.replace("Graphics:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["GRAPHIC_CARDS"].append(graphics)
                print("[+] COMPATIBLE PROESSOR ADDED: {}".format(graphics))

            if("Storage" in dataName):
                storage = listElement.text.replace("Storage:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["STORAGE"] = storage
                print("[+] COMPATIBLE PROESSOR ADDED: {}".format(storage))

        except Exception as E:
            print(E)

    print("="*100)
    print(json.dumps(dataCapsul, indent=4))
    print("="*100)
    
    OUTPUT_BUFFER[appName] = dataCapsul

    
#================================================================================================
# WRITE THE FILLED TEMPLATE TO THE DB.JSON FILE
#================================================================================================
def write_data():
    with open("DB.json", "a+", encoding='utf-8') as fp:
        fp.write(str(json.dumps(OUTPUT_BUFFER, indent=4)))


pull_links()