
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from . import views
from django.conf import settings
from django.conf.urls.static import static


def index(request):
    return render(request,'index.html')

urlpatterns = [
    path('', views.index, name='index'),
    path('airecommend/', views.airecommend, name='airecommend'),
    path('file-upload/', views.file_upload, name='file_upload'),
    path('path-to-image-upload-handler', views.image_upload_handler, name='image-upload-handler'),
    path('airecommend_result', views.airecommend_result, name='airecommend_result'),
    path('signup/', views.signup, name='signup'),
    path('rule/', views.rule, name='rule'),
    path('board/', include('board.urls')),
    path('common/', include('common.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
