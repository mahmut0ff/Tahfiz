from django.db import models
from apps.user.models import User
from apps.group.models import Group
from django.db.models import Q, Avg
from apps.schedule.models import *
from apps.dashboard.models import Course
from datetime import datetime

class Student(models.Model):
    """Студент"""
    STUDENT_STATUS_CHOICES = [
        ('active', 'Активный'),
        ('inactive', 'Неактивный'),
        ('graduated', 'Выпускник'),
        ('expelled', 'Отчислен'),
    ]
    
    image = models.ImageField(upload_to='student/', null=True)
    to_pay = models.IntegerField(null=True)
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        null=True)
    name = models.CharField(max_length=150)
    status = models.BooleanField(default=True)  # Оставляем для обратной совместимости
    student_status = models.CharField(
        max_length=20,
        choices=STUDENT_STATUS_CHOICES,
        default='active',
        verbose_name='Статус студента'
    )
    phone = models.CharField(max_length=12, default='996')
    group = models.ManyToManyField(Group)
    course = models.ForeignKey(Course, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


    def __str__(self):
        return self.name
    
    @property
    def is_graduated(self):
        """Проверяет, является ли студент выпускником"""
        return self.student_status == 'graduated'
    
    @property
    def show_grade(self):
        data_list = [''] * 31
        marks = self.mark_set.filter(day__month = datetime.now().month)
        for i in marks:
            data_list[i.day.day-1] = i.mark
        return data_list