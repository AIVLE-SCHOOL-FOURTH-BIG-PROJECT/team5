import io
from PIL import Image
from google.cloud import vision

# def get_image_size(path):
#     with Image.open(path) as img:
#         return img.size  # (width, height)

def box_percentage(f_size, box):
    # 박스의 좌표: (x1, y1, x2, y2)
    box_size = box # obj['box']
    # 박스의 면적 계산
    box_width = box_size[2] - box_size[0]
    box_height = box_size[3] - box_size[1]
    box_area = box_width * box_height
    # 전체 사진의 면적
    full_size = f_size
    # 박스가 차지하는 비율 계산
    box_percentage = (box_area / full_size) * 100
    return box_percentage
    
def localize_objects_file(content): #file
    objectBox = []
    box = []
    temp = []
    
    client = vision.ImageAnnotatorClient()
    image_stream = io.BytesIO(content)
    with Image.open(image_stream) as img:
        width, height = img.size    
    image = vision.Image(content=content)
    objects = client.object_localization(image=image).localized_object_annotations

    for object_ in objects:
        for vertex in object_.bounding_poly.normalized_vertices:
            pixel_x = int(vertex.x * width)
            pixel_y = int(vertex.y * height)
            temp.append(pixel_x)
            temp.append(pixel_y)
        box.append(temp[0])
        box.append(temp[1])
        box.append(temp[4])
        box.append(temp[5])
        temp = []
        object_info = {
            "name": object_.name,
            "confidence": object_.score,
            "box": box,
        }
        box = []
        objectBox.append(object_info)
        
    return objectBox
'ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'
def obj_detection_file(content):
    # np_arr = np.frombuffer(content, np.uint8)
    # img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    objects = localize_objects_file(content)
    
    image_stream = io.BytesIO(content)
    with Image.open(image_stream) as img:
        width, height = img.size
        result = {
            'size': [width, height],
        }
        
        for i, obj in enumerate(objects):
            x1, y1, x2, y2 = obj['box']
            cropped_img = img.crop((x1, y1, x2, y2))
            obj['crop_img'] = cropped_img
        
    result['objects'] = objects
    return result
'ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'
# def localize_objects_path(path): 
#     objectBox = []
#     box = []
#     temp = []
#     imgWidth, imgHeight = get_image_size(path)
    
#     client = vision.ImageAnnotatorClient()
#     with open(path, "rb") as image_file:
#         content = image_file.read()
#     image = vision.Image(content=content)

#     objects = client.object_localization(image=image).localized_object_annotations

#     for object_ in objects:
#         for vertex in object_.bounding_poly.normalized_vertices:
#             pixel_x = int(vertex.x * imgWidth)
#             pixel_y = int(vertex.y * imgHeight)
#             temp.append(pixel_x)
#             temp.append(pixel_y)
#         box.append(temp[0])
#         box.append(temp[1])
#         box.append(temp[4])
#         box.append(temp[5])
#         temp = []
#         object_info = {
#             "name": object_.name,
#             "confidence": object_.score,
#             "box": box,
#         }
#         box = []
#         objectBox.append(object_info)
        
#     return objectBox
# 'ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ'
# def obj_detection_path(path):
#     objects = localize_objects_path(path)

#     fileName = os.path.basename(path)
#     with Image.open(path) as img:
#         width, height = img.size
#         result = {
#             'fileName': fileName,
#             'size': [width, height],
#         }

#         for i, obj in enumerate(objects):
#             x1, y1, x2, y2 = obj['box']
#             cropped_img = img.crop((x1, y1, x2, y2))
#             obj['crop_img'] = cropped_img

#     result['objects'] = objects
#     return result
            
    