# notes/urls.py
from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('notes/', views.note_list, name='note_list'),
    path('notes/create/', views.note_create, name='note_create'),
    path('notes/<int:pk>/delete/', views.note_delete, name='note_delete'),
    path('notes/<int:pk>/update/', views.note_update, name='note_update'),
]