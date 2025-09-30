from django.urls import path
from . import views

app_name = 'social'

urlpatterns = [
    path('', views.social, name='social'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('create/', views.create_post, name='create_post'),
    path('edit/<int:pk>/', views.edit_post, name='edit_post'),
    path('delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('comment/<int:pk>/', views.add_comment, name='add_comment'),

]