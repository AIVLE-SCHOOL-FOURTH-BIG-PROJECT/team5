
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView, LogoutView
from .views import check_username
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from .views import delete_account, find_user_info,find_user_info_pw


def index(request):
    return render(request,'index.html')

urlpatterns = [
    path('', views.index, name='index'),
    path('airecommend/', views.airecommend, name='airecommend'),
    path('file-upload/', views.file_upload, name='file_upload'),
    path('path-to-image-upload-handler', views.image_upload_handler, name='image-upload-handler'),
    path('airecommend_result', views.airecommend_result, name='airecommend_result'),
    path('signup/', views.signup, name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('accounts/', include('allauth.urls')),
    path('signup/', views.signup, name='signup'),
    path('personaldata/', views.personal_data, name='personal_data'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('check_username/', check_username, name='check_username'),
    path("password_change/", views.MyPasswordChangeView.as_view(), name="password_change"),
    path("password_change/done/",auth_views.PasswordChangeDoneView.as_view(),name="password_change_done",),
    path('delete_account/', delete_account, name='delete_account'),
    path('find_user_info/', find_user_info, name='find_user_info'),
    path('find_user_info_pw/', find_user_info_pw, name='find_user_info_pw'),
    path('board/', include('board.urls')),
    path('common/', include('common.urls')),
    path('accounts/', include('allauth.urls')),
    path('rule/', views.rule, name='rule'),
    path('check_username/', views.check_username, name='check_username'),  # 아이디 중복 확인 URL
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

