from django import template

register = template.Library()

@register.filter
def to_rgb(value):
    return int(float(value) * 255)
def multiply(value, arg):
    return value * arg