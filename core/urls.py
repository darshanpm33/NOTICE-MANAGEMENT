from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Auth
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Notices
    path('notices/', views.notice_list, name='notice_list'),
    path('notices/create/', views.notice_create, name='notice_create'),
    path('notices/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('notices/<int:pk>/edit/', views.notice_edit, name='notice_edit'),
    path('notices/delete/<int:pk>/', views.notice_delete, name='notice_delete'),
    
    # Comments & Notifications
    path('notices/<int:pk>/comment/', views.add_comment, name='add_comment'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
    # Users (Admin only)
    path('users/', views.user_management, name='user_management'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<int:pk>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    
    # Departments (Admin only)
    path('departments/', views.department_management, name='department_management'),
    path('departments/add/', views.add_department, name='add_department'),
    path('departments/delete/<int:pk>/', views.delete_department, name='delete_department'),
    
    # Profile & Reports
    path('profile/', views.profile, name='profile'),
    path('reports/', views.reports, name='reports'),
    path('reports/export/', views.export_report, name='export_report'),
]
