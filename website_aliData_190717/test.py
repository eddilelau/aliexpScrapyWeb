from datetime import date
import os
import time
import pymysql
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")   # project_name
django.setup()
from blog.models import *

data={"key1":"value1","key2":"value2","key3":{"key4":"value4"}}

print("key4" in data["key3"].keys())