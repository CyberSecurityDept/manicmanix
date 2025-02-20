from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://167.71.195.26:27017"))
print(client)
db = client["cyber_security"]
