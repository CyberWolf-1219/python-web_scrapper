#==========================================================================
import json
from textwrap import indent
import requests as r
from bs4 import BeautifulSoup as bs
from bs4.element import ResultSet, Tag, NavigableString
import colorama
from colorama import Fore, Back
colorama.init(autoreset=True)

import traceback
#==========================================================================
HEADER = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
#==========================================================================
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

def export(fileName:str, content:str):
    try:
        with open(fileName, mode="a+", encoding="UTF-8") as fp:
            fp.write(content)
            fp.close()
    except Exception as E:
        cprint(Fore.WHITE + traceback.format_exc())
        cprint('+', "exporting data: {}", E)

def get_page(url: str) -> bs:
    responseBuffer = r.get(url, headers=HEADER)
    responseBuffer.encoding = "UTF-8"
    page = bs(responseBuffer.content, "lxml")
    return page

def get_tables(page: bs, filters: dict = {}) -> ResultSet:
    tables = page.find_all("table", filters)
    return tables

def get_table_dimentions(table: Tag | NavigableString) -> list:
    rows = table.find_all("tr")
    row = rows[0]
    cells = row.find_all(['th', 'tr'])
    rowLength = 0
    for cell in cells:
        try:
            cellColSpan = cell['colspan']
        except:
            cellColSpan = 1

        rowLength += int(cellColSpan)

    return [len(rows), rowLength]

def get_table_rows(table: Tag | NavigableString, filters: dict = {}) -> ResultSet:
    tableRows = table.find_all("tr", filters)
    return tableRows

def get_row_cells(tableRow: Tag | NavigableString, filters: dict = {}) -> ResultSet:
    rowCells = tableRow.find_all(["td", "th"], filters)
    return rowCells

def create_virtual_table(rows: int, columns: int) -> dict:
    virtualTable = {}
    for row in range(rows):
        virtualTable[row] = {}
        for cell in range(columns):
            virtualTable[row][cell] = "N/A"

    print(json.dumps(virtualTable, indent=4))
    return virtualTable

def fill_virtula_table(virtualTable: dict, tableElement: Tag | NavigableString) -> dict:
    tableRows = get_table_rows(tableElement)
    carryList = {}
    for i in range(0, len(tableRows)):
        carryList["Row " + str(i)] = {}

    

    for currentRowIndex in range(len(tableRows)):
        tableRow = tableRows[currentRowIndex]
        vTableRow = virtualTable[currentRowIndex]
        tableCells = get_row_cells(tableRow)

        print("\n{:=<158}\n".format("CARRY LIST "))
        print(json.dumps(carryList, indent=4))
        print("=" * 158)

        print("\n{:=<158}\n".format("TABLE ROW "))
        print(bs.prettify(tableRow))
        print("=" * 158)

        carried = carryList["Row " + str(currentRowIndex)]
        print("\n{:=<158}\n".format("CARRIED ITEMS "))
        print(json.dumps(carried, indent=4))
        print("=" * 158)

        if(len(carried) > 0):
            for value, carryDirections in carried.items():
                startCell, colSpan = carryDirections

                for cellIndex in range(startCell, startCell + colSpan):
                    vTableRow[cellIndex] = value
        
        for cellIndex in range(len(tableCells)):
            tableCell = tableCells[cellIndex]
            cellValue = tableCell.text.strip()

            print("\n{:=<158}\n".format("VIRTUAL TABLE ROW "))
            print(json.dumps(vTableRow, indent=4))
            print("=" * 158)

            print("\n{:=<158}\n".format("CURRENT CELL "))
            print(tableCell)
            print("=" * 158)

            for vCellIndex, vCellValue in vTableRow.items():
                if(vCellValue == "N/A"):
                    firstEmptyVCell = vCellIndex
                    break
            
            print("\n{:=<158}\n".format("FIRST VIRTUAL EMPTY CELL "))
            print(firstEmptyVCell)
            print('=' * 158)

            cellRowSpan = 1
            cellColSpan = 1
            try:
                cellRowSpan = int(tableCell['rowspan'])
            except Exception as E:
                print(f"NO: {E}")

            try:
                cellColSpan = int(tableCell['colspan'])
            except Exception as E:
                print(f"NO: {E}")

            if(cellRowSpan > 1):
                for rowIndexToCarry in range(currentRowIndex + 1, currentRowIndex + cellRowSpan):
                    rowToCarry = carryList["Row " + str(rowIndexToCarry)]
                    rowToCarry[cellValue] = [firstEmptyVCell, cellColSpan]

            for cellIndexToFill in range(firstEmptyVCell, firstEmptyVCell + cellColSpan):
                vTableRow[cellIndexToFill] = cellValue

        print("\n{:~^158}".format(" END OF ROW "))
        # input("ON HOLD...")

    return virtualTable

def print_virtual_table(virtualTable: dict):
    rows = virtualTable.keys()

    for row in rows:
        cells = virtualTable[row].values()
        cellCount = len(cells)

        rowTemplate = ""
        for i in range(cellCount):
            rowTemplate += "|{0[" + str(i) + "]:^20}|"
            
        print("-" * 20 * cellCount)
        print(rowTemplate.format(list(cells)))
        print("-" * 20 * cellCount)

def main():
    url = ""
    while ("http" not in url):
        url = input("ENTER URL TO THE PAGE: ")

    page = get_page(url)
    tables = get_tables(page)
    tableDimentions = get_table_dimentions(tables[0])

    vTable = create_virtual_table(tableDimentions[0], tableDimentions[1])
    vTable = fill_virtula_table(vTable, tables[0])
    print(json.dumps(vTable, indent=4))
    print_virtual_table(vTable)
    #export("table.txt", json.dumps(vTable, indent=4))

if __name__ == '__main__':
    main()