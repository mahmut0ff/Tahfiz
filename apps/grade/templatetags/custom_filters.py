from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Получить элемент из словаря по ключу"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.filter
def default_if_none(value, default):
    """Вернуть значение по умолчанию, если значение None"""
    return default if value is None else value

@register.filter
def add_days(date, days):
    """Добавить дни к дате"""
    from datetime import timedelta
    try:
        return date + timedelta(days=int(days))
    except (ValueError, TypeError):
        return date