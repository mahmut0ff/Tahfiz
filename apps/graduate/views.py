from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Graduate, GraduateAchievement
from .forms import GraduateForm, GraduateAchievementForm, MakeGraduateForm
from apps.student.models import Student


@login_required
def graduate_list(request):
    """Список выпускников"""
    graduates = Graduate.objects.select_related('student__user', 'graduation_group').all()
    
    # Поиск
    search_query = request.GET.get('search', '')
    if search_query:
        graduates = graduates.filter(
            Q(student__name__icontains=search_query) |
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(diploma_number__icontains=search_query)
        )
    
    # Фильтр по году выпуска
    year_filter = request.GET.get('year', '')
    if year_filter:
        graduates = graduates.filter(graduation_date__year=year_filter)
    
    # Фильтр по группе
    group_filter = request.GET.get('group', '')
    if group_filter:
        graduates = graduates.filter(graduation_group_id=group_filter)
    
    # Пагинация
    paginator = Paginator(graduates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем годы для фильтра
    years = Graduate.objects.values_list('graduation_date__year', flat=True).distinct().order_by('-graduation_date__year')
    
    # Получаем группы для фильтра
    from apps.group.models import Group
    groups = Group.objects.all()
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'year_filter': year_filter,
        'group_filter': group_filter,
        'years': years,
        'groups': groups,
    }
    return render(request, 'graduate/list.html', context)


@login_required
def graduate_detail(request, pk):
    """Детальная информация о выпускнике"""
    graduate = get_object_or_404(Graduate, pk=pk)
    achievements = graduate.post_graduation_achievements.all().order_by('-date_achieved')
    
    context = {
        'graduate': graduate,
        'achievements': achievements,
    }
    return render(request, 'graduate/detail.html', context)


@login_required
def graduate_create(request):
    """Создание записи о выпускнике"""
    if request.method == 'POST':
        form = GraduateForm(request.POST)
        if form.is_valid():
            graduate = form.save()
            # Обновляем статус студента
            graduate.student.student_status = 'graduated'
            graduate.student.save()
            messages.success(request, f'Выпускник {graduate.full_name} успешно добавлен.')
            return redirect('graduate:detail', pk=graduate.pk)
    else:
        form = GraduateForm()
    
    return render(request, 'graduate/create.html', {'form': form})


@login_required
def graduate_update(request, pk):
    """Редактирование информации о выпускнике"""
    graduate = get_object_or_404(Graduate, pk=pk)
    
    if request.method == 'POST':
        form = GraduateForm(request.POST, instance=graduate)
        if form.is_valid():
            form.save()
            messages.success(request, f'Информация о выпускнике {graduate.full_name} обновлена.')
            return redirect('graduate:detail', pk=graduate.pk)
    else:
        form = GraduateForm(instance=graduate)
    
    return render(request, 'graduate/update.html', {'form': form, 'graduate': graduate})


@login_required
def graduate_delete(request, pk):
    """Удаление записи о выпускнике"""
    graduate = get_object_or_404(Graduate, pk=pk)
    
    if request.method == 'POST':
        student = graduate.student
        student.student_status = 'active'  # Возвращаем статус активного студента
        student.save()
        graduate.delete()
        messages.success(request, f'Запись о выпускнике {graduate.full_name} удалена.')
        return redirect('graduate:list')
    
    return render(request, 'graduate/delete.html', {'graduate': graduate})


@login_required
def achievement_create(request, graduate_pk):
    """Добавление достижения выпускника"""
    graduate = get_object_or_404(Graduate, pk=graduate_pk)
    
    if request.method == 'POST':
        form = GraduateAchievementForm(request.POST)
        if form.is_valid():
            achievement = form.save(commit=False)
            achievement.graduate = graduate
            achievement.save()
            messages.success(request, 'Достижение добавлено.')
            return redirect('graduate:detail', pk=graduate.pk)
    else:
        form = GraduateAchievementForm()
    
    return render(request, 'graduate/achievement_create.html', {
        'form': form, 
        'graduate': graduate
    })


@login_required
def achievement_delete(request, pk):
    """Удаление достижения выпускника"""
    achievement = get_object_or_404(GraduateAchievement, pk=pk)
    graduate = achievement.graduate
    
    if request.method == 'POST':
        achievement.delete()
        messages.success(request, 'Достижение удалено.')
        return redirect('graduate:detail', pk=graduate.pk)
    
    return render(request, 'graduate/achievement_delete.html', {
        'achievement': achievement,
        'graduate': graduate
    })


@login_required
def make_graduate(request, student_pk):
    """Перевод студента в выпускники"""
    student = get_object_or_404(Student, pk=student_pk)
    
    # Проверяем, не является ли уже выпускником
    if hasattr(student, 'graduate_info'):
        messages.warning(request, f'{student.name} уже является выпускником.')
        return redirect('student:details', pk=student.pk)
    
    if request.method == 'POST':
        form = MakeGraduateForm(request.POST)
        
        if form.is_valid():
            try:
                graduate = form.save(commit=False)
                graduate.student = student
                graduate.save()
                
                # Обновляем статус студента
                student.student_status = 'graduated'
                student.save()
                
                messages.success(request, f'{student.name} переведен в выпускники.')
                return redirect('graduate:detail', pk=graduate.pk)
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            # Добавляем ошибки формы в сообщения
            if form.errors:
                for field, errors in form.errors.items():
                    field_label = form.fields.get(field, {}).label or field
                    for error in errors:
                        messages.error(request, f'Ошибка в поле "{field_label}": {error}')
            
            if form.non_field_errors():
                for error in form.non_field_errors():
                    messages.error(request, f'Ошибка: {error}')
    else:
        # Предзаполняем форму данными студента
        initial_data = {
            'graduation_group': student.group.first() if student.group.exists() else None,
            'contact_phone': student.phone,
        }
        form = MakeGraduateForm(initial=initial_data)
    
    return render(request, 'graduate/make_graduate.html', {
        'form': form,
        'student': student
    })