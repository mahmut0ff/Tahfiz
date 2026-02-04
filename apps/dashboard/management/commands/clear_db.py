from django.core.management.base import BaseCommand
from django.db import transaction

from apps.user.models import User
from apps.dashboard.models import Course
from apps.group.models import Group
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.administrator.models import Administrator
from apps.schedule.models import Day, Subject, Schedule
from apps.grade.models import Grade
from apps.graduate.models import Graduate, GraduateAchievement


class Command(BaseCommand):
    help = 'Очищает базу данных от тестовых данных'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Подтверждение очистки без интерактивного запроса'
        )
        parser.add_argument(
            '--keep-superusers',
            action='store_true',
            help='Сохранить суперпользователей'
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            confirm = input('⚠️  Вы уверены, что хотите очистить базу данных? (yes/no): ')
            if confirm.lower() not in ['yes', 'y', 'да']:
                self.stdout.write('❌ Операция отменена')
                return

        with transaction.atomic():
            self.stdout.write('🗑️  Очистка базы данных...')
            
            # Порядок важен из-за внешних ключей
            models_to_clear = [
                (Grade, 'оценок'),
                (GraduateAchievement, 'достижений выпускников'),
                (Graduate, 'выпускников'),
                (Schedule, 'записей расписания'),
                (Student, 'студентов'),
                (Teacher, 'преподавателей'),
                (Administrator, 'администраторов'),
                (Subject, 'предметов'),
                (Day, 'дней недели'),
                (Group, 'групп'),
                (Course, 'курсов'),
            ]
            
            total_deleted = 0
            
            for model, description in models_to_clear:
                count = model.objects.count()
                if count > 0:
                    model.objects.all().delete()
                    total_deleted += count
                    self.stdout.write(f'   ✅ Удалено {count} {description}')
            
            # Удаление пользователей
            if options['keep_superusers']:
                users_query = User.objects.filter(is_superuser=False)
                user_type = 'обычных пользователей'
            else:
                users_query = User.objects.all()
                user_type = 'пользователей'
            
            users_count = users_query.count()
            if users_count > 0:
                users_query.delete()
                total_deleted += users_count
                self.stdout.write(f'   ✅ Удалено {users_count} {user_type}')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'🎉 База данных очищена!\n'
                    f'   Всего удалено записей: {total_deleted}'
                )
            )
            
            if not options['keep_superusers']:
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  Все пользователи удалены. Создайте нового суперпользователя:\n'
                        '   python manage.py create_superuser'
                    )
                )