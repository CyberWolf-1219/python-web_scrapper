from io import TextIOWrapper
import json
import pymongo
from pymongo.collection import Collection

def load_data_file(dataFile: TextIOWrapper) -> dict:
    DATA_OBJ = json.load(dataFile)
    print(f"SIZE: {len(DATA_OBJ)}")
    return DATA_OBJ

def print_table(table: dict) -> bool:
    if (table == None):
        return False
    try:
        rows = list(table.keys())
        headingRow_1 = list(table[rows[0]].values())
        headingRow_2 = list(table[rows[1]].values())
        for i in range(len(headingRow_1)):
            print(f"{i} => {headingRow_1[i]}")
        
        for i in range(len(headingRow_2)):
            print(f"{i} => {headingRow_2[i]}")

        for row in rows:
            cells = list(table[row].values())
            cellCount = len(cells)

            rowTemplate = ""
            for i in range(cellCount):
                rowTemplate += "|{0[" + str(i) + "]:^30}|"

            print("-" * 32 * cellCount)
            print(rowTemplate.format(cells))
            print("-" * 32 * cellCount)

        return True
    except Exception as E:
        print(f"TABLE PRINTING ERROR: {E}")

def check_data_presence(dbCollection: Collection, data: dict) -> bool:
    result = dbCollection.find(data)
    resultLength = len(list(result.clone()))
    if(resultLength > 0):
        return True
    else:
        return False

def push_data_cpu(DATA: dict, COLLECTION: Collection):
    for cpu in DATA.values():
        print(json.dumps(cpu, indent=4))
        isDataInDB = check_data_presence(COLLECTION, {"MODEL": cpu["MODEL"]})
        if(not isDataInDB):
            COLLECTION.insert_one(cpu)

def push_data_gpu(DATA: dict, COLLECTION: Collection):
    for table in DATA.values():
        if(not print_table(table)):
            continue
        nameColumnIndex = int(input("ENTER THE NAME COLUMN INDEX: "))
        memoryColumnIndex = int(input("ENTER THE MEMORY COLUMN INDEX: "))
        for row in table.values():
            print(json.dumps(row, indent=4))
            obj = {
                "NAME": row[str(nameColumnIndex)],
                "MEMORY": row[str(memoryColumnIndex)]
            }
            isDataInDB = check_data_presence(COLLECTION, {"NAME": obj["NAME"]})
            if(not isDataInDB):
                COLLECTION.insert_one(obj)

def push_data_game(DATA: dict, COLLECTION: Collection):
    for game in DATA.keys():
        print(f"INSERTING: {game} = {json.dumps(DATA[game], indent=4)}")
        isDataInDB = check_data_presence(COLLECTION, {"DETAILS.NAME": game})
        if(not isDataInDB):
            COLLECTION.insert_one(DATA[game])

def main():
    HOST = "mongodb://localhost:27017"
    try:
        CLIENT = pymongo.MongoClient(HOST)
    except Exception as E:
        print(f"[-] DATABASE CONNECTION ERROR: {E}")

    databaseNames = CLIENT.list_database_names()
    for database in databaseNames:
        print(f"{databaseNames.index(database)} => {database}")
    selection = int(input("SELECTE A DATABSE: "))
    DATABASE = CLIENT.get_database(databaseNames[selection])

    collectionNames = DATABASE.list_collection_names()
    for collectionName in collectionNames:
        print(f"{collectionNames.index(collectionName)} => {collectionName}")
    selection = int(input("SELECT A COLLECTOIN: "))
    COLLECTION = DATABASE.get_collection(collectionNames[selection])

    dataFile = None
    while(dataFile == None):
        try:
            dataFileName = input("ENTER THE DATA FILE NAME(WITH EXTENTION): ")
            dataFile = open(dataFileName, 'r', encoding='UTF-8')
        except Exception as E:
            print(f"[-] ERROR: {E}")
    
    #dataFileName = "./data/data.json"
    dataObj = load_data_file(dataFile)

    if(COLLECTION.name == 'CPUs'):
        push_data_cpu(dataObj, COLLECTION)
    elif(COLLECTION.name == "GPUs"):
        push_data_gpu(dataObj, COLLECTION)
    elif(COLLECTION.name == "GAMES"):
        push_data_game(dataObj, COLLECTION)

if __name__ == '__main__':
    main()