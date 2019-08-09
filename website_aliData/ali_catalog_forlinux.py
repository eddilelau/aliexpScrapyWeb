import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
# print(django.VERSION)
django.setup()
from blog.models import *
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import pymongo
from pymongo import UpdateOne
from config import *
from requests import *
import requests.exceptions
import json
import json.decoder
import random

# 配置mongodb数据库
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_catalog]

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

def getSession():
    session=requests.Session()  # 创建session对象s
    session.get('https://www.aliexpress.com/')  # 获取cookies，并存储于s对象中
    headers={
        'User-Agent': getRandomAgent(),
    }
    session.headers.update(headers)
    return session

def fetch_content(key_word,page,retry_num,session):   #异步函数
    try:
        _url ='https://www.aliexpress.com/glosearch/api/product'
        data={
            'ltype':'premium',
            'd':'y',
            'CatId':0,
            'SearchText':key_word,
            'trafficChannel':'ppc',
            'SortType':'default',
            'g':'n',
            'page':page
        }
        response=session.get(_url,params=data)
        content =response.text.replace("&quot;","\"")    #等待直到获取成功
        status  = response.status_code
        data_json=json.loads(content)
        if status == 200 and 'items' in data_json:
            productList=[]
            for i in range(len(data_json['items'])):
                if 'tradeDesc' in data_json['items'][i]:
                    productId=data_json['items'][i]['productId']
                    tradeDesc=data_json['items'][i]['tradeDesc'].replace(' Sold','')
                    productList.append({'productId':productId,'tradeDesc':int(tradeDesc)})
            return productList
        elif status ==404:
            print("服务器没有返回{}搜索结果,重试第{}次".format(key_word,retry_num))
            time.sleep(10*random.randint(1,6))
            retry_num+=1
            if retry_num <= 4:
                fetch_content(key_word,page, retry_num,session)
            else:
                return None

    except (requests.exceptions.ConnectionError,requests.exceptions.SSLError,KeyError) as EX:
        retry_num += 1
        if retry_num <=4:
            print(EX)
            fetch_content(key_word,page,retry_num,session)
        else:
            time.sleep(60*10)
            print(str(key_word) + '服务器没有响应' + '\n')
            return None

def saveToSQLite(sqlDB,NCPI_set):
        sqlDB.objects.bulk_create(NCPI_set)

def send_mail(catelog, Total_time):
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        message = MIMEMultipart()
        message['From'] = Header("Python_关键词销售数据", 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject = '类目关键词销售数据' + '_' + str(catelog)
        message['Subject'] = Header(subject, 'utf-8')
        message.attach(
            MIMEText('类目关键词销售数据' + '_' + str(catelog) + '\n Spend Total Time:' + Total_time, 'plain', 'utf-8'))

        # 构造附件1，传送当前目录下的 test.txt 文件
        # att1 = MIMEText(open('./ali_catalog_forlinux_keyword_data/' + file_name, 'rb').read(), 'base64', 'utf-8')
        # att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att1["Content-Disposition"] = 'attachment; filename=' + file_name
        # message.attach(att1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print('邮件发送成功')
    except Exception as ex:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(ex)
        return False

def main():
    catalog_list=[filename[2] for filename in os.walk('./ali_catalog_forlinux_keyword', topdown=False)]
    for catalog in catalog_list[0]:
        Start_Time = time.time()
        for key_word in open('./ali_catalog_forlinux_keyword/' + catalog).readlines():
            if key_word.strip() not in ['Emergency Button']:
                competingProductLists=competingProductInfo.objects.all().values_list("productId", flat=True)
                newCompetingProductInfoLists=newCompetingProductInfo.objects.all().values_list("productId", flat=True)
                mongodProductInfoList = list(db[catalog].find({},{'productID': 1,'ProductOrder':1}))
                mongodProductInfoDict = {mongodProductInfoList[i]['productID']:int(mongodProductInfoList[i]['ProductOrder']) for i in range(len(mongodProductInfoList))}
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Catalog :{}--Keyword:{}--Start Spider!!!! '.format(catalog, key_word.replace('\n', '')))
                session=getSession()
                total=30
                NCPI_set=set()
                bulkUpdate=[]
                for page in range(1, total + 1):
                    productList=fetch_content(key_word, page=page,retry_num=1, session=session)
                    if productList:
                        for product in productList:
                                if product['productId'] in mongodProductInfoDict.keys() and product['tradeDesc'] - mongodProductInfoDict[product['productId']] >= 5:
                                    if product['productId'] not in competingProductLists and product['productId'] not in newCompetingProductInfoLists:
                                        NCPI_set.add(product['productId'])
                                bulkUpdate.append(UpdateOne({'productID': product['productId']},{'$set': {'ProductOrder': product['tradeDesc']}}, True))
                        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                                  'Catalog :{}--Keyword:{}--PageNum:{}--Spider Finished'.format(catalog, key_word.replace('\n', ''),page))
                db[catalog].bulk_write(bulkUpdate)
                NCPI_list=[]
                for productId in NCPI_set:
                    NCPI_item = newCompetingProductInfo(productId=productId)
                    NCPI_list.append(NCPI_item)
                saveToSQLite(newCompetingProductInfo,NCPI_list)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'Catalog :{}--Keyword:{}--success insert {} productIds in blog_newCompetingProductInfo ,update {} productInfos in Mongodb'.format(catalog, key_word.replace('\n', ''),len(NCPI_set),len(bulkUpdate)))

        End_Time = time.time()
        Total_time = str(round((End_Time - Start_Time) / 60, 2))
        send_mail(catalog, Total_time)


if __name__ == '__main__':
    main()
