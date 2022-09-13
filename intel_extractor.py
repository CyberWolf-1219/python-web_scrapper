from bs4 import BeautifulSoup as BS
import requests as R
import json
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

def cprint(sign: str, text: str, parameters: list):
    fore = None
    back = None
    buffer = None

    if(sign == "+"):
        fore = Fore.WHITE
        back = Fore.GREEN
        buffer = fore + back + f"[{sign}] " + text.format(parameters)
    elif(sign == "i"):
        fore = Fore.WHITE
        back = Back.BLUE
        buffer = fore + back + f"[{sign}] " + text.format(parameters)
    elif(sign == "-"):
        fore = Fore.WHITE
        back = Back.RED
        buffer = fore + back + f"[{sign}] " + text.format(parameters)
    
    print(buffer)

def write_to_file(fileName: str, content: str):
    try:
        with open(fileName, encoding="UTF-8", mode="a+") as fp:
            fp.write(content)
            fp.close()
    except Exception as E:
        cprint('-', "FILE WRITING ERROR: {}", E)

def find_element(parentElement, elementName, attribute = str | None):
    elementList = []
    try:
        if(attribute == None):
             return elementList
            
        return elementList

    except Exception as E:
        cprint('-', "CRAWLING ERROR: {}", E)

def crawl_table(tableElement):
    tableHead = None
    tableBody = None

    try:
        pass
    except Exception as E:
        cprint('-', "TABLE CRAWLING ERROR: {}", E)

def get_page(URL: str):
    pass

CONTAIN_CHILDEN = False
def main():
    # GET PAGE
    # SEARCH FOR ELEMENTS
    # GET EACH PAGE
    # CRAWL TABLE
    # WRITE OUT PUT
    pass