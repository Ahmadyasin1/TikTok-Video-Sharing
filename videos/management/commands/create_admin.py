from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create admin superuser for development'
    
    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@videoshare.com',
                password='admin123',
                user_type='creator'
            )
            self.stdout.write(
                self.style.SUCCESS(f'Admin user created: {admin.username}')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Admin user already exists')
            )
