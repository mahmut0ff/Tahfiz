from django.db import models
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.schedule.models import Subject

import datetime
from django.core.exceptions import ValidationError


class Grade(models.Model):
    """Оценка студента"""

    student = models.ForeignKey(
        Student,
        verbose_name="Студент",
        on_delete=models.SET_NULL,
        null=True
    )

    mark = models.FloatField(verbose_name="Оценка")
    pages = models.FloatField(verbose_name="Страницы", null=True)
    subject = models.ForeignKey(
        Subject,
        verbose_name="Предмет",
        on_delete=models.SET_NULL,
        null=True
    )
    teacher = models.ForeignKey(
        Teacher,
        verbose_name="Преподаватель",
        on_delete=models.SET_NULL,
        null=True
    )

    date = models.DateField(verbose_name="День")

    class Meta:
        verbose_name = 'Оценка'
        verbose_name_plural = 'Оценки'

    def __str__(self):
        return f"{self.student} - {self.mark}"

    def clean(self):
        """Валидация даты: только вчера, сегодня, завтра (+/-3 дня от текущей даты)"""
        today = datetime.date.today()
        min_date = today - datetime.timedelta(days=2)  # позавчера
        max_date = today + datetime.timedelta(days=2)  # послезавтра

        if not (min_date <= self.date <= max_date):
            self.date = today

    def save(self, *args, **kwargs):
        self.full_clean()  # запускаем clean() перед сохранением
        super().save(*args, **kwargs)
