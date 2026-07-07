from django.core.management.base import BaseCommand
from core.models import User
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Seeds a Super Admin account'

    def handle(self, *args, **options):
        email = 'admin@company.com'
        password = 'Admin@123'
        
        try:
            if not User.objects.filter(email=email).exists():
                User.objects.create_superuser(
                    username='admin',
                    email=email,
                    password=password,
                    first_name='Super',
                    last_name='Admin',
                    role='ADMIN'
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully seeded admin user: {email}'))
            else:
                self.stdout.write(self.style.WARNING(f'Admin user with email {email} already exists.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error seeding admin: {str(e)}'))
