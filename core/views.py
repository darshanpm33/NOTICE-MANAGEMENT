import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.utils import timezone
from .models import User, Department, Notice, NoticeRead, Comment, Notification, AuditLog
from datetime import datetime, timedelta

# Helper: Check Admin
def is_admin(user):
    return user.is_authenticated and user.role == 'ADMIN'

# Helper: Check Manager
def is_manager(user):
    return user.is_authenticated and (user.role == 'ADMIN' or user.role == 'MANAGER')

# Auth Views
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember') == 'on'
        
        try:
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                if not remember:
                    request.session.set_expiry(0) # Browser close
                else:
                    request.session.set_expiry(1209600) # 2 weeks
                AuditLog.objects.create(user=user, action='LOGIN', target='Self')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
        except Exception as e:
            # Catching database connection issues (common in cloud deployments)
            if 'SelectionTimeout' in str(e) or 'connection' in str(e).lower():
                messages.error(request, 'Database connection failed. Please contact your system administrator.')
            else:
                messages.error(request, f'An unexpected error occurred: {str(e)[:50]}')
            
    return render(request, 'login.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )
            login(request, user)
            AuditLog.objects.create(user=user, action='REGISTER', target='Self')
            messages.success(request, f'Welcome, {first_name}!')
            return redirect('dashboard')
    return render(request, 'register.html')

# Dashboard
@login_required
def dashboard(request):
    # Stats - Use Python-side filtering for absolute reliability with Djongo/Python 3.14
    all_notices = list(Notice.objects.all())
    all_users = list(User.objects.all())
    all_departments = list(Department.objects.all())
    
    total_notices = len([n for n in all_notices if n.status == 'PUBLISHED'])
    active_users = len([u for u in all_users if u.is_active])
    total_departments = len(all_departments)
    
    # Unread notices
    try:
        user_reads = list(NoticeRead.objects.filter(user=request.user).values_list('notice_id', flat=True))
    except:
        user_reads = [r.notice_id for r in NoticeRead.objects.all() if r.user_id == request.user.id]
        
    unread_notices = 0
    published_notices = [n for n in all_notices if n.status == 'PUBLISHED']
    for n in published_notices:
        if n.id not in user_reads:
            unread_notices += 1
            
    # Recent Notices
    recent_notices = sorted(published_notices, key=lambda x: x.created_at, reverse=True)[:5]
    
    # Chart Data: Notices per department
    labels = []
    data = []
    for dept in all_departments:
        labels.append(dept.name)
        # Manual Python-side count to avoid M2M query issues in Djongo
        dept_notice_count = 0
        for n in all_notices:
            # Check if dept is in notice.target_departments
            # We use .all() carefully
            try:
                if dept in n.target_departments.all():
                    dept_notice_count += 1
            except:
                pass
        data.append(dept_notice_count)
    
    context = {
        'total_notices': total_notices,
        'active_users': active_users,
        'total_departments': total_departments,
        'unread_notices': unread_notices,
        'recent_notices': recent_notices,
        'chart_labels': labels,
        'chart_data': data,
    }
    return render(request, 'dashboard.html', context)

# Notice List
@login_required
def notice_list(request):
    query = request.GET.get('q', '').lower()
    dept_id = request.GET.get('department', '')
    priority = request.GET.get('priority', '')
    status = request.GET.get('status', 'PUBLISHED')
    
    # Fetch all for Python-side filtering (Safer for Djongo)
    all_notices = list(Notice.objects.all())
    
    # Role-based filtering
    if request.user.role == 'EMPLOYEE':
        filtered = []
        user_dept = request.user.department
        now = timezone.now()
        for n in all_notices:
            if n.status != 'PUBLISHED':
                continue
            # Target check
            target_depts = list(n.target_departments.all())
            is_targeted = False
            if not target_depts:
                is_targeted = True
            elif user_dept in target_depts:
                is_targeted = True
            
            if is_targeted:
                # Expiry check
                if n.expiry_date is None or n.expiry_date > now:
                    filtered.append(n)
        notices = filtered
    else:
        notices = all_notices

    # Additional filters
    if query:
        notices = [n for n in notices if query in n.title.lower() or query in n.content.lower()]
    if dept_id:
        try:
            target_dept_id = int(dept_id)
            notices = [n for n in notices if any(d.id == target_dept_id for d in n.target_departments.all())]
        except:
            pass
    if priority:
        notices = [n for n in notices if n.priority == priority]
    if status and request.user.role != 'EMPLOYEE':
        notices = [n for n in notices if n.status == status]

    # Sort
    notices.sort(key=lambda x: (x.is_pinned, x.created_at), reverse=True)

    from django.core.paginator import Paginator
    paginator = Paginator(notices, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = list(Department.objects.all())
    
    # Mark as read for the user
    user_reads = set(NoticeRead.objects.filter(user=request.user).values_list('notice_id', flat=True))
    for notice in page_obj:
        notice.is_read = notice.id in user_reads
        
    context = {
        'notices': page_obj,
        'departments': departments,
    }
    return render(request, 'notices/list.html', context)

@login_required
def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    # Check access
    if request.user.role == 'EMPLOYEE':
        if notice.status != 'PUBLISHED':
            return redirect('notice_list')
        # Check if targeted to user's dept or no target
        if notice.target_departments.exists() and request.user.department not in notice.target_departments.all():
            return redirect('notice_list')
            
    # Mark as read
    read_obj, created = NoticeRead.objects.get_or_create(notice=notice, user=request.user)
    
    comments = notice.comments.all().order_by('-created_at')
    read_by = notice.reads.all().order_by('-read_at')
    
    context = {
        'notice': notice,
        'comments': comments,
        'read_by': read_by,
        'is_author': notice.author == request.user or request.user.role == 'ADMIN',
    }
    return render(request, 'notices/detail.html', context)

@login_required
@user_passes_test(is_manager)
def notice_create(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        priority = request.POST.get('priority')
        expiry_date = request.POST.get('expiry_date')
        status = request.POST.get('status', 'PUBLISHED')
        is_pinned = request.POST.get('is_pinned') == 'on'
        target_depts = request.POST.getlist('target_departments')
        attachment = request.FILES.get('attachment')
        
        notice = Notice.objects.create(
            title=title,
            content=content,
            author=request.user,
            priority=priority,
            is_pinned=is_pinned,
            status=status,
            attachment=attachment
        )
        if expiry_date:
            notice.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M')
        
        if target_depts:
            notice.target_departments.set(target_depts)
        
        notice.save()
        AuditLog.objects.create(user=request.user, action='CREATE_NOTICE', target=f'Notice {notice.id}')
        
        # Notify users in target departments
        if notice.status == 'PUBLISHED':
            users_to_notify = User.objects.all()
            if target_depts:
                users_to_notify = users_to_notify.filter(department__id__in=target_depts)
            for user in users_to_notify:
                if user != request.user:
                    Notification.objects.create(user=user, message=f'New Notice Published: {notice.title}')
        
        return redirect('notice_detail', pk=notice.pk)
        
    departments = Department.objects.all()
    return render(request, 'notices/create.html', {'departments': departments})

@login_required
@user_passes_test(is_manager)
def notice_edit(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.user != notice.author and request.user.role != 'ADMIN':
        return redirect('notice_list')
        
    if request.method == 'POST':
        notice.title = request.POST.get('title')
        notice.content = request.POST.get('content')
        notice.priority = request.POST.get('priority')
        notice.is_pinned = request.POST.get('is_pinned') == 'on'
        notice.status = request.POST.get('status')
        expiry_date = request.POST.get('expiry_date')
        if expiry_date:
            notice.expiry_date = datetime.strptime(expiry_date, '%Y-%m-%dT%H:%M')
        
        if request.FILES.get('attachment'):
            notice.attachment = request.FILES.get('attachment')
            
        target_depts = request.POST.getlist('target_departments')
        notice.target_departments.set(target_depts)
        notice.save()
        
        AuditLog.objects.create(user=request.user, action='EDIT_NOTICE', target=f'Notice {notice.id}')
        return redirect('notice_detail', pk=notice.pk)
        
    departments = Department.objects.all()
    target_ids = list(notice.target_departments.values_list('id', flat=True))
    return render(request, 'notices/edit.html', {'notice': notice, 'departments': departments, 'target_ids': target_ids})

@login_required
@user_passes_test(is_manager)
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.user == notice.author or request.user.role == 'ADMIN':
        AuditLog.objects.create(user=request.user, action='DELETE_NOTICE', target=f'Notice {notice.id}')
        notice.delete()
    return redirect('notice_list')

# User Management
@login_required
@user_passes_test(is_admin)
def user_management(request):
    users = User.objects.all().order_by('-date_joined')
    departments = Department.objects.all()
    return render(request, 'users/list.html', {'users': users, 'departments': departments})

@login_required
@user_passes_test(is_admin)
def add_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        dept_id = request.POST.get('department')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            if dept_id:
                user.department = Department.objects.get(id=dept_id)
                user.save()
            AuditLog.objects.create(user=request.user, action='ADD_USER', target=f'User {user.email}')
            messages.success(request, 'User added successfully.')
            
    return redirect('user_management')

@login_required
@user_passes_test(is_admin)
def toggle_user_active(request, pk):
    user = get_object_or_404(User, pk=pk)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        AuditLog.objects.create(user=request.user, action='TOGGLE_USER', target=f'User {user.email}')
    return redirect('user_management')

# Department Management
@login_required
@user_passes_test(is_admin)
def department_management(request):
    departments = list(Department.objects.all())
    for dept in departments:
        dept.member_count = len(list(User.objects.filter(department=dept)))
        dept.notice_count = len(list(Notice.objects.filter(target_departments=dept)))
    users = User.objects.all()
    return render(request, 'departments/list.html', {'departments': departments, 'users': users})

@login_required
@user_passes_test(is_admin)
def add_department(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        manager_id = request.POST.get('manager')
        
        dept = Department.objects.create(name=name, description=description)
        if manager_id:
            dept.manager = User.objects.get(id=manager_id)
            dept.save()
        AuditLog.objects.create(user=request.user, action='ADD_DEPT', target=f'Dept {dept.name}')
    return redirect('department_management')

@login_required
@user_passes_test(is_admin)
def delete_department(request, pk):
    dept = get_object_or_404(Department, pk=pk)
    AuditLog.objects.create(user=request.user, action='DELETE_DEPT', target=f'Dept {dept.name}')
    dept.delete()
    return redirect('department_management')

# Notifications
@login_required
def notifications(request):
    notifs = request.user.notifications.all().order_by('-created_at')
    return render(request, 'notifications.html', {'notifications': notifs})

@login_required
def mark_all_notifications_read(request):
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return redirect('notifications')

# Profile
@login_required
def profile(request):
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        if request.FILES.get('profile_pic'):
            request.user.profile_pic = request.FILES.get('profile_pic')
        
        new_password = request.POST.get('new_password')
        if new_password:
             request.user.set_password(new_password)
             login(request, request.user) # Keep user logged in
             
        request.user.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
        
    logs = AuditLog.objects.filter(user=request.user).order_by('-timestamp')[:20]
    return render(request, 'users/profile.html', {'logs': logs})

# Reports
@login_required
@user_passes_test(is_admin)
def reports(request):
    # Fetch all for safe processing
    all_notices = list(Notice.objects.all())
    all_depts = list(Department.objects.all())
    all_users = list(User.objects.all())

    # Notices per month
    month_data = []
    for m in range(1, 13):
        count = len([n for n in all_notices if n.created_at.month == m])
        month_data.append({'month': str(m).zfill(2), 'count': count})
        
    # Department breakdown
    dept_breakdown = []
    for dept in all_depts:
        # Check target_departments for each notice in memory
        count = 0
        for n in all_notices:
            try:
                if dept in n.target_departments.all():
                    count += 1
            except:
                pass
        dept_breakdown.append({
            'name': dept.name,
            'notice_count': count
        })
        
    # Most active users
    for u in all_users:
        u.notice_count = len([n for n in all_notices if n.author_id == u.id])
    active_users = sorted(all_users, key=lambda x: getattr(x, 'notice_count', 0), reverse=True)[:10]
    
    # Simple data for JS
    month_counts = [len([n for n in all_notices if n.created_at.month == m]) for m in range(1, 13)]
    dept_labels  = [d.name for d in all_depts]
    dept_counts  = []
    for dept in all_depts:
        count = 0
        for n in all_notices:
            try:
                if dept in n.target_departments.all(): count += 1
            except: pass
        dept_counts.append(count)

    context = {
        'dept_breakdown': dept_breakdown,
        'active_users': active_users,
        'month_counts': month_counts,
        'dept_labels': dept_labels,
        'dept_counts': dept_counts,
    }
    return render(request, 'reports.html', context)

@login_required
@user_passes_test(is_admin)
def export_report(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="notice_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['Title', 'Author', 'Department', 'Priority', 'Created At', 'Status'])
    for notice in Notice.objects.all():
        depts = ",".join([d.name for d in notice.target_departments.all()])
        writer.writerow([notice.title, notice.author.email, depts, notice.priority, notice.created_at, notice.status])
    return response

# Comments
@login_required
def add_comment(request, pk):
    if request.method == 'POST':
        notice = get_object_or_404(Notice, pk=pk)
        content = request.POST.get('content')
        if content:
            Comment.objects.create(notice=notice, user=request.user, content=content)
            # Notify author
            if notice.author != request.user:
                Notification.objects.create(user=notice.author, message=f'{request.user.first_name} commented on your notice: {notice.title}')
    return redirect('notice_detail', pk=pk)
