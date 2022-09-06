from array import array
from doctest import FAIL_FAST
import json
import string
from textwrap import indent
import requests as R
import argparse
import sys
import re
from bs4 import BeautifulSoup as BS


def extract_links(page: BS, filter: str = "") -> dict:
    LINKS = {}
    anchors = page.find_all('a')

    for anchor in anchors:
        try:
            linkText = anchor.text.strip()
            link = "https://en.wikipedia.org" + anchor["href"]

            if(filter != ""):
                if(filter in linkText):
                    LINKS[linkText] = link
                    print(f"[+] NEW LINK FOUND: {linkText}")
            else:
                LINKS[linkText] = link
                print(f"[+] NEW LINK FOUND: {linkText}")

        except Exception as E:
            print(f"[-] LINK EXTRACTION ERROR: {E}")
    
    keys = list(LINKS.keys())
    for i in range(len(keys)):
        print(f"{[i]} => {keys[i]}")

    indexes = input("Choose the Links You Want: ").split(' ')

    if(len(indexes) <= 0):
        return LINKS
    else:
        NEW_LINKS = {}

        for index in indexes:
            key = keys[int(index)]
            NEW_LINKS[key] = LINKS[key]
        
        return NEW_LINKS

def crawler(URL: str, ELEMENT: str) -> dict:
    pageBuffer = R.get(URL)
    pageBuffer.encoding = 'UTF-8'

    page = BS(pageBuffer.content, "lxml")

    elements = page.find_all(ELEMENT)
    print(f"{len(elements)} {ELEMENT} FOUND")

    # ASKING IF THE USER WANT TO CONTINUE THE CRAWLING
    prompt = input("Do you want to continue (Y/N)?: ")
    if(prompt == 'n' or prompt == 'N'):
        return elements
    else:
        TABLES = {}
        tables = elements #JUST RENAMING FOR BETTER UNDERSTANDING

        #LOOPING THROUGH EVERY TABLE FOUND ON THE PAGE
        for table in tables:
            TABLE = {}

            print('=' * 50)
            print(f"TABLE: {tables.index(table)}")
            print('=' * 50)

            # GET EVERY TABLE ROW IN THE TABLE
            tableRows = table.find_all('tr')
            headers = []

            # LOOPING THOURGH FIRST 2 ROWS TO FIND HEADERS OF THE TABLE
            for tableRow in tableRows[0:2]:
                print(f"SCANNING HEADING ROW: {tableRows.index(tableRow)}")

                try:
                    headingElements = tableRow.find_all("th")
                    if headingElements:
                        headings = []
                        for headingElement in headingElements:
                            headings.append(headingElement.text.strip())
                        headers.append(headings)
                except:
                    pass
            
            print(headers)

            HEADING_INDEXES = {
                "MODEL": None,
                "FREQUENCY": None,
                "CORES": None,
                "THREADS": None
            }

            # LOOPING THORUGH FOUND HEADERS TO GET THE INDEXES OF THE REQUIRED TABLE COLUMNS
            for headingsRow in headers:
                for heading in headingsRow:
                    if("Model" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"MODEL HEADING INDEX: {index}")
                        HEADING_INDEXES["MODEL"] = index
                    elif("Fre" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"FREQUENCY HEADING INDEX: {index}")
                        HEADING_INDEXES["FREQUENCY"] = index
                    elif("Cores" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"CORES HEADING INDEX: {index}")
                        HEADING_INDEXES["CORES"] = index
                        if("(threads)" in heading):
                            index = headers.index(headingsRow) + headingsRow.index(heading)
                            print(f"THREADS HEADING INDEX: {index}")
                            HEADING_INDEXES["THREADS"] = index
                    elif("Threads)" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"THREADS HEADING INDEX: {index}")
                        HEADING_INDEXES["THREADS"] = index
            
            print('=' * 50)
            print("HEADING INDEXES")
            print('=' * 50)
            print(json.dumps(HEADING_INDEXES, indent=4))
            print('=' * 50)

            # CHOOSING WHAT TABLE ROWS TO GO THORUGH DEPENDING ON THE HEADING ROWS FOUND
            if(len(headers) == 1):
                selectedTableRows = tableRows[1:]
            elif(len(headers) == 2):
                selectedTableRows = tableRows[2:]
            else:
                continue
            
            # LOOPING THOURGH REST OF THE TABLE ROWS TO GET THE DATA
            for tableRow in selectedTableRows:
                ROW = {
                    "MODEL": None,
                    "FREQUENCY": None,
                    "CORES": None,
                    "THREADS": None,
                }

                # PULLING EVERY TABLE DATA ELEMENT IN THE ROW
                tableData = tableRow.find_all('td')

                # PULLING THE TEXT OUT OF THE SELECTED TABLE DATA ELEMETNS
                for property, index in HEADING_INDEXES.items():
                    try:
                        ROW[property] = tableData[index].text.strip()
                    except:
                        pass

                TABLE[f"ROW {tableRows.index(tableRow)}"] = ROW

                print('=' * 50)
                print(f"ROW: {tableRows.index(tableRow)}")
                print('=' * 50)
                print(json.dumps(ROW, indent=4))
                print('=' * 50)

            TABLES[f"TABLE {tables.index(table)}"] = TABLE

    print('=' * 50)
    print(json.dumps(TABLES, indent=4))
    print('=' * 50)

    return TABLES


def main():
    WIKI_PAGE_URL = "https://en.wikipedia.org/wiki/Category:Lists_of_microprocessors"

    wikiPageBffer = R.get(WIKI_PAGE_URL)
    wikiPageBffer.encoding = "UTF-8"

    wikiPage = BS(wikiPageBffer.content, "lxml")

    links = extract_links(wikiPage, "processors")
    print(json.dumps(links, indent=4))

    elementToFind = input("What ELEMENT to Find: ")

    for link in list(links.values()):
        result = crawler(link, elementToFind)
        with open("data.json", "a+") as fp:
            fp.write(str(json.dumps(result, indent=4)))
            fp.close()

if __name__ == "__main__":
    main()