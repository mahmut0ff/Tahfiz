from django.core.management.base import BaseCommand
from apps.dashboard.models import Course
from apps.group.models import Group
from apps.schedule.models import Day, Subject


class Command(BaseCommand):
    help = 'Тестирует модели на правильность полей'

    def handle(self, *args, **options):
        self.stdout.write('🔍 Тестирование моделей...')
        
        try:
            # Тест Course
            course = Course.objects.create(title='Тест курс')
            self.stdout.write(f'✅ Course создан: {course}')
            
            # Тест Group
            group = Group.objects.create(title='Тест группа', course=course)
            self.stdout.write(f'✅ Group создан: {group}')
            
            # Тест Day
            day = Day.objects.create(title='Понедельник')
            self.stdout.write(f'✅ Day создан: {day}')
            
            # Тест Subject
            subject = Subject.objects.create(name='Тест предмет')
            self.stdout.write(f'✅ Subject создан: {subject}')
            
            # Очистка тестовых данных
            course.delete()
            group.delete()
            day.delete()
            subject.delete()
            
            self.stdout.write(self.style.SUCCESS('🎉 Все модели работают корректно!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Ошибка: {e}'))