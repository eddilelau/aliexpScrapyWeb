from datetime import date
import os
import time
import pymysql
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")   # project_name
django.setup()
from blog.models import *

data=competingProductInfo.objects.filter(productId =32840271725).values_list('tag', flat=True)[0]

print(data == None )