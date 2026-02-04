from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from collections import defaultdict
from django.contrib import messages
from apps.user.utils import is_admin
from django.db.models import Count
from datetime import datetime


def create_schedule(group_id, day_id, subject_id):
    day = Day.objects.get(id=day_id)
    group = Group.objects.get(id=group_id)
    subject = Subject.objects.get(id=subject_id)
    return Schedule.objects.create(group=group, day=day, subject=subject)


@login_required(login_url='user:login')
def schedule(request):
    schedules = Schedule.objects.select_related("group", "day", "subject").all()
    groups = Group.objects.prefetch_related("schedule_set__subject", "schedule_set__day").all()
    
    # Get days with schedule counts
    days = Day.objects.annotate(
        schedule_count=Count('schedule')
    ).all()
    
    subjects = Subject.objects.all()
    
    # Get current day name in Russian
    current_day_mapping = {
        0: 'Понедельник',
        1: 'Вторник', 
        2: 'Среда',
        3: 'Четверг',
        4: 'Пятница',
        5: 'Суббота',
        6: 'Воскресенье'
    }
    current_day = current_day_mapping.get(datetime.now().weekday(), '')

    if request.method == 'POST' and 'lesson' in request.POST:
        group = request.POST.get('group')
        day = request.POST.get('day')
        subject = request.POST.get('subject')
        try:
            create_schedule(group_id=group, day_id=day, subject_id=subject)
            messages.success(request, 'Занятие успешно добавлено в расписание!')
        except Exception as e:
            messages.error(request, f'Ошибка при добавлении занятия: {str(e)}')
        return redirect('schedule:list')
    
    context = {
        'schedules': schedules,
        'groups': groups,
        'days': days,
        'subjects': subjects,
        'current_day': current_day
    }
    return render(request, 'schedule/list.html', context)


@login_required(login_url='user:login')
def calendar_view(request):
    schedules = Schedule.objects.select_related("group", "day", "subject").all()
    groups = Group.objects.all()
    days = Day.objects.all()
    subjects = Subject.objects.all()
    
    context = {
        'schedules': schedules,
        'groups': groups,
        'days': days,
        'subjects': subjects
    }
    return render(request, 'schedule/calendar_simple.html', context)


@is_admin
def delete(request, pk):
    schedule = Schedule.objects.get(id=pk)
    schedule.delete()
    return redirect('schedule:list')


@login_required(login_url='user:login')
@is_admin
def subject_create(request):
    if request.user.role == 'student' or request.user.role == 'teacher':
        return redirect('schedule:list')
    subjects = Subject.objects.all()
    form = SubjectForm()
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('schedule:subject_create')
    context = {
        'form': form,
        'subjects': subjects
    }
    return render(request, 'schedule/subject_create.html', context)