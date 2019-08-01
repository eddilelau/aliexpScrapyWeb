import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")   # project_name
django.setup()
from blog.models import *
import datetime

today =datetime.date.today()
tagsName=competingProductInfo.objects.all().values_list('tag', flat=True).distinct()

for tagName in tagsName:
    tag.objects.update_or_create(tag=tagName)


catalogsName=competingProductDailySales.objects.filter(date = today).values_list(
    'home','allCategories','firstCategory','secondCategory','thirdCategory',
    'fourthCategory','fifthCategory','sixthCategory','seventhCategory','eigthCategory'
).distinct()

for catalogName in catalogsName:
    catalog.objects.update_or_create(
        home=catalogName[0],
        allCategories=catalogName[1],
        firstCategory=catalogName[2],
        secondCategory=catalogName[3],
        thirdCategory=catalogName[4],
        fourthCategory=catalogName[5],
        fifthCategory=catalogName[6],
        sixthCategory=catalogName[7],
        seventhCategory=catalogName[8],
        eigthCategory=catalogName[9]
    )
