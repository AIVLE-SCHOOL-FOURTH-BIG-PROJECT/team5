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


# API 키 직접 설정
# 부계정 api
# api_key = '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'
# 본계정 api
# api_key = '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'

#client = openai.Client(api_key=api_key)
with open('./nabang/utils/gptKey.txt', 'r') as file:
    api_key = file.read().strip()
openai.api_key = api_key

# OpenAI API 키 설정
# openai.api_key = 
# client = openai.OpenAI()
# image_path = '/home/myeong/ex_room_img/room.jpg'
image_path = 'data:image/jpeg;base64,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'


# OpenAI 클라이언트 초기화
# client = openai(api_key="YOUR_API_KEY")

able_object_list = ['Sectional_Sofas', 'Sleeper_Sofas', 'Reclining_Sofas', 'LoveSeats', 'Futons', 'Settles', 'Convertibles', 
                        'Accent_Chairs', 'Coffee_Tables', 'TV_Stands', 'End_Tables', 'Console_Tables', 'Ottomans', 'Living_Room_Sets', 
                        'Decorative_Pillows', 'Throw_Blankets', 'Area_Rugs', 'Wall_Arts', 'Table_Lamps', 'Floor_Lamps', 
                        'Pendants_and_Chandeliers', 'Sconces', 'Baskets_and_Storage', 'Candles', 'Live_Plants', 'Artificial_Plants', 
                        'Planters', 'Decorative_Accessories', 'Window_Coverings', 'Decorative_Mirrors', 'Dining_Sets', 
                        'Dining_Tables', 'Dining_Chairs', 'Bar_Stools', 'Kitchen_Islands', 'Buffets_and_Sideboards', 'China_Cabinets', 
                        'Bakers_Recks', 'Bedroom_Sets', 'Mattresses', 'Nightstands', 'Dressers', 'Beds', 'Bedframes', 'Bases', 'Vanities', 
                        'Entryway_Furnitures', 'Desks', 'Desk_Chairs', 'Bookcases', 
                        'File_Cabinets', 'Computer_Armoires', 'Drafting_Tables', 'Cabinets', 'Furniture_Sets']


def analyze_room_and_recommend_furniture(image_path):
    """
    방 사진을 분석하고 셜록 홈즈 스타일로 방에 대한 추리와 가구 추천을 제공합니다.

    :param image_path: 방 사진의 경로 또는 URL
    :return: 추리 및 가구 추천 결과
    """
    # 'gpt-4-vision-preview' 모델에 이미지와 프롬프트 전달
    prompt = "As Sherlock Holmes, please analyze the pictures of the following rooms and recommend what furniture you would like for this room. Here's a list of furniture you can recommend, so all you have to do is pick one piece of furniture.'able_object_list': {}. you just need to tell one object. just a one word.".format(able_object_list)
    # 'gpt-4-vision-preview' 모델에 이미지와 프롬프트 전달
    response = openai.ChatCompletion.create(
        model="gpt-4-vision-preview",
        messages=[{
            "role": "system",
            "content": prompt
        }, {
            "role": "user",
            "content": image_path
        }]
    )

    return response.choices[0].message.content

# 예시 이미지 경로
# image_path = '/home/myeong/ex_room_img/room.jpg'

# 분석 및 추천 실행
# result = analyze_room_and_recommend_furniture(image_path)
# print(result)











####################################################
# gpt4 설명
# 참고 사항
# low"고해상도" 모델이 비활성화됩니다. 모델은 저해상도 512px x 512px 버전의 이미지를 수신하고 65개의 토큰 예산으로 이미지를 나타냅니다. 
# 이를 통해 API는 높은 세부 정보가 필요하지 않은 사용 사례에 대해 더 빠른 응답을 반환하고 더 적은 입력 토큰을 사용할 수 있습니다.

# high먼저 모델이 저해상도 이미지를 볼 수 있도록 한 다음 입력 이미지 크기를 기반으로 512px 정사각형으로 입력 이미지의 세부 자르기를 생성하는 "고해상도" 모드를 활성화합니다. 
# 각각의 세부 작물은 토큰 예산(65개 토큰)의 두 배를 사용하여 총 129개 토큰을 사용합니다.