from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from apps.user.utils import generate_password
from django.contrib import messages

@login_required(login_url='user:login')
def list(request):
    administrators = Administrator.objects.all().order_by('-id')
    context = {
        'administrators': administrators,
    }
    return render(request, 'administrator/list.html', context)

@login_required(login_url='user:login')
def details(request, pk):

    administrator = Administrator.objects.get(id=pk)
    form = AdministratorForm(instance=administrator)

    if request.method == 'POST':
        if 'delete' in request.POST:
            administrator.delete()
            return redirect('administrator:list')
        else:
            form = AdministratorForm(request.POST, instance=administrator)
            if form.is_valid():
                form.save()
                return redirect('administrator:details', pk=pk)

    context = {
        'administrator': administrator,
        'form': form
        }
    return render(request, 'administrator/details.html', context)


@login_required(login_url='user:login')
def create(request):

    form = AdministratorForm()

    if request.method == 'POST':
        form = AdministratorForm(request.POST, request.FILES)
        if form.is_valid():
            password = generate_password()
            user = User.objects.create_user(
                username=password,
                password=password,
                role='administrator')
            
            form.instance.user = user
            form.save()
            messages.success(request, 'Администратор создан')
            return redirect('administrator:create')

    context = {
        'form': form
    }
    return render(request, 'administrator/create.html', context)


@login_required(login_url='user:login')
def delete(request, pk):
    administrator = Administrator.objects.get(id=pk)
    administrator.delete()
    user = User.objects.get(id=administrator.user.id)
    user.delete()
    return redirect('administrator:list')