# ===== core/urls.py =====
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [

    path('', views.home, name='home'),

    path('about/', views.about, name='about'),
    path('api/cascade-filters/', views.cascade_filters_api, name='cascade_filters_api'),
    path('search/', views.search_view, name='search'),
]