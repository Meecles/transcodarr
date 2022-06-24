import pymongo
import os
from pymongo import MongoClient

mongo_ip = "localhost"
if "MONGO_HOST" in os.environ:
    mongo_ip = os.environ['MONGO_HOST']
db_connect_string = "mongodb://{}:27017".format(mongo_ip)
db_name = "transcodarr"
if "MONGO_INITDB_DATABASE" in os.environ:
    db_name = os.environ['MONGO_INITDB_DATABASE']
print("Connecting to {}".format(db_connect_string))
username, password = None, None
if "MONGO_INITDB_ROOT_USERNAME" in os.environ and "MONGO_INITDB_ROOT_PASSWORD" in os.environ:
    username = os.environ['MONGO_INITDB_ROOT_USERNAME']
    password = os.environ['MONGO_INITDB_ROOT_PASSWORD']
connect_auth = username is not None and password is not None

client = None

if connect_auth:
    client = MongoClient(mongo_ip, username=username,
                         password=password,
                         authSource='admin',
                         authMechanism='SCRAM-SHA-1')
else:
    client = pymongo.MongoClient(db_connect_string)

db = client[db_name]
