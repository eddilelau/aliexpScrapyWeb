from django.shortcuts import render
from blog.models import *
import datetime
from django.http import HttpResponse
import json
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from blog.utils import *
import os,sys
from xlwt import *
import xlwt,datetime
from io import BytesIO




import itertools
# Create your views here.

#页面加载
def competingSales(request):
    # 展示区
    firstCategorySet=catalog.objects.values_list('firstCategory', flat=True).exclude(firstCategory="").order_by('firstCategory').distinct()
    tagsID=monitorProductTag.objects.values_list('tag',flat=True).exclude(tag="").distinct()


    # # 输入区
    firstCategory=request.GET.get("firstCategory", "")
    secondCategory=request.GET.get("secondCategory","")
    dateString=request.GET.get("date", "08/08/2018")
    page=request.GET.get("page",1)
    salesFilter=request.GET.get("salesFilter",0)
    print("firstCategory",firstCategory,"secondCategory",secondCategory)

    date=datetime.datetime.strptime(dateString, "%m/%d/%Y")
    print("date formate {}".format(date))
    productIds=competingProductInfo.objects.filter(tag='')
    if secondCategory != "" and int(salesFilter) == 0:
        productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,secondCategory=secondCategory,date=date).order_by('secondTags','firstTags')
    elif secondCategory != "" and int(salesFilter) == 1:
        productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,secondCategory=secondCategory,date=date,productId__in=productIds).extra(where=["past1_Sales>4"]).order_by('secondTags','firstTags')
    elif secondCategory == "" and int(salesFilter) == 0:
        productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,date=date).order_by('secondTags','firstTags')
    elif secondCategory == "" and int(salesFilter) == 1:
        productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,date=date,productId__in=productIds).extra(where=["past1_Sales>4"]).order_by('secondTags','firstTags')

    print("从数据库中查询出信息数:" + str(len(productInfo)))

    paginator=Paginator(productInfo, 50, 0)
    try:
        pagecontent=paginator.page(page)
    except EmptyPage:
        pagecontent=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        pagecontent=paginator.page(1)
    print("从数据库中查询出信息数:", str(len(productInfo)), "现在显示第{}页数据".format(page))
    dataset={
             "salesFilter":salesFilter,
              "date": dateString, "firstCategorySet": firstCategorySet,
              "pagecontent": pagecontent , "totalPages":paginator.num_pages,
             "totaLNumber":len(productInfo),
            "firstCategory_select":firstCategory,
            "secondCategory_select":secondCategory,
             "firstCategory":firstCategory.replace(' ','+').replace('&','%26'),
             "secondCategory":secondCategory if secondCategory =="" else secondCategory.replace(' ','+').replace('&','%26'),
            "tagsID":tagsID,
             }
    return render(request,"competingSales.html", dataset)

def infringeProductInfo(request):
    # 展示区
    dateString=request.GET.get("date", "08/09/2018")
    date=datetime.datetime.strptime(dateString, "%m/%d/%Y")
    needDate=request.GET.get("needDate",1)
    page=request.GET.get("page", 1)
    if needDate==1:
        productInfo=infringeProductinfo.objects.filter(updateDate=date,been_deleted=1).order_by('catalog')
    else:
        productInfo=infringeProductinfo.objects.filter(been_deleted=1).order_by('updateDate')
    paginator=Paginator(productInfo, 30, 0)
    try:
        pagecontent=paginator.page(page)
    except EmptyPage:
        pagecontent=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        pagecontent=paginator.page(1)
    print("从数据库中查询出信息数:", str(len(productInfo)), "现在显示第{}页数据".format(page))


    dataset={'date':dateString, "pagecontent": pagecontent,'needDate':needDate,'totaLNumber':len(productInfo)}
    return render(request, "infringeProductInfo.html", dataset)

def manageMonitorProductTag(request):
    '''
    manageMoniterProductTag
    '''
    data = monitorProductTag.objects.all()
    result = {"data":data,"totaLNumber":len(data)}
    return render(request,"manageMonitorProductTag.html",result)

def readMe(request):
    return render(request,'readMe.html')

def infringementInfo(request):
    return render(request,'infringementInfo.html')

def adminPage(request):
    monitorProducts=competingProductInfo.objects.exclude(tag='')
    monitorProductCountToday=competingProductDailySales.objects.filter(productId__in=monitorProducts,date=datetime.date.today()).count()
    monitorProductCountFiveDayToday=competingProductDailySalesforFiveDays.objects.filter(productId__in=monitorProducts,date=datetime.date.today()).count()
    competingProducts=competingProductInfo.objects.all()
    competingProductCountToday=competingProductDailySales.objects.filter(date=datetime.date.today()).count()
    competingProductCountFiveDaysToday=competingProductDailySalesforFiveDays.objects.filter(date=datetime.date.today()).count()
    newCompetingProducts=newCompetingProductInfo.objects.all()
    newCompetingProductCountToday=newCompetingProductDailySales.objects.filter(date=datetime.date.today()).count()
    infringeProducts=infringeProductinfo.objects.filter(been_deleted=1)
    infringeProductsToday=infringeProductinfo.objects.filter(productId__in=infringeProducts,updateDate=datetime.date.today()).count()


    dataset={'monitorProductCount':len(monitorProducts),
             'monitorProductCountToday':monitorProductCountToday,
             'monitorProductCountFiveDayToday':monitorProductCountFiveDayToday,
             'competingProducts':len(competingProducts),
             'competingProductCountToday': competingProductCountToday,
             'competingProductCountFiveDaysToday':competingProductCountFiveDaysToday,
             'newCompetingProducts': len(newCompetingProducts),
             'newCompetingProductCountToday': newCompetingProductCountToday,
             'infringeProducts':len(infringeProducts),
             'infringeProductsToday':infringeProductsToday,
             }
    return render(request, "adminPage.html",dataset)

def monitoringProduct(request):
    # 查询框
    tagsID=monitorProductTag.objects.values_list('tag',flat=True).exclude(tag="").distinct()

    # select some tag
    tagID=request.GET.get("tagID","brief")
    dateString=request.GET.get('date',default=(datetime.date.today()).strftime("%m/%d/%Y"))
    date=datetime.datetime.strptime(dateString, "%m/%d/%Y")
    print(tagID,dateString,date)
    if tagID == 'brief'and competingProductDailySalesforFiveDays.objects.filter(date=date):
        tags=competingProductInfo.objects.values_list('tag', flat=True).distinct()
        tagsInfo={item['tag']: item['comment'] for item in monitorProductTag.objects.filter(tag__in=tags).values('tag', 'comment')}
        tagsProducts={key: competingProductInfo.objects.filter(tag=key).values_list('productId', flat=True) for key,value in tagsInfo.items() }
        print("tagsInfo",len(tagsInfo),"tagsProducts",len(tagsProducts))
        tagsBestSales={
            tag: competingProductDailySalesforFiveDays.objects.filter(productId__in=productIds,date=date).order_by('-past1_Sales')[0] for tag, productIds in tagsProducts.items()
        }

        tagTables=[]
        for tag in tagsInfo.keys():
            tagTables.append(
                {
                    'tag': tag,
                    'comment': tagsInfo[tag],
                    'productIdNum': len(tagsProducts[tag]) or 0 ,
                    'max_productId': tagsBestSales[tag].productId or 0,
                    'max_productId_totalSales': tagsBestSales[tag].totalSales or 0,
                    'max_productId_totalEvaluation': tagsBestSales[tag].totalEvaluation or 0,
                    'max_productId_past1_Sales': tagsBestSales[tag].past1_Sales or 0,
                    'max_productId_past2_Sales': tagsBestSales[tag].past2_Sales or 0,
                    'max_productId_past3_Sales': tagsBestSales[tag].past3_Sales or 0,
                    'max_productId_past4_Sales': tagsBestSales[tag].past4_Sales or 0,

                }
            )
        dataset={'tagsID':tagsID,'QuerySets':tagTables,'chooseTagID':tagID,'date':dateString}
    else:
        productIdSet=competingProductInfo.objects.filter(tag=tagID).values_list('productId',flat=True)
        QuerySets=list(competingProductDailySalesforFiveDays.objects.filter(productId__in=productIdSet, date=date).order_by('-past1_Sales'))
        dataset={'tagsID':tagsID,'QuerySets':QuerySets,'chooseTagID':tagID}
    return render(request,"monitoringProduct.html",dataset)


#ajax
def checkProductId(request):
    if request.method == "POST":
        productId = request.POST.get("productId")
        # print(productId)
        tag=competingProductInfo.objects.filter(productId=productId).values_list('tag',flat=True)[0]
        return HttpResponse(json.dumps({"productId":productId,"tag":tag}))

def addMonitorProduct(request):
    if request.method == "POST":
        form_data = request.POST.get("form_data")
        act = request.POST.get("act","")
        data=json.loads(str(form_data))  # 将JSON格式的数据转化为Python中的dict时，应使用loads：
        dic={}
        for item in data:
            dic[item['name']]=item['value']
        if act == "add" and competingProductInfo.objects.filter(productId=int(dic.get("productId"))).exists():
            competingProductInfo.objects.filter(productId=int(dic.get("productId"))).update(tag=str(dic.get("tag")))
            return HttpResponse("ok")

def deleteProduct(request):
    productId=request.POST.get('productId')
    if newCompetingProductInfo.objects.filter(productId=productId).exists():
        newCompetingProductInfo.objects.filter(productId=productId).delete()
        return HttpResponse("OK")
    else:
        return HttpResponse(0)

def checkMonitorTag(request):
    if request.method == "POST":
        tag = request.POST.get("tag")
        tagInformation=list(monitorProductTag.objects.filter(tag=tag).values('tag','comment'))[0]
        return HttpResponse(json.dumps({"comment":tagInformation['comment'],"tag":tagInformation['tag']}))

def changeMonitorProductTag(request):
    # return HttpResponse("ok")

    if request.method == "POST":
        form_data = request.POST.get("form_data")
        act = request.POST.get("act")
        print("act is {}".format(act))
        data=json.loads(str(form_data))  # 将JSON格式的数据转化为Python中的dict时，应使用loads：
        dic={}
        for item in data:
            dic[item['name']]=item['value']
        if act == "add" or act == "update":
            print("add_product_tag========" + act)
            competingProductInfo.objects.filter(productId=dic.get("productId")).update(tag=str(dic.get("tag")))
            return HttpResponse("ok")
        elif act == "delete":
            print("delete_product_tag========" + act)
            competingProductInfo.objects.filter(productId=dic.get("deleteProductId")).update(tag="")
            return HttpResponse("ok")

def modifyMonitorTag(request):
    if request.method == "POST":
        form_data = request.POST.get("form_data","")
        print("form_data",form_data)
        act = request.POST.get("act","")
        data=json.loads(str(form_data))  # 将JSON格式的数据转化为Python中的dict时，应使用loads：
        dic={}
        for item in data:
            dic[item['name']]=item['value']

        if act == "add":
            print("add_MonitorTag========" + act)
            if monitorProductTag.objects.filter(tag=dic.get("addMonitorTag")).exists():
                return HttpResponse(0)
            else:
                print(dic, dic.get("updateMonitorTag"), dic.get("addComment"))
                monitorProductTag.objects.create(tag=dic.get("addMonitorTag"),comment=dic.get("addComment"))
                return HttpResponse("ok")
        elif act == "update":
            print("update_MonitorTag========" + act)
            monitorProductTag.objects.filter(tag=dic.get("updateMonitorTag")).update(comment=dic.get("updateComment"))
            return HttpResponse("ok")
        elif act == "delete":
            print("delete_MonitorTag========" + act)
            if monitorProductTag.objects.filter(tag=dic.get("deleteMonitorTag")).exists():
                monitorProductTag.objects.filter(tag=dic.get("deleteMonitorTag")).delete()
                return HttpResponse("ok")
            else:
                return HttpResponse(0)

def reloadSecondCategory(request):
    firstCategory=request.POST.get("firstCategory"), #这里注意ajax传进来的是一个元组
    # print(firstCategory)
    secondCategorys=list(catalog.objects.filter(firstCategory=firstCategory[0]).values_list('secondCategory',flat=True).order_by('secondCategory').distinct())
    # print(len(secondCategorys))

    return HttpResponse(json.dumps({"secondCategorys":secondCategorys}))

def reloadMonitorTagComment(request):
    tagText=request.POST.get("tagText") #这里注意ajax传进来的是一个元组
    if monitorProductTag.objects.filter(tag=tagText).values_list('comment',flat=True)[0] =="":
        return HttpResponse(json.dumps({"comment": ""}))
    else:
        comment=monitorProductTag.objects.filter(tag=tagText).values_list('comment',flat=True)
        return HttpResponse(json.dumps({"comment": comment[0]}))




# 下载类


def download_competingSales(request):
    catalog=request.GET.get("catalogID", None)
    dateString=request.GET.get('date', default="2019-04-03")
    date=datetime.datetime.strptime(dateString, "%Y-%m-%d")

    # 设置HTTPResponse的类型
    response=HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition']='attachment;filename={}.xls'.format("competinglisting")
    # 创建一个文件对象
    wb=xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet=wb.add_sheet('order-sheet')
    # 写入文件标题
    sheet.write(0, 0, '产品ID')
    sheet.write(0, 1, '类目')
    sheet.write(0, 2, '第一标签')
    sheet.write(0, 3, '第二标签')
    sheet.write(0, 4, '标题')
    sheet.write(0, 5, '总销量')
    sheet.write(0, 6, '总评价')
    sheet.write(0, 7, '产品评分')
    sheet.write(0, 8, '价格')
    sheet.write(0, 9, '图片地址')
    sheet.write(0, 10, '日期')
    sheet.write(0, 11, '近1天销量')
    sheet.write(0, 12, '近2天销量')
    sheet.write(0, 13, '近3天销量')
    sheet.write(0, 14, '近4天销量')



    data_row = 1
    for i in competingProductDailySalesforFiveDays.objects.filter(date=date):
        sheet.write(data_row,0,i.productId)
        sheet.write(data_row,1,i.catalog)
        sheet.write(data_row,2,i.firstTags)
        sheet.write(data_row,3,i.secondTags)
        sheet.write(data_row,4,i.title)
        sheet.write(data_row,5,i.totalSales)
        sheet.write(data_row,6,i.totalEvaluation)
        sheet.write(data_row,7,i.productScore)
        sheet.write(data_row,8,i.price)
        sheet.write(data_row,9,i.picUrl)
        sheet.write(data_row,10,i.date.strftime('%Y-%m-%d'))
        sheet.write(data_row,11,i.past1_Sales)
        sheet.write(data_row,12,i.past2_Sales)
        sheet.write(data_row,13,i.past3_Sales)
        sheet.write(data_row,14,i.past4_Sales)
        data_row = data_row + 1

    # 写出到IO
    output=BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

def download_infring(request):
    dateString=request.GET.get("date", "2018-12-26")
    needDate=request.GET.get("needDate", 1)

    # 设置HTTPResponse的类型
    response=HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition']='attachment;filename={}.xls'.format("infring_listing")
    # 创建一个文件对象
    wb=xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet=wb.add_sheet('order-sheet')
    # 写入文件标题
    sheet.write(0, 0, '产品ID')
    sheet.write(0, 1, '类目')
    sheet.write(0, 2, '第一标签')
    sheet.write(0, 3, '第二标签')
    sheet.write(0, 4, '总销量')
    sheet.write(0, 5, '总评价')
    sheet.write(0, 6, '产品评分')
    sheet.write(0, 7, '价格')
    sheet.write(0, 8, '被删除日期')

    if needDate == 1:
        date=datetime.datetime.strptime(dateString, "%Y-%m-%d")
        productInfo=infringeProductinfo.objects.filter(createdate=date).order_by('catalog')
    else:
        productInfo=infringeProductinfo.objects.all().order_by('catalog')

    data_row = 1
    for i in productInfo:
        sheet.write(data_row,0,i.productId)
        sheet.write(data_row,1,i.catalog)
        sheet.write(data_row,2,i.firstTags)
        sheet.write(data_row,3,i.secondTags)
        sheet.write(data_row,4,i.totalSales)
        sheet.write(data_row,5,i.totalEvaluation)
        sheet.write(data_row,6,i.productScore)
        sheet.write(data_row,7,i.price)
        sheet.write(data_row,8,i.createdate.strftime('%Y-%m-%d'))
        data_row = data_row + 1

    # 写出到IO
    output=BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

