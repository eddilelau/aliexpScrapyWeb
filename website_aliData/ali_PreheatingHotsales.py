import os
import queue
import threading
import asyncio
import aiohttp
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
django.setup()
import requests
import time
import re
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
from scrapy.selector import Selector
from blog.models import *
import random
# import uvloop
import pymysql
import json
from django.db.models import Count

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

def download_image(url,file_path):
    #print('正在下载图片', url)
    headers = {
        'User-Agent': getRandomAgent(),
    }
    try:
        if not os.path.exists(file_path):
            response=requests.get(url, headers=headers)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                    f.close()
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'下载图片{}'.format(url))
    except requests.RequestException:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'请求图片错误', url)

def insertToNewCompetingProductDailySales(productInfo):
    newCompetingProductDailySales.objects.bulk_create(productInfo)
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"写入blog_newCompetingProductDailySales表数据{}".format(len(productInfo)))

def updateToNewCompetingProductDailySalesforFiveDays():
        date=datetime.date.today()
        past1_date=date + datetime.timedelta(days=-1)
        past2_date=date + datetime.timedelta(days=-2)
        past3_date=date + datetime.timedelta(days=-3)
        past4_date=date + datetime.timedelta(days=-4)
        past1_data={productInfo['productId']: productInfo['totalSales'] for productInfo in newCompetingProductDailySales.objects.filter(date=past1_date).values('productId', 'totalSales')}
        past2_data={productInfo['productId']: productInfo['totalSales'] for productInfo in newCompetingProductDailySales.objects.filter(date=past2_date).values('productId', 'totalSales')}
        past3_data={productInfo['productId']: productInfo['totalSales'] for productInfo in newCompetingProductDailySales.objects.filter(date=past3_date).values('productId', 'totalSales')}
        past4_data={productInfo['productId']: productInfo['totalSales'] for productInfo in newCompetingProductDailySales.objects.filter(date=past4_date).values('productId', 'totalSales')}
        competingProductId=competingProductInfo.objects.values_list('productId',flat=True)

        competingProductDailySalesforFiveDaysData=[]
        competingProductDailySalesData=[]
        competingProductInfoAdd=set()
        newCompetingProductIdDelete=[]
        for product_summary in newCompetingProductDailySales.objects.filter(date=date):
            if product_summary.productId not in competingProductId and (product_summary.productId in past1_data.keys()) and (product_summary.productId in past2_data.keys()) and (product_summary.productId in past3_data.keys()) and (product_summary.productId in past4_data.keys()):
                # calculate pastX_Sales
                past1_Sales=int(product_summary.totalSales) - past1_data[product_summary.productId]
                past2_Sales=int(product_summary.totalSales) - past2_data[product_summary.productId]
                past3_Sales=int(product_summary.totalSales) - past3_data[product_summary.productId]
                past4_Sales=int(product_summary.totalSales) - past4_data[product_summary.productId]
                # Eliminate competing product
                if past4_Sales < 5:
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"{}飙升新品近5日销量少于5,从列表中剔除".format(product_summary.productId))
                    newCompetingProductIdDelete.append(product_summary.productId)
                # add hot competing product
                elif past1_Sales>=5 and past2_Sales>=10:
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"{}飙升新品被添加到热卖产品,并从飙升新品列表中删除".format(product_summary.productId))
                    competingProductInfoAdd.add(competingProductInfo(productId=product_summary.productId))
                    newProductIdFiveDayData=newCompetingProductDailySales.objects.filter(date__range=(past4_date, date),productId=product_summary.productId).order_by('-date')
                    for productData in newProductIdFiveDayData:
                        competingProductDailySalesData.append(competingProductDailySales(
                            productId=productData.productId,
                            title=productData.title,
                            totalSales=productData.totalSales,
                            totalEvaluation=productData.totalEvaluation,
                            productScore=productData.productScore,
                            price=productData.price,
                            picUrl=productData.picUrl,
                            date=productData.date,
                            home=productData.home,
                            IF_New_User_BONUS=productData.IF_New_User_BONUS,
                            allCategories=productData.allCategories,
                            firstCategory=productData.firstCategory,
                            secondCategory=productData.secondCategory,
                            thirdCategory=productData.thirdCategory,
                            fourthCategory=productData.fourthCategory,
                            fifthCategory=productData.fifthCategory,
                            sixthCategory=productData.sixthCategory,
                            seventhCategory=productData.seventhCategory,
                            eigthCategory=productData.eigthCategory,
                        ))
                    competingProductDailySalesforFiveDaysData.append(
                        competingProductDailySalesforFiveDays(
                        productId=product_summary.productId,
                        title=product_summary.title,
                        totalSales=product_summary.totalSales,
                        totalEvaluation=product_summary.totalEvaluation,
                        productScore=product_summary.productScore,
                        price=product_summary.price,
                        picUrl=product_summary.picUrl,
                        date=product_summary.date,
                        past1_Sales=past1_Sales,
                        past2_Sales=past2_Sales,
                        past3_Sales=past3_Sales,
                        past4_Sales=past4_Sales,
                        home=product_summary.home,
                        IF_New_User_BONUS=product_summary.IF_New_User_BONUS,
                        allCategories=product_summary.allCategories,
                        firstCategory=product_summary.firstCategory,
                        secondCategory=product_summary.secondCategory,
                        thirdCategory=product_summary.thirdCategory,
                        fourthCategory=product_summary.fourthCategory,
                        fifthCategory=product_summary.fifthCategory,
                        sixthCategory=product_summary.sixthCategory,
                        seventhCategory=product_summary.seventhCategory,
                        eigthCategory=product_summary.eigthCategory,
                    ))
                    newCompetingProductIdDelete.append(product_summary.productId)
            if len(newCompetingProductIdDelete) % 200 == 0 and len(newCompetingProductIdDelete) != 0:
                newCompetingProductInfo.objects.filter(productId__in=newCompetingProductIdDelete).delete()
                competingProductInfo.objects.bulk_create(competingProductInfoAdd)
                competingProductDailySales.objects.bulk_create(competingProductDailySalesData)
                competingProductDailySalesforFiveDays.objects.bulk_create(competingProductDailySalesforFiveDaysData)
                print(
                    time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                    "{}个飙升新品被删除".format(len(newCompetingProductIdDelete)),
                    "{}个飙升产品被添加到热卖竞品".format(len(competingProductInfoAdd)),
                    "{}条飙升产品销售数据被添加到热卖竞品".format(len(competingProductDailySalesData)),
                    "{}条飙升产品销售宽表数据被添加热卖竞品".format(len(competingProductDailySalesforFiveDaysData)),
                )
                competingProductDailySalesforFiveDaysData=[]
                competingProductDailySalesData=[]
                competingProductInfoAdd=set()
                newCompetingProductIdDelete=[]
        newCompetingProductInfo.objects.filter(productId__in=newCompetingProductIdDelete).delete()
        competingProductInfo.objects.bulk_create(competingProductInfoAdd)
        competingProductDailySales.objects.bulk_create(competingProductDailySalesData)
        competingProductDailySalesforFiveDays.objects.bulk_create(competingProductDailySalesforFiveDaysData)
        print(
            time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
            "{}个飙升新品被删除".format(len(newCompetingProductIdDelete)),
            "{}个飙升产品被添加到热卖竞品".format(len(competingProductInfoAdd)),
            "{}条飙升产品销售数据被添加到热卖竞品".format(len(competingProductDailySalesData)),
            "{}条飙升产品销售宽表数据被添加热卖竞品".format(len(competingProductDailySalesforFiveDaysData)),
        )

def addToinfringeProductinfo(product_id):
    # variable
    infringeProductNum=infringeProductinfo.objects.filter(productId=product_id).exists()
    productInfoNum=newCompetingProductDailySales.objects.filter(productId=product_id).exists()
    # logic
    if productInfoNum:
        productData=newCompetingProductDailySales.objects.filter(productId=product_id).order_by('-date')[0]
        if infringeProductNum:
            infringeProductData=infringeProductinfo.objects.filter(productId=product_id)[0]
            if infringeProductData.updateDate == datetime.date.today() - datetime.timedelta(days=1):
                if infringeProductData.confirm_times>=2:
                    infringeProductinfo.objects.filter(productId = product_id).update(
                        totalSales=productData.totalSales,
                        totalEvaluation=productData.totalEvaluation,
                        productScore=productData.productScore,
                        price=productData.price,
                        been_deleted=1,
                        confirm_times=3,
                        updateDate=datetime.date.today())
                    newCompetingProductInfo.objects.filter(productId = product_id).delete()
                else:
                    infringeProductinfo.objects.filter(productId=product_id).update(
                        totalSales=productData.totalSales,
                        totalEvaluation=productData.totalEvaluation,
                        productScore=productData.productScore,
                        price=productData.price,
                        been_deleted=0,
                        confirm_times=2,
                        updateDate=datetime.date.today())
            else:
                infringeProductinfo.objects.filter(productId=product_id).update(
                    totalSales=productData.totalSales,
                    totalEvaluation=productData.totalEvaluation,
                    productScore=productData.productScore,
                    price=productData.price,
                    been_deleted=0,
                    confirm_times=1,
                    updateDate=datetime.date.today())
        else:
            infringeProductinfo.objects.update_or_create(
                productId=product_id,
                totalSales=productData.totalSales,
                totalEvaluation=productData.totalEvaluation,
                productScore=productData.productScore,
                price=productData.price,
                been_deleted=0,
                confirm_times=1,
                updateDate=datetime.date.today())
    else:
        newCompetingProductInfo.objects.filter(productId=product_id).delete()

def fetch_content(product_id,retry_num,session):   #异步函数
    try:
        _url = 'https://www.aliexpress.com/item/Tendway-Magnetic-Bluetooth-Earphones-Sport-Running-Wireless-Stereo-Earbuds-with-Micro-Microphone-for-Climbing-Running-auriculare/{}.html'.format(
            product_id)
        response=session.get(_url)
        content=response.text  # 等待直到获取成功
        status=response.status_code
        if status == 200:
            content_gbk=content.encode('utf-8').decode('gbk', 'ignore')
            if re.findall('window.runParams = \{\s*data:(.*?),\s*csrfToken', content_gbk, re.S):
                return parseContent(product_id, content=content)
            else:
                # print(content_gbk)
                print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"{}产品没返回正确数据:暂停30s".format(product_id))
                return product_id
        elif status == 404:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"产品ID:{},服务器找不到产品详情,重试{}".format(product_id, retry_num))
            retry_num+=1
            if retry_num <= 4:
                fetch_content(product_id, retry_num, session)
            else:
                addToinfringeProductinfo(product_id)
                return None
    except (requests.exceptions.ConnectionError,requests.exceptions.SSLError,KeyError) as EX:
        retry_num += 1
        if retry_num <=4:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),EX)
            fetch_content(product_id,retry_num,session)
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),str(product_id) + '服务器没有响应' + '\n')
            # time.sleep(60*10)
            return product_id

def parseContent(product_id,content):
    content_gbk=content.encode('utf-8').decode('gbk', 'ignore')
    data_string=re.findall('window.runParams = \{\s*data:(.*?),\s*csrfToken', content_gbk, re.S)[0]
    try:
        data_json=json.loads(data_string.replace("&",""))
    except:
        return "json_decode_error"
    if "formatedActivityPrice" in data_json["priceModule"].keys():
        product_price=data_json["priceModule"]["formatedActivityPrice"]
    else:
        product_price=data_json["priceModule"]["formatedPrice"]
    if "activityMessage" in data_json["priceModule"].keys():
        IF_New_User_BONUS=1 if data_json["priceModule"]["activityMessage"] == 'New User BONUS' else 0
    else:
        IF_New_User_BONUS=0
    product_Score=data_json["titleModule"]["feedbackRating"]["averageStar"]
    productReviews=data_json["titleModule"]["feedbackRating"]["totalValidNum"]
    product_order=data_json["titleModule"]["tradeCount"]
    product_tittle=data_json["titleModule"]["subject"]
    product_img=data_json["imageModule"]["imagePathList"][0]

    sel=Selector(text=content_gbk, type="html")
    Home=sel.xpath('//div[@class="breadcrumb"]/span[1]/a/text()').extract()
    allCategories=sel.xpath('//div[@class="breadcrumb"]/span[2]/a/text()').extract()
    product_catalog=sel.xpath('//div[@class="breadcrumb"]/a/text()').extract()

    product_summary={
        'productId': product_id,
        'totalSales': product_order,
        'totalEvaluation': productReviews,
        'date': datetime.date.today(),
        'title': product_tittle,
        'productScore': product_Score.strip(),
        'price': product_price,
        'picUrl': product_img,
        'catalog': product_catalog[0] if len(product_catalog) >= 1 else "",
        'home': Home[0] if len(Home) >= 1 else "",
        'IF_New_User_BONUS': IF_New_User_BONUS,
        'allCategories': allCategories[0] if len(allCategories) >= 1 else "",
        'firstCategory': product_catalog[0] if len(product_catalog) >= 1 else "",
        'secondCategory': product_catalog[1] if len(product_catalog) >= 2 else "",
        'thirdCategory': product_catalog[2] if len(product_catalog) >= 3 else "",
        'fourthCategory': product_catalog[3] if len(product_catalog) >= 4 else "",
        'fifthCategory': product_catalog[4] if len(product_catalog) >= 5 else "",
        'sixthCategory': product_catalog[5] if len(product_catalog) >= 6 else "",
        'seventhCategory': product_catalog[6] if len(product_catalog) >= 7 else "",
        'eigthCategory': product_catalog[7] if len(product_catalog) >= 8 else "",
    }

    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'完成' + str(product_id) + "销售数据爬取!")
    return product_summary

def send_mail(Spend_Time):
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        message = MIMEMultipart()
        message['From'] = Header("Python_ali_备选热销_每日销量", 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject ='Python_ali_备选热销_每日销量'+'_'+str(datetime.date.today())
        message['Subject'] = Header(subject, 'utf-8')
        message.attach( MIMEText('备选热销_每日销量'+'_'+str(datetime.date.today())+'\n Spend Total Time:'+ Spend_Time +'mins', 'plain', 'utf-8'))
        # msg = MIMEText('热销竞品的销售数据', 'plain', 'utf-8')
        # msg['From'] = formataddr(["FromRunoob", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        # msg['To'] = formataddr(["FK", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        # msg['Subject'] = file_name  # 邮件的主题，也可以说是标题

        # 构造附件1，传送当前目录下的 test.txt 文件
        # att1 = MIMEText(open('./ali_PreheatingHotsales_Data/'+ file_name, 'rb').read(), 'base64', 'utf-8')
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

def main(productIdlist):
    sessionNum=0
    session = getSession()
    productInfo=[]
    while productIdlist:
        productId=productIdlist.pop(0)  #FIFO
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"开始爬虫{}".format(productId),"等待爬虫产品数据为{}".format(len(productIdlist)))
        result=fetch_content(productId, retry_num=1,session=session)
        if type(result) is int:
            productIdlist.append(productId)
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"产品{}爬虫失败,返回消息列表".format(productId), "等待爬虫产品数据为{}".format(len(productIdlist)))
            time.sleep(10*random.randint(1,6))
        elif type(result) is dict:
            if result['firstCategory'] not in ( "Consumer Electronics", "Cellphones & Telecommunications", "Computer & Office", "Security & Protection",""):
                newCompetingProductInfo.objects.filter(productId=result['productId']).delete()
            else:
                productInfo.append(
                    newCompetingProductDailySales(
                        productId=result['productId'],
                        title=result['title'],
                        totalSales=result['totalSales'],
                        totalEvaluation=result['totalEvaluation'],
                        productScore=result['productScore'],
                        price=result['price'],
                        picUrl=result['picUrl'],
                        date=result['date'],
                        home=result['home'],
                        IF_New_User_BONUS=result['IF_New_User_BONUS'],
                        allCategories=result['allCategories'],
                        firstCategory=result['firstCategory'],
                        secondCategory=result['secondCategory'],
                        thirdCategory=result['thirdCategory'],
                        fourthCategory=result['fourthCategory'],
                        fifthCategory=result['fifthCategory'],
                        sixthCategory=result['sixthCategory'],
                        seventhCategory=result['seventhCategory'],
                        eigthCategory=result['eigthCategory'],
                    )
                )
                download_image(result['picUrl'], './static/' + str(result['productId']) + '.jpg')
        elif result == "json_decode_error":
            newCompetingProductInfo.objects.filter(productId=productId).delete()
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"产品{}json数据出错,直接从newCompetingProductInfo表删除".format(productId))

        if len(productInfo) % 200 == 0 and len(productInfo) != 0:
            insertToNewCompetingProductDailySales(productInfo)
            productInfo=[]
        sessionNum+=1
        if sessionNum % 4 ==0 and len(productInfo) != 0:
            session=getSession()
    insertToNewCompetingProductDailySales(productInfo)
    updateToNewCompetingProductDailySalesforFiveDays()


if __name__ == '__main__':
    date=datetime.date.today()
    while 1:
        if os.path.exists('./ali_hotsales_log/finish/Ali_hotsales_finish_{}.txt'.format(date)):
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"ali_hotsales.py is finished,the script is going on")
            break
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),"process ali_hotsales.py is not finish,the script will hang up 5 mins")
        time.sleep(60*5)
    Start_Time = time.time()
    productIdlist = list(newCompetingProductInfo.objects.values_list('productId', flat=True))   # 数据库读取产品ID
    main(productIdlist)
    End_Time = time.time()
    Spend_Time = str(round((End_Time - Start_Time) / 60, 2))
    send_mail(Spend_Time)

