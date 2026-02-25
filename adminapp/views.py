

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils import timezone
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.db.models.functions import TruncMonth, TruncDay
from django.db.models import Q
from ecommerce.models import Order, Coupon
from university.models import University, Degree, Branch
from papers.models import Paper
from notes.models import Note
from roadmaps.models import Roadmap, Syllabus
from .forms import CouponForm, UserBulkActionForm
import csv
from datetime import timedelta

from accounts.models import User

def is_staff(user):
    return user.is_staff

@login_required
@user_passes_test(is_staff)
def dashboard(request):
    # Base stats
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

    # Analytics (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    from django.db.models import Q

    signups = User.objects.filter(
        Q(created_at__gte='1970-01-01') & Q(created_at__lte=end_date)
    ).annotate(date=TruncDay('created_at')).values('date').annotate(count=Count('id'))

    logins = User.objects.filter(
        Q(last_login__gte='1970-01-01') & Q(last_login__lte=end_date)
    ).annotate(date=TruncDay('last_login')).values('date').annotate(count=Count('id'))


    orders = Order.objects.filter(created_at__range=(start_date, end_date)).annotate(date=TruncDay('created_at')).values('date').annotate(count=Count('id'), total=Sum('total_amount'))

    context.update({
        'signups': list(signups),
        'logins': list(logins),
        'orders': list(orders),
    })

    # Recent Users (paginated)
    recent_users = User.objects.order_by('-last_login')[:20]  # Top 20
    for user in recent_users:
        user.orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
        user.total_spent = user.orders.aggregate(total=Sum('total_amount'))['total'] or 0
    paginator = Paginator(recent_users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context['users_page'] = page_obj

    # Coupons
    if request.method == 'POST' and 'coupon_submit' in request.POST:
        form = CouponForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coupon created successfully!')
            return redirect('adminapp:dashboard')
        else:
            messages.error(request, 'Invalid coupon data.')
    else:
        form = CouponForm()
    coupons = Coupon.objects.all()
    context['coupons'] = coupons
    context['coupon_form'] = form

    # Order Stats
    order_status_counts = Order.objects.values('status').annotate(count=Count('id'))
    total_revenue = Order.objects.filter(status='paid').aggregate(total=Sum('total_amount'))['total'] or 0
    context.update({
        'order_status_counts': order_status_counts,
        'total_revenue': total_revenue,
    })

    # Bulk Actions
    if request.method == 'POST' and 'bulk_action' in request.POST:
        form = UserBulkActionForm(request.POST, queryset=recent_users)
        if form.is_valid():
            action = form.cleaned_data['action']
            user_ids = request.POST.getlist('selected_users')
            users = User.objects.filter(id__in=user_ids)
            if action == 'activate':
                users.update(is_active=True)
                messages.success(request, f'Activated {len(users)} users.')
            elif action == 'deactivate':
                users.update(is_active=False)
                messages.success(request, f'Deactivated {len(users)} users.')
            elif action == 'make_staff':
                users.update(is_staff=True)
                messages.success(request, f'Made {len(users)} users staff.')
            elif action == 'remove_staff':
                users.update(is_staff=False)
                messages.success(request, f'Removed staff status from {len(users)} users.')
            return redirect('adminapp:dashboard')
    bulk_form = UserBulkActionForm(queryset=recent_users)
    context['bulk_form'] = bulk_form

    return render(request, 'adminapp/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_users(request):
    users = User.objects.all().values('username', 'email', 'is_staff', 'is_active', 'created_at', 'last_login')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Username', 'Email', 'Is Staff', 'Is Active', 'Joined At', 'Last Login'])
    for user in users:
        writer.writerow([user['username'], user['email'], user['is_staff'], user['is_active'], user['created_at'], user['last_login']])
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_orders(request):
    orders = Order.objects.all().select_related('user').values('id', 'user__username', 'total_amount', 'status', 'created_at', 'paid_at')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="orders_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order ID', 'Username', 'Total Amount', 'Status', 'Created At', 'Paid At'])
    for order in orders:
        writer.writerow([order['id'], order['user__username'], order['total_amount'], order['status'], order['created_at'], order['paid_at']])
    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def reset_credits(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.credits = 0
    user.save()
    messages.success(request, f'Reset credits for {user.username} to 0.')
    return redirect('adminapp:dashboard')



@login_required
@user_passes_test(lambda u: u.is_superuser)
def toggle_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.is_active = not coupon.is_active
    coupon.save()
    messages.success(request, f'Coupon {coupon.code} toggled.')
    return redirect('adminapp:dashboard')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.delete()
    messages.success(request, f'Coupon {coupon.code} deleted.')
    return redirect('adminapp:dashboard')



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