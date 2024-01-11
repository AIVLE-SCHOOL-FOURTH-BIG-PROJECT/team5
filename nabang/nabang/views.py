from django.shortcuts import render, redirect
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
from django.db import IntegrityError, connection
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
import nabang.utils.viseionAI as viseionAI
import nabang.utils.style_classify as style_classify
import nabang.utils.gpt_recommendation as gpt_recommendation
import nabang.utils.gpt_change_room_style as gpt_change_room_style
import joblib, os, requests
from .utils.color_labeling import color_label

style_model = joblib.load('./nabang/utils/svm_model.joblib')
le = joblib.load('./nabang/utils/label_encoder.joblib') # Load the LabelEncoder

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

def image_change_handler(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(image_file.name, image_file)
            uploaded_file_url = fs.url(filename)
            
            selected_style = request.POST.get('style')
            print('1' ,selected_style)
            
            img_path = f'./media/{image_file}'
            remodeling_img = gpt_change_room_style.change_room_style(img_path, selected_style)
            
            # image_url 이미지 저장
            save_path = f'./media/remodeling.png'
            response = requests.get(remodeling_img, stream=True) 
            if response.status_code == 200:
                with open(save_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=128): 
                        file.write(chunk)
                print("이미지 다운로드 완료: {save_path}")
            else:
                print("이미지 다운로드 실패. HTTP 상태코드: {response.status_code}")
                
            #리모델링 이미지 분석
            image_file.seek(0)
            objects = viseionAI.obj_detection_file(image_file.read())
            image_file.seek(0)
            size = objects['size'][0] * objects['size'][1]
            style_percentage =[]
            tempdic ={}
            for obj in objects['objects']:
                percent = viseionAI.box_percentage(size, obj['box'])
                crop_processing = style_classify.process_image_file(obj['crop_img'])
                crop_predict = style_model.predict(crop_processing)
                crop_style = le.inverse_transform(crop_predict)
                style = str(crop_style[0])
                print(style, type(style))
                try:
                    tempdic[style] += round(percent, 2)
                except:
                    tempdic[style] = round(percent, 2)
                   
            # temp =[crop_style[0], percent] # 각 obj 스타일-비율
            print(tempdic)
            # style_percentage.append(temp) # 순위별 style-비율
            total_percentage = sum(tempdic.values())
            for sty, per in tempdic.items():
                adjusted_percentage = (per / total_percentage) * 100
                temp = [sty, round(adjusted_percentage, 2)]
                style_percentage.append(temp)
            print(style_percentage)
            num_colors = 10
            color_percentage = extract_ordered_dominant_colors(image_file, num_colors) # 순위별 rgb-비율
            print('all: ',color_percentage)
            

            image_file.seek(0)
            # 사용자의 사진에서 가장 dominant 한 색깔을 추출, 미리 db가구들 색깔 라벨링 해둔대로 라벨을 return
            color_label_num = color_label(image_file)
            print('color_label', color_label_num)
            
            image_file.seek(0)
            reco_furniture = gpt_recommendation.analyze_room_and_recommend_furniture(img_path)
            print('추천 가구: ',reco_furniture)
            
            # 세션에 분석 결과 저장
            request.session['analysis_result2'] = {
                'remodeling_img': remodeling_img,
                'style_percentage': style_percentage,
                'reco_furniture': reco_furniture,
                'color_label': color_label_num,
            }
            
            uploaded_file_url = request.session.get('uploaded_image_url', '')
            return JsonResponse({'result': 'success', 'image_url': uploaded_file_url})
        except Exception as e:
            # 오류 처리
            print("error:",e)
            return JsonResponse({'result': 'error', 'reason': str(e)}, status=500)
    else:
        return JsonResponse({'result': 'error'}, status=400)

def airemodeling_result2(request):
    analysis_result2 = request.session.get('analysis_result2', {})
    gptr = analysis_result2.get('reco_furniture')
    color_l = analysis_result2.get('color_label')
    query = "SELECT * from furniture where 1=1"
    style = analysis_result2.get('style_percentage')
    style1 = style[0][0]
    # if style1:
    #     query+=f" AND style LIKE '%{style1[1:-1]}%'"
    # if gptr:
    #     query+=f" AND category LIKE '%{gptr}%'"
    # if color_l:
    #     query+=f" AND color = '{color_l}'"
    # query +=" LIMIT 4"
    # with connection.cursor() as cursor:
    #     cursor.execute(query)
    #     furniture_list=cursor.fetchall()
    # print(query)
    
    context = {
        'result': '리모델링 결과',
        're_img': analysis_result2.get('remodeling_img'),
        'style_per': style,
        'reco_fur': gptr,
        'color_label': color_l,
    }
    print(context['re_img'])
    print(context['style_per'])
    print(context['reco_fur'])
    print(context['color_label'])
    
    return render(request, 'airemodeling_result.html', context)  

def image_upload_handler(request):
    if request.method == 'POST':
        try:
            image_file = request.FILES['file']

            # 탐지모델
            objects = viseionAI.obj_detection_file(image_file.read())
            image_file.seek(0)
            size = objects['size'][0] * objects['size'][1]
            style_percentage =[]
            tempdic = {}
            for obj in objects['objects']:
                percent = viseionAI.box_percentage(size, obj['box'])
                crop_processing = style_classify.process_image_file(obj['crop_img'])
                crop_predict = style_model.predict(crop_processing)
                crop_style = le.inverse_transform(crop_predict)
                style = str(crop_style[0])
                print(style, type(style))
                try:
                    tempdic[style] += round(percent, 2)
                except:
                    tempdic[style] = round(percent, 2)
                    
            # temp =[crop_style[0], percent] # 각 obj 스타일-비율
            print(tempdic)
            # style_percentage.append(temp) # 순위별 style-비율
            for sty, per in tempdic.items():
                temp = [sty,round(per,2)]
                style_percentage.append(temp)
            print(style_percentage)
            
            num_colors = 3
            color_percentage = extract_ordered_dominant_colors(image_file, num_colors) # 순위별 rgb-비율
            print('all: ',color_percentage)
            
            image_file.seek(0)
            # 가구 종류 추천
            img_path = f'./media/{image_file}'
            # reco_furniture = gpt_recommendation.analyze_room_and_recommend_furniture(img_path)
            # print('추천 가구::::::::: ',reco_furniture)
            
            # 세션에 분석 결과 저장
            request.session['analysis_result'] = {
                'color_percentage': color_percentage,
                'style_percentage': style_percentage,
                # 'reco_furniture': reco_furniture,
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
            print("error:",e)
            return JsonResponse({'result': 'error', 'reason': str(e)}, status=500)
    else:
        return JsonResponse({'result': 'error'}, status=400)

def airecommend_result(request):
    analysis_result = request.session.get('analysis_result', {})
    image_url = request.session.get('image_url', '')
    #로그 확인 부분
    products = [
        {'name': '상품1', 'price': '1000원', 'image_url': '#', 'purchase_link': '#'},
        {'name': '상품2', 'price': '2000원', 'image_url': '#', 'purchase_link': '#'},
        {'name': '상품3', 'price': '3000원', 'image_url': '#', 'purchase_link': '#'},
        {'name': '상품4', 'price': '4000원', 'image_url': '#', 'purchase_link': '#'},
    ]
    context = {
        'result': '분석 결과',
        # 'reco_furn': analysis_result.get('reco_furniture'),
        'color_per': analysis_result.get('color_percentage'),
        'style_per': analysis_result.get('style_percentage'),            
        'image_url': image_url,  # 이미지 URL 추가
        'products': products
    }
        
    return render(request, 'airecommend_result.html', context)        
    

@csrf_protect
def signup(request):
    if request.method == 'POST':
        User = get_user_model()
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        try:
            if password == confirm_password:
                user = User.objects.create_user(username, email, password)

                # 사용자 생성 후에 추가 필드를 설정합니다
                # 로그인 처리 등 추가 로직
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
    template_name = 'registration/change_pw.html'
    success_url = reverse_lazy('index')
    def form_valid(self, form):
        messages.success(self.request, '암호 변경을 성공했습니다.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # 폼이 유효하지 않을 때 사용자에게 메시지를 보냅니다.
        messages.error(self.request, '암호 변경을 실패했습니다. 다시 시도해 주세요.')
        return super().form_invalid(form)
    
@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        user.delete()  # 사용자 삭제
        logout(request)  # 로그아웃
        return redirect('index')  # 삭제 후 리다이렉트할 페이지를 지정합니다.
    return render(request, 'registration/delete_account.html')

# def find_user_info(request):
#     if request.method == 'POST':
#         email = request.POST.get('email')
#         username = request.POST.get('username')

#         # Check if the user is trying to find ID or reset password
#         if username:
#             # Password reset
#             try:
#                 user = User.objects.get(username=username, email=email)
#                 # Perform password reset logic here if needed
#                 return render(request, 'registration/password_reset_success.html')
#             except ObjectDoesNotExist:
#                 return render(request, 'registration/user_not_found.html')
#         else:
#             # ID retrieval
#             try:
#                 user = User.objects.get(email=email)
#                 return render(request, 'registration/found_id.html', {'username': user.username})
#             except ObjectDoesNotExist:
#                 return render(request, 'registration/id_not_found.html')

#     return render(request, 'registration/find_user_info.html')

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

def kakao_login(request):

	#settings에 등록해둔 rest_api_key와 redirect_uri
    REST_API_KEY = 'be56835380f36db1533c79bddf121f90'
    KAKAO_REDIRECT_URI = 'http://114.205.122.111/accounts/kakao/login/callback/'

	# 인가코드 가져오기
    code = request.GET.get("code")

	# token 받아오기
    data = {'grant_type': "authorization_code", 'client_id': REST_API_KEY,
            'redirect_uri': KAKAO_REDIRECT_URI,
            'code': code}
    headers = {'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}

    token_response = requests.post('https://kauth.kakao.com/oauth/token', data = data, headers = headers)
    access_token = token_response.json().get('access_token')

	# token 검증하기
    headers = {"Authorization": f'Bearer {access_token}'}
    token_validate_response = requests.get('https://kapi.kakao.com/v1/user/access_token_info', headers = headers)
    print(token_validate_response.json())

	# 사용자 정보 받아오기
    headers = {"Authorization": f'Bearer {access_token}', 'Content-type': 'application/x-www-form-urlencoded;charset=utf-8'}
    user_info_response = requests.post('https://kapi.kakao.com/v2/user/me', headers = headers)
    print(user_info_response.json())

    return render(request, 'index.html')

def kakao_logout(request, access_token):

    REST_API_KEY = 'be56835380f36db1533c79bddf121f90'
    LOGOUT_REDIRECT_URI = '/../'

	# 로그아웃 
    headers = {"Authorization": f'Bearer {access_token}'}
    logout_response = requests.post('https://kapi.kakao.com/v1/user/logout', headers=headers)
    print(logout_response.json())
    
    # 카카오계정과 함께 로그아웃
    logout_response = requests.get(f'https://kauth.kakao.com/oauth/logout?client_id=${REST_API_KEY}&logout_redirect_uri=${LOGOUT_REDIRECT_URI}')

def airemodeling(request):
    return render(request, 'airemodeling.html')

def airemodeling_result(request):
    return render(request, 'airemodeling_result.html')