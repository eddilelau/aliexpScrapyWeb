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


yesterday=datetime.date.today() - datetime.timedelta(days=1)



print(yesterday)

print(datetime.date.today().replace(day=datetime.date.today().day - 1))