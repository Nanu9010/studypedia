from django.urls import path
from . import views
from papers import views as papers_views
from notes import views as notes_views
from roadmaps import views as roadmaps_views
from university import views as university_views
from core import views as core_views
from . import views as admin_views
app_name = "university"   # <-- this line is required

urlpatterns = [
    # Universities
    path('universities/create/', university_views.university_create, name='university_create'),
    path('universities/', university_views.university_list, name='university_list'),
    path('universities/<int:pk>/delete/', university_views.university_delete, name='university_delete'),
    path('universities/<int:pk>/update/', university_views.university_update, name='university_update'),

    # Degrees
    path('degrees/create/', university_views.degree_create, name='degree_create'),
    path('degrees/', university_views.degree_list, name='degree_list'),
    path('degrees/<int:pk>/delete/', university_views.degree_delete, name='degree_delete'),
    path('degrees/<int:pk>/update/', university_views.degree_update, name='degree_update'),

    # Branches
    path('branches/create/', university_views.branch_create, name='branch_create'),
    path('branches/', university_views.branch_list, name='branch_list'),
    path('branches/<int:pk>/delete/', university_views.branch_delete, name='branch_delete'),
    path('branches/<int:pk>/update/', university_views.branch_update, name='branch_update'),






    # add other urls...
]
