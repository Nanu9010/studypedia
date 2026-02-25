from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.db.models import Exists, OuterRef
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from django_ratelimit.decorators import ratelimit

from .models import User, Follow
from .forms import SignUpForm, LoginForm, ProfileForm
from ecommerce.models import PurchaseRequest, Order
from social.models import Post
from notifications.models import Notification


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def is_staff(user):
    return user.is_staff

def jwt_auth(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        token = request.COOKIES.get('access_token')
        if token:
            try:
                validated_token = AccessToken(token)
                user_id = validated_token['user_id']
                request.user = User.objects.get(id=user_id)
                login(request, request.user)
                return view_func(request, *args, **kwargs)
            except TokenError:
                refresh_token = request.COOKIES.get('refresh_token')
                if refresh_token:
                    try:
                        refresh = RefreshToken(refresh_token)
                        new_access = str(refresh.access_token)
                        request.user = User.objects.get(id=refresh['user_id'])
                        login(request, request.user)
                        response = view_func(request, *args, **kwargs)
                        response.set_cookie(
                            key='access_token',
                            value=new_access,
                            httponly=True,
                            secure=not settings.DEBUG,
                            samesite='Strict'
                        )
                        return response
                    except TokenError:
                        return redirect('accounts:login')
                return redirect('accounts:login')
        return redirect('accounts:login')

    return wrapper


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            tokens = get_tokens_for_user(user)
            response = redirect('core:home')
            response.set_cookie(key='refresh_token', value=tokens['refresh'], httponly=True, secure=not settings.DEBUG,
                                samesite='Strict')
            response.set_cookie(key='access_token', value=tokens['access'], httponly=True, secure=not settings.DEBUG,
                                samesite='Strict')
            messages.success(request, 'Account created successfully!')
            return response
        else:
            messages.error(request, 'Error creating account. Please check your details.')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            tokens = get_tokens_for_user(user)
            response = redirect('core:home')
            response.set_cookie(key='refresh_token', value=tokens['refresh'], httponly=True, secure=not settings.DEBUG,
                                samesite='Strict')
            response.set_cookie(key='access_token', value=tokens['access'], httponly=True, secure=not settings.DEBUG,
                                samesite='Strict')
            messages.success(request, f'Welcome back, {user.username}!')
            return response
        else:
            messages.error(request, 'Invalid username/email or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@jwt_auth
def profile(request, username=None):
    if username:
        user = get_object_or_404(User, username=username)
        is_own_profile = False
    else:
        user = request.user
        is_own_profile = True

    posts = Post.objects.filter(user=user).select_related('user').prefetch_related('comments')
    purchases = PurchaseRequest.objects.filter(user=user).select_related('content_type')[:10] if is_own_profile else []
    orders = Order.objects.filter(user=user).prefetch_related('items')[:10] if is_own_profile else []
    notifications = Notification.objects.filter(recipient=user)[:10] if is_own_profile else []

    followers = request.user.followers.all().order_by('id')
    following = request.user.following.all().order_by('id')

    followers_paginator = Paginator(followers, 10)
    following_paginator = Paginator(following, 10)
    followers_page = followers_paginator.get_page(request.GET.get('followers_page'))
    following_page = following_paginator.get_page(request.GET.get('following_page'))

    is_following = request.user.following.filter(pk=user.pk).exists() if request.user != user else False

    context = {
        'profile_user': user,
        'posts': posts,
        'purchases': purchases,
        'orders': orders,
        'notifications': notifications,
        'followers_page': followers_page,
        'following_page': following_page,
        'is_following': is_following,
        'is_own_profile': is_own_profile,
        'form': ProfileForm(instance=user) if is_own_profile else None,
        'stats': {
            'total_purchases': PurchaseRequest.objects.filter(user=user, status='paid').count(),
            'pending_purchases': PurchaseRequest.objects.filter(user=user, status='pending').count(),
            'follower_count': user.follower_count(),
            'following_count': user.following_count(),
        }
    }
    return render(request, 'accounts/profile.html', context)


@jwt_auth
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Error updating profile.')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/edit_profile.html', {'form': form})







@jwt_auth
@require_POST
@ratelimit(key='user', rate='5/m', method='POST', block=True)
def follow_user(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        return JsonResponse({'error': 'Cannot follow yourself'}, status=400)
    if request.user.following.filter(pk=user_to_follow.pk).exists():
        request.user.following.remove(user_to_follow)
        following = False
        messages.success(request, f'You unfollowed @{user_to_follow.username}')
    else:
        request.user.following.add(user_to_follow)
        following = True
        messages.success(request, f'You followed @{user_to_follow.username}')
    return JsonResponse({
        'following': following,
        'followers_count': user_to_follow.follower_count()
    })


def logout_view(request):
    response = redirect('core:home')
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return response