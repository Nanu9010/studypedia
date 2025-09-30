from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle-staff/<int:user_id>/', views.toggle_staff, name='toggle_staff'),
    path('toggle-active/<int:user_id>/', views.toggle_active, name='toggle_active'),
]