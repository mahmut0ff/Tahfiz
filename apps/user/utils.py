import random
import string
from django.shortcuts import redirect

def generate_password():
    symbols = ''.join(random.choice(string.ascii_lowercase) for _ in range(5))
    digits = ''.join(random.choice(string.digits) for _ in range(3))
    return f'{symbols}-{digits}'


def is_admin(func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_superuser or request.user.role == 'admin' or request.user.role == 'administrator':
            return func(request, *args, **kwargs)
        else:
            return redirect('schedule:list')
    return wrapper


def is_teacher(func):
    def wrapper(request, *args, **kwargs):
        if request.user.role == 'teacher':
            return func(request, *args, **kwargs)
        else:
            return redirect('schedule:list')
    return wrapper