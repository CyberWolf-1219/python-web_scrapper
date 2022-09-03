import json
import pymongo

CLIENT_CONNECTION = "mongodb://localhost:27017"

# CONNECT TO THE DATABASE
CLIENT = pymongo.MongoClient(CLIENT_CONNECTION)

# ASK FOR DATABASE TO INTERACT WITH
print(CLIENT.list_database_names())
selectedDatabase = int(input("ENTER DATA BASE INDEX: "))

try:
    DATABASE = CLIENT.get_database(CLIENT.list_database_names()[selectedDatabase])
except Exception as E:
    print(f"[-] CANNOT CONNECT TO THE DATABASE: {E}")

# ASK FOR THE COLLECTION TO INTERACT WITH
print(DATABASE.list_collection_names())
selectedCollection = int(input("ENTER COLLECTION INDEX: "))

try:
    COLLECTION = DATABASE.get_collection(DATABASE.list_collection_names()[selectedCollection])
except Exception as E:
    print(f"[-] CANNOT GET THE COLLECTION: {E}")

# ASK FOR THE FILE TO PULL THE DATA FROM
dataFileName = input("ENTER DATA FILE (with extention): ")

dataFile = open(dataFileName, encoding="UTF-8", mode="r")

# PULL THE DATA FROM THE FILE
JSON_DATA = json.load(dataFile)

# PUSH DATA TO THE COLLECTION
def pushData(data):
    COLLECTION.insert_one(data)

print(len(JSON_DATA.values()))
print(len(JSON_DATA.keys()))
input()

for value in JSON_DATA.values():
    print(value)
    pushData(value)

