from django.shortcuts import render
from django.http import JsonResponse
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
        
        # 파일 처리 로직 작성
        # 예: 파일을 서버에 저장하고, 처리 결과를 반환
        return JsonResponse({'status': 'success', 'filename': uploaded_file.name})
    return JsonResponse({'status': 'error'}, status=400)

def image_upload_handler(request):
    if request.method == 'POST':
        # 이미지 파일 처리
        
        image_file = request.FILES['file']
        content = image_file.read()
        objects = viseionAI.obj_detection_file(content)
        
        for obj in objects['objects']:
            obj['crop_img'].show()        
        
        return JsonResponse({'result': 'success'})
    return JsonResponse({'result': 'error'}, status=400)

def airecommend_result(request):
    # TODO: 실제 분석 결과를 여기에 넣으세요.
    context = {'result': '분석 결과'}
    return render(request, 'airecommend_result.html', context)