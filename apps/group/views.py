from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.student.models import *
from apps.teacher.models import *
from .models import *
from django.db.models import Count
from django.contrib import messages
from apps.schedule.models import *
from .forms import *
from apps.user.utils import is_admin


@login_required(login_url='user:login')
@is_admin
def create(request):
    
    form = GroupForm()
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Группа создана')
            return redirect('group:create')

    context = {
        'form': form
    }
    return render(request, 'group/create.html', context)


@login_required(login_url='user:login')
def list(request):
    
    
    form = GroupForm()
    groups = (
    Group.objects
    .select_related("course")                # подтянет курс через JOIN
    .prefetch_related("teacher_set", "student_set")  # подтянет преподавателей и студентов отдельными запросами
    .order_by("-id")
    )

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

    search_q = request.GET.get('group-search', '')
    if request.user.role == 'student':
        groups = Group.objects.filter(student=request.user.student)
    else:
        groups = Group.objects.all().order_by('-id')
        
    context = {
        'groups': groups,
        'form': form
    }
    return render(request, 'group/list.html', context)


@login_required(login_url='user:login')
def details(request, pk):
    group = get_object_or_404(Group, id=pk)
    teachers = group.teacher_set.all()
    students = group.student_set.all()
    schedules = group.schedule_set.all()  # Расписание для выбранной группы
    subject_count = schedules.values('subject__name').annotate(total=Count('id'))
    days = Day.objects.all()  # Все дни недели

    context = {
        'group': group,
        'teachers': teachers,
        'students': students,
        'schedules': schedules,
        'days': days,
        'subject_count': subject_count
    }
    return render(request, 'group/details.html', context)


@login_required(login_url='user:login')
@is_admin
def update(request, pk):
    if request.user.role == 'student' or request.user.role == 'teacher':
        return redirect('schedule:list')
    group = Group.objects.get(id=pk)
    form = GroupForm(instance=group)
    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group)
        if form.is_valid():
            form.save()
            return redirect('group:details', pk=pk)
    context = {
        'group': group,
        'form': form
    }
    return render(request, 'group/update.html', context)


@login_required(login_url='user:login')
@is_admin
def delete(request, pk):
    group = Group.objects.get(id=pk)
    group.delete()
    return redirect('group:list')