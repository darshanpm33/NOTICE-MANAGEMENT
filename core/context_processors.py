from .models import Notification

def notification_count(request):
    if hasattr(request, 'user') and request.user.is_authenticated:
        try:
            # Safer direct query for Djongo
            count = Notification.objects.filter(user=request.user, is_read=False).count()
            return {'unread_notif_count': count}
        except Exception:
            try:
                 # Fallback to len(list) if count() fails
                 return {'unread_notif_count': len(list(Notification.objects.filter(user=request.user, is_read=False)))}
            except Exception:
                 return {'unread_notif_count': 0}
    return {'unread_notif_count': 0}
