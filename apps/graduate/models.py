from django.db import models
from apps.user.models import User
from apps.student.models import Student
from apps.group.models import Group


class Graduate(models.Model):
    """Модель выпускника - дополнительная информация о студенте после выпуска"""
    
    student = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE, 
        verbose_name="Студент",
        related_name="graduate_info"
    )
    graduation_date = models.DateField(
        verbose_name="Дата выпуска"
    )
    graduation_group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Группа выпуска"
    )
    final_grade = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        verbose_name="Итоговая оценка"
    )
    diploma_number = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Номер диплома"
    )
    achievements = models.TextField(
        blank=True,
        verbose_name="Достижения"
    )
    current_occupation = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Текущая деятельность"
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="Контактный телефон"
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name="Email"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Примечания"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания записи"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Дата обновления"
    )

    class Meta:
        verbose_name = "Выпускник"
        verbose_name_plural = "Выпускники"
        ordering = ['-graduation_date']

    def __str__(self):
        return f"{self.student.name} - {self.graduation_date.year}"

    @property
    def full_name(self):
        return self.student.name

    @property
    def graduation_year(self):
        return self.graduation_date.year


class GraduateAchievement(models.Model):
    """Достижения выпускника после окончания"""
    
    graduate = models.ForeignKey(
        Graduate,
        on_delete=models.CASCADE,
        related_name="post_graduation_achievements",
        verbose_name="Выпускник"
    )
    title = models.CharField(
        max_length=200,
        verbose_name="Название достижения"
    )
    description = models.TextField(
        blank=True,
        verbose_name="Описание"
    )
    date_achieved = models.DateField(
        verbose_name="Дата достижения"
    )
    category = models.CharField(
        max_length=50,
        choices=[
            ('education', 'Образование'),
            ('career', 'Карьера'),
            ('religious', 'Религиозная деятельность'),
            ('social', 'Общественная деятельность'),
            ('other', 'Другое'),
        ],
        default='other',
        verbose_name="Категория"
    )

    class Meta:
        verbose_name = "Достижение выпускника"
        verbose_name_plural = "Достижения выпускников"
        ordering = ['-date_achieved']

    def __str__(self):
        return f"{self.graduate.full_name} - {self.title}"