from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from apps.student.models import Student
from apps.user.models import User


def login_page(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            
            login(request, user)
            messages.success(request, 'Вы вошли в систему')
            return redirect('dashboard:dashboard')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'user/login.html')


def logout_user(request):
    logout(request)
    return redirect('user:login')


def update(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.get(id=request.user.id)
        user.username = username
        user.save()
        messages.success(request, 'Вы успешно изменили свой логин')
        return redirect('user:update')
    return render(request, 'user/update.html')