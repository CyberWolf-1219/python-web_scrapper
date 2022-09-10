import json
import requests as R
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
    
    print('=' * 100)
    keys = list(LINKS.keys())
    for i in range(len(keys)):
        print(f"{[i]} => {keys[i]}")
    print('=' * 100)

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
    print(f"[i] {len(elements)} {ELEMENT} FOUND")

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

            #print('=' * 50)
            print(f"[i] TABLE: {tables.index(table)}")
            #print('=' * 50)

            # GET EVERY TABLE ROW IN THE TABLE
            tableRows = table.find_all('tr')
            headers = []

            # LOOPING THOURGH FIRST 2 ROWS TO FIND HEADERS OF THE TABLE
            for tableRow in tableRows[0:2]:
                print(f"[i] SCANNING HEADING ROW: {tableRows.index(tableRow)}")
                #print(f"[i] HEADINGS ROW: {BS.prettify(tableRow)}")

                try:
                    headingElements = tableRow.find_all("th")
                    if headingElements:
                        headings = []
                        for headingElement in headingElements:
                            headings.append(headingElement.text.strip())
                        headers.append(headings)
                except:
                    pass
            
            #print(headers)

            HEADING_INDEXES = {
                "MODEL": None,
                "FREQUENCY": None,
                "CORES": None,
                "THREADS": None,
            }

            # LOOPING THORUGH FOUND HEADERS TO GET THE INDEXES OF THE REQUIRED TABLE COLUMNS
            for headingsRow in headers:
                for heading in headingsRow:
                    if("Model" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"[i] MODEL HEADING INDEX: {index}")
                        HEADING_INDEXES["MODEL"] = index
                    elif("Fre" in heading or "Clock" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"[i] FREQUENCY HEADING INDEX: {index}")
                        HEADING_INDEXES["FREQUENCY"] = index
                    elif("Cores" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"[i] CORES HEADING INDEX: {index}")
                        HEADING_INDEXES["CORES"] = index
                        if("(threads)" in heading):
                            index = headers.index(headingsRow) + headingsRow.index(heading)
                            print(f"[i] THREADS HEADING INDEX: {index}")
                            HEADING_INDEXES["THREADS"] = index
                    elif("Threads)" in heading):
                        index = headers.index(headingsRow) + headingsRow.index(heading)
                        print(f"[i] THREADS HEADING INDEX: {index}")
                        HEADING_INDEXES["THREADS"] = index
            
            if(HEADING_INDEXES["MODEL"] == "None" or HEADING_INDEXES["FREQUENCY"] == None):
                print(f"[-] SKIPPING TABLE {tables.index(table)} DUE TO MISSING DATA")
                continue

            #print('=' * 50)
            #print("HEADING INDEXES")
            #print('=' * 50)
            #print(json.dumps(HEADING_INDEXES, indent=4))
            #print('=' * 50)

            # CHOOSING WHAT TABLE ROWS TO GO THORUGH DEPENDING ON THE HEADING ROWS FOUND
            if(len(headers) == 1):
                selectedTableRows = tableRows[1:]
            elif(len(headers) == 2):
                selectedTableRows = tableRows[2:]
            else:
                continue
            
            # LOOPING THOURGH REST OF THE TABLE ROWS TO GET THE DATA
            for tableRow in selectedTableRows:
                #print(f"TABLE ROW: {BS.prettify(tableRow)}")
                print('=' * 100)
                print(f"ROW: {tableRows.index(tableRow)}")
                #print('=' * 50)
                ROW = {
                    "MODEL": "",
                    "FREQUENCY": "",
                    "CORES": "",
                    "THREADS": "",
                }

                # PULLING EVERY TABLE DATA ELEMENT IN THE ROW
                tableDataElements = tableRow.find_all('td')
                if(len(tableDataElements) <= 1):
                    continue

                # PULLING THE TEXT OUT OF THE SELECTED TABLE DATA ELEMETNS
                for property, index in HEADING_INDEXES.items():
                    try:
                        if(property == "CORES"):
                            value = tableDataElements[index].text.strip().split('  ')[0]
                            print(f"[+] {property}: {value}")
                            ROW[property] = value
                        elif(property == "THREADS"):
                            value = tableDataElements[index].text.strip().split('  ')[1].replace('(', '').replace(')', '')
                            print(f"[+] {property}: {value}")
                            ROW[property] = value
                        else:
                            value = re.sub(r"&nbsp[GgMm][Hh]z", "", tableDataElements[index].text.strip())
                            print(f"[+] {property}: {value}")
                            ROW[property] = value
                    except Exception as E:
                        print(f"[-] DATA PULLING ERROR: {E}")

                TABLE[f"ROW {tableRows.index(tableRow)}"] = ROW

                #print('=' * 50)
                #print(f"ROW: {tableRows.index(tableRow)}")
                #print('=' * 50)
                #print(json.dumps(ROW, indent=4))
                print('=' * 100)

            TABLES[f"TABLE {tables.index(table)}"] = TABLE

    #print('=' * 50)
    #print(json.dumps(TABLES, indent=4))
    #print('=' * 50)

    return TABLES

def main():
    WIKI_PAGE_URL = "https://en.wikipedia.org/wiki/Category:Lists_of_microprocessors"
    URL = input("PASTE URL: ")

    if (not URL):
        wikiPageBffer = R.get(WIKI_PAGE_URL)
    elif (URL):
        wikiPageBffer = R.get(URL)

    wikiPageBffer.encoding = "UTF-8"

    wikiPage = BS(wikiPageBffer.content, "lxml")

    links = extract_links(wikiPage, "processors")
    print(json.dumps(links, indent=4))

    elementToFind = input("What ELEMENT to Find: ")

    DATA = {}
    PAGES = list(links.keys())
    for page in PAGES:
        result = crawler(links[page], elementToFind)
        DATA[page] = result

    with open("./data/data.json", "w") as fp:
        fp.write(str(json.dumps(DATA, indent=4)))
        fp.close()

if __name__ == "__main__":
    main()