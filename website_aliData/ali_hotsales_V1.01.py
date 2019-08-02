import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
# print(django.VERSION)
django.setup()
import asyncio
import aiohttp
import requests
# from bs4 import BeautifulSoup
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
from  requests import *
import random
import uvloop
import pymysql


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

async def download_image(url,file_path):
    headers = {
        'User-Agent': getRandomAgent(),
    }
    try:
        if not os.path.exists(file_path):
            async with aiohttp.ClientSession() as session:  # 创建异步请求对象
                async with session.get(url, headers=headers) as response:  # 创建异步获取响应对象
                    content = await response.read()  # 等待直到获取成功
                    status = response.status
            if status == 200:
                with open(file_path, 'wb') as f:
                    f.write(content)
                    f.close()
                    print('下载图片{}'.format(url))

    except RequestException:
        print('请求图片错误', url)
        pass

async def fetch_content(product_id,retry_num):   #异步函数
    try:
        headers = {
            'User-Agent': getRandomAgent(),
        }
        _url ='https://www.aliexpress.com/item/Tendway-Magnetic-Bluetooth-Earphones-Sport-Running-Wireless-Stereo-Earbuds-with-Micro-Microphone-for-Climbing-Running-auriculare/{}.html'.format(product_id)
        async with aiohttp.ClientSession() as session:   #创建异步请求对象
            async with session.get(_url,headers =headers) as response:     #创建异步获取响应对象
                content = await response.text()    #等待直到获取成功
                status  = response.status
                if status ==200:
                    product_summary=await parseContent(product_id,response=content)
                    if product_summary != None:
                        await saveTomysql(product_summary)
                        await download_image(product_summary['picUrl'], './static/' + str(product_id) + '.jpg')
                else:
                    sel=Selector(text=content, type="html")
                    tittel=sel.xpath('//div[@class="item-not-found-title"]/span/text()').extract()[0]
                    if tittel == "Sorry, this page is unavailable, but check out our other pages that are just as great. ":
                        print("产品ID:{},服务器找不到产品详情".format(product_id), tittel)
                        await addToinfringeProductinfo(product_id)
                    return None
    except (requests.exceptions.ConnectionError,requests.exceptions.SSLError) as EX:
        retry_num += 1
        if retry_num <=4:
            print(EX)
            await fetch_content(product_id,retry_num)
        else:
            time.sleep(60*10)
            print(str(product_id) + '服务器没有响应' + '\n')
            return await None

async def saveTomysql(product_summary):
    competingProductDailySales.objects.update_or_create(
        productId=product_summary['productId'],
        title=product_summary['title'],
        totalSales=product_summary['totalSales'],
        totalEvaluation=product_summary['totalEvaluation'],
        productScore=product_summary['productScore'],
        price=product_summary['price'],
        picUrl=product_summary['picUrl'],
        date=product_summary['date'],
        home=product_summary['home'],
        allCategories=product_summary['allCategories'],
        firstCategory=product_summary['firstCategory'],
        secondCategory=product_summary['secondCategory'],
        thirdCategory=product_summary['thirdCategory'],
        fourthCategory=product_summary['fourthCategory'],
        fifthCategory=product_summary['fifthCategory'],
        sixthCategory=product_summary['sixthCategory'],
        seventhCategory=product_summary['seventhCategory'],
        eigthCategory=product_summary['eigthCategory'],
    )

    date=(product_summary['date'])
    past1_date=date + datetime.timedelta(days=-1)
    past2_date=date + datetime.timedelta(days=-2)
    past3_date=date + datetime.timedelta(days=-3)
    past4_date=date + datetime.timedelta(days=-4)
    past1_date_data_exist=competingProductDailySales.objects.filter(date=past1_date,productId=product_summary['productId']).count()
    past2_date_data_exist=competingProductDailySales.objects.filter(date=past2_date,productId=product_summary['productId']).count()
    past3_date_data_exist=competingProductDailySales.objects.filter(date=past3_date,productId=product_summary['productId']).count()
    past4_date_data_exist=competingProductDailySales.objects.filter(date=past4_date,productId=product_summary['productId']).count()
    if past1_date_data_exist and past4_date_data_exist and past2_date_data_exist and past3_date_data_exist:
        # calculate pastX_Sales
        past1_date_totalsales=competingProductDailySales.objects.filter(date=past1_date, productId=product_summary[ 'productId']).values_list('totalSales', flat=True)
        past2_date_totalsales=competingProductDailySales.objects.filter(date=past2_date, productId=product_summary[ 'productId']).values_list('totalSales', flat=True)
        past3_date_totalsales=competingProductDailySales.objects.filter(date=past3_date, productId=product_summary[ 'productId']).values_list('totalSales', flat=True)
        past4_date_totalsales=competingProductDailySales.objects.filter(date=past4_date, productId=product_summary['productId']).values_list('totalSales', flat=True)
        past1_Sales=int(product_summary['totalSales']) - past1_date_totalsales[0]
        past2_Sales=int(product_summary['totalSales']) - past2_date_totalsales[0]
        past3_Sales=int(product_summary['totalSales']) - past3_date_totalsales[0]
        past4_Sales=int(product_summary['totalSales']) - past4_date_totalsales[0]

        competingProductDailySalesforFiveDays.objects.update_or_create(
            productId=product_summary['productId'],
            title=product_summary['title'],
            totalSales=product_summary['totalSales'],
            totalEvaluation=product_summary['totalEvaluation'],
            productScore=product_summary['productScore'],
            price=product_summary['price'],
            picUrl=product_summary['picUrl'],
            date=product_summary['date'],
            past1_Sales=past1_Sales,
            past2_Sales=past2_Sales,
            past3_Sales=past3_Sales,
            past4_Sales=past4_Sales,
            home=product_summary['home'],
            allCategories=product_summary['allCategories'],
            firstCategory=product_summary['firstCategory'],
            secondCategory=product_summary['secondCategory'],
            thirdCategory=product_summary['thirdCategory'],
            fourthCategory=product_summary['fourthCategory'],
            fifthCategory=product_summary['fifthCategory'],
            sixthCategory=product_summary['sixthCategory'],
            seventhCategory=product_summary['seventhCategory'],
            eigthCategory=product_summary['eigthCategory']
        )

        if past4_Sales<5 and competingProductInfo.objects.filter(productId =product_summary['productId']).values_list('tag', flat=True)[0] ==None:
            competingProductInfo.objects.filter(productId =product_summary['productId']).delete()

async def addToinfringeProductinfo(product_id):
    # variable
    infringeProductNum=infringeProductinfo.objects.filter(productId=product_id).exists()
    productInfoNum=competingProductDailySales.objects.filter(productId=product_id).exists()

    # logic
    if productInfoNum:
        productData=competingProductDailySales.objects.filter(productId=product_id).order_by('-date')[0]
        if infringeProductNum:
            infringeProductData=infringeProductinfo.objects.filter(productId=product_id)[0]
            if infringeProductData.date == datetime.date.today().replace(day=datetime.date.today().day - 1):
                if infringeProductData.confirm_times >= 2:
                    infringeProductinfo.objects.filter(productId=product_id).update(
                        totalSales=productData.totalSales,
                        totalEvaluation=productData.totalEvaluation,
                        productScore=productData.productScore,
                        price=productData.price,
                        been_deleted=1,
                        confirm_times=3,
                        updateDate=datetime.date.today())
                    competingProductDailySales.objects.filter(productId=product_id).delete()
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
        competingProductDailySales.objects.filter(productId=product_id).delete()

async def parseContent(product_id,response):
    try:
        pattern_tittle = re.compile( '<div class="detail-wrap".*?itemprop="name">(.*?)</h1>', re.S)
        pattern_Score = re.compile( '</h1>.*?class="percent-num">(.*?)</span>', re.S)
        pattern_Reviews = re.compile('<span class="rantings-num">(.*?)</span>', re.S)
        pattern_order = re.compile('id="j-order-num">(.*?)</span>', re.S)
        pattern_price = re.compile( 'class="p-price" itemprop="price">(.*?)</span>|class="p-price".*?"lowPrice">(.*?)</span>(.*?)<span itemprop="highPrice">(.*?)</span>',re.S)
        pattern_img = re.compile('<a class="ui-image-viewer-thumb-frame".*?src="(.*?)data-role="thumb"', re.S)

        sel=Selector(text=response, type="html")
        if re.findall(pattern_tittle, response) == []:
            print(str(product_id) + '响应数据有误')
            return None
        else:
            # print(re.findall(pattern_tittle, response.text))
            product_tittle=re.findall(pattern_tittle, response)[0]

        if re.findall(pattern_Score, response) == []:
            product_Score=str(5.0)
        else:
            product_Score=re.findall(pattern_Score, response)[0]
        if re.findall(pattern_order, response) == []:
            product_order=str(0)
        else:
            product_order=re.findall(pattern_order, response)[0].replace('orders', '').replace('order', '')
        if re.findall(pattern_Reviews, response) == []:
            productReviews=str(0)
        else:
            productReviews=re.findall(pattern_Reviews, response)[0].replace('votes', '').replace('vote', '').replace(
                '(', '').replace(')', '')
        product_price_list=re.findall(pattern_price, response)
        product_price=(''.join(product_price_list[0]).replace(" ", "")).strip()
        product_img=re.findall(pattern_img, response)[0]
        product_catalog=[]
        product_catalog1=sel.xpath('//div[@class="ui-breadcrumb"]/div[1]/a/text()').extract()
        product_catalog2=sel.xpath('//div[@class="ui-breadcrumb"]/div[1]/h2/a[1]/text()').extract()
        product_catalog.extend(product_catalog1)
        product_catalog.extend(product_catalog2)

        product_summary={
            'productId': product_id,
            'totalSales': product_order,
            'totalEvaluation': productReviews,
            'date': datetime.date.today(),
            'title': product_tittle,
            'productScore': product_Score.strip(),
            'price': product_price,
            'picUrl': product_img,
            'catalog': product_catalog[0],
            'home': product_catalog[0] if len(product_catalog) >= 1 else "",
            'allCategories': product_catalog[1] if len(product_catalog) >= 2 else "",
            'firstCategory': product_catalog[2] if len(product_catalog) >= 3 else "",
            'secondCategory': product_catalog[3] if len(product_catalog) >= 4 else "",
            'thirdCategory': product_catalog[4] if len(product_catalog) >= 5 else "",
            'fourthCategory': product_catalog[5] if len(product_catalog) >= 6 else "",
            'fifthCategory': product_catalog[6] if len(product_catalog) >= 7 else "",
            'sixthCategory': product_catalog[7] if len(product_catalog) >= 8 else "",
            'seventhCategory': product_catalog[8] if len(product_catalog) >= 9 else "",
            'eigthCategory': product_catalog[9] if len(product_catalog) >= 10 else "",
        }

        print('完成' + str(product_id) + "销售数据爬取!")
        return product_summary

    except (requests.exceptions.ConnectionError,requests.exceptions.SSLError) as EX:
        retry_num += 1
        if retry_num <=10:
            print(EX)
            await parseContent(product_id,retry_num)
        else:
            time.sleep(60*10)
            print(str(product_id) + '服务器没有响应'  + '\n')
            return None

def send_mail(Spend_Time):
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        message = MIMEMultipart()
        message['From'] = Header("Python_ali_竞品日销", 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject = '竞品销售数据'+'_'+str(datetime.date.today())
        message['Subject'] = Header(subject, 'utf-8')
        message.attach( MIMEText('竞品销售数据'+'_'+str(datetime.date.today())+'\n Spend Total Time:'+ Spend_Time +'mins', 'plain', 'utf-8'))
        # msg = MIMEText('热销竞品的销售数据', 'plain', 'utf-8')
        # msg['From'] = formataddr(["FromRunoob", my_sender])  # 括号里的对应发件人邮箱昵称、发件人邮箱账号
        # msg['To'] = formataddr(["FK", my_user])  # 括号里的对应收件人邮箱昵称、收件人邮箱账号
        # msg['Subject'] = file_name  # 邮件的主题，也可以说是标题

        # 构造附件1，传送当前目录下的 test.txt 文件
        # att1 = MIMEText(open('./ali_hotsales_history_Data/'+ file_name, 'rb').read(), 'base64', 'utf-8')
        # att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        # att1["Content-Disposition"] = 'attachment; filename='+file_name
        # message.attach(att1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print('邮件发送成功')
    except Exception as ex:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(ex)
        ret = False
    return ret

def main(productIdlist):
    # loop = asyncio.get_event_loop()  # 实例循环
    loop = uvloop.new_event_loop()      #can not use in windows
    asyncio.set_event_loop(loop)        #asyncio异步请求
    tasks = [asyncio.ensure_future(fetch_content(product.productId, retry_num=1)) for product in productIdlist]  #多任务tasks
    loop.run_until_complete(asyncio.wait(tasks))  #事务循环

if __name__ == '__main__':
    Start_Time = time.time()
    productIdlist = competingProductInfo.objects.all()   # 数据库读取产品ID
    groupNum = 50  #分组数
    m = int(len(productIdlist)/groupNum) #求分组数
    n = len(productIdlist)%groupNum      #求余
    if n>0:
        m +=1
    for number in range(m):
        main(productIdlist[number*groupNum:(number+1) * groupNum])
    End_Time = time.time()
    Spend_Time = str(round((End_Time - Start_Time) / 60, 2))
    print('结束')
    send_mail(Spend_Time)