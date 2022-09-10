import sys
from bs4 import BeautifulSoup as BS
import requests as R
import json
import argparse

# CONSTANTS =====================================================================================
URL = "https://store.steampowered.com/search?query&start={}&count={}&sort_by=Released_DESC&force_infinite=1&category1=998&infinite=1"

EXTRACTED_LINKS = []
OUTPUT_BUFFER = {}
CPUs = []
GPUs = []

ITERATIONS = None
COUNT = None
OUTPUT_FILE_NAME = None
#TEMPLATE = {
#   "DETAILS":{
#    "NAME": None,
#    "GENRES": [],
#    "TAGS": [],
#    "RELEASE_YEAR": None,
#    "DEVELOPER": None,
#    "STEAM_LINK": None,
#    }
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
    request_start = 0
    for i in range(ITERATIONS):
        print("[*] STEAM REQUEST ITERATIONS: {}".format(i))
        try:
            print("[*] SENDING REQUEST TO STEAM...")
            print("[i] REQUEST: {}".format(URL.format(request_start, COUNT)))
            steamResponse = R.get(URL.format(request_start, COUNT))
            print("[+] RESPONSE RECIEVED...")

            steamResponse.encoding = 'UTF-8'
            extract_links(steamResponse.json()['results_html'])

            request_start += COUNT
        except Exception as E:
            print(E)

    crawl_links()

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
def extract_data(htmlBuffer: str, appLink: str):
    print("[i] EXTRACTING DATA...")
    dataCapsul = {
        "DETAILS": {
            "NAME": "",
            "GENRES": [],
            "TAGS": [],
            "RELEASE_YEAR": None,
            "DEVELOPER": "",
            "STEAM_LINK": "",
        },
        "SYSTEM_REQUIREMENTS":{
            "PROCESSORS":[],
            "GRAPHICS": [],
            "MEMORY": None,
            "STORAGE": None,
        }
    }
    
    appPage = BS(htmlBuffer, 'lxml')

    #enter link to capsul ===============================================================
    dataCapsul["DETAILS"]["STEAM_LINK"] = appLink
    print("[+] WEBPAGE LINK ADDED: {}".format(appLink))

    #extract name ========================================================================
    appName = appPage.find('div', id="appHubAppName").text
    dataCapsul["DETAILS"]["NAME"] = appName
    print("[+] APP NAME ADDED: {}".format(appName))

    #extract genres + developer ==========================================================
    detailsElement = appPage.find('div', id="genresAndManufacturer")
    linksInElement = detailsElement.find_all('a')
    
    for link in linksInElement:
        href = link["href"]

        if("/genre/" in href):
            genre = link.text.strip()
            dataCapsul["DETAILS"]["GENRES"].append(genre)
            print("[+] NEW GENRE ADDED: {}".format(genre))
        elif("developer" in href):
            dev = link.text.strip()
            dataCapsul["DETAILS"]["DEVELOPER"] = dev
            print("[+] APP DEVELOPER FOUND: {}".format(dev))

    #extract release year ===============================================================
    dateElement = appPage.find('div', class_='date')
    if(dateElement == None):
        date = 0000
    else:
        date = dateElement.text.split(',')[-1].strip()

    dataCapsul["DETAILS"]["RELEASE_YEAR"] = date
    print("[+] APP RELEASE DATE ADDED: {}".format(date))

    #extract tags =======================================================================
    appTagElements = appPage.find_all('a', class_="app_tag")
    
    for tagElement in appTagElements:
        tag = tagElement.text.replace("\t", "").replace("\r", "").replace("\n", "")
        dataCapsul["DETAILS"]["TAGS"].append(tag)
        print("[+] NEW TAG ADDED: {}".format(tag))

    # SYSTEM REQ EXTRACTION =============================================================
    print('=' * 100)
    
    sysReqElement = appPage.find('div', class_="game_area_sys_req_leftCol")
    if(sysReqElement == None):
        sysReqElement = appPage.find('div', class_="game_area_sys_req_full")



    listElements = sysReqElement.find_all('li')
    
    for listElement in listElements:
        try:
            dataName = listElement.find("strong").text.strip()

            if("Processor" in dataName):
                processor = listElement.text.replace("Processor:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["PROCESSORS"].append(processor)
                CPUs.append(processor)
                print("[+] COMPATIBLE PROESSOR ADDED: {}".format(processor))

            if("Memory" in dataName):
                memory = listElement.text.replace("Memory:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["MEMORY"] = memory
                print("[+] REQUIRED MEMORY CAPACITY ADDED: {}".format(memory))

            if("Graphics" in dataName):
                graphics = listElement.text.replace("Graphics:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["GRAPHICS"].append(graphics)
                GPUs.append(graphics)
                print("[+] COMPATIBLE GRAPHIC CARD ADDED: {}".format(graphics))

            if("Storage" in dataName):
                storage = listElement.text.replace("Storage:", "").strip()
                dataCapsul["SYSTEM_REQUIREMENTS"]["STORAGE"] = storage
                print("[+] REQUIRED STORAGE CAPACITY ADDED: {}".format(storage))

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
    print("[i] WRITING DATA OF {} GAMES TO {}.JSON".format(len(OUTPUT_BUFFER), OUTPUT_FILE_NAME))
    with open(OUTPUT_FILE_NAME +".json", "a+", encoding='utf-8') as fp:
        fp.write(str(json.dumps(OUTPUT_BUFFER, indent=4)))
        fp.close()

    with open("./data/steam_cpu_names.txt", encoding="UTF-8", mode="a+") as f:
        for cpu in CPUs:
            f.write(cpu + "\n")
        f.close()

    with open("./data/steam_gpu_names.txt", encoding="UTF-8", mode="a+") as f:
        for gpu in GPUs:
            f.write(gpu + "\n")
        f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crawl the Steam and pull data about games.")
    parser.add_argument("-lc", default=10, type=int, help="Amount of links per iterations to request.")
    parser.add_argument("-ic", default=1, type=int, help="How many iterations to run.")
    parser.add_argument("-o", default="data", type=str, help="Output file name. (Without Extention)")
    
    args = parser.parse_args()
    
    if(len(sys.argv) < 2):
        parser.print_help()
        parser.print_usage()
    else:
        ITERATIONS = args.ic
        COUNT = args.lc
        OUTPUT_FILE_NAME = "./data/" + args.o
        
        pull_links()

    
