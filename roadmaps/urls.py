# roadmaps/urls.py
from django.urls import path
from . import views

app_name = 'roadmaps'

urlpatterns = [
    path('', views.roadmap_list, name='roadmap_list'),
    path('create/', views.roadmap_create, name='roadmap_create'),
    path('<int:pk>/edit/', views.roadmap_update, name='roadmap_update'),
    path('<int:pk>/delete/', views.roadmap_delete, name='roadmap_delete'),


    path('syllabi/', views.syllabus_list, name='syllabus_list'),
    path('syllabi/create/', views.syllabus_create, name='syllabus_create'),
    path('syllabi/<int:pk>/edit/', views.syllabus_update, name='syllabus_update'),
    path('syllabi/<int:pk>/delete/', views.syllabus_delete, name='syllabus_delete'),
]