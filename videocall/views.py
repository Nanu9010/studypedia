# videocall/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import VideoRoom, RoomParticipant, ChatMessage, UserPreferences, User
import uuid
from django.db import models

import random
from accounts.views import jwt_auth
from django.views.decorators.http import require_GET, require_POST

@jwt_auth
def lobby(request):
    """Enhanced lobby with statistics"""
    current_room = VideoRoom.objects.filter(
        participants=request.user,
        status__in=['waiting', 'active'],
        roomparticipant__left_at__isnull=True
    ).first()

    stats = {
        'online_users': VideoRoom.objects.filter(
            status__in=['waiting', 'active']
        ).aggregate(count=models.Count('participants'))['count'] or 0,
        'active_chats': VideoRoom.objects.filter(status='active').count(),
        'waiting_users': VideoRoom.objects.filter(status='waiting').count(),
    }

    context = {
        'current_room': current_room,
        'stats': stats,
    }
    return render(request, 'videocall/lobby.html', context)

@jwt_auth
def find_random_chat(request):
    """Enhanced random matching algorithm"""
    existing_room = VideoRoom.objects.filter(
        participants=request.user,
        status__in=['waiting', 'active'],
        roomparticipant__left_at__isnull=True
    ).first()

    if existing_room:
        return redirect('videocall:room', room_id=existing_room.id)

    preferences, created = UserPreferences.objects.get_or_create(user=request.user)

    available_rooms = VideoRoom.objects.filter(
        room_type='random',
        status='waiting',
        is_active=True
    ).exclude(participants=request.user)

    if preferences.location_based_matching and request.user.location:
        available_rooms = available_rooms.filter(
            Q(location_filter=request.user.location) | Q(location_filter='')
        )

    if available_rooms.exists():
        matched_room = random.choice(available_rooms)
        RoomParticipant.objects.create(user=request.user, room=matched_room)
        matched_room.status = 'active'
        matched_room.save()
        return JsonResponse({
            'status': 'matched',
            'room_id': str(matched_room.id),
            'redirect_url': f'/video/room/{matched_room.id}/'
        })
    else:
        new_room = VideoRoom.objects.create(
            name="Random Chat",
            created_by=request.user,
            room_type='random',
            location_filter=request.user.location or '',
            max_participants=2,
            status='waiting'
        )
        RoomParticipant.objects.create(user=request.user, room=new_room, is_host=True)
        return JsonResponse({
            'status': 'waiting',
            'room_id': str(new_room.id),
            'redirect_url': f'/video/room/{new_room.id}/'
        })

@jwt_auth
def room(request, room_id):
    """Enhanced room view"""
    room = get_object_or_404(VideoRoom, id=room_id, is_active=True)
    participant = RoomParticipant.objects.filter(
        user=request.user,
        room=room,
        left_at__isnull=True
    ).first()

    if not participant:
        if room.is_full:
            messages.error(request, "This room is full.")
            return redirect('videocall:lobby')
        RoomParticipant.objects.create(user=request.user, room=room)
        if room.current_participants_count == 2:
            room.status = 'active'
            room.save()

    messages_qs = ChatMessage.objects.filter(room=room)[:50]
    other_participants = room.participants.exclude(id=request.user.id)
    context = {
        'room': room,
        'messages': messages_qs,
        'other_participants': other_participants,
        'is_host': participant.is_host if participant else False,
    }
    return render(request, 'videocall/room.html', context)

@jwt_auth
def skip_chat(request, room_id):
    """Skip current chat and find new partner"""
    room = get_object_or_404(VideoRoom, id=room_id)
    participant = RoomParticipant.objects.filter(
        user=request.user,
        room=room,
        left_at__isnull=True
    ).first()

    if participant:
        participant.left_at = timezone.now()
        participant.save()
        if room.current_participants_count == 0:
            room.status = 'ended'
            room.ended_at = timezone.now()
            room.save()
        elif room.current_participants_count == 1:
            room.status = 'waiting'
            room.save()
        room.skip_count += 1
        room.save()

    return find_random_chat(request)

@jwt_auth
def end_chat(request, room_id):
    """End current chat session"""
    room = get_object_or_404(VideoRoom, id=room_id)
    participant = RoomParticipant.objects.filter(
        user=request.user,
        room=room,
        left_at__isnull=True
    ).first()

    if participant:
        participant.left_at = timezone.now()
        participant.save()
        if room.current_participants_count == 0:
            room.status = 'ended'
            room.ended_at = timezone.now()
            room.is_active = False
            room.save()

    return redirect('videocall:lobby')

@jwt_auth
def preferences(request):
    """User chat preferences"""
    preferences, created = UserPreferences.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        interests = request.POST.getlist('interests')
        preferences.interests = interests
        preferences.preferred_age_min = int(request.POST.get('age_min', 18))
        preferences.preferred_age_max = int(request.POST.get('age_max', 100))
        preferences.location_based_matching = bool(request.POST.get('location_based'))
        preferences.text_chat_only = bool(request.POST.get('text_only'))
        preferences.save()
        messages.success(request, "Preferences updated successfully!")
        return redirect('videocall:preferences')
    context = {'preferences': preferences}
    return render(request, 'videocall/preferences.html', context)

@jwt_auth
@require_GET
def room_status_api(request, room_id):
    """Returns JSON status of a given room"""
    try:
        room = VideoRoom.objects.get(id=room_id)
        return JsonResponse({
            "status": room.status,
            "participants": room.current_participants_count,
            "max_participants": room.max_participants
        })
    except VideoRoom.DoesNotExist:
        return JsonResponse({"error": "Room not found"}, status=404)

@jwt_auth
@require_POST
def find_match_api(request):
    """Finds or creates a random match"""
    existing = VideoRoom.objects.filter(
        participants=request.user,
        status__in=['waiting', 'active'],
        roomparticipant__left_at__isnull=True
    ).first()
    if existing:
        return JsonResponse({
            "status": "matched",
            "room_id": str(existing.id),
            "redirect_url": f"/video/room/{existing.id}/"
        })
    return find_random_chat(request)






@jwt_auth
def create_private_room(request, username):
    other_user = get_object_or_404(User, username=username)
    if other_user == request.user:
        messages.error(request, "Cannot start video call with yourself.")
        return redirect('accounts:profile')
    room = VideoRoom.objects.create(
        name=f"Private Chat: {request.user.username} & {other_user.username}",
        created_by=request.user,
        room_type='private',
        max_participants=2,
        status='waiting'
    )
    RoomParticipant.objects.create(user=request.user, room=room, is_host=True)
    RoomParticipant.objects.create(user=other_user, room=room)
    room.status = 'active'
    room.save()
    return redirect('videocall:room', room_id=room.id)