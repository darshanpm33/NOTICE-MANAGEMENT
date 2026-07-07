from django.core.management.base import BaseCommand
from core.models import User, Department
from django.contrib.auth.hashers import make_password

class Command(BaseCommand):
    help = 'Seeds the database with 7 realistic users as per requirements'

    def handle(self, *args, **options):
        # 1. Create Departments
        print("Creating Departments...")
        depts_data = [
            {'name': 'IT', 'desc': 'Information Technology'},
            {'name': 'HR', 'desc': 'Human Resources'},
            {'name': 'Finance', 'desc': 'Finance & Accounting'},
            {'name': 'Customer Support', 'desc': 'Support & Success'},
        ]
        dept_objs = {}
        for d in depts_data:
            obj, created = Department.objects.get_or_create(name=d['name'], defaults={'description': d['desc']})
            dept_objs[d['name']] = obj
            if created:
                print(f"Created Department: {d['name']}")

        # 2. Create Users
        print("\nCreating/Updating Users...")
        users_data = [
            {
                'first_name': 'Darshan', 'last_name': 'PM', 'email': 'admin@company.com', 
                'role': 'ADMIN', 'dept': 'IT', 'active': True
            },
            {
                'first_name': 'Sundar', 'last_name': 'K', 'email': 'manager@company.com', 
                'role': 'MANAGER', 'dept': 'IT', 'active': True
            },
            {
                'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'hr@company.com', 
                'role': 'MANAGER', 'dept': 'HR', 'active': True
            },
            {
                'first_name': 'Rahul', 'last_name': 'Verma', 'email': 'finance@company.com', 
                'role': 'EMPLOYEE', 'dept': 'Finance', 'active': True
            },
            {
                'first_name': 'Anjali', 'last_name': 'N', 'email': 'support@company.com', 
                'role': 'EMPLOYEE', 'dept': 'Customer Support', 'active': False
            },
            {
                'first_name': 'Karthik', 'last_name': 'R', 'email': 'karthik@company.com', 
                'role': 'EMPLOYEE', 'dept': 'IT', 'active': True
            },
            {
                'first_name': 'Meena', 'last_name': 'S', 'email': 'meena@company.com', 
                'role': 'EMPLOYEE', 'dept': 'HR', 'active': True
            },
        ]

        for u in users_data:
            # Check if user already exists
            user = User.objects.filter(email=u['email']).first()
            if not user:
                user = User.objects.create(
                    email=u['email'],
                    username=u['email'], # Username is required, using email as unique
                    first_name=u['first_name'],
                    last_name=u['last_name'],
                    role=u['role'],
                    department=dept_objs.get(u['dept']),
                    is_active=u['active'],
                    password=make_password('admin123') # Default password for all
                )
                print(f"User Created: {u['first_name']} {u['last_name']}")
            else:
                # Update existing user if needed
                user.role = u['role']
                user.department = dept_objs.get(u['dept'])
                user.is_active = u['active']
                user.save()
                print(f"User Updated: {u['first_name']} {u['last_name']}")

        print("\nSeeding Complete! All 7 users are live.")
