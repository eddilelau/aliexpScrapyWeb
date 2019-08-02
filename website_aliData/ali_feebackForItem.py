"""
登陆页
1、加载https://www.aliexpress.com/item/Tendway-Car-Phone-Holder-Dashboard-Mount-Universal-Cradle-Cellphone-Clip-GPS-Bracket-Mobile-Phone-Holder-Stand/32856844088.html
2、正则表达式匹配<input id="_csrf_token" name="_csrf_token" type="hidden" value="e6bvu2x86idk"> xpath?selector?pearl?
3、向发送服务器发送请求  https://feedback.aliexpress.com/display/productEvaluation.htm

head={
ownerMemberId: 225674640
memberType: seller
productId: 32856844088
companyId:
evaStarFilterValue: all Stars
evaSortValue: sortdefault@feedback
page: 3
currentPage: 2
startValidDate:
i18n: true
withPictures: false
withPersonalInfo: false
withAdditionalFeedback: false
onlyFromMyCountry: false
version: evaNlpV1_4
isOpened: true
jumpToTop: false
${csrfToken.parameterName}: ${csrfToken.token}
)
"""

import requests
import random
from pyquery import PyQuery as pq
import time
import re
from urllib import parse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email.header import Header
import datetime
import smtplib

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
    try:
        data = re.findall(reg_text,content)[0].replace('\'','')
    except IndexError as IE:
        print(IE,'使用google翻译太频繁,停止爬虫60s')
        time.sleep(60)
        data=''
    finally:
        return data

def getFeedback(ownerMemberId,productId,companyId,page,fileName):
    headers  = {
        'authority':'feedback.aliexpress.com',
        'method':'GET',
        'path':'/display/productEvaluation.htm?productId=32856844088&ownerMemberId=225674640&companyId=235300955&memberType=seller&startValidDate=&i18n=true',
        'scheme':'https',
        'user-agent':getRandomAgent(),

    }
    data = {
        'ownerMemberId':ownerMemberId,
        'memberType':'seller',
        'productId': productId,
        'companyId': companyId,
        'evaStarFilterValue': 'all Stars',
        'evaSortValue':'sortdefault@feedback',
        'page':page+1,
        'currentPage': page,
        'i18n':'true',
        'withPictures':'false',
        'withPersonalInfo': 'false',
        'withAdditionalFeedback': 'false',
        'onlyFromMyCountry':'false',
        'version':'evaNlpV1_4',
        'isOpened':'true',
        'translate': 'Y',
        'jumpToTop': 'false',
        '${csrfToken.parameterName}': '${csrfToken.token}',
    }
    url ='https://feedback.aliexpress.com/display/productEvaluation.htm'
    res =requests.post(url,headers=headers,data=data)
    result=pq(res.text)
    items=result(".feedback-list-wrap .feedback-item").items()
    with open('./ali_feebackForItem_Data/'+fileName,'a+',encoding='utf-8')as f:
        for item in items:
            buyerName=item(".fb-user-info .user-name").text()
            buyerCountry=item(".fb-user-info .user-country b").text()
            feedbackRate=item(".fb-main .f-rate-info .star-view span").attr('style')
            itemInfo=item(".fb-main .user-order-info .first").text()
            logistics=item(".fb-main .user-order-info .first").siblings().text()
            feedback_original=item(".fb-main .f-content .buyer-feedback").text().strip()
            # if feedback_original != '':
            #     feedbackContent_En = translateGoogle(feedback_original)
            # else:
            #     feedbackContent_En = ''
            feedbackTime = item(".fb-main .f-content .buyer-review .r-time").text()
            additionFeedback_original = item(".fb-main .f-content .buyer-addition-feedback").text().strip()
            # if additionFeedback_original != '':
            #     additionFeedback_original_En = translateGoogle(additionFeedback_original)
            # else:
            #     additionFeedback_original_En = ''
            additionFeedbackTime = item(".fb-main .f-content .buyer-additional-review .r-time").text()
            pics = [item('img').attr('src') for item in item(".fb-main .f-content .r-photo-list .util-clearfix .pic-view-item").items()]


            print(buyerName,
                  buyerCountry,
                  feedbackRate,
                  itemInfo,
                  logistics,
                  feedback_original,
                  # feedbackContent_En,
                  feedbackTime,
                  additionFeedback_original,
                  # additionFeedback_original_En,
                  additionFeedbackTime,
                  pics)

            f.write('{}|{}|{}|{}|{}|{}|{}|{}|{}|{}'.format(
                buyerName,
                buyerCountry,
                feedbackRate,
                itemInfo,
                logistics,
                feedback_original,
                # feedbackContent_En,
                feedbackTime,
                additionFeedback_original,
                # additionFeedback_original_En,
                additionFeedbackTime,
                pics)+'\n')



def send_mail(file_name,productId):
    my_sender = '395407702@qq.com'  # 发件人邮箱账号
    my_pass = 'fxtgbvgdvahubgec'  # 发件人邮箱密码
    my_user = '395407702@qq.com'  # 收件人邮箱账号，我这边发送给自己
    try:
        message = MIMEMultipart()
        message['From'] = Header("Python_ali_itemFeedback_"+productId, 'utf-8')
        message['To'] = Header("工作邮箱", 'utf-8')
        subject = 'Python_ali_itemFeedback_'+productId
        message['Subject'] = Header(subject, 'utf-8')
        message.attach( MIMEText("Python_ali_itemFeedback_"+productId, 'plain', 'utf-8'))


        # 构造附件1，传送当前目录下的 test.txt 文件
        att1 = MIMEText(open('./ali_feebackForItem_Data/' + file_name, 'rb').read(), 'base64', 'utf-8')
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


def main():
    product_dict = [
        #[productID,ownerMemberId,evalutePage]
        [32922559774, 231246967, 87],
        [32922194268, 228486479, 60],
        [32898145904, 119127337, 27],
        [32869943495, 230025104, 25],
        [32931281009, 119127337, 6],
        [32911249300, 205953570, 8],
        [32890626198, 202388313, 82],
        [32888633952, 205953570, 24],
        [32905468202, 220232309, 14],
        [32916109302, 230426576, 28],
    ]
    for i in range(len(product_dict)):
        fileName='itemFeedback_'+str(product_dict[i][0])+'.txt'
        for number in range(product_dict[i][2]):
          #  def getFeedback(ownerMemberId, productId, companyId, page, fileName):
            getFeedback(ownerMemberId=product_dict[i][1], productId=product_dict[i][0],companyId='',page=number,fileName=fileName)
        send_mail(fileName,str(product_dict[i][0]))

if __name__ == '__main__':
    main()

