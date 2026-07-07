from django.core.management.base import BaseCommand
from core.models import User, Department, Notice
from django.utils import timezone

class Command(BaseCommand):
    help = 'Seeds the database with 5 realistic notices'

    def handle(self, *args, **options):
        # 1. Fetch Users
        print("Fetching Users...")
        authors = {
            'Darshan PM': User.objects.get(email='admin@company.com'),
            'Sundar K': User.objects.get(email='manager@company.com'),
            'Priya Sharma': User.objects.get(email='hr@company.com'),
            'Rahul Verma': User.objects.get(email='finance@company.com'),
            'Anjali N': User.objects.get(email='support@company.com'),
        }

        # 2. Fetch Departments
        print("Fetching Departments...")
        depts = {
            'IT': Department.objects.get(name='IT'),
            'HR': Department.objects.get(name='HR'),
            'Finance': Department.objects.get(name='Finance'),
            'Customer Support': Department.objects.get(name='Customer Support'),
        }

        # 3. Create Notices
        print("\nCreating Sample Notices...")
        notices_data = [
            {
                'title': 'Server Maintenance Downtime',
                'content': 'All internal systems will be unavailable from 10 PM to 12 AM due to scheduled maintenance.',
                'dept': 'IT', 'priority': 'HIGH', 'author': 'Sundar K'
            },
            {
                'title': 'Updated Leave Policy',
                'content': 'New leave policy has been implemented. Employees are requested to review it in the HR portal.',
                'dept': 'HR', 'priority': 'MEDIUM', 'author': 'Priya Sharma'
            },
            {
                'title': 'Salary Credited',
                'content': 'March month salary has been credited to all employees successfully.',
                'dept': 'Finance', 'priority': 'LOW', 'author': 'Rahul Verma'
            },
            {
                'title': 'Customer Support Training',
                'content': 'Mandatory training session for support team will be conducted this Friday at 3 PM.',
                'dept': 'Customer Support', 'priority': 'MEDIUM', 'author': 'Anjali N'
            },
            {
                'title': 'Security Alert',
                'content': 'Do not share your login credentials. Report any suspicious emails immediately to IT team.',
                'dept': 'IT', 'priority': 'HIGH', 'author': 'Darshan PM'
            },
        ]

        for n_data in notices_data:
            author = authors.get(n_data['author'])
            dept = depts.get(n_data['dept'])
            if not author:
                print(f"Skipping: Author {n_data['author']} not found.")
                continue

            # Create notice
            notice, created = Notice.objects.get_or_create(
                title=n_data['title'],
                author=author,
                defaults={
                    'content': n_data['content'],
                    'priority': n_data['priority'],
                    'status': 'PUBLISHED',
                    'created_at': timezone.now()
                }
            )
            
            try:
                if dept:
                    notice.target_departments.add(dept)
            except Exception as e:
                print(f"Warning: Could not link department to notice '{n_data['title']}': {e}")
            
            if created:
                print(f"Notice Created: {n_data['title']}")
            else:
                print(f"Notice Already Exists: {n_data['title']}")

        print("\nSeeding Complete! 5 sample notices are live.")
