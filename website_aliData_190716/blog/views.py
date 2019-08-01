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
    print(firstCategorySet)
    # catalogsID=[{"id":index,"name":ct['firstCategory']} for index,ct in enumerate(firstCategorySet)]

    # 输入区
    firstCategory=request.GET.get("firstCategory", "")
    secondCategory=request.GET.get("secondCategory","")
    # print(secondCategory,secondCategory== None)
    dateString=request.GET.get("date", "2018-12-26")
    page=request.GET.get("page",1)
    salesFilter=request.GET.get("salesFilter",0)
    date=datetime.datetime.strptime(dateString, "%Y-%m-%d")
    if secondCategory != "":
        if int(salesFilter) == 0:
            productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,secondCategory=secondCategory,date=date).order_by('secondTags','firstTags')
        else:
            productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,secondCategory=secondCategory,date=date).extra(where=["past1_Sales>4"]).order_by('secondTags','firstTags')
    else:
        if int(salesFilter) == 0:
            productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,date=date).order_by('secondTags','firstTags')
        else:
            productInfo=competingProductDailySalesforFiveDays.objects.filter(firstCategory=firstCategory,date=date).extra(where=["past1_Sales>4"]).order_by('secondTags','firstTags')

    print("从数据库中查询出信息数:" + str(len(productInfo)))

    paginator=Paginator(productInfo, 50, 0)
    try:
        pagecontent=paginator.page(page)
    except EmptyPage:
        pagecontent=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        pagecontent=paginator.page(1)
    print("从数据库中查询出信息数:", str(len(productInfo)), "现在显示第{}页数据".format(page))
    # print(pagecontent)
    dataset={"salesFilter":salesFilter,"date": dateString,"firstCategorySet": firstCategorySet,"pagecontent": pagecontent , "totalPages":paginator.num_pages,
             "totaLNumber":len(productInfo),
             "firstCategory":firstCategory.replace(' ','+').replace('&','%26'),
             "secondCategory":secondCategory if secondCategory =="" else secondCategory.replace(' ','+').replace('&','%26')
             }
    return render(request,"competingSales.html", dataset)

def preCompetingsalesData(request):
    # 展示区
    # catalog = request.POST.get("catalogID", "earphone")
    # print("获得类目参数:" + catalog)
    dateString=request.GET.get('date', default="2019-04-03")
    page=request.GET.get('page',default=1)
    date=datetime.datetime.strptime(dateString, "%Y-%m-%d")
    productInfo=preCompetingProductDailySales.objects.filter(date=date)
    paginator=Paginator(productInfo, 30, 0)
    try:
        pagecontent=paginator.page(page)
    except EmptyPage:
        pagecontent=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        pagecontent=paginator.page(1)
    print("从数据库中查询出信息数:",str(len(productInfo)),"现在显示第{}页数据".format(page))
    # for i in pagecontent.object_list:
    #     print(i.productId)


    dataset={"date":dateString, "pagecontent": pagecontent,"totalPages":paginator.num_pages,"totaLNumber":len(productInfo)}
    return render(request, "preCompetingsalesData.html", dataset)

def infringeProductInfo(request):
    # 展示区
    dateString=request.GET.get("date", "2018-12-26")
    needDate=request.GET.get("needDate",1)
    page=request.GET.get("page", 1)
    print("needDate",needDate)
    if needDate==1:
        date=datetime.datetime.strptime(dateString, "%Y-%m-%d")
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

def catalogAndTags(request):
    #获取catalogs列表
    catalogs = catalogAndtags.objects.values_list('catalog',flat=True).order_by('catalog').distinct()
    #查询结果
    catalog=request.GET.get('catalog',None)
    if catalog == None:
        data = catalogAndtags.objects.all()
    else:
        data = catalogAndtags.objects.filter(catalog=catalog).order_by('firstTags')

    result = {"data":data,"catalogs":catalogs,"totaLNumber":len(data),"catalog":catalog}

    # result = {"pagecontent":pagecontent,"catalogs":catalogs,"totaLNumber":len(data),"catalog":catalog}
    print("从数据库中查询出信息数:", str(len(data)),)
    return render(request,"catalogAndTags.html",result)

def readMe(request):
    return render(request,'readMe.html')

def infringementInfo(request):
    return render(request,'infringementInfo.html')

def adminPage(request):
    return render(request, "adminPage.html")

def monitoringProduct(request):
    # 查询框
    tags=tag.objects.values('tag').exclude(tag="").distinct()
    tagsID=[{"id":index,"name":ct['tag']} for index,ct in enumerate(tags)]

    # 数据查询
    tagID=request.GET.get("tagID",None)
    dateString=request.GET.get('date',default="2019-04-03")
    date=datetime.datetime.strptime(dateString, "%Y-%m-%d")
    print(tagID)

    productIdSet=competingProductInfo.objects.filter(tag=tagID).values_list('productId',flat=True)
    QuerySets=[]
    for productId in productIdSet:
        if competingProductDailySalesforFiveDays.objects.filter(productId=productId,date=date).exists():
            productInfo=competingProductDailySalesforFiveDays.objects.filter(productId=productId,date=date)[0]
            print(productInfo.productId)
            QuerySets.append(productInfo)


    dataset={'tagsID':tagsID,'QuerySets':QuerySets}
    return render(request,"monitoringProduct.html",dataset)

def competingProductList(request):
    # 展示区
    catalog=request.GET.get("catalogID", None)
    page=request.GET.get("page",1)

    productInfo=competingProductInfo.objects.filter(catalog=catalog).order_by('firstTags','secondTags')
    print("从数据库中查询出信息数:" + str(len(productInfo)))
    catalogSet=catalogAndtags.objects.values('catalog').order_by('catalog').distinct()
    catalogID=[{"id":index,"name":ct['catalog']} for index,ct in enumerate(catalogSet)]
    paginator=Paginator(productInfo, 50, 0)
    try:
        pagecontent=paginator.page(page)
    except EmptyPage:
        pagecontent=paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        pagecontent=paginator.page(1)
    print("从数据库中查询出信息数:", str(len(productInfo)), "现在显示第{}页数据".format(page))
    # print(pagecontent)
    dataset={"catalogID": catalogID, "pagecontent": pagecontent ,"totalPages":paginator.num_pages,'totaLNumber':len(productInfo),"currentCatalog":catalog}
    return render(request, "competingProductList.html", dataset)

#ajax
def checkProductId(request):
    if request.method == "POST":
        productId = request.POST.get("productId")
        print(productId)
        tag=competingProductInfo.objects.filter(productId=productId).values_list('tag',flat=True)[0]
        print(tag)
        return HttpResponse(json.dumps({"productId":productId,"tag":tag}))

def addTags(request):
    if request.method == "POST":
        Catalog = request.POST.get("addCatalog")
        firstTags = request.POST.get("addFirstTags")
        SecondTags= request.POST.get("addSecondTags","")

    if catalogAndtags.objects.filter(catalog=Catalog, firstTags=firstTags,secondTags=SecondTags).exists():
        return HttpResponse(0)
    else:
        catalogAndtags.objects.get_or_create(catalog=Catalog, firstTags=firstTags, secondTags=SecondTags)
        return HttpResponse("ok")

def addProduct(request):
    # return HttpResponse("ok")

    if request.method == "POST":
        form_data = request.POST.get("form_data")
        act = request.POST.get("act")
        print("act is {}".format(act))
        data=json.loads(str(form_data))  # 将JSON格式的数据转化为Python中的dict时，应使用loads：
        dic={}
        for item in data:
            dic[item['name']]=item['value']

        if act == "add":
            print("add_product_tag========" + act)
            competingProductInfo.objects.filter(productId=dic.get("productId")).update(tag=str("MP"+dic.get("tag")))
            tagsName=competingProductInfo.objects.all().values_list('tag', flat=True).distinct()
            for tagName in tagsName:
                tag.objects.update_or_create(tag=tagName)
            return HttpResponse("ok")
        elif act == "delete":
            print("delete_product_tag========" + act)
            competingProductInfo.objects.filter(productId=dic.get("productId")).update(tag="")
            tagsName=competingProductInfo.objects.all().values_list('tag', flat=True).distinct()
            for tagName in tagsName:
                tag.objects.update_or_create(tag=tagName)
            return HttpResponse("ok")

def reloadTags(request):
    catalog=request.POST.get("catalog"), #这里注意ajax传进来的是一个元组
    firstTags=list(catalogAndtags.objects.filter(catalog=catalog[0]).values_list('firstTags',flat=True).distinct().order_by('firstTags'))
    return HttpResponse(json.dumps({"firstTags":firstTags,"catalog":catalog}))

def reloadSecondTags(request):
    catalog_tags=request.POST.get("firstTags"), #这里注意ajax传进来的是一个元组
    catalog=catalog_tags[0].split('$')[0]
    tags=catalog_tags[0].split('$')[1]
    secondTags=list(catalogAndtags.objects.filter(catalog=catalog,firstTags=tags).values_list('secondTags',flat=True).order_by('secondTags'))
    return HttpResponse(json.dumps({"secondTags":secondTags}))

def reloadSecondCategory(request):
    firstCategory=request.POST.get("firstCategory"), #这里注意ajax传进来的是一个元组
    # print(firstCategory)
    secondCategorys=list(catalog.objects.filter(firstCategory=firstCategory[0]).values_list('secondCategory',flat=True).order_by('secondCategory').distinct())
    # print(len(secondCategorys))

    return HttpResponse(json.dumps({"secondCategorys":secondCategorys}))


def deleteTag(request):
    id=request.POST.get("id")
    if catalogAndtags.objects.filter(id=id).exists():
        catalogAndtags.objects.filter(id=id).delete()
        return HttpResponse("ok")
    return HttpResponse("0")

def deleteProduct(request):
    productId=request.POST.get('productId')
    if newCompetingProductInfo.objects.filter(productId=productId).exists():
        newCompetingProductInfo.objects.filter(productId=productId).delete()
        return HttpResponse("OK")
    else:
        return HttpResponse(0)


# 下载类

def download_preCompeting(request):
    dateString=request.GET.get('date', default="2019-04-03")
    date=datetime.datetime.strptime(dateString, "%Y-%m-%d")

    # 设置HTTPResponse的类型
    response=HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition']='attachment;filename={}.xls'.format("listing")
    # 创建一个文件对象
    wb=xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet=wb.add_sheet('order-sheet')
    # 写入文件标题
    sheet.write(0, 0, '产品ID')
    sheet.write(0, 1, '总销量')
    sheet.write(0, 2, '总评价数')
    sheet.write(0, 3, '统计日期')
    sheet.write(0, 4, '标题')
    sheet.write(0, 5, '产品评分')
    sheet.write(0, 6, '产品价格')
    sheet.write(0, 7, '图片地址')
    sheet.write(0, 8, '类目')
    sheet.write(0, 9, '近1天销量')
    sheet.write(0, 10, '近2天销量')
    sheet.write(0, 11, '近3天销量')
    sheet.write(0, 12, '近4天销量')


    data_row = 1
    for i in preCompetingProductDailySales.objects.filter(date=date):
        sheet.write(data_row,0,i.productId)
        sheet.write(data_row,1,i.totalSales)
        sheet.write(data_row,2,i.totalEvaluation)
        sheet.write(data_row,3,i.date.strftime('%Y-%m-%d'))
        sheet.write(data_row,4,i.title)
        sheet.write(data_row,5,i.productScore)
        sheet.write(data_row,6,i.price)
        sheet.write(data_row,7,i.picUrl)
        sheet.write(data_row,8,i.catalog)
        sheet.write(data_row,9,i.past1_Sales)
        sheet.write(data_row,10,i.past2_Sales)
        sheet.write(data_row,11,i.past3_Sales)
        sheet.write(data_row,12,i.past4_Sales)
        data_row = data_row + 1

    # 写出到IO
    output=BytesIO()
    wb.save(output)
    # 重新定位到开始
    output.seek(0)
    response.write(output.getvalue())
    return response

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

