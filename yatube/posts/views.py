from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def Pg(request, objects):
    paginator = Paginator(objects, settings.POP)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20)
def index(request):
    post_list = Post.objects.all().order_by('-pub_date')
    page_obj = Pg(request, post_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_list(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')
    page_obj = Pg(request, posts)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user_p = get_object_or_404(User, username=username)
    posts = user_p.posts.all()
    user = request.user
    following = user.is_authenticated and user_p.following.exists()
    paginator = Paginator(posts, settings.POP)
    page_obj = Pg(request, posts)
    count = paginator.count

    context = {
        'count': count,
        'user_p': user_p,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    group = post.group
    author = post.author
    count = Post.objects.filter(author=author).count()
    text_30 = post.text[0:30]
    comments = post.comments.all()
    new_comment = None
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.post = post
            new_comment.save()
    else:
        form = CommentForm()

    context = {
        'count': count,
        'group': group,
        'post': post,
        'text_30': text_30,
        'comments': comments,
        'new_comment': new_comment,
        'form': form
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def add_comment(request, post_id):
    # Получите пост
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        npost = form.save(commit=False)
        npost.author = request.user
        npost.save()
        success_url = reverse_lazy(
            'posts:profile', args=[request.user.username]
        )
        return redirect(success_url)
    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    login_author = request.user
    is_edit = True
    if login_author != author:
        return redirect('posts:post_detail', post_id)
    form = PostForm(request.POST or None,
                    files=request.FILES or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id)
    context = {
        'form': form,
        'post_pk': post_id,
        'is_edit': is_edit
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def follow_index(request):
    posts_list = Post.objects.filter(author__following__user=request.user)
    page_obj = Pg(request, posts_list)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """ Подписка """
    author = User.objects.get(username=username)
    user = request.user
    if Follow.objects.filter(
        user=user, author=author
    ).exists() or author == user:
        return redirect(reverse_lazy(
            'posts:profile', args=[username]
        ))
    else:
        Follow.objects.create(user=user, author=author)
        return redirect(
            'posts:profile',
            username=username
        )
    return redirect(reverse_lazy(
        'posts:profile', args=[username]
    ))


@login_required
def profile_unfollow(request, username):
    user = request.user
    Follow.objects.filter(user=user, author__username=username).delete()
    return redirect(reverse_lazy(
        'posts:profile', args=[username]
    ))
