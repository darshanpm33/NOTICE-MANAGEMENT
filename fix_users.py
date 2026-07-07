import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'company_notice_system.settings')
django.setup()

from core.models import User

users_data = [
    {'email': 'admin@company.com',   'username': 'admin@company.com',   'first_name': 'Darshan', 'last_name': 'PM',     'role': 'ADMIN',    'is_superuser': True,  'is_staff': True},
    {'email': 'manager@company.com', 'username': 'manager@company.com', 'first_name': 'Sundar',  'last_name': 'K',      'role': 'MANAGER',  'is_superuser': False, 'is_staff': False},
    {'email': 'hr@company.com',      'username': 'hr@company.com',      'first_name': 'Priya',   'last_name': 'Sharma', 'role': 'MANAGER',  'is_superuser': False, 'is_staff': False},
    {'email': 'finance@company.com', 'username': 'finance@company.com', 'first_name': 'Rahul',   'last_name': 'Verma',  'role': 'EMPLOYEE', 'is_superuser': False, 'is_staff': False},
    {'email': 'support@company.com', 'username': 'support@company.com', 'first_name': 'Anjali',  'last_name': 'N',      'role': 'EMPLOYEE', 'is_superuser': False, 'is_staff': False},
    {'email': 'karthik@company.com', 'username': 'karthik@company.com', 'first_name': 'Karthik', 'last_name': 'R',      'role': 'EMPLOYEE', 'is_superuser': False, 'is_staff': False},
    {'email': 'meena@company.com',   'username': 'meena@company.com',   'first_name': 'Meena',   'last_name': 'S',      'role': 'EMPLOYEE', 'is_superuser': False, 'is_staff': False},
]

PASSWORD = 'Admin@123'

for ud in users_data:
    user, created = User.objects.get_or_create(email=ud['email'])
    user.username    = ud['username']
    user.first_name  = ud['first_name']
    user.last_name   = ud['last_name']
    user.role        = ud['role']
    user.is_superuser= ud['is_superuser']
    user.is_staff    = ud['is_staff']
    user.is_active   = True
    user.set_password(PASSWORD)
    user.save()
    status = 'CREATED' if created else 'UPDATED'
    print(f'{status}: {ud["email"]}  |  Password: {PASSWORD}')

print('\nAll users ready! Login at http://127.0.0.1:8000/login/')
print('Universal Password: Admin@123')
