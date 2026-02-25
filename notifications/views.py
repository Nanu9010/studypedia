from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Notification
from django.core.paginator import Paginator
#notifications/views.py

@login_required
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).select_related('sender', 'related_post', 'related_comment', 'related_message')
    paginator = Paginator(notifications, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    if request.method == 'POST':
        notification_ids = request.POST.getlist('notification_ids')
        Notification.objects.filter(id__in=notification_ids, recipient=request.user).update(is_read=True)
        channel_layer = get_channel_layer()
        for notif_id in notification_ids:
            async_to_sync(channel_layer.group_send)(f'notifications_{request.user.id}', {
                'type': 'new_notification',
                'id': notif_id,
                'is_read': True
            })
        messages.success(request, 'Notifications marked as read!')
        return redirect('notifications:notifications_list')
    return render(request, 'notifications/notifications_list.html', {'page_obj': page_obj})