from django.shortcuts import render
from django.http import JsonResponse
from .utils.color_extraction import extract_ordered_dominant_colors 
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import viseionAI
import numpy as np
from PIL import Image

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
            
            # 탐지모델
            content = image_file.read()
            objects = viseionAI.obj_detection_file(content)
            
            for obj in objects['objects']:
                obj['crop_img'].show()        

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