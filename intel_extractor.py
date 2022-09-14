# GET MAIN PAGE
# SEARCH FOR ANCHOR TAGS
# GET LINKS FROM ANCHOR TAGS
# GET EACH LIST PAGE
# CRAWL THE TABLE
# WRITE TO JSON FILE

# IMPORTS ==============================================
import re
from statistics import mode
from turtle import heading
import requests as r
from bs4 import BeautifulSoup as bs
from bs4.element import Tag, NavigableString
import json

from colorama import Fore, Back
import colorama
colorama.init(autoreset=True)

import traceback
# ======================================================
HEADER = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
DOMAIN = "https://ark.intel.com"
OUTPUT_OBJ = {}
# ======================================================
# EXPORT FUNCTION ======================================
def export(fileName:str, content:str):
    try:
        with open(fileName, mode="a+", encoding="UTF-8") as fp:
            fp.write(content)
            fp.close()
    except Exception as E:
        cprint(Fore.WHITE + Back.RED + traceback.format_exc())
        cprint('+', "exporting data: {}", E)
# ======================================================

# PRINT FUNCTION =======================================
def cprint(sign:str = "", text:str = "",):
    buffer = "[" + sign + "] " + text

    if(sign == "+"):
        print(Fore.WHITE + Back.GREEN + buffer)
    elif(sign == "-"):
        print(Fore.WHITE + Back.RED + buffer)
    elif(sign == "i"):
        print(Fore.WHITE + Back.BLUE + buffer)
    else:
        print(Fore.WHITE + buffer)
# ======================================================

def crawl_table(tableElement: Tag | NavigableString, tableIndex: int):
    cprint("i", "CRAWLING TABLE...")

    try:
        cprint("i", "SEARCHING FOR TABLE HEADING ELEMENT...")
        tableHead = tableElement.find("thead")
        cprint("+", "TABLE HEADING ELEMENT FOUND...")
        cprint("i", "SEARCHING FOR TABLE BODY ELEMENT...")
        tableBody = tableElement.find("tbody")
        cprint("+", "TABLE BODY ELEMENT FOUND...")
    except Exception as E:
        cprint('-', f"CANNOT FIND ELEMENT: {E}")
        cprint(Fore.WHITE + Back.RED + traceback.format_exc())

    HEADING_INDEXES = {
        "PRODUCT_NAME" : None,
        "CLOCK" : None,
        "CORES" : None,
    }

    try:
        cprint("i", "SEARCHING FOR HEADINGS IN TABLE HEAD ELEMENT...")
        headings = tableHead.find_all('th')
        cprint("+", "TABLE HEAD ELEMENT FOUND: {}".format(len(headings)))

        cprint("i", "SEARCHING INDEXES OF TABLE HEAD ELEMENT...")
        for index in range(len(headings)):
            headingText = headings[index].text
            cprint("CURRENT HEADING: {}".format(headingText))

            if("Product Name" in headingText):
                HEADING_INDEXES["PRODUCT_NAME"] = index
                cprint('+', "INDEX FOUND FOR PRODUCT NAME: {}".format(index))
            elif("Frequency" in headingText):
                HEADING_INDEXES["CLOCK"] = index
                cprint('+', "INDEX FOUND FOR CLOCK SPEED: {}".format(index))
            elif("Total Cores" in headingText):
                HEADING_INDEXES["CORES"] = index
                cprint('+', "INDEX FOUND FOR CORE COUNT: {}".format(index))
    except Exception as E:
        cprint('-', f"ERROR SEARCHING FOR HEADING INDEXES: {E}")
        cprint(Fore.WHITE + Back.RED + traceback.format_exc())

    try:
        cprint('i', f"SEARCHIN FOR ROWs IN TABLE BODY...")
        rows = tableBody.find_all('tr')
        cprint('+', f"ROWS FOUND IN TABLE BODY: {len(rows)}")
        row_index = 0
        for row in rows:
            ROW_DATA = {
                "FAMILY":"",
                "MODEL":"",
                "BASE CLOCK":"",
                "CORES":"",
                "THREADS": ""
            }
            tableDataElements = row.find_all("td")
            productName = tableDataElements[HEADING_INDEXES["PRODUCT_NAME"]].text.strip().replace("®", "").replace("™", "").replace("Intel ", "").replace("Processor", "").replace("  ", " ")
            clockSpeed = tableDataElements[HEADING_INDEXES["CLOCK"]].text.strip()
            coreCount = tableDataElements[HEADING_INDEXES["CORES"]].text.strip()

            cprint(f"PRODUCT NAME => {productName}")
            ROW_DATA["FAMILY"] = productName.split(" ")[0]
            ROW_DATA["MODEL"] = productName

            cprint(f"CLOCK SPEED => {clockSpeed}")
            ROW_DATA["BASE CLOCK"] = clockSpeed

            cprint(f"CORE COUNT => {coreCount}")
            ROW_DATA["CORES"] = coreCount

            print('=' * 100)
            print(json.dumps(ROW_DATA, indent=4))
            print('=' * 100)
            OUTPUT_OBJ[str(tableIndex) + '_' + str(row_index)] = ROW_DATA
            row_index += 1
    except Exception as E:
        print('=' * 100)
        cprint('-', f"ERROR CARWLING TABLE BODY: {E}")
        print('=' * 100)
        cprint(Fore.WHITE + traceback.format_exc())
        print('=' * 100)

def main():
    url = "https://ark.intel.com/content/www/us/en/ark.html"
    cprint('i', "SENDING REQUEST TO: {}".format(url))
    responseBuffer = r.get(url, headers=HEADER)
    cprint('+', "BUFFER RECIEVED FROM THE SERVER: {}".format(len(responseBuffer.content)))
    responseBuffer.encoding = "UTF-8"
    
    page = bs(responseBuffer.content, "lxml")
    cprint('i', "SEARCHING FOR ANCHOR TAGS...")
    anchorTags = page.find_all('a', href=re.compile("processor"))
    cprint('+', "FOUND ANCHOR TAG COUNT: {}".format(len(anchorTags)))
    
    LINKS = {}

    cprint('i', "RIPPING URLs FROM ANCHOR TAGS...")
    count = 0
    for anchorTag in anchorTags:
        url = DOMAIN + anchorTag['href']
        name = anchorTag.text

        cprint("LINK FOUND FOR: {}".format(name))
        LINKS[count] = url
        count += 1

    cprint('i', "BEGINNING LINK CRAWLING...")
    for index, link in LINKS.items():
        cprint('i', "CURRENT LINK: {}".format(link))
        buffer = r.get(link, headers=HEADER)
        buffer.encoding = 'UTF-8'
        page = bs(buffer.content, "lxml")

        try:
            cprint("i", "SEARCHING TABLE...")
            table = page.find("table")
            cprint("+", "TABLE ELEMENT FOUND...")
            crawl_table(table, index)
        except Exception as E:
            cprint('-', "ERROR CRAWLING PAGE: {}".format(E))

    export("intel_cpus.json", json.dumps(OUTPUT_OBJ, indent=4))
    print(json.dumps(OUTPUT_OBJ, indent=4))

if __name__ == '__main__':
    main()