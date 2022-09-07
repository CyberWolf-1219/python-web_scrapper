from io import TextIOWrapper
import json
import pymongo
from pymongo.collection import Collection

def load_data_file(dataFile: TextIOWrapper) -> dict:
    DATA_OBJ = json.load(dataFile)
    print(f"SIZE: {len(DATA_OBJ)}")
    return DATA_OBJ

def push_data(DATA: dict, COLLECTION: Collection):
    for list in DATA:
        if("Intel" in list):
            MANUFACTURER = "INTEL"
        elif("AMD" in list):
            MANUFACTURER = "AMD"
        tables = DATA[list]
        for table in tables:
            rows = tables[table]
            for row in rows:
                ROW = rows[row]
                MODEL = ROW["MODEL"]
                FREQUENCY = ROW["FREQUENCY"]
                CORES = ROW["CORES"]
                THREADS = ROW["THREADS"]

                print(f"{MANUFACTURER} {MODEL} {FREQUENCY} {CORES} {THREADS}")
                COLLECTION.insert_one({"MANUFACTURER": MANUFACTURER, "MODEL": MODEL, "FREQUENCY": FREQUENCY, "CORES": CORES, "THREADS": THREADS})

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

    #dataFileName = input("ENTER THE DATA FILE NAME(WITH EXTENTION): ")
    dataFileName = "./data/data.json"
    dataFile = open(dataFileName, 'r', encoding='UTF-8')

    dataObj = load_data_file(dataFile)
    push_data(dataObj, COLLECTION)

if __name__ == '__main__':
    main()