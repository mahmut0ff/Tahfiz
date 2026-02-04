from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date
from apps.student.models import Student
from apps.group.models import Group
from apps.dashboard.models import Course
from .models import Graduate, GraduateAchievement


class GraduateModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            first_name='Тест',
            last_name='Пользователь'
        )
        self.course = Course.objects.create(name='Тестовый курс')
        self.group = Group.objects.create(name='Тестовая группа', course=self.course)
        self.student = Student.objects.create(
            user=self.user,
            name='Тест Пользователь',
            course=self.course
        )
        self.student.group.add(self.group)

    def test_graduate_creation(self):
        graduate = Graduate.objects.create(
            student=self.student,
            graduation_date=date.today(),
            graduation_group=self.group,
            final_grade=4.5,
            diploma_number='DIP-2024-001'
        )
        
        self.assertEqual(graduate.student, self.student)
        self.assertEqual(graduate.full_name, 'Тест Пользователь')
        self.assertEqual(graduate.graduation_year, date.today().year)
        self.assertTrue(str(graduate).startswith('Тест Пользователь'))

    def test_graduate_achievement_creation(self):
        graduate = Graduate.objects.create(
            student=self.student,
            graduation_date=date.today(),
            graduation_group=self.group
        )
        
        achievement = GraduateAchievement.objects.create(
            graduate=graduate,
            title='Поступление в университет',
            description='Поступил в КНУ им. Баласагына',
            date_achieved=date.today(),
            category='education'
        )
        
        self.assertEqual(achievement.graduate, graduate)
        self.assertEqual(achievement.title, 'Поступление в университет')
        self.assertEqual(achievement.category, 'education')


class GraduateViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='admin',
            password='testpass123'
        )
        self.client.login(username='admin', password='testpass123')
        
        self.student_user = User.objects.create_user(
            username='student',
            first_name='Студент',
            last_name='Тестовый'
        )
        self.course = Course.objects.create(name='Тестовый курс')
        self.group = Group.objects.create(name='Тестовая группа', course=self.course)
        self.student = Student.objects.create(
            user=self.student_user,
            name='Студент Тестовый',
            course=self.course
        )

    def test_graduate_list_view(self):
        response = self.client.get(reverse('graduate:list'))
        self.assertEqual(response.status_code, 200)

    def test_graduate_create_view(self):
        response = self.client.get(reverse('graduate:create'))
        self.assertEqual(response.status_code, 200)
        
        # Тест создания выпускника
        data = {
            'student': self.student.id,
            'graduation_date': date.today(),
            'graduation_group': self.group.id,
            'final_grade': 4.0,
            'diploma_number': 'TEST-001'
        }
        response = self.client.post(reverse('graduate:create'), data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful creation
        
        # Проверяем, что выпускник создан
        self.assertTrue(Graduate.objects.filter(student=self.student).exists())
        
        # Проверяем, что статус студента изменился
        self.student.refresh_from_db()
        self.assertEqual(self.student.student_status, 'graduated')