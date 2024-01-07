from django.shortcuts import render
from django.http import JsonResponse
from .utils.color_extraction import extract_ordered_dominant_colors 
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from nabang.adapters import CustomSocialAccountAdapter
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

def index(request):
    return render(request, 'index.html')

def airecommend(request):
    return render(request, 'airecommend.html')

def file_upload(request):
    if request.method == 'POST' and request.FILES['file']:
        uploaded_file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)

        # 상대 URL을 전체 URL로 변환
        full_url = request.build_absolute_uri(uploaded_file_url)

        return JsonResponse({'status': 'success', 'filename': uploaded_file.name, 'image_url': full_url})
    return JsonResponse({'status': 'error'}, status=400)

def image_upload_handler(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES['file']
            num_colors = 3
            ordered_dominant_colors, ordered_percentages = extract_ordered_dominant_colors(image_file, num_colors)
            
            # 세션에 분석 결과 저장
            request.session['analysis_result'] = {
                'colors': ordered_dominant_colors,
                'percentages': ordered_percentages
            }

            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            image_url = fs.url(filename)

            request.session['image_url'] = {
                'url': image_url
            }
            # file_upload 함수에서 저장한 이미지 URL을 사용
            uploaded_file_url = request.session.get('uploaded_image_url', '')
            return JsonResponse({'result': 'success', 'image_url': uploaded_file_url})
        except Exception as e:
            # 오류 처리
            return JsonResponse({'result': 'error', 'reason': str(e)}, status=500)
    else:
        return JsonResponse({'result': 'error'}, status=400)


def airecommend_result(request):
    analysis_result = request.session.get('analysis_result', {})
    image_url = request.session.get('image_url', '')
    #로그 확인 부분
    context = {
        'result': '분석 결과',
        'analysis_colors': analysis_result.get('colors'),
        'analysis_percentages': analysis_result.get('percentages'),
        'image_url': image_url,  # 이미지 URL 추가
    }

    return render(request, 'airecommend_result.html', context)

def your_view_function(request):
    # 색상 분석 로직 수행
    ordered_colors, ordered_percentages = extract_ordered_dominant_colors(image_file, num_colors)

    # 색상 값을 RGB 스케일로 변환하고 색상과 비율을 결합
    rgb_colors = [[int(r * 255), int(g * 255), int(b * 255)] for r, g, b in ordered_colors]
    colors_and_percentages = [{'color': color, 'percentage': percentage} for color, percentage in zip(rgb_colors, ordered_percentages)]

    context = {
        'result': result,
        'analysis_colors_and_percentages': colors_and_percentages,
    }
    return render(request, 'airecommend_result.html', context)

@csrf_protect
def custom_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # 로그인 성공 시 원하는 페이지로 리다이렉트
                return redirect('index')
            else:
                messages.error(request, '로그인 실패. 아이디 또는 비밀번호를 확인하세요.')
                return render(request, 'index', {'form': form, 'login_failed': True})
    else:
        form = AuthenticationForm()
    return render(request, 'index.html', {'form': form, 'login_failed': False})

@csrf_protect
def signup(request):
    if request.method == 'POST':
        User = get_user_model()
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        birthdate = request.POST['birthdate']
        gender = request.POST['gender']
        print('birthdate:',birthdate)
        print('gender:',gender)
        try:
            if password == confirm_password:
                user = User.objects.create_user(username, email, password)
                print('user:',user)
                # 사용자 생성 후에 추가 필드를 설정합니다.
                user.birthdate = birthdate
                print('user:',user.birthdate)
                user.gender = gender
                print('user:',user.gender)
                user.save()

#                 # 로그인 처리 등 추가 로직
                return redirect('index')  # 또는 다른 페이지로 리디렉션
            else:
                return render(request, 'signup.html', {'error': '비밀번호가 일치하지 않습니다.'})
        except IntegrityError as e:
            print('Exception:', e)
            return render(request, 'signup.html', {'error': '이미 사용 중인 아이디입니다.'})

    return render(request, 'signup.html')


def personal_data(request):
    return render(request, 'personaldata.html')

def terms_of_service(request):
    return render(request, 'terms.html')

def check_username(request):
    username = request.get('username', None)

    if username:
        is_taken = User.objects.filter(username=username).exists()
        data = {'is_taken': is_taken}
        return JsonResponse(data)

    return render({'error': '이미 사용 중인 아이디입니다.'})

class MyPasswordChangeView(PasswordChangeView) :
    success_url = reverse_lazy('index')
    def form_valid(self, form):
        messages.info(self.request, '암호 변경을 완료했습니다!')
        return super().form_valid(form)
    
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # 사용자 삭제
        logout(request)  # 로그아웃
        return redirect('index')  # 삭제 후 리다이렉트할 페이지를 지정합니다.
    return render(request, 'registration/delete_account.html')

def find_user_info(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        username = request.POST.get('username', None)

        if username:
            users = User.objects.filter(username=username)
        elif email:
            users = User.objects.filter(email=email)
        else:
            # Handle the case where neither email nor username is provided
            return render(request, 'registration/find_user_info.html', {'error_message': 'Please provide either email.'})

        if users.exists():
            # Handle the case where one or more users are found
            # You might want to display a list of users or take some other action
            return render(request, 'registration/user_list.html', {'users': users, 'email': email, 'username': username})
        else:
            # Handle the case where no users are found
            return render(request, 'registration/find_user_info.html',{'error_message': '찾으시는 유저가 없습니다'})

    return render(request, 'registration/find_user_info.html',{'error_message': 'POST방식으로 전송하시요'})

def find_user_info_pw(request):
    if request.method == 'POST':
        email = request.POST.get('email', None)
        username = request.POST.get('username', None)

        if username and email:
            users = User.objects.filter(username=username,email=email)
        else:
            # Handle the case where neither email nor username is provided
            return render(request, 'registration/find_user_info.html', {'error_message': 'Please provide either email and username.'})

        if users.exists():
            # Handle the case where one or more users are found
            # You might want to display a list of users or take some other action
            return render(request, 'registration/user_list.html', {'users': users})
        else:
            # Handle the case where no users are found
            return render(request, 'registration/find_user_info.html',{'error_message': '찾으시는 유저가 없습니다'})

    return render(request, 'registration/find_user_info.html',{'error_message': 'POST방식으로 전송하시요'})

def rule(request):
    return render(request, 'rule.html')

def check_username(request):
    username = request.GET.get('username', None)
    response = {
        'is_taken': User.objects.filter(username=username).exists()
    }
    return JsonResponse(response)