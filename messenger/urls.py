from django.urls import path
from . import views

app_name = 'messenger'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<int:room_id>/', views.chat_room, name='chat_room'),
    path('room/<int:room_id>/send/', views.send_message, name='send_message'),
    path('start/<str:username>/', views.start_chat, name='start_chat'),
    path('create-group/', views.create_group_chat, name='create_group_chat'),
]