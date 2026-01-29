from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models_notification import Notification

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/notifications.html', {'notifications': notifications})

@login_required
def mark_notification_read(request, notification_id):
    notif = Notification.objects.get(id=notification_id, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect('notifications')
