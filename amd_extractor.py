from doctest import OutputChecker
from bs4 import BeautifulSoup as BS
import requests as R
import json
from urllib.parse import quote, unquote, unquote_plus

import os
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

# =========================================================================================================
HEADER = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",}

URL = "https://www.amd.com/en/products/specifications"

REQ_URL = "https://www.amd.com/en/products/specifications/processors?s_family%5B%5D={}s_series%5B%5D={}&s_platform%5B%5D=23296"

REQ_URL_2 = "https://www.amd.com/en/products/specifications/processors?s_family%5B%5D={}&s_series%5B%5D={}&s_platform%5B%5D=23296&s_segment%5B%5D=23311"

LINK_FRAGMENTS = {
    23341: [25431, 23276, 23241, 23996, 23236, 23266, 23256, 23261, 23251,  23246, 23191,  23211,  23216,  23196,  23201,  23206,  24161,  23271,  23286,  23281,  23231,  23226,  23221,  23186],
    23331: [23206, 23201, 23196, 23216, 23211, 23191]
}

OUTPUT_OBJ = {}

# =========================================================================================================

def start():
    # LOOP THROUGH IDS
    for family, series in LINK_FRAGMENTS.items():
        for seriesNumber in series:
            print(f"[i] FAMILY: {family} SERIES: {seriesNumber}")
            # GENERATE URL
            reqURL = REQ_URL_2.format(family, seriesNumber)
            print(f"[i] REQUESTING URL: {reqURL}")
            # REQUEST URL
            print(f"[i] REQUESTING DATA...")
            responseBuffer = R.get(reqURL, headers=HEADER)
            print(Fore.WHITE + Back.GREEN + f"[+] RESPONSE RECIEVED FROM THE SERVER...")
            # GET THE PAGEBUFFER
            responseBuffer.encoding = "UTF-8"
            write_to_file(os.getcwd() + "/HTML/" + str(family) + "-" + str(seriesNumber) + ".html", responseBuffer.text)
            # PARSE THE BUFFER TO BS
            print(f"[i] PARSING RESPONSE BUFFER TO BS...")
            responsePage = BS(responseBuffer.content, "lxml")
            print(f"[i] STARTING CRAWLER...")
            crawler(responsePage, family, seriesNumber)
            #input()

    print(json.dumps(OUTPUT_OBJ, indent=4))
    input("PAUSED...")
    # write_to_file(os.getcwd() + "/AMD_CPUS.json", json.dumps(OUTPUT_OBJ, indent=4))
    write_to_file(".data/amd_cpus.json", json.dumps(OUTPUT_OBJ, indent=4))

def write_to_file(fileName: str, content: str):
    print(f"[i] WRITING RESPONSE BUFFER TO A FILE...")
    try:
        with open(fileName, mode="a+", encoding="UTF-8") as fp:
            fp.write(content)
            fp.close()
        print(Fore.WHITE + Back.GREEN + f"[+] WRITE COMPLETE: {fileName}")
    except Exception as E:
        print(Fore.WHITE + Back.RED + f"[-] ERROR WRITING DATA TO FILE: {E}")

def crawler(page: BS, familyNumber: int, modelNumber: int):
    # SEARCH MAIN ELEMENTS
    try:
        # GRAB THE TABLE ELEMENT
        print(f"[i] SEARCHING FOR TABLE ELEMENT...")
        table = page.find("table")
        print(Fore.WHITE + Back.GREEN + f"[+] TABLE ELEMENT FOUND...")
        # FIND <THEAD> AND <TBODY>
        print(f"[i] SEARCHING FOR THEAD ELEMENT...")
        tableHeadingsSection = table.find("thead")
        print(Fore.WHITE + Back.GREEN + f"[+] THEAD ELEMENT FOUND...")
        # GET TBODY
        print(f"[i] SEARCHING FOR TBODY ELEMENT...")
        tableBody = table.find("tbody")
        print(Fore.WHITE + Back.GREEN + f"[+] TBODY ELEMENT FOUND...")

    except Exception as E:
        print(Fore.WHITE + Back.RED + f"[-] ERROR GRABING THE TABLE: {E}")

    # CRAWLING THEAD =================================================================================================
    # FIND MODEL, CLOCK, CORES, THREADS, HEADINGS' PLACEMNETS IN <THEAD> -> <TR> -> <TH>
    try:
        print(f"[i] SEARCHING FOR TABLE HEADINGS ELEMENT...")
        tableHeadings = tableHeadingsSection.find_all("th")
        print(Fore.WHITE + Back.GREEN + f"[+] TABLE HEADINGS FOUND...")
        headingIndexes = {
            "FAMILY": None,
            "MODEL" : None,
            "BASE CLOCK" : None,
            "CORES" : None,
            "THREADS" : None
        }
        
        for i in range(len(tableHeadings)):
            headingText = tableHeadings[i].text
            print(f"HEADING TEXT: {headingText}")
            if("Family" in headingText):
                headingIndexes["FAMILY"] = i
                print(Fore.WHITE + Back.GREEN + f"[+] FAMILY HEADING INDEX FOUND: {i}")
            elif(("Model" in headingText) & ("Graphics" not in headingText)):
                headingIndexes["MODEL"] = i
                print(Fore.WHITE + Back.GREEN + f"[+] MODEL HEADING INDEX FOUND: {i}")
            elif("Base Clock" in headingText):
                headingIndexes["BASE CLOCK"] = i
                print(Fore.WHITE + Back.GREEN + f"[+] BASE CLOCK HEADING INDEX FOUND: {i}")
            elif("# of CPU Cores" in headingText):
                headingIndexes["CORES"] = i
                print(Fore.WHITE + Back.GREEN + f"[+] CPU CORES HEADING INDEX FOUND: {i}")
            elif("# of Threads" in headingText):
                headingIndexes["THREADS"] = i
                print(Fore.WHITE + Back.GREEN + f"[+] THREADS HEADING INDEX FOUND: {i}")
        print('=' * 100)
        print(json.dumps(headingIndexes, indent=4))
        print('=' * 100)
    except Exception as E:
        print(Fore.WHITE + Back.RED + f"[-] ERROR CRAWLING THE TABLE HEADINGS: {E}")

    # CRAWLING ROWs ===============================================================================================================
    try:
        # LOOP THROUGH ALL <TR>S
        print(f"[i] SEARCHING FOR TR ELEMENTs...")
        tableRows = tableBody.find_all("tr")
        print(Fore.WHITE + Back.GREEN + f"[+] TR ELEMENTs FOUND...")
        rowIndex = 0
        for row in tableRows:
            ROW_DATA = {
                "FAMILY": "",
                "MODEL" :"",
                "BASE CLOCK" : "",
                "CORES" : "",
                "THREADS" : ""
            }
            # IN EACH <TR> GET THE <TD> CONTAINING REQUIRED DATA
            print(f"[i] SEARCHING FOR TABLE DATA ELEMENTs...")
            tableDataElements = row.find_all("td")
            print(Fore.WHITE + Back.GREEN + f"[+] TABLE DATA ELEMENTs FOUND...")
            print('=' * 100)
            for heading, index in headingIndexes.items():
                if(index == None):
                    continue
                ROW_DATA[heading] = tableDataElements[index].text
                #print(f"[i] {heading} => {tableDataElements[index].text}")
            print('=' * 100)
            OUTPUT_OBJ[str(familyNumber) + '_' + str(modelNumber) + '_' + str(rowIndex)] = ROW_DATA
            print(json.dumps(ROW_DATA, indent=4))
            rowIndex += 1
    except Exception as E:
        print(Fore.WHITE + Back.RED + f"[-] ERROER CRAWLING TABLE BODY: {E}")

if __name__ == '__main__':
    start()