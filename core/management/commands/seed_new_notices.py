from django.core.management.base import BaseCommand
from core.models import User, Department, Notice
from django.utils import timezone
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):
    help = 'Seeds the database with 10 new realistic company notices'

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("  NoticeHub — Seeding 10 New Notices")
        self.stdout.write("=" * 60)

        # ────────────────────────────────────────────────────────────
        # 1. Ensure required departments exist
        # ────────────────────────────────────────────────────────────
        self.stdout.write("\n[1/3] Ensuring departments exist...")
        dept_configs = [
            {'name': 'IT',               'description': 'Information Technology'},
            {'name': 'HR',               'description': 'Human Resources'},
            {'name': 'Finance',          'description': 'Finance & Accounting'},
            {'name': 'Customer Support', 'description': 'Customer Support & Success'},
        ]
        depts = {}
        for cfg in dept_configs:
            obj, created = Department.objects.get_or_create(
                name=cfg['name'],
                defaults={'description': cfg['description']}
            )
            depts[cfg['name']] = obj
            status = "Created" if created else "Already exists"
            self.stdout.write(f"  Department [{status}]: {cfg['name']}")

        # ────────────────────────────────────────────────────────────
        # 2. Ensure required author accounts exist / are updated
        #    Authors needed: Admin, IT Manager, HR Manager,
        #                    Finance Manager, Support Manager
        # ────────────────────────────────────────────────────────────
        self.stdout.write("\n[2/3] Ensuring author accounts are ready...")
        author_configs = [
            {
                'email': 'admin@company.com',
                'first_name': 'Darshan', 'last_name': 'PM',
                'role': 'ADMIN', 'dept': 'IT', 'active': True,
                'alias': 'Admin',
            },
            {
                'email': 'manager@company.com',
                'first_name': 'Sundar', 'last_name': 'K',
                'role': 'MANAGER', 'dept': 'IT', 'active': True,
                'alias': 'IT Manager',
            },
            {
                'email': 'hr@company.com',
                'first_name': 'Priya', 'last_name': 'Sharma',
                'role': 'MANAGER', 'dept': 'HR', 'active': True,
                'alias': 'HR Manager',
            },
            {
                'email': 'finance@company.com',
                'first_name': 'Rahul', 'last_name': 'Verma',
                'role': 'MANAGER', 'dept': 'Finance', 'active': True,
                'alias': 'Finance Manager',
            },
            {
                'email': 'support@company.com',
                'first_name': 'Anjali', 'last_name': 'N',
                'role': 'MANAGER', 'dept': 'Customer Support', 'active': True,
                'alias': 'Support Manager',
            },
        ]
        authors = {}
        for cfg in author_configs:
            try:
                user = User.objects.get(email=cfg['email'])
            except User.DoesNotExist:
                user = None
            
            if not user:
                user = User.objects.create(
                    email=cfg['email'],
                    username=cfg['email'],
                    first_name=cfg['first_name'],
                    last_name=cfg['last_name'],
                    role=cfg['role'],
                    department=depts.get(cfg['dept']),
                    is_active=cfg['active'],
                    password=make_password('admin123'),
                )
                self.stdout.write(f"  User Created: {cfg['first_name']} {cfg['last_name']} ({cfg['alias']})")
            else:
                # Promote to MANAGER / ADMIN if needed & ensure active
                changed = False
                if user.role != cfg['role']:
                    user.role = cfg['role']
                    changed = True
                if not user.is_active and cfg['active']:
                    user.is_active = True
                    changed = True
                if user.department != depts.get(cfg['dept']):
                    user.department = depts.get(cfg['dept'])
                    changed = True
                if changed:
                    user.save()
                    self.stdout.write(f"  User Updated : {cfg['first_name']} {cfg['last_name']} ({cfg['alias']})")
                else:
                    self.stdout.write(f"  User OK      : {cfg['first_name']} {cfg['last_name']} ({cfg['alias']})")
            authors[cfg['alias']] = user

        # ────────────────────────────────────────────────────────────
        # 3. Insert 10 new notices
        # ────────────────────────────────────────────────────────────
        self.stdout.write("\n[3/3] Creating 10 new notices...")

        notices_data = [
            {
                'title': 'Office Network Upgrade',
                'content': (
                    'The company network infrastructure will be upgraded this weekend to improve '
                    'speed and security. All employees are advised to save their work and log off '
                    'before leaving on Friday. Minor disruptions may occur during the upgrade '
                    'period. The IT team will be on-site to ensure a smooth transition. For '
                    'urgent assistance, please contact the IT helpdesk.'
                ),
                'dept': 'IT',
                'priority': 'MEDIUM',
                'author_alias': 'IT Manager',
            },
            {
                'title': 'Employee Feedback Survey',
                'content': (
                    'HR has launched the annual employee feedback survey to better understand '
                    'workplace satisfaction and areas of improvement. All employees are '
                    'encouraged to participate and share their honest suggestions. The survey is '
                    'completely anonymous and will take approximately 10 minutes to complete. '
                    'Please submit your responses by the end of this week.'
                ),
                'dept': 'HR',
                'priority': 'MEDIUM',
                'author_alias': 'HR Manager',
            },
            {
                'title': 'Budget Planning Meeting',
                'content': (
                    'Department heads are requested to attend the annual budget planning meeting '
                    'scheduled next Monday at 2:00 PM in the Conference Room. Please come '
                    'prepared with your department\'s financial projections and resource '
                    'requirements for the upcoming fiscal year. Kindly confirm your attendance '
                    'with the Finance team at the earliest.'
                ),
                'dept': 'Finance',
                'priority': 'HIGH',
                'author_alias': 'Finance Manager',
            },
            {
                'title': 'New Employee Onboarding',
                'content': (
                    'A new batch of employees will be joining the organisation next week. All '
                    'department heads and team leads are requested to support the onboarding '
                    'process by ensuring workstations, system access, and orientation schedules '
                    'are ready. HR will share the detailed onboarding plan by end of day. '
                    'Please coordinate accordingly.'
                ),
                'dept': 'HR',
                'priority': 'LOW',
                'author_alias': 'HR Manager',
            },
            {
                'title': 'System Password Reset Requirement',
                'content': (
                    'As part of the company\'s ongoing security compliance initiative, all '
                    'employees are required to reset their system passwords within the next '
                    '3 business days. Passwords must be at least 12 characters long and include '
                    'a combination of uppercase, lowercase, numbers, and special characters. '
                    'Failure to comply may result in temporary account suspension. Please '
                    'contact IT support if you need assistance.'
                ),
                'dept': 'IT',
                'priority': 'HIGH',
                'author_alias': 'Admin',
            },
            {
                'title': 'Customer Satisfaction Review',
                'content': (
                    'The Customer Support team is requested to review all recent customer '
                    'feedback reports submitted this quarter. Focus areas include response '
                    'time, issue resolution rates, and overall satisfaction scores. Team leads '
                    'should prepare a brief summary of action items to be discussed in the '
                    'upcoming weekly review meeting. Improving our CSAT score remains a top '
                    'priority for Q2.'
                ),
                'dept': 'Customer Support',
                'priority': 'MEDIUM',
                'author_alias': 'Support Manager',
            },
            {
                'title': 'Expense Submission Deadline',
                'content': (
                    'This is a reminder to all employees that all pending expense claims and '
                    'reimbursement requests must be submitted through the Finance portal before '
                    'the end of this month. Late submissions will not be processed until the '
                    'next billing cycle, which may result in significant delays. Please ensure '
                    'all receipts and supporting documents are attached to your claims.'
                ),
                'dept': 'Finance',
                'priority': 'MEDIUM',
                'author_alias': 'Finance Manager',
            },
            {
                'title': 'Holiday Announcement',
                'content': (
                    'The management is pleased to inform all employees that the office will '
                    'remain closed next Friday on account of a public holiday. Regular '
                    'operations will resume on the following Monday. Employees with critical '
                    'deliverables are advised to plan accordingly and communicate timelines '
                    'with their respective managers. Enjoy the long weekend!'
                ),
                'dept': 'All',
                'priority': 'LOW',
                'author_alias': 'Admin',
            },
            {
                'title': 'Performance Appraisal Cycle',
                'content': (
                    'The annual performance appraisal cycle has officially commenced. All '
                    'employees are requested to log in to the HR portal and complete their '
                    'self-evaluation forms by the due date. Managers are also requested to '
                    'review their team members\' evaluations and submit ratings on time. '
                    'Timely completion of appraisals is critical for processing increments '
                    'and promotions.'
                ),
                'dept': 'HR',
                'priority': 'HIGH',
                'author_alias': 'HR Manager',
            },
            {
                'title': 'Data Backup Reminder',
                'content': (
                    'The IT team would like to remind all employees to regularly back up their '
                    'important files and project data. Please follow the official IT backup '
                    'guidelines available on the intranet. Employees working on shared drives '
                    'should verify that their auto-sync settings are enabled. Data loss due to '
                    'negligence will not be recoverable. When in doubt, back it up!'
                ),
                'dept': 'IT',
                'priority': 'MEDIUM',
                'author_alias': 'IT Manager',
            },
        ]

        created_count = 0
        skipped_count = 0

        for idx, n_data in enumerate(notices_data, 1):
            author = authors.get(n_data['author_alias'])
            if not author:
                self.stdout.write(
                    self.style.WARNING(f"  [{idx:02d}] SKIP — Author '{n_data['author_alias']}' not found.")
                )
                skipped_count += 1
                continue

            # Determine target department(s)
            dept_obj = None if n_data['dept'] == 'All' else depts.get(n_data['dept'])

            notice, created = Notice.objects.get_or_create(
                title=n_data['title'],
                defaults={
                    'content':  n_data['content'],
                    'author':   author,
                    'priority': n_data['priority'],
                    'status':   'PUBLISHED',
                },
            )

            # Attach department (skip for "All" — empty M2M = all departments)
            try:
                if dept_obj and created:
                    notice.target_departments.set([dept_obj])
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"  Warning: Could not link department: {e}"))

            if created:
                created_count += 1
                dept_label = n_data['dept']
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  [{idx:02d}] CREATED — [{n_data['priority']:6s}] [{dept_label:16s}] {n_data['title']}"
                    )
                )
            else:
                skipped_count += 1
                self.stdout.write(
                    f"  [{idx:02d}] EXISTS  — {n_data['title']}"
                )

        # ────────────────────────────────────────────────────────────
        # Summary
        # ────────────────────────────────────────────────────────────
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(
            self.style.SUCCESS(
                f"  Done!  {created_count} notice(s) created, {skipped_count} skipped."
            )
        )
        self.stdout.write("=" * 60)
