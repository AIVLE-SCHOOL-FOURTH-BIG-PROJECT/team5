# from django import template

# register = template.Library()

# @register.filter
# def to_rgb(value):
#     return int(float(value) * 255)
# def multiply(value, arg):
#     return value * arg

from django import template

register = template.Library()

@register.filter(name='to_rgb')
def to_rgb(value):
    try:
        # 숫자로 변환 시도
        value = float(value)
    except (ValueError, TypeError):
        # 변환 실패 시 기본값 0 사용
        value = 0

    # 0과 1 사이의 값을 0-255 사이로 변환
    value = int(max(0, min(value, 1)) * 255)

    return value