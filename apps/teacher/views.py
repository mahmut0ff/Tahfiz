from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import datetime
from apps.teacher.utils import generate_code
from .models import *
from .forms import *
from django.contrib import messages
from apps.user.utils import generate_password, is_admin, is_teacher
from django.db.models import Q

@is_admin
def create(request):
    form = TeacherForm()

    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES)
        if form.is_valid():
            password = generate_password()
            user = User.objects.create_user(username=password, password=password, role='teacher')
            form.instance.user = user
            form.save()
            messages.success(request, 'Учитель создан')
            return redirect('teacher:list')
        else:
            messages.error(request, 'Учитель не создан')


    context = {
        'form': form
    }
    return render(request, 'teacher/create.html', context)

@login_required(login_url='user:login')
@is_admin
def list(request):
    teachers = Teacher.objects.all().order_by('-id')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        teachers = teachers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Фильтр по предмету
    subject_filter = request.GET.get('subject', '')
    if subject_filter:
        teachers = teachers.filter(subjects__id=subject_filter)
    
    # Получаем данные для фильтров
    from apps.schedule.models import Subject
    subjects = Subject.objects.all()

    context = {
        'teachers': teachers,
        'subjects': subjects,
        'search_query': search_query,
        'subject_filter': subject_filter,
    }
    return render(request, 'teacher/list.html', context)


# Профиль учителя
@login_required(login_url='user:login')
@is_admin
def details(request, pk):

    teacher = get_object_or_404(Teacher, id=pk)
    form = TeacherForm(instance=teacher)
    if request.method == 'POST':
        form = TeacherForm(request.POST, request.FILES, instance=teacher)
        if form.is_valid():
            form.save()
            return redirect('teacher:details', pk=pk)

    context = {'teacher': teacher, 'form': form}
    return render(request, 'teacher/details.html', context)


# Ученики учителя
@login_required(login_url='user:login')
@is_teacher
def students(request):

    teacher = get_object_or_404(Teacher, user=request.user)
    groups = Group.objects.filter(teacher=teacher)
    students = Student.objects.filter(group__in=groups)

    context = {'students': students, 'teacher': teacher}
    return render(request, 'teacher/students.html', context)


# Список отчетов учителя
@login_required(login_url='user:login')
def report_list(request):
    report_list = TeacherReport.objects.all().order_by('-id')
    form = TeacherReportForm()

    try:
        teacher = Teacher.objects.get(user_id=request.user.id)
        groups = teacher.group
        if request.method == 'POST':
            form = TeacherReportForm(request.POST)
            if form.is_valid():
                group_id = request.POST.get('group_id')
                group = Group.objects.get(id=group_id)
                form.instance.teacher = teacher
                form.instance.group = group
                form.save()
                return redirect('teacher:reports')
    except Teacher.DoesNotExist:
        form = None
        groups = []

    context = {'report_list': report_list, 'groups': groups, 'form': form}
    return render(request, 'teacher/report_list.html', context)


def delete(request, pk):
    teacher = get_object_or_404(Teacher, id=pk)
    user = User.objects.get(teacher=teacher)
    teacher.delete()
    user.delete()
    return redirect('teacher:list')


@login_required(login_url='user:login')
@is_admin
def generated_code(request):
    generate_code()
    code = Code.objects.latest('created_at')
    return render(request, 'teacher/generated_code.html', {'code': code.value})

@login_required(login_url='user:login')
@is_teacher
def code(request):
    form = TeacherCodeForm()
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    if request.method == 'POST':
        form = TeacherCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data.get('code')
            generated_code = Code.objects.latest('created_at')
            if code == generated_code.value:
                teacher = Teacher.objects.get(user=request.user)
                Attendance.objects.create(teacher=teacher)
                messages.success(request, 'Код подтвержден')
                return redirect('teacher:code')
            else:
                messages.error(request, 'Код не подтвержден')
                return redirect('teacher:code')
    
    context = {
        'form': form,
        'today': Attendance.objects.filter(
            Q(date__month=current_month) & Q(date__year=current_year) & Q(date__day=current_day) & Q(teacher__user__id=request.user.id)).exists()
            
        }
    return render(request, 'teacher/code.html', context)


@login_required(login_url='user:login')
@is_admin
def attendance_list(request):
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day
    date = request.GET.get('date', '')

    if date:
        current_year = date.split('-')[0]
        current_month = date.split('-')[1]
        current_day = date.split('-')[2]
    
    attendance_list = Attendance.objects.filter(
        Q(date__month=current_month) & Q(date__year=current_year) & Q(date__day=current_day)
    ).order_by('-id')
    context = {
        'attendance_list': attendance_list,
        'current_month': current_month,
        'current_year': current_year,
        'current_day': current_day,
    }
    return render(request, 'teacher/attendance_list.html', context)