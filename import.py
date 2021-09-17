#!/usr/bin/env python
import sys
import pandas as pd
import pymongo
import json

mng_client = pymongo.MongoClient('mongodb://52.176.146.117:27017')
mng_db = mng_client['mongodb_name']
collection_name = 'collection_name'
db_cm = mng_db[collection_name]
data = pd.read_csv('test.csv')
data_json = json.loads(data.to_json(orient='records'))
print(str(data_json))
#db_cm.remove()
db_cm.insert_many(data_json)
