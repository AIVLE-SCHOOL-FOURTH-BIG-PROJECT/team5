from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils.color_extraction import extract_ordered_dominant_colors
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_protect
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from nabang.adapters import CustomSocialAccountAdapter
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import viseionAI

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

        # 세션에 업로드된 이미지 URL 저장
        request.session['uploaded_image_url'] = full_url

        return JsonResponse({'status': 'success', 'filename': uploaded_file.name, 'image_url': full_url})
    return JsonResponse({'status': 'error'}, status=400)

def image_upload_handler(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES['file']
            
            # 탐지모델
            objects = viseionAI.obj_detection_file(image_file.read())
            image_file.seek(0)
            for obj in objects['objects']:
                obj['crop_img'].show() 
                
            num_colors = 3
            ordered_dominant_colors, ordered_percentages = extract_ordered_dominant_colors(image_file, num_colors)
            print(ordered_dominant_colors)
            print(ordered_percentages)
            # 세션에 분석 결과 저장
            request.session['analysis_result'] = {
                'colors': ordered_dominant_colors,
                'percentages': ordered_percentages,
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