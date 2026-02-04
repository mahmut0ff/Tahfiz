from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает суперпользователя с предустановленными данными'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Имя пользователя (по умолчанию: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='admin123',
            help='Пароль (по умолчанию: admin123)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@tahfiz.site',
            help='Email (по умолчанию: admin@tahfiz.site)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        email = options['email']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'⚠️  Пользователь {username} уже существует')
            )
            return
        
        user = User.objects.create_superuser(
            username=username,
            password=password,
            email=email,
            first_name='Super',
            last_name='Admin'
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Суперпользователь создан:\n'
                f'   Логин: {username}\n'
                f'   Пароль: {password}\n'
                f'   Email: {email}'
            )
        )