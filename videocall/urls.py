from django.urls import path
from . import views

app_name = 'videocall'

urlpatterns = [
    path('', views.lobby, name='lobby'),
    path('find-random/', views.find_random_chat, name='find_random'),
    path('room/<uuid:room_id>/', views.room, name='room'),
    path('skip/<uuid:room_id>/', views.skip_chat, name='skip_chat'),
    path('end/<uuid:room_id>/', views.end_chat, name='end_chat'),
    path('preferences/', views.preferences, name='preferences'),

    path('create-room/<str:username>/', views.create_private_room, name='create_private_room'),
    path('api/room-status/<uuid:room_id>/', views.room_status_api, name='room_status_api'),
    path('api/find-match/', views.find_match_api, name='find_match_api'),
]