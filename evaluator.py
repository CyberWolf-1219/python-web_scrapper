import re
import json
import pymongo
from pymongo.collection import Collection

# CPU PATTERNS ==================================================================================================
INTEL_PATTERNS = {
    "INTEL_I_MODEL_PATTERN" : re.compile(r"\bi\d\s?\d{3,5}\w{,2}", re.IGNORECASE),
    "INTEL_CORE_PATTERN" : re.compile(r"\bcore\s{,1}2\s{,1}duo|quad", re.IGNORECASE),
    "INTEL_CORE_PATTERN_2" : re.compile(r"\b(quad\s|dual\s)core", re.IGNORECASE),
    "INTEL_CELERON_PATTERN" : re.compile(r"\bceleron\s\S{3,5}", re.IGNORECASE),
    "INTEL_PENTIUM_PATTERN" : re.compile(r"\bpentium\s\S{3,5}", re.IGNORECASE),
    "INTEL_ATOM_PATTERN" : re.compile(r"\bAtom\s\S{4,5}", re.IGNORECASE)
}

AMD_PATTERNS = {
    "AMD_RYZEN_PATTERN" : re.compile(r"\bRyzen\s\d\s\S{4,5}\w{,2}", re.IGNORECASE),
    "AMD_FX_PATTERN" : re.compile(r"\bFX\s?\d{3,4}", re.IGNORECASE),
    # ADD AMD A SERIES PATTERN
    # ADD AMD ATHLON PATTERN
}
# =================================================================================================================

# GPU PATTERNS =====================================================================================================
NVIDIA_GRAPHIC_PATTERNS = {
    # GTX
    "GTX_PATTERN" : re.compile(r"\bgtx\s\d{3,4} ?\w?", re.IGNORECASE),
    # GT
    "GT_PATTERN" : re.compile(r"\bgt\s\d{3,4}", re.IGNORECASE),
    # RTX
    "RTX_PATTERN": re.compile(r"\brtx\s\d{3,4}\w?", re.IGNORECASE)
}

AMD_GRAPHIC_PATTERNS = {
    # R{}
    "R_PATTERN" : re.compile(r"Radeon \bR\d ?\b\S{3,6}", re.IGNORECASE),
    # RX
    "RX_PATTERN" : re.compile(r"Radeon \brx ?\d{3,4} ?x?t?", re.IGNORECASE),
    # HD
    "RADEON_HD_PATTERN" : re.compile(r"Radeon \bHD ?\d{3,4}\w?", re.IGNORECASE)
}
# ==================================================================================================================

# SYSTEM MEMORY PATTERN ============================================================================================
MEMORY_PATTERN = re.compile(r"\d{1,4} *[GM][B]", re.IGNORECASE)
# ==================================================================================================================

def load_json_file(fileName: str) -> dict:
    try:
        json_obj = None
        fileParser = open(fileName, encoding="UTF-8", mode='r')
        json_obj = json.load(fileParser)
        return json_obj
    except Exception as E:
        print(f"FILE LOADING ERROR: {E}")

def export_to_json(fileName: str, obj: dict):
    try:
        with open(fileName, encoding="UTF-8", mode='a+') as fp:
            fp.write(json.dumps(obj, indent=4))
            fp.close()
        
        print(f"EXPORTING COMPLETE: {fileName}")
    except Exception as E:
        print(f"EXPOTING ERROR: {E}")

def pull_from_database(collection_: Collection, query: dict) -> str:
    for i in collection_.aggregate(query):
        return str(i["_id"])

def evaluate_data(category: str, itemString: str) -> str | None:
    if(category == "cpu"):
        result = pull_from_database(cpuCollection, [
            {
                "$project":{
                    "MODEL":{
                        "$replaceAll":{
                            "input":"$MODEL",
                            "find": " ",
                            "replacement": ""
                        }
                    },
                }
            },
            {
                "$project":{
                    "MODEL":{
                        "$replaceAll":{
                            "input":"$MODEL",
                            "find": "-",
                            "replacement": ""
                        }
                    }
                }
            },
            {
                "$match":{
                    "MODEL":{
                        "$regex":itemString,
                        "$options": "i"
                    }
                }
            }
        ])
        
        if(result != None):
            return(result)
        else:
            return None

    if(category == "gpu"):
        result = pull_from_database(gpuCollection, [
            {"$project":{
                "NAME":{
                    "$replaceAll":{
                        "input": "$NAME",
                        "find": " ",
                        "replacement": "",
                    }
                }
            }},
            {
                "$project":{
                    "NAME":{
                        "$replaceAll":{
                            "input": "$NAME",
                            "find": "-",
                            "replacement": "",
                        }
                    }
                }
            },
            {
                "$match":{
                    "NAME":{
                        "$regex": itemString
                    }
                }
            }
        ])
        
        if(result != None):
            return(result)
        else:
            return None

def check_cpu(cpuString: str) -> list:
    print("{:=<158}".format("# PROCESSOR "))

    try:
        print(f"CPU STRING: {cpuString}")
        cpuString = re.sub(r"(\(R\)|\s{2,}|@|\+|-|™|®|,)", " ", cpuString, re.IGNORECASE)
        print(f"CPU STRING: {cpuString}")
        matchingPhrases = []

        for patternName, pattern in INTEL_PATTERNS.items():
            print(f"CURRENT PATTERN: {patternName}")
            matchedPhrases = re.findall(pattern, cpuString)
            print(f"MATCHED PHRASES: {matchedPhrases}")
            if(len(matchedPhrases) > 0):
                for phrase in matchedPhrases:
                    matchingPhrases.append(phrase)
        
        for patternName, pattern in AMD_PATTERNS.items():
            print(f"CURRENT PATTERN: {patternName}")
            matchedPhrases = re.findall(pattern, cpuString)
            print(f"MATCHED PHRASES: {matchedPhrases}")
            if(len(matchedPhrases) > 0):
                for phrase in matchedPhrases:
                    matchingPhrases.append(phrase)

        print(matchingPhrases)
        evalueatedCPUList = []
        for item in matchingPhrases:
            item = item.replace(" ", "")
            print(f"SENDING TO VALIDATOR: {item}")
            matched = evaluate_data("cpu", item)
            if(matched != None):
                evalueatedCPUList.append(matched)

        print('=' * 158)
        return evalueatedCPUList
    except Exception as E:
        print(f"CPU CHECK ERROR: {E}")

def check_gpu(gpuString: str) -> list:
    print("{:=<158}".format("# GRAPHIC "))
    try:
        print(f"CPU STRING: {gpuString}")
        gpuString = re.sub(r"(\(R\)|\s{2,}|@|\+|-|™|®|,|\d ?[gm]b)", " ", gpuString, re.IGNORECASE)
        print(f"CPU STRING: {gpuString}")
        matchingPhrases = []

        for patternName, pattern in NVIDIA_GRAPHIC_PATTERNS.items():
            print(f"CURRENT PATTERN: {patternName}")
            matchedPhrases = re.findall(pattern, gpuString)
            print(f"MATCHED PHRASES: {matchedPhrases}")
            if(len(matchedPhrases) > 0):
                for phrase in matchedPhrases:
                    matchingPhrases.append(phrase)

        for patternName, pattern in AMD_GRAPHIC_PATTERNS.items():
            print(f"CURRENT PATTERN: {patternName}")
            matchedPhrases = re.findall(pattern, gpuString)
            print(f"MATCHED PHRASES: {matchedPhrases}")
            if(len(matchedPhrases) > 0):
                for phrase in matchedPhrases:
                    matchingPhrases.append(phrase)

        print(matchingPhrases)
        evalueatedGPUList = []
        for item in matchingPhrases:
            item = item.replace(" ", "")
            print(f"SENDING TO VALIDATOR: {item}")
            matched = evaluate_data("gpu", item)
            if(matched != None):
                evalueatedGPUList.append(matched)

        print('=' * 158)
        return evalueatedGPUList
    except Exception as E:
        print(f"GPU CHECK ERROR: {E}")

def check_memory(memoryString: str) -> str:
    print("{:=<158}".format("# MEMORY "))

    try:
        print(f"MEMORY STRING: {memoryString}")
        memoryString = re.sub(r"(\s{2,}|@|\+|-|™|®|,|ram)", "", memoryString, re.IGNORECASE)
        print(f"MEMORY STRING: {memoryString}")

        matchingPhrase = re.findall(MEMORY_PATTERN, memoryString)[0]
        print(f"MEMORY MATCH: {matchingPhrase}")
        if(("GB" in matchingPhrase) | ("gb" in matchingPhrase)):
            matchingPhrase = matchingPhrase.replace("GB", "").replace("gb", "")
            memoryInGB = int(matchingPhrase)
            memoryInMB = memoryInGB * 1024
        else:
            matchingPhrase = matchingPhrase.replace("MB", "").replace("GB", "")
            memoryInMB = int(matchingPhrase)
        
        print(f"MEMORY IN MB: {memoryInMB}")
        print('=' * 158)

        return memoryInMB
    except Exception as E:
        print(f"REGEX MEMORY ERROR: {E}")

def walk_game_obj(gamesObj: dict) -> dict:
    outPutGames = {}

    for game in gamesObj.values():
        systemSection = game["SYSTEM_REQUIREMENTS"]
        cpu = systemSection["PROCESSORS"]
        gpu = systemSection["GRAPHICS"]
        memory = systemSection["MEMORY"]
        storage = systemSection["STORAGE"]

        if((cpu != None) & (cpu != "")):
            checkedCPU = check_cpu(cpu)
            print(f"CPU IDs: {checkedCPU}")

        if((gpu != None) & (gpu != "")):
            checkedGPU = check_gpu(gpu)
            print(f"GPU IDs: {checkedGPU}")

        if((memory != None) & (memory != "")):
            checkedMemory = check_memory(memory)
            print(f"CHECKED MEMORY: {checkedMemory}")

        if((storage != None) & (storage != "")):
            checkedStorage = check_memory(storage)
            print(f"CHECKED STORAGE: {checkedStorage}")

        if((checkedCPU != []) and (checkedGPU != [])):
            gameName = game["DETAILS"]["NAME"]
            evaluatedGame = game
            evaluatedGame["SYSTEM_REQUIREMENTS"]["PROCESSORS"] = checkedCPU
            evaluatedGame["SYSTEM_REQUIREMENTS"]["GRAPHICS"] = checkedGPU
            evaluatedGame["SYSTEM_REQUIREMENTS"]["MEMORY"] = checkedMemory
            evaluatedGame["SYSTEM_REQUIREMENTS"]["STORAGE"] = checkedStorage
            outPutGames[gameName] = evaluatedGame

            print(json.dumps(game, indent=4))

    return outPutGames

def main():
    # fileName = input("FILE NAME: ")
    fileName = "./data/games.json"
    gamesObj = load_json_file(fileName)

    HOST = "mongodb://localhost:27017"
    try:
        CLIENT = pymongo.MongoClient(HOST)
    except Exception as E:
        print(f"MONGO CONNECT ERROR: {E}")

    databases = CLIENT.list_database_names()
    for i in range(len(databases)):
        print(f"{[i]} => {databases[i]}")
    selectedDatabaseIndex = int(input("SELECT A DATABASE: "))
    DATABASE = CLIENT.get_database(databases[selectedDatabaseIndex])

    collections = DATABASE.list_collection_names()
    for i in range(len(collections)):
        print(f"{[i]} => {collections[i]}")
    cpuCollectionIndex = int(input("SELECT CPU COLLECTION: "))
    gpuCollectionIndex = int(input("SELECT GPU COLLECTION: "))

    global gpuCollection
    global cpuCollection

    cpuCollection = DATABASE.get_collection(collections[cpuCollectionIndex])
    gpuCollection = DATABASE.get_collection(collections[gpuCollectionIndex])

    evaluatedGames = walk_game_obj(gamesObj)

    nameParts = fileName.split(".json")
    fileName = nameParts[0] + "_evaluated.json"
    export_to_json(fileName, evaluatedGames)

if __name__ == '__main__':
    main()