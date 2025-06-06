from django import template
register = template.Library()

@register.filter
def times(number):
    try:
        return range(int(number))
    except:
        return []

@register.filter
def get_item(dictionary, key):
    return dictionary.get(str(key))

@register.simple_tag
def seat_key(row, col):
    return f"{row},{col}"