# papers/urls.py
from django.urls import path
from . import views

app_name = 'papers'

urlpatterns = [
    path('', views.paper_list, name='paper_list'),
    path('create/', views.paper_create, name='paper_create'),
    path('<int:pk>/delete/', views.paper_delete, name='paper_delete'),
    path('<int:pk>/update/', views.paper_update, name='paper_update'),
]