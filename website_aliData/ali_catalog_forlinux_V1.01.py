import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aliData.settings")# project_name 项目名称
# print(django.VERSION)
django.setup()
from blog.models import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import *
from pyquery import PyQuery as pq
import time
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import pymongo
from config import *


# 配置mongodb数据库
client = pymongo.MongoClient(MONGO_URI)
db = client[MONGO_DB_catalog]


def openBrowser():
    try:
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_argument("headless")
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('no-sandbox')
        # browser = webdriver.Chrome(chrome_options=chrome_options)  # use in windows
        browser = webdriver.Chrome(executable_path='/root/venv/chromedriver', chrome_options=chrome_options)   # use in linux
        browser.set_page_load_timeout(40)
        browser.set_script_timeout(40)
        browser.maximize_window()
        wait = WebDriverWait(browser, 40)
        browser.get('https://www.aliexpress.com')
        return wait, browser
    except TimeoutException as TE:
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), TE.msg)
        browser.quit()
        return openBrowser()

def search(key_word, try_time, wait, browser):
    try:
        browser.refresh()
        browser.get('https://www.aliexpress.com')
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#search-key"))
        )
        input.send_keys(key_word)
        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#form-searchbar > div.searchbar-operate-box > input"))
        )
        submit.click()
    except (TimeoutException, WebDriverException) as TW:
        try_time += 1
        if try_time > 10:
            return False
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                  'Error !!!! Search key word {} try_time{}'.format(key_word, try_time), 'Exception:' + str(TW.msg))
            return search(key_word, try_time, wait, browser)

def scroll_website(scrollRang, browser):
    js_1 = "var q=document.documentElement.scrollTop=" + scrollRang
    browser.execute_script(js_1)

def writeToTXT(file_name,productId):
    f = open('./ali_catalog_forlinux_keyword_data/' + file_name, "a+")
    f.write(str(productId) + '\n')
    f.close()

def saveToSQLite(sqlDB,productId,productLists):
    if productId not in productLists:
        sqlDB.objects.get_or_create(
            productId=productId,
        )

def get_product_data( wait, browser):
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#hs-below-list-items")))
    html = browser.page_source
    doc = pq(html)
    items = doc("#hs-below-list-items .list-item ").items()
    productList=[]
    for item in items:
        try:#避开峰推位
            if item.attr('qrdata'):
                product={
                'ProductID': int('0' + re.findall(r"\|(\d{0,100})\|", item.attr('qrdata'))[0]),
                'ProductReview' : int('0' + item.find('.rate-num ').text().replace('(', '').replace(')', '')),
                'ProductOrder' : int('0' + re.findall(r'[^()]+', item.find('.order-num-a ').text())[1]),
                }
                productList.append(product)
        except:
            continue
    return productList


def next_page(catalog, key_word, page_num, try_time, wait, browser):
    time.sleep(20)
    try:
        browser.refresh()
        target = browser.find_element_by_id("pagination-bottom-input")
        scroll_website('10000', browser)
        browser.execute_script("arguments[0].scrollIntoView();", target)
        input = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#pagination-bottom-input"))
        )
        input.clear()
        input.send_keys(page_num)

        submit = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#pagination-bottom-goto"))
        )
        submit.click()
        scroll_website('2000', browser)
        submit_Galley = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "#view-thum"))
        )
        submit_Galley.click()
        wait.until(EC.text_to_be_present_in_element
                   ((By.CSS_SELECTOR,
                     '#pagination-bottom > div.ui-pagination-navi.util-left > span.ui-pagination-active'),
                    str(page_num))
                   )
    except (TimeoutException, WebDriverException) as TW:
        try_time = try_time + 1
        if try_time > 3:
            return False
        else:
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),
                  'Error!!!! Keyword {} at {} Page Loading Fail, Now Try_time {},Exception :{}'.format(
                      key_word.replace('\n', ''), page_num, try_time, str(TW)))
            return next_page(catalog, key_word, page_num, try_time, wait, browser)
    except NoSuchElementException:
        return False


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
    start_spiderTime = time.time()
    competingProductList=competingProductInfo.objects.all().only("productId")
    productLists = []
    for productList in competingProductList:
        productLists.append(productList.productId)
    catalog_list=[
        'Access_Control.txt',
        'airpods.txt',
        'Alarm_Sensor.txt',
        'audio_cable.txt',
        'bluetooth_receiver.txt',
        'cable_winder.txt',
        'card_readers.txt',
        'Computer_Cables_Connectors.txt',
        'computer_cleaners.txt',
        'Computer_Cleaners.txt',
        'Computer_Components.txt',
        'Computer_Peripherals.txt',
        'cooling_phone.txt',
        'digital_photo_frames.txt',
        'digital_tablets.txt',
        'dock.txt',
        'Door_Intercom.txt',
        'earphone.txt',
        'Fire_Protection.txt',
        'game_accessories.txt',
        'game_bag.txt',
        'handheld_game_console.txt',
        'iphone_case.txt',
        'keyboards.txt',
        'Laptop_Accessories.txt',
        'laptop_cooling_pads.txt',
        'laptop_docking_stations.txt',
        'laptop_stand.txt',
        'Microphones.txt',
        'Mini_Camcorders.txt',
        'mouse_pads.txt',
        'mouse.txt',
        'Networking.txt',
        'Office_Electronics.txt',
        'pc_game_console.txt',
        'phone_adapter.txt',
        'phone_charge.txt',
        'phone_holder.txt',
        'phone_len.txt',
        'Plotters.txt',
        'remote_control.txt',
        'sd_card_reader.txt',
        'self_stcick.txt',
        'set_up_box.txt',
        'sim_card.txt',
        'smart_remote.txt',
        'smart_socket.txt',
        'smart_tracker.txt',
        'smart_watch.txt',
        'Sports_And_Action_Video_Cameras_Accessories.txt',
        'Surveillance_Products.txt',
        'tablet_case.txt',
        'tablet_holder.txt',
        'Tablet_Pen.txt',
        'Tablets.txt',
        'touch_pads.txt',
        'usb_hubs.txt',
        'VR_glasses.txt',
        'Watchbands.txt',
        'Workplace_Safety_Supplies.txt',
    ]
    for catalog in catalog_list:
        Start_Time = time.time()
        # file_name = catalog + '_Increase_Sale.txt'
        for key_word in open('./ali_catalog_forlinux_keyword/' + catalog).readlines():
            wait, browser = openBrowser()
            print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()), 'Catalog :{}--Keyword:{}--Start Spider!!!! '.format(catalog, key_word.replace('\n', '')))
            try_time = 1
            respone_search = search(key_word, try_time, wait, browser)
            if respone_search == False:
                browser.quit()
                time.sleep(60 * 60 * 1.5)
                start_spiderTime = time.time()
                continue
            total = 30
            for page in range(1, total + 1):
                try_time = 1
                respone_NextPage = next_page(catalog, key_word, page, try_time, wait, browser)
                if respone_NextPage != False:
                    productList = get_product_data(wait, browser)
                    # print(productList)
                    for product in productList:
                        if db[catalog].find_one({'productID': product['ProductID']}) and product['ProductOrder'] - db[catalog].find_one({'productID': product['ProductID']})['ProductOrder'] >= 5:
                            db[catalog].update_one({'productID': product['ProductID']},{'$set': {'ProductOrder': product['ProductOrder'], 'ProductReview': product['ProductReview']}},True)
                            # writeToTXT(file_name, product['ProductID'])
                            saveToSQLite(newCompetingProductInfo, product['ProductID'],productLists)
                        else:
                            db[catalog].update_one({'productID': product['ProductID']},{'$set': {'ProductOrder': product['ProductOrder'], 'ProductReview': product['ProductReview']}},True)
                    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),'Catalog :{}--Keyword:{}--PageNum:{}--Spider Finished'.format(catalog,key_word.replace('\n', ''),page))
                else:
                    break

            browser.quit()
            if round((time.time() - start_spiderTime) / (60 * 60), 0) >= 2:
                time.sleep(60 * 60)
                start_spiderTime = time.time()



        End_Time = time.time()
        Total_time = str(round((End_Time - Start_Time) / 60, 2))
        send_mail(catalog, Total_time)
        # os.remove('./KeywordSale_Data/' + file_name)


if __name__ == '__main__':
    main()
