from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from faker import Faker
import random
from datetime import date, timedelta

from apps.user.models import User
from apps.dashboard.models import Course
from apps.group.models import Group
from apps.student.models import Student
from apps.teacher.models import Teacher
from apps.administrator.models import Administrator
from apps.schedule.models import Day, Subject, Schedule
from apps.grade.models import Grade
from apps.graduate.models import Graduate, GraduateAchievement

fake = Faker('ru_RU')  # Русская локализация


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def add_arguments(self, parser):
        parser.add_argument(
            '--students',
            type=int,
            default=50,
            help='Количество студентов (по умолчанию: 50)'
        )
        parser.add_argument(
            '--teachers',
            type=int,
            default=10,
            help='Количество преподавателей (по умолчанию: 10)'
        )
        parser.add_argument(
            '--graduates',
            type=int,
            default=20,
            help='Количество выпускников (по умолчанию: 20)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие данные перед заполнением'
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('🗑️  Очистка существующих данных...')
            self.clear_data()

        with transaction.atomic():
            self.stdout.write('📚 Создание базовых данных...')
            self.create_base_data()
            
            self.stdout.write('👨‍🏫 Создание преподавателей...')
            teachers = self.create_teachers(options['teachers'])
            
            self.stdout.write('👨‍🎓 Создание студентов...')
            students = self.create_students(options['students'])
            
            self.stdout.write('📅 Создание расписания...')
            self.create_schedule(teachers)
            
            self.stdout.write('📊 Создание оценок...')
            self.create_grades(students, teachers)
            
            self.stdout.write('🎓 Создание выпускников...')
            self.create_graduates(options['graduates'])
            
            self.stdout.write('👤 Создание администраторов...')
            self.create_administrators()

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ База данных успешно заполнена!\n'
                f'   Студентов: {options["students"]}\n'
                f'   Преподавателей: {options["teachers"]}\n'
                f'   Выпускников: {options["graduates"]}'
            )
        )

    def clear_data(self):
        """Очистка существующих данных"""
        models_to_clear = [
            Grade, GraduateAchievement, Graduate, Schedule, 
            Student, Teacher, Administrator, Subject, Day, 
            Group, Course
        ]
        
        for model in models_to_clear:
            count = model.objects.count()
            if count > 0:
                model.objects.all().delete()
                self.stdout.write(f'   Удалено {count} записей из {model.__name__}')
        
        # Удаление пользователей (кроме суперпользователей)
        users_count = User.objects.filter(is_superuser=False).count()
        if users_count > 0:
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(f'   Удалено {users_count} пользователей')

    def create_base_data(self):
        """Создание базовых данных: курсы, группы, дни недели, предметы"""
        
        # Курсы
        courses_data = [
            'Основы Ислама',
            'Коран и Хадисы', 
            'Арабский язык',
            'Исламская история',
            'Фикх (Исламское право)'
        ]
        
        courses = []
        for course_name in courses_data:
            course, created = Course.objects.get_or_create(title=course_name)
            courses.append(course)
            if created:
                self.stdout.write(f'   Создан курс: {course_name}')

        # Группы
        group_names = [
            'Начинающие-1', 'Начинающие-2', 'Начинающие-3',
            'Средний-1', 'Средний-2', 'Средний-3',
            'Продвинутый-1', 'Продвинутый-2',
            'Выпускной-1', 'Выпускной-2'
        ]
        
        groups = []
        for i, group_name in enumerate(group_names):
            course = courses[i % len(courses)]
            group, created = Group.objects.get_or_create(
                title=group_name,
                defaults={'course': course}
            )
            groups.append(group)
            if created:
                self.stdout.write(f'   Создана группа: {group_name}')

        # Дни недели
        days_data = [
            'Понедельник', 'Вторник', 'Среда', 'Четверг', 
            'Пятница', 'Суббота', 'Воскресенье'
        ]
        
        for day_name in days_data:
            day, created = Day.objects.get_or_create(title=day_name)
            if created:
                self.stdout.write(f'   Создан день: {day_name}')

        # Предметы
        subjects_data = [
            'Чтение Корана', 'Заучивание Корана', 'Тафсир',
            'Хадисы', 'Арабская грамматика', 'Арабская лексика',
            'Исламская история', 'Фикх', 'Акыда (Вероучение)',
            'Исламская этика', 'Дуа и Зикр'
        ]
        
        for subject_name in subjects_data:
            subject, created = Subject.objects.get_or_create(name=subject_name)
            if created:
                self.stdout.write(f'   Создан предмет: {subject_name}')

        return courses, groups

    def create_teachers(self, count):
        """Создание преподавателей"""
        teachers = []
        subjects = list(Subject.objects.all())
        groups = list(Group.objects.all())
        
        for i in range(count):
            # Создание пользователя
            username = f'teacher_{i+1}'
            first_name = fake.first_name_male()
            last_name = fake.last_name_male()
            
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                role='teacher'
            )
            
            # Создание преподавателя
            teacher = Teacher.objects.create(
                user=user,
                name=f'{first_name} {last_name}',
                phone=fake.phone_number()[:12]
            )
            
            # Назначение предметов (1-3 предмета)
            teacher_subjects = random.sample(subjects, random.randint(1, 3))
            teacher.subjects.set(teacher_subjects)
            
            # Назначение групп (1-2 группы)
            teacher_groups = random.sample(groups, random.randint(1, 2))
            teacher.group.set(teacher_groups)
            
            teachers.append(teacher)
            
            if (i + 1) % 5 == 0:
                self.stdout.write(f'   Создано {i + 1} преподавателей...')
        
        return teachers

    def create_students(self, count):
        """Создание студентов"""
        students = []
        courses = list(Course.objects.all())
        groups = list(Group.objects.all())
        
        for i in range(count):
            # Создание пользователя
            username = f'student_{i+1}'
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                role='student'
            )
            
            # Создание студента
            student = Student.objects.create(
                user=user,
                name=f'{first_name} {last_name}',
                phone=fake.phone_number()[:12],
                to_pay=random.randint(5000, 25000),
                status=random.choice([True, False]),
                student_status=random.choice(['active', 'active', 'active', 'inactive']),  # Больше активных
                course=random.choice(courses)
            )
            
            # Назначение групп (1-2 группы)
            student_groups = random.sample(groups, random.randint(1, 2))
            student.group.set(student_groups)
            
            students.append(student)
            
            if (i + 1) % 10 == 0:
                self.stdout.write(f'   Создано {i + 1} студентов...')
        
        return students

    def create_schedule(self, teachers):
        """Создание расписания"""
        days = list(Day.objects.all()[:6])  # Понедельник-Суббота
        subjects = list(Subject.objects.all())
        groups = list(Group.objects.all())
        
        schedule_count = 0
        
        for group in groups:
            # Для каждой группы создаем 3-5 занятий в неделю
            lessons_per_week = random.randint(3, 5)
            selected_days = random.sample(days, lessons_per_week)
            
            for day in selected_days:
                subject = random.choice(subjects)
                time_slot = random.randint(1, 6)  # 6 временных слотов в день
                
                # Проверяем, что расписание не дублируется
                if not Schedule.objects.filter(
                    group=group, day=day, time_slot=time_slot
                ).exists():
                    Schedule.objects.create(
                        group=group,
                        subject=subject,
                        day=day,
                        time_slot=time_slot
                    )
                    schedule_count += 1
        
        self.stdout.write(f'   Создано {schedule_count} записей расписания')

    def create_grades(self, students, teachers):
        """Создание оценок"""
        subjects = list(Subject.objects.all())
        grades_count = 0
        
        for student in students:
            # Для каждого студента создаем 10-30 оценок за последние 3 месяца
            num_grades = random.randint(10, 30)
            
            for _ in range(num_grades):
                # Случайная дата за последние 90 дней
                days_ago = random.randint(0, 90)
                grade_date = date.today() - timedelta(days=days_ago)
                
                # Проверяем ограничение на дату (±2 дня от текущей даты для новых оценок)
                # Но для тестовых данных создаем исторические оценки
                
                Grade.objects.create(
                    student=student,
                    mark=random.randint(2, 5),
                    pages=random.randint(1, 10),
                    subject=random.choice(subjects),
                    teacher=random.choice(teachers),
                    date=grade_date
                )
                grades_count += 1
        
        self.stdout.write(f'   Создано {grades_count} оценок')

    def create_graduates(self, count):
        """Создание выпускников"""
        # Создаем дополнительных студентов для выпускников
        courses = list(Course.objects.all())
        groups = list(Group.objects.all())
        
        for i in range(count):
            # Создание пользователя
            username = f'graduate_{i+1}'
            first_name = fake.first_name()
            last_name = fake.last_name()
            
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                role='student'
            )
            
            # Создание студента-выпускника
            student = Student.objects.create(
                user=user,
                name=f'{first_name} {last_name}',
                phone=fake.phone_number()[:12],
                to_pay=0,  # Выпускники обычно не должны
                status=True,
                student_status='graduated',
                course=random.choice(courses)
            )
            
            # Назначение группы
            student.group.set([random.choice(groups)])
            
            # Создание записи выпускника
            graduation_date = fake.date_between(
                start_date=date(2020, 1, 1),
                end_date=date.today()
            )
            
            graduate = Graduate.objects.create(
                student=student,
                graduation_date=graduation_date,
                graduation_group=random.choice(groups),
                final_grade=round(random.uniform(3.0, 5.0), 1),
                diploma_number=f'DIP-{graduation_date.year}-{i+1:03d}',
                achievements=fake.text(max_nb_chars=200),
                current_occupation=random.choice([
                    'Имам мечети',
                    'Преподаватель исламских наук',
                    'Студент университета',
                    'Переводчик арабского языка',
                    'Исламский консультант',
                    'Работает в исламском центре',
                    'Продолжает обучение',
                    'Частный преподаватель'
                ]),
                contact_phone=fake.phone_number()[:12],
                contact_email=fake.email() if random.choice([True, False]) else '',
                notes=fake.text(max_nb_chars=100) if random.choice([True, False]) else ''
            )
            
            # Создание достижений для некоторых выпускников
            if random.choice([True, False]):
                num_achievements = random.randint(1, 3)
                for j in range(num_achievements):
                    achievement_date = fake.date_between(
                        start_date=graduation_date,
                        end_date=date.today()
                    )
                    
                    GraduateAchievement.objects.create(
                        graduate=graduate,
                        title=random.choice([
                            'Поступление в исламский университет',
                            'Получение иджазы по Корану',
                            'Назначение имамом мечети',
                            'Завершение курса арабского языка',
                            'Участие в международной конференции',
                            'Публикация исламской статьи',
                            'Организация исламского мероприятия'
                        ]),
                        description=fake.text(max_nb_chars=150),
                        date_achieved=achievement_date,
                        category=random.choice([
                            'education', 'career', 'religious', 'social', 'other'
                        ])
                    )
            
            if (i + 1) % 5 == 0:
                self.stdout.write(f'   Создано {i + 1} выпускников...')

    def create_administrators(self):
        """Создание администраторов"""
        admin_data = [
            ('admin1', 'Администратор', 'Системный'),
            ('admin2', 'Заместитель', 'Директора'),
        ]
        
        for username, first_name, last_name in admin_data:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                role='administrator'
            )
            
            Administrator.objects.create(
                user=user,
                name=f'{first_name} {last_name}',
                phone=fake.phone_number()[:12]
            )
            
            self.stdout.write(f'   Создан администратор: {first_name} {last_name}')

    def create_superuser_if_not_exists(self):
        """Создание суперпользователя если не существует"""
        if not User.objects.filter(is_superuser=True).exists():
            User.objects.create_superuser(
                username='admin',
                password='admin123',
                first_name='Super',
                last_name='Admin'
            )
            self.stdout.write('   Создан суперпользователь: admin/admin123')