
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
print(django.VERSION)
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
from  requests import *
import random
import pymysql
import json


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
                    print('下载图片{}'.format(url))

    except RequestException:
        print('请求图片错误', url)
        pass

def fetch_content(product_id,retry_num,session):   #异步函数
    try:
        _url ='https://www.aliexpress.com/item/Tendway-Magnetic-Bluetooth-Earphones-Sport-Running-Wireless-Stereo-Earbuds-with-Micro-Microphone-for-Climbing-Running-auriculare/{}.html'.format(product_id)
        response=session.get(_url)
        content =response.text    #等待直到获取成功
        status  = response.status_code
        if status ==200:
            content_gbk=content.encode('utf-8').decode('gbk', 'ignore')
            # print(content_gbk)
            sel=Selector(text=content_gbk, type="html")
            if sel.xpath('//h1[@class="product-name"]/text()').extract() !=[]:
                product_summary=parseContent(product_id,content_gbk=content_gbk)
                if product_summary != None:
                    saveTomysql(product_summary)
                    download_image(product_summary['picUrl'], './static/' + str(product_id) + '.jpg')
            else:
                print("{}产品没返回正确数据:暂停爬虫".format(product_id))
                return product_id

        elif status ==404:
            print("产品ID:{},服务器找不到产品详情,重试{}".format(product_id,retry_num))
            retry_num+=1
            if retry_num <= 4:
                fetch_content(product_id, retry_num,session)
            else:
                addToinfringeProductinfo(product_id)
                return None
    except (requests.exceptions.ConnectionError,requests.exceptions.SSLError,KeyError) as EX:
        retry_num += 1
        if retry_num <=4:
            print(EX)
            fetch_content(product_id,retry_num,session)
        else:
            time.sleep(60*10)
            print(str(product_id) + '服务器没有响应' + '\n')
            return product_id

def saveTomysql(product_summary):
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
    print(past1_date_data_exist and past4_date_data_exist and past2_date_data_exist and past3_date_data_exist)
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

def addToinfringeProductinfo(product_id):
    # variable
    infringeProductNum=infringeProductinfo.objects.filter(productId=product_id).exists()
    productInfoNum=competingProductDailySales.objects.filter(productId=product_id).exists()

    # logic
    if productInfoNum:
        productData=competingProductDailySales.objects.filter(productId=product_id).order_by('-date')[0]
        if infringeProductNum:
            infringeProductData=infringeProductinfo.objects.filter(productId=product_id)[0]
            if infringeProductData.updateDate == datetime.date.today().replace(day=datetime.date.today().day - 1):
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

def parseContent(product_id,content_gbk):
    sel=Selector(text=content_gbk, type="html")
    product_Score=sel.xpath('//span[@class="ui-rating-star"]/span[1]/span[1]/text()').extract()[0] if sel.xpath('//span[@class="ui-rating-star"]/span[1]/span[1]/text()').extract() !=[] else 5
    productReviews=sel.xpath('//span[@class="ui-rating-star"]/span[1]/span[2]/text()').extract()[0] if sel.xpath('//span[@class="ui-rating-star"]/span[1]/span[2]/text()').extract() !=[] else 0
    product_order=sel.xpath('//span[@id="j-order-num"]/text()').extract()[0].replace('orders', '').replace('order', '') if sel.xpath('//span[@id="j-order-num"]/text()').extract() !=[] else 0
    product_tittle=sel.xpath('//h1[@class="product-name"]/text()').extract()[0] if sel.xpath('//h1[@class="product-name"]/text()').extract() !=[] else ""
    product_img=sel.css('meta[property*=image]').xpath('@content').getall()[0] if sel.css('meta[property*=image]').xpath('@content').getall() !=[] else ""
    product_price="".join(sel.xpath('//div[@class="p-current-price"]/div/span//text()').extract()) if sel.xpath('//div[@class="p-current-price"]/div/span//text()').extract() !=[] else ""

    product_catalog=[]
    categories_front=sel.xpath('//div[@class="ui-breadcrumb"]/div/a/text()').extract()
    categories_last=sel.xpath('//div[@class="ui-breadcrumb"]/div/h2/a/text()').extract()
    product_catalog.extend(categories_front)
    product_catalog.extend(categories_last)


    product_summary={
        'productId': product_id,
        'totalSales': product_order,
        'totalEvaluation': productReviews,
        'date': datetime.date.today(),
        'title': product_tittle,
        'productScore': product_Score,
        'price': product_price,
        'picUrl': product_img,
        'catalog': product_catalog[0] if len(product_catalog) >= 1 else "",
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

    print('完成' + str(product_id) + "销售数据爬取!",product_summary)
    return product_summary

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
    sessionNum=0
    session = getSession()
    while productIdlist:
        productId=productIdlist.pop()
        print("开始爬虫{}".format(productId),"等待爬虫产品数据为{}".format(len(productIdlist)))
        productId=fetch_content(productId, retry_num=1,session=session)
        if productId:
            productIdlist.append(productId)
            print("产品{}爬虫失败,返回消息列表".format(productId), "等待爬虫产品数据为{}".format(len(productIdlist)))
            time.sleep(10*random.randint(1,6))
        sessionNum+=1
        if sessionNum % 20 ==0:
            session=getSession()


if __name__ == '__main__':
    Start_Time = time.time()
    productIdlist = list(competingProductInfo.objects.values_list('productId', flat=True))  # 数据库读取产品ID

    # test data
    # productIdlist=[
    #     32861516622,
    #     32887755558,
    #     32868334765,
    #     32871391355,
    #     32915408299,
    #     32733564246,
    #     32846789656,
    #     32849267839,
    #     32859764400,
    #     32840845274,
    #     32843789538,
    #     32864736748,
    #     32843605585,
    #     32863797905,
    #     32816975451,
    #     32847639499,
    #     32902184643,
    #     32820773751,
    #     32850430777,
    #     32882014811,
    #     32926972345,
    #     32878549408,
    #     32949930690,
    #     32747366518,
    #     32888500911,
    #     32853261329,
    #     32800289688,
    #     32886364691,
    #     32266526239,
    #     32911507267,
    #     32883659218,
    #     32704745486,
    #     32852674627,
    #     32790918877,
    #     32795045802,
    #     32817171139,
    #     32900933184,
    #     32850953889,
    #     32945529506,
    #     32839092568,
    #     32833487200,
    #     32859576018,
    #     32869858103,
    #     32895727295,
    #     32828028158,
    #     32848127846,
    #     32813636076,
    #     32925932830,
    #     32867892119,
    #     32848017688,
    #     32839171433,
    #     32760793423,
    #     32826101506,
    #     32664020995,
    #     32829496091,
    #     32845508167,
    #     32915022871,
    #     32751732383,
    #     32828878670,
    #     32896904742,
    #     32952122090,
    #     32804526347,
    #     32841181807,
    #     32857672627,
    #     32848061403,
    #     32919998920,
    #     32862359004,
    #     32889505763,
    #     32853306366,
    #     32925803607,
    #     32749484465,
    #     32950216089,
    #     32918805325,
    #     32949608631,
    #     32812828061,
    #     32945137990,
    #     32890240596,
    #     32789502955,
    #     32953212240,
    #     32928738822,
    #     32932396408,
    #     32851239357,
    #     32853720495,
    #     32774432159,
    #     32833213044,
    #     32829845598,
    #     32820707719,
    #     32855508176,
    #     32295902254,
    #     32827053222,
    #     32891739519,
    #     32887592676,
    #     32854977225,
    #     32864592760,
    #     32884157393,
    #     32891127758,
    #     32885764929,
    #     32865323130,
    #     32880849128,
    #     32855661832,
    #     32911249300,
    #     32852118560,
    #     32824957700,
    #     32854052487,
    #     32886344341,
    #     32828096748,
    #     32845151225,
    #     32816682431,
    #     32883804882,
    #     32857163457,
    #     32870660896,
    #     32855431697,
    #     32870157122,
    #     32912264547,
    #     32850756645,
    #     32885147034,
    # ]
    main(productIdlist)
    End_Time = time.time()
    Spend_Time = str(round((End_Time - Start_Time) / 60, 2))
    print('结束')
    send_mail(Spend_Time)