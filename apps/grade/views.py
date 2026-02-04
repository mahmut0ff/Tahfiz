from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Prefetch, Count
from django.db import transaction
from django.http import JsonResponse
from datetime import datetime, date, timedelta
from collections import defaultdict
from .models import Grade
from .forms import GradeForm
from apps.group.models import Group
from apps.schedule.models import Subject
from apps.student.models import Student
from apps.teacher.models import Teacher


@login_required
def group_list(request):
    """Список групп для журнала"""
    groups = Group.objects.select_related('course').annotate(
        student_count=Count('student', filter=Q(student__student_status='active'))
    ).order_by('title')

    if request.user.role == 'teacher':
        teacher = get_object_or_404(Teacher, user=request.user)
        groups = groups.filter(teacher=teacher)
    
    context = {
        'groups': groups
    }
    return render(request, 'grade/group_list.html', context)


@login_required
def subject_list(request, pk):
    """Список предметов для группы"""
    group = get_object_or_404(Group, id=pk)
    
    # Получаем предметы, которые есть в расписании для этой группы
    subjects = Subject.objects.filter(
        schedule__group=group
    ).distinct().annotate(
        grade_count=Count('grade', filter=Q(grade__student__group=group))
    ).order_by('name')
    
    context = {
        'subjects': subjects,
        'group': group
    }
    return render(request, 'grade/subject_list.html', context)


@login_required
def grade_list(request, group_pk, subject_pk):
    """Журнал оценок для группы и предмета"""
    group = get_object_or_404(Group, id=group_pk)
    subject = get_object_or_404(Subject, id=subject_pk)
    
    # Получаем дату из параметров
    date_param = request.GET.get('month')
    if date_param:
        try:
            year, month = map(int, date_param.split('-'))
        except (ValueError, AttributeError):
            today = datetime.now()
            year, month = today.year, today.month
    else:
        today = datetime.now()
        year, month = today.year, today.month
    
    date_filter = f'{year}-{month:02}'
    current_date = date.today()  # Определяем current_date в начале функции
    
    # Обработка AJAX запроса для добавления оценки
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if request.user.role != 'teacher':
            return JsonResponse({'success': False, 'error': 'Недостаточно прав'})
        
        teacher = get_object_or_404(Teacher, user=request.user)
        
        try:
            with transaction.atomic():
                mark = float(request.POST.get('mark'))
                pages = int(request.POST.get('pages', 0))
                student_id = int(request.POST.get('student_id'))
                grade_date = request.POST.get('date')
                
                # Валидация оценки
                if not (1 <= mark <= 5):
                    return JsonResponse({'success': False, 'error': 'Оценка должна быть от 1 до 5'})
                
                student = get_object_or_404(Student, id=student_id)
                
                # Проверяем, что студент в этой группе
                if not student.group.filter(id=group.id).exists():
                    return JsonResponse({'success': False, 'error': 'Студент не принадлежит к этой группе'})
                
                # Проверяем дату (не более 3 дней от текущей даты)
                grade_date_obj = datetime.strptime(grade_date, '%Y-%m-%d').date()
                if abs((grade_date_obj - current_date).days) > 3:
                    return JsonResponse({'success': False, 'error': 'Дата должна быть в пределах 3 дней от сегодня'})
                
                grade = Grade.objects.create(
                    teacher=teacher,
                    student=student,
                    mark=mark,
                    subject=subject,
                    date=grade_date_obj,
                    pages=pages
                )
                
                return JsonResponse({
                    'success': True, 
                    'message': f'Оценка {mark} добавлена для {student.name}',
                    'grade_id': grade.id
                })
                
        except (ValueError, TypeError) as e:
            return JsonResponse({'success': False, 'error': 'Неверный формат данных'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': f'Произошла ошибка: {str(e)}'})
    
    # Обработка обычного POST запроса
    elif request.method == 'POST' and request.user.role == 'teacher':
        teacher = get_object_or_404(Teacher, user=request.user)
        
        try:
            with transaction.atomic():
                mark = float(request.POST.get('mark'))
                pages = int(request.POST.get('pages', 0))
                student_id = int(request.POST.get('student_id'))
                grade_date = request.POST.get('date')
                
                student = get_object_or_404(Student, id=student_id)
                
                # Проверяем, что студент в этой группе
                if not student.group.filter(id=group.id).exists():
                    messages.error(request, 'Студент не принадлежит к этой группе.')
                    return redirect('grade:list', group_pk=group_pk, subject_pk=subject_pk)
                
                Grade.objects.create(
                    teacher=teacher,
                    student=student,
                    mark=mark,
                    subject=subject,
                    date=grade_date,
                    pages=pages
                )
                messages.success(request, f'Оценка {mark} добавлена для {student.name}')
                
        except (ValueError, TypeError) as e:
            messages.error(request, 'Ошибка при добавлении оценки. Проверьте введенные данные.')
        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')
    
    # Оптимизированный запрос студентов с предзагрузкой оценок
    students = Student.objects.filter(
        group=group,
        student_status='active'
    ).select_related('user').prefetch_related(
        Prefetch(
            'grade_set',
            queryset=Grade.objects.filter(
                subject=subject,
                date__year=year,
                date__month=month
            ).select_related('teacher__user').order_by('date'),
            to_attr='monthly_grades'
        )
    ).order_by('name')
    
    # Фильтрация для преподавателей
    if request.user.role == 'teacher':
        teacher = get_object_or_404(Teacher, user=request.user)
        students = students.filter(group__teacher=teacher)
    
    # Получаем все уникальные даты за месяц
    dates_qs = Grade.objects.filter(
        subject=subject,
        date__year=year,
        date__month=month,
        student__in=students
    ).values_list('date', flat=True).distinct().order_by('date')
    
    sorted_dates = list(dates_qs)
    
    # Создаем структуру данных для таблицы
    grade_matrix = {}
    student_averages = {}
    total_grades = 0
    total_sum = 0
    
    for student in students:
        grade_matrix[student.id] = {}
        student_grades = []
        
        for grade in student.monthly_grades:
            if grade.date not in grade_matrix[student.id]:
                grade_matrix[student.id][grade.date] = []
            grade_matrix[student.id][grade.date].append(grade)
            student_grades.append(grade.mark)
            total_grades += 1
            total_sum += grade.mark
        
        # Вычисляем средний балл студента
        if student_grades:
            student_averages[student.id] = round(sum(student_grades) / len(student_grades), 2)
        else:
            student_averages[student.id] = 0
    
    # Общая статистика
    class_average = round(total_sum / total_grades, 2) if total_grades > 0 else 0
    best_average = max(student_averages.values()) if student_averages.values() else 0
    
    # Сортируем студентов по средней оценке (по убыванию)
    students = sorted(students, key=lambda s: student_averages[s.id], reverse=True)
    
    # Создаем удобную структуру для шаблона
    students_data = []
    for student in students:
        student_data = {
            'student': student,
            'average': student_averages[student.id],
            'grades_by_date': {}
        }
        
        for grade_date in sorted_dates:
            if grade_date in grade_matrix[student.id]:
                student_data['grades_by_date'][grade_date] = grade_matrix[student.id][grade_date]
            else:
                student_data['grades_by_date'][grade_date] = []
        
        students_data.append(student_data)
    
    context = {
        'students_data': students_data,
        'subject': subject,
        'group': group,
        'dates': sorted_dates,
        'date_filter': date_filter,
        'current_month': f'{year}-{month:02}',
        'can_edit': request.user.role == 'teacher',
        'class_average': class_average,
        'best_average': best_average,
        'total_grades': total_grades,
        'today': current_date,
    }
    
    return render(request, 'grade/list.html', context)


@login_required
def diary(request):
    """Дневник студента"""
    if request.user.role != 'student':
        messages.error(request, 'Доступ только для студентов.')
        return redirect('dashboard:dashboard')
    
    student = get_object_or_404(Student, user=request.user)
    
    # Получаем дату из параметров
    date_param = request.GET.get('month')
    if date_param:
        try:
            year, month = map(int, date_param.split('-'))
        except (ValueError, AttributeError):
            today = datetime.now()
            year, month = today.year, today.month
    else:
        today = datetime.now()
        year, month = today.year, today.month
    
    date_filter = f'{year}-{month:02}'
    
    # Получаем предметы студента
    subjects = Subject.objects.filter(
        schedule__group__in=student.group.all()
    ).distinct().order_by('name')
    
    # Получаем оценки за месяц с предзагрузкой
    grades_qs = Grade.objects.filter(
        student=student,
        date__year=year,
        date__month=month
    ).select_related('subject', 'teacher').order_by('date')
    
    # Группируем оценки по предметам и датам
    grades_by_subject_date = defaultdict(lambda: defaultdict(list))
    all_dates = set()
    
    for grade in grades_qs:
        grades_by_subject_date[grade.subject.id][grade.date].append(grade)
        all_dates.add(grade.date)
    
    # Сортируем даты
    sorted_dates = sorted(all_dates)
    
    # Вычисляем средние оценки по предметам
    subject_averages = {}
    for subject in subjects:
        subject_grades = [g.mark for g in grades_qs if g.subject_id == subject.id]
        if subject_grades:
            subject_averages[subject.id] = round(sum(subject_grades) / len(subject_grades), 2)
        else:
            subject_averages[subject.id] = 0
    
    context = {
        'student': student,
        'subjects': subjects,
        'dates': sorted_dates,
        'date_filter': date_filter,
        'grades_by_subject_date': dict(grades_by_subject_date),
        'subject_averages': subject_averages,
    }
    
    return render(request, 'grade/diary.html', context)


@login_required
def delete(request, group_pk, subject_pk, pk):
    """Удаление оценки (AJAX)"""
    if request.user.role != 'teacher':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Недостаточно прав'})
        messages.error(request, 'Недостаточно прав для удаления оценки.')
        return redirect('grade:list', group_pk=group_pk, subject_pk=subject_pk)
    
    grade = get_object_or_404(Grade, id=pk)
    teacher = get_object_or_404(Teacher, user=request.user)
    
    # Проверяем, что преподаватель может удалить эту оценку
    if grade.teacher != teacher:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Вы можете удалять только свои оценки'})
        messages.error(request, 'Вы можете удалять только свои оценки.')
        return redirect('grade:list', group_pk=group_pk, subject_pk=subject_pk)
    
    student_name = grade.student.name
    mark = grade.mark
    grade.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': f'Оценка {mark} для {student_name} удалена'})
    
    messages.success(request, f'Оценка {mark} для {student_name} удалена.')
    return redirect('grade:list', group_pk=group_pk, subject_pk=subject_pk)
