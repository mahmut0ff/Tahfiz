
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Avg, F, Count, Q
from django.db.models.functions import Round, Cast
from django.db.models import IntegerField
from django.contrib import messages
from datetime import datetime

from apps.dashboard.forms import *
from apps.dashboard.models import *
from .models import *
from .forms import *
from apps.teacher.models import *
from apps.group.models import *
from apps.user.utils import generate_password, is_admin
from apps.schedule.models import *


@login_required(login_url='user:login')
@is_admin
def create(request):

    form = StudentForm()
    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES)
        if form.is_valid():
            password = generate_password()
            user = User.objects.create_user(username=password, password=password, role='student')
            form.instance.user = user
            form.instance.status = True
            form.save()
            messages.success(request, 'Студент создан')
            return redirect('student:create')

    context = {
        'form': form
    }
    return render(request, 'student/create.html', context)


@login_required(login_url='user:login')
@is_admin
def list(request):
    students = Student.objects.all().order_by('-id')
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        students = students.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # Фильтр по курсу
    course_filter = request.GET.get('course', '')
    if course_filter:
        students = students.filter(course_id=course_filter)
    
    # Фильтр по статусу студента
    status_filter = request.GET.get('student_status', '')
    if status_filter:
        students = students.filter(student_status=status_filter)
    
    # Фильтр по статусу обучения
    learning_status = request.GET.get('learning_status', '')
    if learning_status:
        if learning_status == 'active':
            students = students.filter(status=True)
        elif learning_status == 'inactive':
            students = students.filter(status=False)
    
    # Получаем данные для фильтров
    from apps.dashboard.models import Course
    courses = Course.objects.all()
    
    context = {
        'students': students,
        'courses': courses,
        'search_query': search_query,
        'course_filter': course_filter,
        'status_filter': status_filter,
        'learning_status': learning_status,
    }
    return render(request, 'student/list.html', context)



@login_required(login_url='user:login')
@is_admin
def details(request, pk):
    student = get_object_or_404(Student, id=pk)
    form = StudentForm(instance=student)

    if request.method == 'POST':
        form = StudentForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            return redirect('student:details', pk=pk)

    context = {
        'student': student,
        'form': form,
        }
    
    return render(request, 'student/details.html', context)


@login_required(login_url='user:login')
@is_admin
def delete(request, pk):
    student = get_object_or_404(Student, id=pk)
    
    if request.method == 'POST':
        user = User.objects.get(student=student)
        student.delete()
        user.delete()
        messages.success(request, f'Студент {student.name} успешно удален')
        return redirect('student:list')
    
    context = {
        'student': student,
    }
    return render(request, 'student/delete.html', context)


def total_rating_list(request):
    """Общий рейтинг студентов"""
    month, year = datetime.now().month, datetime.now().year

    students = Student.objects.filter(
        student_status='active'
    ).annotate(
        total_marks=Sum('grade__mark', filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        total_pages=Sum('grade__pages', filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        weighted_score=Sum(F('grade__mark') * F('grade__pages'), filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        average_mark=Round(Avg('grade__mark', filter=Q(grade__date__month=month) & Q(grade__date__year=year)), 2),
        grade_count=Count('grade', filter=Q(grade__date__month=month) & Q(grade__date__year=year))
    ).filter(
        grade_count__gt=0  # Только студенты с оценками
    ).order_by('-weighted_score')

    # Добавляем информацию о месте в рейтинге
    for i, student in enumerate(students, 1):
        student.rank = i
        student.display_score = student.weighted_score or 0

    context = {
        'students': students,
        'current_month': month,
        'current_year': year,
    }
    return render(request, 'student/total_rating_list.html', context)



def choose_course_rating(request):
    courses = Course.objects.all()
    context = {
        'courses': courses,
    }
    return render(request, 'student/choose_course_rating.html', context)


def rating_by_course(request, pk):
    """Рейтинг студентов по курсу"""
    course = get_object_or_404(Course, id=pk)
    month, year = datetime.now().month, datetime.now().year

    students = Student.objects.filter(
        course=course,
        student_status='active'
    ).annotate(
        total_marks=Sum('grade__mark', filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        total_pages=Sum('grade__pages', filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        weighted_score=Sum(F('grade__mark') * F('grade__pages'), filter=Q(grade__date__month=month) & Q(grade__date__year=year)),
        average_mark=Round(Avg('grade__mark', filter=Q(grade__date__month=month) & Q(grade__date__year=year)), 2),
        grade_count=Count('grade', filter=Q(grade__date__month=month) & Q(grade__date__year=year))
    ).filter(
        grade_count__gt=0  # Только студенты с оценками
    ).order_by('-weighted_score')

    # Добавляем информацию о месте в рейтинге и медали
    for i, student in enumerate(students, 1):
        student.rank = i
        student.display_score = student.weighted_score or 0
        if i <= 3:
            student.medal_img = f"assets/img/medal-{i}.png"

    context = {
        'students': students,
        'course': course,
        'current_month': month,
        'current_year': year,
    }
    
    return render(request, 'student/rating_by_course.html', context)