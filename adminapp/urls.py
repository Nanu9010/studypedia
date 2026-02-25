from django.urls import path
from . import views

app_name = 'adminapp'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('toggle-staff/<int:user_id>/', views.toggle_staff, name='toggle_staff'),
    path('toggle-active/<int:user_id>/', views.toggle_active, name='toggle_active'),
    path('export-users/', views.export_users, name='export_users'),
    path('export-orders/', views.export_orders, name='export_orders'),
    path('reset-credits/<int:user_id>/', views.reset_credits, name='reset_credits'),
    path('toggle-coupon/<int:coupon_id>/', views.toggle_coupon, name='toggle_coupon'),
    path('delete-coupon/<int:coupon_id>/', views.delete_coupon, name='delete_coupon'),
]