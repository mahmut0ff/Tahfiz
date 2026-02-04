from django.db.models import Q
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from apps.user.models import *
from apps.user.forms import *
from apps.teacher.models import *
from apps.student.models import *
from apps.teacher.forms import *
from apps.student.forms import *
from .models import *
from .forms import *
from apps.user.utils import is_admin


@login_required(login_url='user:login')
@is_admin
def dashboard(request):
    from apps.student.models import Student
    from apps.teacher.models import Teacher
    from apps.group.models import Group
    from apps.graduate.models import Graduate
    from django.db.models import Sum
    
    # Статистика для dashboard
    total_students = Student.objects.count()
    total_teachers = Teacher.objects.count()
    total_groups = Group.objects.count()
    total_graduates = Graduate.objects.count()
    
    # Финансовая статистика
    expected_profit = Student.objects.aggregate(total=Sum('to_pay'))['total'] or 0
    transactions_amount = 0  # Здесь можно добавить логику для оплаченных сумм
    remainder = expected_profit - transactions_amount
    
    context = {
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_groups': total_groups,
        'total_graduates': total_graduates,
        'expected_profit': expected_profit,
        'transactions_amount': transactions_amount,
        'remainder': remainder,
    }
    
    return render(request, 'dashboard/dashboard.html', context)