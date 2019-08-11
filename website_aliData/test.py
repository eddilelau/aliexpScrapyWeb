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
from pymongo import UpdateOne
from django.db.models import Count


client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_otherSale]

tag='MP1'
tagInformation=list(monitorProductTag.objects.filter(tag=tag).values('tag', 'comment'))[0]

print("tag",tag)