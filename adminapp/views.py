from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.utils import timezone
from django.db.models import Sum
from accounts.models import User
from ecommerce.models import Order, Coupon
from university.models import University, Degree, Branch
from papers.models import Paper
from notes.models import Note
from roadmaps.models import Roadmap, Syllabus
from .forms import CouponForm  # Add this form (below)

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def dashboard(request):
    # Existing context
    context = {
        'users_count': User.objects.count(),
        'orders_count': Order.objects.count(),
        'universities_count': University.objects.count(),
        'degrees_count': Degree.objects.count(),
        'branches_count': Branch.objects.count(),
        'papers_count': Paper.objects.count(),
        'notes_count': Note.objects.count(),
        'roadmaps_count': Roadmap.objects.count(),
        'syllabi_count': Syllabus.objects.count(),
    }

    # Recent Users (last 10 by created_at or last_login)
    recent_users = User.objects.order_by('-last_login')[:10]  # Or '-created_at' for signups
    for user in recent_users:
        user.orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        user.total_spent = user.orders.aggregate(total=Sum('total_amount'))['total'] or 0

    context['recent_users'] = recent_users

    # Coupons
    if request.method == 'POST':
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('adminapp:dashboard')
    else:
        form = CouponForm()

    coupons = Coupon.objects.all()
    context['coupons'] = coupons
    context['coupon_form'] = form

    return render(request, 'adminapp/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def toggle_staff(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = not user.is_staff
    user.save()
    messages.success(request, f'User {user.username} staff status toggled.')
    return redirect('adminapp:dashboard')

@user_passes_test(lambda u: u.is_superuser)
def toggle_active(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    messages.success(request, f'User {user.username} activation status toggled.')
    return redirect('adminapp:dashboard')