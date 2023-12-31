"""nabang URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.shortcuts import render
from . import views

def index(request):
    return render(request,'index.html')

urlpatterns = [
    path('', views.index, name='index'),
    path('airecommend/', views.airecommend, name='airecommend'),
    path('file-upload/', views.file_upload, name='file_upload'),
    path('path-to-image-upload-handler', views.image_upload_handler, name='image-upload-handler'),
    path('airecommend_result', views.airecommend_result, name='airecommend_result'),
]
