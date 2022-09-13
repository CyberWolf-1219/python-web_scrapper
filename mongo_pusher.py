from io import TextIOWrapper
import json
import pymongo
from pymongo.collection import Collection

def load_data_file(dataFile: TextIOWrapper) -> dict:
    DATA_OBJ = json.load(dataFile)
    print(f"SIZE: {len(DATA_OBJ)}")
    return DATA_OBJ

def push_data_cpu(DATA: dict, COLLECTION: Collection):
    for cpu in DATA.values():
        print(json.dumps(cpu, indent=4))
        COLLECTION.insert_one(cpu)

def push_data_game(DATA: dict, COLLECTION: Collection):
    for game in DATA:
        print(f"INSERTING: {game} = {json.dumps(DATA[game], indent=4)}")
        try:
            COLLECTION.insert_one(DATA[game])
        except Exception as E:
            print(f"[-] ERROR ON INSERTING DATA: {E}")

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
        pass
    elif(COLLECTION.name == "GAMES"):
        push_data_game(dataObj, COLLECTION)

if __name__ == '__main__':
    main()