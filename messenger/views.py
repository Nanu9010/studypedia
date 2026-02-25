from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Q
from .models import ChatRoom, Participant, Message, User
from .forms import MessageForm
from django_ratelimit.decorators import ratelimit
from django.contrib.auth.decorators import login_required
from django.utils import timezone

@login_required
def chat_list(request):
    rooms = ChatRoom.objects.filter(participants=request.user, is_active=True).select_related('participants').prefetch_related('participants__user')
    search_query = request.GET.get('q', '').strip()
    if search_query:
        rooms = rooms.filter(
            Q(name__icontains=search_query) |
            Q(participants__user__username__icontains=search_query)
        ).distinct()
    paginator = Paginator(rooms, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'messenger/chat_list.html', {'page_obj': page_obj, 'search_query': search_query})

@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user, is_active=True)
    messages_qs = room.messages.select_related('user').order_by('created_at')[:100]
    form = MessageForm()
    other_participants = room.participants.exclude(user=request.user).select_related('user')
    return render(request, 'messenger/chat_room.html', {
        'room': room,
        'messages': messages_qs,
        'form': form,
        'other_participants': other_participants
    })

@login_required
@require_POST
@ratelimit(key='user', rate='10/m', method='POST', block=True)
def send_message(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id, participants=request.user, is_active=True)
    form = MessageForm(request.POST, request.FILES)
    if form.is_valid():
        message = form.save(commit=False)
        message.user = request.user
        message.room = room
        message.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(f'chat_{room_id}', {
            'type': 'chat_message',
            'content': message.content,
            'image': message.image.url if message.image else '',
            'user': message.user.username,
            'user_id': message.user.id,
            'timestamp': message.created_at.isoformat()
        })
        Participant.objects.filter(room=room).update(last_seen=timezone.now())
        messages.success(request, 'Message sent!')
    else:
        messages.error(request, 'Error sending message.')
    return redirect('messenger:chat_room', room_id=room_id)

@login_required
def start_chat(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        messages.error(request, "Cannot chat with yourself.")
        return redirect('messenger:chat_list')
    room = ChatRoom.objects.filter(
        room_type='one_to_one',
        participants=request.user,
        participant =other_user
    ).first()
    if not room:
        room = ChatRoom.objects.create(room_type='one_to_one')
        Participant.objects.create(user=request.user, room=room)
        Participant.objects.create(user=other_user, room=room)
    return redirect('messenger:chat_room', room_id=room.id)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        participants = request.POST.getlist('participants')
        participants.append(str(request.user.id))
        if len(participants) < 2:
            messages.error(request, "A group needs at least 2 participants.")
            return redirect('messenger:chat_list')
        users = User.objects.filter(id__in=participants)
        room = ChatRoom.objects.create(room_type='group', name=request.POST.get('name', f"Group {timezone.now()}"))
        for user in users:
            Participant.objects.create(user=user, room=room)
        return redirect('messenger:chat_room', room_id=room.id)
    return render(request, 'messenger/create_group.html', {'users': User.objects.exclude(id=request.user.id)})