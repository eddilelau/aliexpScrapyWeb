"""
登陆页
1、加载https://www.aliexpress.com/item/Tendway-Smart-Car-Phone-Holder-for-Phone-in-Car-Gravity-Universal-Mobile-Car-Phone-Stand-Holder/32926097679.html
2、正则表达式匹配<input id="_csrf_token" name="_csrf_token" type="hidden" value="1l7tmmwzlxoe">  xpath?selector?pearl?
3、向发送服务器发送请求  https://feedback.aliexpress.com/display/evaluationList.htm

from data={
ownerMemberId: 225674640
companyId:
memberType: seller
evalType:positive/neutral/negative
month: 1/3/6
refreshPage: received
page: 2
dynamicTab:
evaSortValue: sortdefault@feedback
${csrfToken.parameterName}: ${csrfToken.token}
callType: iframe
}

4、正则匹配数据,并导出文档
"""



from pyquery import PyQuery as pq
import re
from urllib import parse
import requests
import random
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
import datetime

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
    return USER_AGENTS[random.randint(0,15)]

def send_mail(file_name,dateToday):
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    ret = True
    try:
        message = MIMEMultipart()
        message['From'] = Header("Python_8号店铺近一天评价", 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject = 'Python_8号店铺近一天评价'
        message['Subject'] = Header(subject, 'utf-8')
        message.attach( MIMEText('Python_8号店铺评价_'+dateToday, 'plain', 'utf-8'))


        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(open('./ali_feebackForShoop_Data/Num8/' + file_name, 'rb').read(), 'base64', 'utf-8')
        att1["Content-Type"] = 'application/octet-stream'
        # 这里的filename可以任意写，写什么名字，邮件中显示什么名字
        att1["Content-Disposition"] = 'attachment; filename='+file_name
        message.attach(att1)

        server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 发件人邮箱中的SMTP服务器，端口是25
        server.login(my_sender, my_pass)  # 括号中对应的是发件人邮箱账号、邮箱密码
        server.sendmail(my_sender, [my_user, ], message.as_string())  # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()  # 关闭连接
        print('邮件发送成功')
    except Exception as ex:  # 如果 try 中的语句没有执行，则会执行下面的 ret=False
        print(ex)
        return False

def translateGoogle(text):
    url_google = 'http://translate.google.cn'
    reg_text = re.compile(r'(?<=TRANSLATED_TEXT=).*?;')
    headers = {
        'user-agent': getRandomAgent(),
    }
    # values = {'sl': 'auto','hl': 'zh-cn', 'ie': 'utf-8', 'text': text, 'langpair': '%s|%s' % (f, t)}
    values = {'sl': 'auto','tl': 'en',  'text': text}

    value = parse.urlencode(values)
    url = url_google + '?' + value
    response=requests.get(url, headers=headers)
    content = response.text
    data = reg_text.search(content) or 'NoneType'
    if data=='NoneType':
        print('使用google翻译太频繁,停止爬虫60s')
        time.sleep(60)
    result = data.group(0).strip(';').strip('\'')
    return result

def getFeedback(i,file_name):
    headers  = {
        'authority':'feedback.aliexpress.com',
        # 'method':'GET',
        # 'path':'/display/productEvaluation.htm?productId={}&ownerMemberId=225674640&companyId=235300955&memberType=seller&startValidDate=&i18n=true'.format('32741219610'),
        'scheme':'https',
        'user-agent':getRandomAgent(),

    }
    data = {
        'ownerMemberId': '225674640',
        'memberType': 'seller',
        'month':'6',
        'refreshPage':'received',
        'evalType': 'positive',
        'page': i,
         'evaSortValue': 'sortdefault@feedback',
        '${csrfToken.parameterName}': '${csrfToken.token}',
         'callType': 'iframe',
    }
    url ='https://feedback.aliexpress.com/display/evaluationList.htm'
    res =requests.post(url,headers=headers,data=data)
    result=pq(res.text)
    items=result("#the-list .rating-table tbody tr").items()
    with open('./ali_feebackForShoop_Data/Num8/'+file_name,'w') as f:
        for item in items:
            if item('.td3 .name a').attr('href'):
                buyer_name = (item('.td3 .name a').text())
            else:
                buyer_name = item('.td3 span').text()
            productLink = item('.td4 .product-name a').attr('href')
            productId = re.findall(r'/-/(.*).html',productLink)[0]
            feedbackRate = item('.td2 .star span').attr('style')
            feedbackDate = item('.td2 .feedback-date').text()
            feedbackContent = item('.td2 .feedback span').text()
            # print(feedbackContent)
            if feedbackContent != '':
                feedbackContent_En=translateGoogle(feedbackContent)
                time.sleep(5)
            else:
                feedbackContent_En=''
            print('{}| {}|{}| {}|{}|{}|{}'.format(buyer_name,productLink,productId,feedbackDate,feedbackRate,feedbackContent,feedbackContent_En))
            f.write('{}| {}|{}| {}|{}|{}|{}'.format(buyer_name,productLink,productId,feedbackDate,feedbackRate,feedbackContent,feedbackContent_En))


def main():
    dateToday =str(datetime.date.today().strftime('%Y-%m-%d'))
    file_name = "Num8_ShoopFeedback"+dateToday+".txt"  #输出爬虫数据
    for i in range(30):
        getFeedback(i,file_name)
    send_mail(file_name,dateToday)

if __name__ == '__main__':
    main()
