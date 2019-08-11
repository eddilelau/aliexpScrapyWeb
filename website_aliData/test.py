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
#tag /comment /competingproductnum/max_productId/past1_sales/past2_sales
date=datetime.date.today().strftime("%m/%d/%Y")
print(date,type(date))
tags = competingProductInfo.objects.values_list('tag',flat=True).distinct()

# tagsInfo={item['tag']:item['comment'] for item in monitorProductTag.objects.values('tag','comment')}
# tagsProducts = {key:competingProductInfo.objects.filter(tag=key).values_list('productId',flat=True) for key,value in tagsInfo.items()}
# tagsBestSales={tag:competingProductDailySalesforFiveDays.objects.filter(productId__in=productIds,date=date).order_by('-past1_Sales')[0] for tag,productIds in tagsProducts.items()}
# tagTables=[]
# for tag in tagsInfo.keys():
#     tagTables.append(
#         {
#             'tag':tag,
#             'comment':tagsInfo[tag],
#             'productIdNum':len(tagsProducts[tag]),
#             'max_productId':tagsBestSales[tag].productId,
#             'max_productId_past1_Sales': tagsBestSales[tag].past1_Sales,
#             'max_productId_past2_Sales': tagsBestSales[tag].past2_Sales,
#             'max_productId_past3_Sales': tagsBestSales[tag].past3_Sales,
#             'max_productId_past4_Sales': tagsBestSales[tag].past4_Sales,
#
#         }
#     )

print(len(tagTables),tagTables)