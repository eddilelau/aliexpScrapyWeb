"""aliData URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from blog import views
from django.conf.urls import include, url



urlpatterns = [
    # ajax
    url(r'^checkProductId', views.checkProductId),
    url(r'^changeMonitorProductTag', views.changeMonitorProductTag),
    url(r'^deleteProduct', views.deleteProduct),
    url(r'^reloadSecondCategory', views.reloadSecondCategory),
    url(r'^checkMonitorTag', views.checkMonitorTag),
    url(r'^modifyMonitorTag', views.modifyMonitorTag),
    url(r'^addMonitorProduct', views.addMonitorProduct),
    url(r'^reloadMonitorTagComment', views.reloadMonitorTagComment),

    # url
    path('', views.adminPage),
    path('competingSales/', views.competingSales),
    path('infringeProductInfo/', views.infringeProductInfo),
    path('monitoringProduct/', views.monitoringProduct),
    path('readMe/',views.readMe),
    path('infringementInfo/',views.infringementInfo),
    path('download_competingSales/', views.download_competingSales),
    path('download_infring/', views.download_infring),
    path('manageMonitorProductTag/',views.manageMonitorProductTag)

]
