import re
import json
import argparse
import sys
import math
from colorama import Fore, Back, Style
import colorama
colorama.init(autoreset=True)
# ==============================================================================================

# LOAD JSON FILE INTO A PYTHON OBJECT
def load_file_json(fileName: str):
    print(Fore.BLUE + f"[*] Loading File: {fileName}")
    try:
        dataFile = open(fileName, mode="r")
        DATA_OBJ = json.load(dataFile)
        print(Fore.GREEN + f"[+] File Loaded...")
    except Exception as E:
        print(Fore.WHITE + Back.RED + f"[-] File Loading Error: {E}")
        return

    #print(json.dumps(DATA_OBJ, indent=4))
    walk_data(DATA_OBJ)
    #print(json.dumps(DATA_OBJ, indent=4))


# ITERATE THROUGH ITEMS
def walk_data(object: dict):
    print(Fore.BLUE + f"[*] STARTING WALKER")

    def walker(obj: dict) -> dict:
        if(len(list(obj.keys())) < 1):
            print(Fore.BLUE + "[i] NULL OBJECT RETURNNING ITSELF...")
            return obj
        
        for key, val in obj.items():
            print(Fore.BLUE + f"[i] WALKING: {key}")

            if(type(val) == str):
                print(Fore.GREEN + f"[+] STRING VALUE FOUND: {val}")
                obj[key] = evaluate(key, val)
            elif(type(val) == list):
                print(Fore.BLUE + f"[i] LIST FOUND: {val}")
                if(len(val) > 0):
                    for itemIndex in range(len(val)):
                        print(Fore.BLUE + f"[i] PARSING LIST ITEM: {val[itemIndex]}")
                        val[itemIndex] = evaluate(key, val[itemIndex])
            elif(type(val) == dict):
                print(Fore.BLUE + f"[i] ANOTHER OBJECT DETECTED: {key}")
                walker(val)
            else:
                obj[key] = val
            
        return obj

    return walker(object)

def evaluate(key: str, val: str) -> str:
    print(Fore.GREEN + f"[+] INCOMING DATA TO EVALUATOR: {key} = {val}")

    if(key == "PROCESSORS"):
        foundProcessors = []
        print(Fore.BLUE + f"[i] PROCESSOR SECTION PASSED IN...")

        #split
        try:
            items = []
            if("/" in val):
                items = val.split("/")
                print(Fore.GREEN + f"[+] SPLITTED INTO {len(items)} PARTS BY '/'")
            elif("or" in val):
                items = val.split("or")
                print(Fore.GREEN + f"[+] SPLITTED INTO {len(items)} PARTS BY 'or'")
            elif("|" in val):
                items = val.split("|")
                print(Fore.GREEN + "[+] SPLITTED INTO {len(items)} PARTS BY '|'")
            elif("," in val):
                items = val.split("|")
                print(Fore.GREEN + "[+] SPLITTED INTO {len(items)} PARTS BY '|'")
            else:
                items.append(val)
                print(Fore.BLUE + f"[i] SPLITTING CHARACTERS NOT FOUND")
        except Exception as E:
            print(Fore.WHITE + Back.RED + f"[-] ERROR WHILE SPLITTING STRING: {E}")
            return

        print(f"ARRAY: {items}")

        #clean up
        try:
            itemsToRemove = ["®", "™", " or better", " or equivalent", "equivalent", "better", "\+", " or faster", "(R)", " or greater", "@", "or similar", "series", "gen", "(", ")"]
            for itemIndex in range(len(items)):
                for removeItem in itemsToRemove:
                    print(Fore.BLUE + f"[i] REMOVING '{removeItem}' IN '{items[itemIndex]}'")
                    items[itemIndex] = re.sub(removeItem, "", items[itemIndex])
        except Exception as E:
            print(Fore.WHITE + Back.RED + f"[-] ERROR WHILE CLEANING UP THE STRINGS: {E}")
            return

        print(f"[i] ARRAY: {items}")

        #replace
        try:
            itemsToReplace = ["-"]
            for itemIndex in range(len(items)):
                for replaceItem in itemsToReplace:
                    print(Fore.BLUE + f"[i] REPLACING {replaceItem} in {items[itemIndex]}")
                    items[itemIndex] = re.sub(replaceItem, " ", items[itemIndex])
        except Exception as E:
            print(Fore.WHITE + Back.RED + f"[-] ERROR WHILE REPLACING '-'s in STRINGS: {E}")
            return

        print(f"[i] ARRAY: {items}")

        #find intel core
        try:
            intelCorePattern = re.compile(r"((intel\s)?(core\s?)?[2i](\s?duo|\s?quad|[3579])\s(\d{1,5}\w?)?)", re.IGNORECASE | re.VERBOSE)
            for item in items:
                matches = intelCorePattern.findall(item)
                if len(matches) > 0:
                    print(f"[+] INTEL CORE PATTERN: {matches[0][0]}")
                    foundProcessors.append(matches[0][0])
        except Exception as E:
            print(Fore.WHITE + Back.RED + f"[-] ERROR INTEL CORE PATTERN: {E}")
            return

        # intelXeonPattern = re.compile(r"")
        # intelAtomPattern = re.compile(r"")
        # intelPentiumPattern = re.compile(r"")
        # intelCeleronPattern = re.compile(r"")

        #find amd
        # try:
        #     amdPattern = re.compile(r"amd", re.IGNORECASE | re.VERBOSE)
        #     for item in items:
        #         matches = amdPattern.findall(item)
        #         if len(matches) > 0:
        #             print(f"[+] AMD PATTERN: {matches[0][0]}")
        # except Exception as E:
        #     print(Fore.WHITE + Back.RED + f"[-] ERROR IN AMD PATTERN: {E}")
        #     return

        #find freqeuency
        try:
            frequencyPattern = re.compile(r"(\d\.\d{1,2}\s?[Gg][Hh]z)", re.IGNORECASE | re.VERBOSE)
            for item in items:
                matches = frequencyPattern.findall(item)
                if len(matches) > 0:
                    print(Fore.GREEN + f"[+] FREQUENCY PATTERN: {matches[0]}")
                    foundProcessors.append(matches[0])
        except Exception as E:
            print(Fore.WHITE + Back.RED + f"[-] ERROR IN FREQUENCY PATTERN: {E}")
            return

        #find explicit
        # try:
        #     explicitItemPattern = re.compile(r"only", re.IGNORECASE | re.VERBOSE)
        #     for item in items:
        #         matches = explicitItemPattern.findall(item)
        #         if len(matches) > 0:
        #             print(f"[+] EXPLICIT PATTERN: {matches[0][0]}")
        # except Exception as E:
        #     print(Fore.WHITE + Back.RED + f"[-] ERROR IN EXPLICIT PATTERN: {E}")
        #     return

        #find any
        # try:
        #     anyPattern = re.compile(r"Any", re.IGNORECASE | re.VERBOSE)
        #     for item in items:
        #         matches = anyPattern.findall(item)
        #         if len(matches) > 0:
        #             print(f"[+] ANY PATTERN: {matches[0][0]}")
        # except Exception as E:
        #     print(Fore.WHITE + Back.RED + f"[-] ERROR IN 'ANY' PATTERN': {E}")
        #     return

    elif(key == "GRAPHICS"):
        pass

    elif(key == "MEMORY"):
        if('GB' in val or 'gb' in val):
            digits = re.findall("\d{1,2}", val, re.VERBOSE)
            print(Fore.GREEN + "[+] MEMORY CAPACITY: {0:.0f} GB".format(int(digits[0])))
            return int(digits[0])
        elif("MB" in val or 'mb' in val):
            digits = re.findall("\d{1,4}", val)
            print(Fore.GREEN + "[+] MEMORY FOUND & CALCULATED: {0:.2f} GB".format(int(digits[0])/1024))
            return round(int(digits[0]), 2)

    elif(key == "STORAGE"):
        if('GB' in val or 'gb' in val):
            digits = re.findall("\d{1,2}", val, re.VERBOSE)
            print(Fore.GREEN + "[+] STORAGE CAPACITY: {0:.0f} GB".format(int(digits[0])))
            return int(digits[0])
        elif("MB" in val or 'mb' in val):
            digits = re.findall("\d{1,4}", val)
            print(Fore.GREEN + "[+] STORAGE FOUND & CALCULATED: {0:.2f} GB".format(int(digits[0])/1024))
            return round(int(digits[0]), 2)

    elif(key == "GENRES"):
        return val

    elif(key == "TAGS"):
        return val
        
    return(val)

# FORMAT DATA ON A TEMPLATE
# REWRITE THE DATA INTO THE FILE

def main():
    parser = argparse.ArgumentParser(description="Clean Text in Your Dataset and Format Data.")
    parser.add_argument("-f", type=str, help="Data File to Read")

    # args = parser.parse_args()

    # if(len(sys.argv) < 2):
    #     parser.print_help()
    #     sys.exit()

    load_file_json("./data/games.json")

if __name__ == "__main__":
    main()