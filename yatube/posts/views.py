from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import pagination


@cache_page(20, key_prefix='index_page')
def index(request):
    posts = Post.objects.all()
    return render(request, 'posts/index.html', {
        'page_obj': pagination(request, posts),
    })


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    return render(request, 'posts/group_list.html', {
        'group': group, 'page_obj': pagination(request, posts)
    })


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.posts.all()
    follow = False
    if ((request.user.is_authenticated)
        and Follow.objects.filter(
            user=request.user, author=author).exists()):
        follow = True
    return render(request, 'posts/profile.html', {
        'author': author, 'page_obj': pagination(request, posts),
        'following': follow
    })


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    comments = Comment.objects.filter(post_id=post_id)
    return render(request, 'posts/post_detail.html', {
        'posts': post,
        'post': post,
        'form': form,
        'comments': comments,
    })


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    post = form.save(commit=False)
    post.author = request.user
    post.save()
    return redirect('posts:profile', post.author)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post.pk)
    return render(request, 'posts/create_post.html', {
        'is_edit': True, 'form': form, 'post_id': post_id,
    })


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    follow = Post.objects.filter(author__following__user=request.user)
    return render(request, 'posts/follow.html', {
        'page_obj': pagination(request, follow),
    })


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(
            user=request.user, author=author
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)


def page_not_found(request, exception):
    return render(request, 'error_pages/404.html', {
        'path': request.path}, status=404)


def permission_denied(request, reason=''):
    return render(request, 'error_pages/403csrf.html')


def server_error(request):
    return render(request, 'error_pages/500.html', status=500)
