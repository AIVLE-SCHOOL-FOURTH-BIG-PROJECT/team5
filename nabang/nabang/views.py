from django.shortcuts import render
from django.http import JsonResponse
from .utils.color_extraction import extract_ordered_dominant_colors 

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

# def image_upload_handler(request):
#     if request.method == 'POST':
#         # 이미지 파일 처리
#         image_file = request.FILES['file']
#         # 이미지 분석 로직 구현
#         num_colors = 3
#         ordered_dominant_colors, ordered_percentages = extract_ordered_dominant_colors(image_file, num_colors)
#         # 분석 결과에 따라 결과 페이지로 리디렉션
#         return JsonResponse({'result': 'success'})

    # return JsonResponse({'result': 'error'}, status=400)

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
            
            return JsonResponse({'result': 'success'})
        except Exception as e:
            # 오류 처리
            return JsonResponse({'result': 'error', 'reason': str(e)}, status=500)
    else:
        return JsonResponse({'result': 'error'}, status=400)



# def airecommend_result(request):
#     # TODO: 실제 분석 결과를 여기에 넣으세요.
#     context = {'result': '분석 결과'}
#     return render(request, 'airecommend_result.html', context)


def airecommend_result(request):
    # 세션에서 분석 결과 불러오기
    analysis_result = request.session.get('analysis_result', {})

    # 템플릿에 전달할 컨텍스트에 결과 추가
    context = {
        'result': '분석 결과',
        'analysis_colors': analysis_result.get('colors'),
        'analysis_percentages': analysis_result.get('percentages')
    }

    return render(request, 'airecommend_result.html', context)
