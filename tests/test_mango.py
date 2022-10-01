import os
import pymongo
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dotenv

dotenv.load_dotenv('keys/keys.env')
print(os.environ['host'])
client = pymongo.MongoClient(host=os.environ['host'],
                             port=27018,
                             replicaSet='rs01',
                             username=os.environ['username'],
                             password=os.environ['password'],
                             authSource=os.environ['database'],
                             tls=True,
                             tlsCAFile='keys/cert.pem')
db = client[os.environ['database']]
print('kuku')
print(db.list_collection_names())