from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from django.db.models import Case, When, IntegerField, Q
from .models import Post, Comment
from notifications.models import Notification
from messenger.models import Message
from messenger.models import ChatRoom
from .forms import PostForm, CommentForm
from messenger.forms import MessageForm
from accounts.views import jwt_auth
from django_ratelimit.decorators import ratelimit
from django.db.models import Exists, OuterRef

from accounts.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Comment
from .forms import PostForm, CommentForm
from django_ratelimit.decorators import ratelimit
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@login_required
def social(request):
    search_query = request.GET.get('q', '').strip()
    posts = Post.objects.select_related('user').prefetch_related('comments')
    if search_query:
        posts = posts.filter(
            Q(user__username__icontains=search_query) | Q(content__icontains=search_query)
        ).distinct()
    paginator = Paginator(posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('social_feed', {
                'type': 'new_post',
                'post_id': post.id,
                'content': post.content,
                'username': post.user.username,
                'image': post.image.url if post.image else '',
                'created_at': post.created_at.isoformat()
            })
            messages.success(request, 'Post created!')
            return redirect('social:social_feed')
    else:
        form = PostForm()
    return render(request, 'social/social_feed.html', {'page_obj': page_obj, 'form': form, 'search_query': search_query})

@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    comments = post.comments.select_related('user').order_by('created_at')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)('social_feed', {
                'type': 'new_comment',
                'comment_id': comment.id,
                'content': comment.content,
                'username': comment.user.username,
                'post_id': post.id,
                'created_at': comment.created_at.isoformat()
            })
            messages.success(request, 'Comment added!')
            return redirect('social:post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'social/post_detail.html', {'post': post, 'comments': comments, 'form': form})

# @jwt_auth
# def social(request):
#     posts = Post.objects.select_related('user').prefetch_related('comments')
#     search_query = request.GET.get('q', '').strip()
#     if search_query:
#         posts = posts.filter(
#             Q(content__icontains=search_query) |
#             Q(user__username__icontains=search_query)
#         )
#     if request.user.is_authenticated:
#         followed_users = request.user.following.all()
#         posts = posts.order_by(
#             Case(
#                 When(user__in=followed_users, then=0),
#                 default=1,
#                 output_field=IntegerField()
#             ),
#             '-created_at'
#         ).annotate(
#             is_own=Exists(Post.objects.filter(user=request.user, id=OuterRef('pk')))
#         )
#     else:
#         posts = posts.order_by('-created_at')
#
#     paginator = Paginator(posts, 10)
#     page_obj = paginator.get_page(request.GET.get('page'))
#     context = {
#         'page_obj': page_obj,
#         'post_form': PostForm(),
#         'search_query': search_query
#     }
#     return render(request, 'social/social_feed.html', context)
#
# @jwt_auth
# def post_detail(request, pk):
#     post = get_object_or_404(Post, pk=pk)
#     comments = post.comments.select_related('user')
#     context = {
#         'post': post,
#         'comments': comments,
#         'comment_form': CommentForm(),
#         'is_owner': post.user == request.user
#     }
#     return render(request, 'social/post_detail.html', context)

@jwt_auth
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()
            messages.success(request, 'Post created!')
            return redirect('social:social')
    else:
        form = PostForm()
    return render(request, 'social/create_post.html', {'form': form})

@jwt_auth
def edit_post(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Post updated!')
            return redirect('social:post_detail', pk=pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'social/edit_post.html', {'form': form})

@jwt_auth
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, user=request.user)
    post.delete()
    messages.success(request, 'Post deleted!')
    return redirect('social:social')

@jwt_auth
@require_POST
@ratelimit(key='user', rate='5/m', method='POST', block=True)
def add_comment(request, pk):
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.post = post
        comment.save()
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)('social_feed', {
            'type': 'new_comment',
            'comment_id': comment.id,
            'content': comment.content,
            'username': comment.user.username,
            'post_id': post.id,
            'created_at': comment.created_at.isoformat()
        })
        Notification.objects.create(
            recipient=post.user,
            sender=request.user,
            type='comment',
            related_post=post,
            related_comment=comment
        )
        messages.success(request, 'Comment added!')
    return redirect('social:post_detail', pk=pk)

