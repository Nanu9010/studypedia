# adminapp/urls.py
from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
]