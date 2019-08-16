from datetime import date
import os
import time
import pymysql
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")   # project_name
django.setup()
from blog.models import *
import pymongo
from config import *
import datetime

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_otherSale]

productIds =[33018221306,33048641947]
pId =[]
for productId in productIds:
    pId.append(competingProductInfo(productId=productId))

newCompetingProductInfo.objects.bulk_create(pId)
print("insert success!")