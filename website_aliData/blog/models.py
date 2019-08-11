# Create your models here.
from django.db import models


# class Blog(models.Model):
#     title = models.CharField(max_length=100)
#     content = models.TextField()
#
#     def __unicode__(self):
#         return self.title



class monitorProductTag(models.Model):
    tag=models.CharField(max_length=128,primary_key=True,default='')
    comment=models.CharField(max_length=128, default='')

class catalog(models.Model):
    home = models.CharField(max_length=128,default='')
    allCategories=models.CharField(max_length=128, default='')
    firstCategory=models.CharField(max_length=128, default='')
    secondCategory=models.CharField(max_length=128, default='')
    thirdCategory=models.CharField(max_length=128, default='')
    fourthCategory=models.CharField(max_length=128, default='')
    fifthCategory=models.CharField(max_length=128, default='')
    sixthCategory=models.CharField(max_length=128, default='')
    seventhCategory=models.CharField(max_length=128, default='')
    eigthCategory=models.CharField(max_length=128, default='')
    def __str__(self):
        return self.firstCategory

# competingProduct

class competingProductInfo(models.Model):
    productId = models.BigIntegerField(64,primary_key=True)
    catalog = models.CharField(max_length=32, null=True)
    firstTags = models.CharField(max_length=128, null=True)
    secondTags=models.CharField(max_length=128, null=True)
    tag=models.CharField(max_length=128, default='')
    def __str__(self):
        return self.productId

class competingProductDailySales(models.Model):
    productId = models.BigIntegerField(64)
    totalSales = models.IntegerField()
    totalEvaluation = models.IntegerField()
    date = models.DateField()
    title = models.CharField(max_length=500)
    productScore = models.CharField(max_length=8)
    price = models.CharField(max_length=64)
    picUrl = models.CharField(max_length=256)
    catalog = models.CharField(max_length=64,default='')
    home = models.CharField(max_length=128,default='')
    allCategories = models.CharField(max_length=128,default='')
    firstCategory = models.CharField(max_length=128,default='')
    secondCategory = models.CharField(max_length=128,default='')
    thirdCategory = models.CharField(max_length=128,default='')
    fourthCategory = models.CharField(max_length=128,default='')
    fifthCategory = models.CharField(max_length=128,default='')
    sixthCategory = models.CharField(max_length=128,default='')
    seventhCategory = models.CharField(max_length=128,default='')
    eigthCategory = models.CharField(max_length=128,default='')

class competingProductDailySalesforFiveDays(models.Model):
    productId = models.BigIntegerField(64)
    catalog = models.CharField(max_length=64,null=True)
    firstTags = models.CharField(max_length=128,null=True)
    secondTags = models.CharField(max_length=128,null=True)
    title = models.CharField(max_length=500)
    totalSales = models.IntegerField()
    totalEvaluation = models.IntegerField()
    productScore = models.CharField(max_length=8)
    price = models.CharField(max_length=64)
    picUrl = models.CharField(max_length=256)
    date = models.DateField()
    past1_Sales= models.IntegerField(default=0)
    past2_Sales= models.IntegerField(default=0)
    past3_Sales= models.IntegerField(default=0)
    past4_Sales= models.IntegerField(default=0)
    home = models.CharField(max_length=128,default='')
    allCategories = models.CharField(max_length=128,default='')
    firstCategory = models.CharField(max_length=128,default='')
    secondCategory = models.CharField(max_length=128,default='')
    thirdCategory = models.CharField(max_length=128,default='')
    fourthCategory = models.CharField(max_length=128,default='')
    fifthCategory = models.CharField(max_length=128,default='')
    sixthCategory = models.CharField(max_length=128,default='')
    seventhCategory = models.CharField(max_length=128,default='')
    eigthCategory = models.CharField(max_length=128,default='')

    def __str__(self):
        return  self.productId

# infringeProduct

class infringeProductinfo(models.Model):
    productId = models.BigIntegerField(64,primary_key=True)
    catalog=models.CharField(max_length=32,null=True)
    firstTags=models.CharField(max_length=128,null=True)
    secondTags = models.CharField(max_length=128,null=True)
    totalSales = models.IntegerField()
    totalEvaluation = models.IntegerField()
    productScore = models.CharField(max_length=8)
    price = models.CharField(max_length=64)
    updateDate = models.DateField()
    been_deleted = models.IntegerField(null=True)
    confirm_times =models.IntegerField(null=True)

# newCompetingProduct

class newCompetingProductInfo(models.Model):
    productId = models.BigIntegerField(64,primary_key=True)

class newCompetingProductDailySales(models.Model):
    productId = models.BigIntegerField(64)
    totalSales = models.IntegerField()
    totalEvaluation = models.IntegerField()
    date = models.DateField()
    title = models.CharField(max_length=500)
    productScore = models.CharField(max_length=8)
    price = models.CharField(max_length=64)
    picUrl = models.CharField(max_length=256)
    catalog = models.CharField(max_length=64)
    home = models.CharField(max_length=128,default='')
    allCategories = models.CharField(max_length=128,default='')
    firstCategory = models.CharField(max_length=128,default='')
    secondCategory = models.CharField(max_length=128,default='')
    thirdCategory = models.CharField(max_length=128,default='')
    fourthCategory = models.CharField(max_length=128,default='')
    fifthCategory = models.CharField(max_length=128,default='')
    sixthCategory = models.CharField(max_length=128,default='')
    seventhCategory = models.CharField(max_length=128,default='')
    eigthCategory = models.CharField(max_length=128,default='')

