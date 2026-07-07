from django.contrib import admin
from .models import User, Department, Notice, NoticeRead, Comment, Notification, AuditLog

admin.site.register(User)
admin.site.register(Department)
admin.site.register(Notice)
admin.site.register(NoticeRead)
admin.site.register(Comment)
admin.site.register(Notification)
admin.site.register(AuditLog)
