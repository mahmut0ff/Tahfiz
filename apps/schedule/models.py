from django.db import models
from apps.group.models import Group


class Day(models.Model):
    """День недели"""

    title = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'День'
        verbose_name_plural = 'Дни'
        ordering = ['order']

    def __str__(self):
        return self.title


class Subject(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

    def __str__(self):
        return self.name


class Schedule(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    day = models.ForeignKey(Day, on_delete=models.CASCADE)
    time_slot = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Таблица расписания'
        verbose_name_plural = 'Таблица расписания'

    def __str__(self):
        return f"{self.group} - {self.day} - {self.time_slot} - {self.subject}"