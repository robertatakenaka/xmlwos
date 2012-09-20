import sys
from pymongo import Connection

conn = Connection('127.0.0.1', 27017)
db = conn['scielo']
article = db['article']
title = db['title']

print sys.argv[1]
