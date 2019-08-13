import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
# print(django.VERSION)
django.setup()
from blog.models import *
import time
import re
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
import sys
import requests
import json
import pymongo
from config import *
import random
import uvloop
import asyncio,aiohttp
from pymongo import UpdateOne

client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_otherSale]
global productIdlist


def getRandomAgent():
    USER_AGENTS = [
     "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
     "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
     "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
     "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
     "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
     "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
     "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
     "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
     "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
     "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
     "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
     "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
     "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
     "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
     "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
     "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
    ]
    return USER_AGENTS[random.randint(0,9)]

def saveToSQLite(sqlDB,NCPI_set):
    sqlDB.objects.bulk_create(NCPI_set)
    # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'insert {} products into {}'.format(len(NCPI_set),sqlDB))

async def getData(productId,try_num):
    try:
        header = {
            'User-Agent': getRandomAgent(),
        }
        url = "https://gpsfront.aliexpress.com/getI2iRecommendingResults.do?currentItemList={}&shopId=1718464&companyId=233056744&recommendType=toOtherSeller&scenario=pcDetailBottomMoreOtherSeller&limit=30&offset=0&callback=__jp7".format(productId)
        async with aiohttp.ClientSession() as session:
            async with session.get(url,headers =header) as response:
                response,status = await response.text(),response.status
                # print(response,status)
                response_json=json.loads(re.findall(r'__jp7\((.*)\)', response)[0])
        if status == 200 and ('results' in response_json.keys()):
            otherSalesList = response_json['results']
            if otherSalesList is not None:
                NCPI_set=set()
                bulkUpdate=[]
                mongodProductInfoList=list(db['otherSales'].find({}, {'productID': 1, 'ProductOrder': 1}))
                mongodProductInfoDict={mongodProductInfoList[i]['productID']: int(mongodProductInfoList[i]['ProductOrder']) for i in range(len(mongodProductInfoList))}
                competingProductLists=competingProductInfo.objects.all().values_list("productId", flat=True)
                for otherSales in otherSalesList:
                    productID=otherSales['productId']  # 已确认空格被清除
                    if productID in mongodProductInfoDict.keys() and (int(otherSales['totalTranpro3']) - int(mongodProductInfoDict[productID])) >= 5:
                        if productID not in competingProductLists:
                            NCPI_set.add(productID)
                    bulkUpdate.append(UpdateOne({'productID': productID}, { '$set': {'ProductOrder': otherSales['totalTranpro3'],'ProductReview': otherSales['itemEvalTotalNum']}}, True))
                db['otherSales'].bulk_write(bulkUpdate)
                # print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'update {} products into {}'.format(len(bulkUpdate), 'mongodb'))
                NCPI_list=[]
                for productId in NCPI_set:
                    NCPI_item=newCompetingProductInfo(productId=productId)
                    NCPI_list.append(NCPI_item)
                saveToSQLite(newCompetingProductInfo, NCPI_list)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"{}的其他相似产品爬取完成！更新mongodb产品数{}个,插入newCompetingProductInfo产品数{}个".format(str(productId),len(bulkUpdate),len(NCPI_list)))
        elif 'blocked' in response_json.keys():
            if response_json['blocked'] == True:
                productIdlist.append(productId)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'{}产品请求失败重新加回消息列表,{}个产品待爬取'.format(productId,len(productIdlist)))
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),str(productId),'无相似产品推荐',status)
    except Exception as EX:
        try_num += 1
        if try_num <= 3:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),EX,"获取{}数据失败,重新尝试{}次".format(productId,try_num))
            # time.sleep(60)
            return getData(productId,try_num)
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),str(productId) + '服务器没有响应'  + '\n')

def sendEmail(Total_time):
    """
    将输出的文档发送到我的邮箱

    """
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        today = datetime.date.today()
        message = MIMEMultipart()
        message['From'] = Header("Python_热销产品的otherSales", 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject = '热销产品的otherSales_{}'.format(today)
        message['Subject'] = Header(subject, 'utf-8')
        message.attach( MIMEText('热销产品的'+'_'+'\n Spend Total Time:'+Total_time, 'plain', 'utf-8'))


        # 构造附件1，传送当前目录下的 test.txt 文件
        # att1 = MIMEText(open('./ali_otherSales/{}'.format(file_name), 'rb').read(), 'base64', 'utf-8')
        # att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att1["Content-Disposition"] = 'attachment; filename='+file_name
        # message.attach(att1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'邮件发送成功')
    except Exception as ex:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),ex)
        ret = False
    return ret

def main(scrapyProduct):
    # loop = asyncio.get_event_loop()
    loop=uvloop.new_event_loop()  # can not use in windows
    asyncio.set_event_loop(loop)
    tasks = [asyncio.ensure_future(getData(product,try_num= 1)) for product in scrapyProduct]
    loop.run_until_complete(asyncio.wait(tasks))


if __name__ == '__main__':
    Start_Time = time.time()
    productIdlist = list(competingProductInfo.objects.all().values_list('productId',flat=True))  # 数据库读取产品ID
    scrapyProduct=[]
    while productIdlist:
        scrapyProduct.append(productIdlist.pop())
        if len(scrapyProduct) >= 30:
            main(scrapyProduct)
            scrapyProduct=[]
    main(scrapyProduct)
    End_Time=time.time()
    Total_time=str(round((End_Time - Start_Time) / 60, 2))
    sendEmail( Total_time)
