from django.shortcuts import render
from django.http import JsonResponse
from .utils.color_extraction import extract_ordered_dominant_colors 
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate

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
    uploaded_image_url = request.session.get('uploaded_image_url', '')

    context = {
        'result': '분석 결과',
        'analysis_colors': analysis_result.get('colors'),
        'analysis_percentages': analysis_result.get('percentages'),
        'image_url': uploaded_image_url  # 이미지 URL 추가
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

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password == confirm_password:
            user = User.objects.create_user(username, email, password)
            # 로그인 처리 등 추가 로직
            return redirect('index')  # 또는 다른 페이지로 리디렉션
        else:
            return render(request, 'signup.html', {'error': '비밀번호가 일치하지 않습니다.'})

    return render(request, 'signup.html')

def personal_data(request):
    return render(request, 'personaldata.html')

def terms_of_service(request):
    return render(request, 'terms.html')