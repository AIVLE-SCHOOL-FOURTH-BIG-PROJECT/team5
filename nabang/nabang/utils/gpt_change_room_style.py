# GPT 기반 작성
import os
import openai
import requests
import io  # 이 줄을 추가하세요
import base64  # base64 모듈도 추가
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np


with open('./nabang/utils/gptKey.txt', 'r') as file:
    api_key = file.read().strip()
openai.api_key = api_key

# prompt : 첫 번째 GPT의 질문
prompt = "The picture I just presented is a picture of the house. Look at the picture and summarize the atmosphere of the room."

# Function to encode the image
def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


# Getting the base64 string
def change_room_style(image_path, style):
    base64_image = encode_image(image_path)
    
    # 첫 번째 GPT 이용(사진 -> 텍스트(설명)) 
    headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
    "model": "gpt-4-vision-preview",
    "messages": [
        {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": prompt
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
        }
    ],
    "max_tokens": 300
    }
    
    # OpenAI API에 POST 요청 보내기
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    
    # API 응답에서 필요한 정보 추출
    analyze_room_answer = response.json()['choices'][0]['message']['content']
    

    # 두 번째 GPT 이용(텍스트(설명) -> 사진) 
    response = openai.Image.create(
        # model="dall-e-3",
        # model="text2img-1.0",
        prompt= f"{analyze_room_answer}. \n\n It's a specific description of which room. Based on this description, show the room when you changed the atmosphere to a {style} room with a picture.",
        n=1,
        size="1024x1024",
    )

    image_url = response.data[0].url
    
    return image_url # 리모델링된 이미지는 주소(URL) 형태로 받음



# # 지정해줘야할 변수 # (교석님이 수정해주실 부분, 여기 이하)
# # stlyes = ['modern', 'contemporary', 'classic', 'urban', 'country']
# # style : stlyes중에 하나를 style로 지정
# style = 'classic'
# # image_path : 리모델링 전의 사진
# image_path = '/home/myeong/ex_room_img/room2.jpg'
# # filename : image_path에서 filename만 추출해서 save_path에 넣기 위함(제 경우 filename에 room2가 들어갑니다.)
# filename_with_extension = os.path.basename(image_path)
# filename, _ = os.path.splitext(filename_with_extension)
# # save_path : GPT한테 스타일 변경을 받고 난 사진 저장 경로
# save_path = f"/home/myeong/ex_room_img/{filename}_{style}.png" # 다른 방법으로 저장하셔도 됩니다!!



# image_url = change_room_style(image_path, style)

# # image_url 이미지 저장
# response = requests.get(image_url, stream=True) 
# if response.status_code == 200:
#     with open(save_path, 'wb') as file:
#         for chunk in response.iter_content(chunk_size=128): 
#             file.write(chunk)
#     print("이미지 다운로드 완료: {save_path}")
# else:
#     print("이미지 다운로드 실패. HTTP 상태코드: {response.status_code}")


####################################################
# gpt4 설명
# 참고 사항
# low"고해상도" 모델이 비활성화됩니다. 모델은 저해상도 512px x 512px 버전의 이미지를 수신하고 65개의 토큰 예산으로 이미지를 나타냅니다. 
# 이를 통해 API는 높은 세부 정보가 필요하지 않은 사용 사례에 대해 더 빠른 응답을 반환하고 더 적은 입력 토큰을 사용할 수 있습니다.

# high먼저 모델이 저해상도 이미지를 볼 수 있도록 한 다음 입력 이미지 크기를 기반으로 512px 정사각형으로 입력 이미지의 세부 자르기를 생성하는 "고해상도" 모드를 활성화합니다. 
# 각각의 세부 작물은 토큰 예산(65개 토큰)의 두 배를 사용하여 총 129개 토큰을 사용합니다.