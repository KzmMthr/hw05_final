import datetime as dt

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


@cache_page(20)
def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
        )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    following = None
    if request.user != author and request.user.is_active:
        if Follow.objects.filter(user=request.user, author=author):
            following = True
        else:
            following = False
    post_list = Post.objects.filter(author=author)
    post_count = Post.objects.filter(author=author).count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'profile.html',
        {'page': page, 'paginator': paginator, 'post_count': post_count, 'following': following,
         'author': author, }
        )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, 'group.html',
        {'group': group, 'paginator': paginator, 'page': page}
        )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id)
    post_count = Post.objects.filter(author=author).count()
    form = CommentForm(request.POST)
    items = Comment.objects.filter(post=post)
    following = None
    if request.user.is_active:
        user = request.user
        if Follow.objects.filter(user=user, author=author):
            following = True
    return render(
        request, 'post.html',
        {'post': post, 'post_count': post_count, 'post_id': post_id,
         'author': author, 'form': form, 'items': items, }
        )


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    group = post.group
    form = PostForm(instance=post)
    action = 'edit'
    if request.method == "POST":
        form = PostForm(request.POST, files=request.FILES or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('post', username=username, post_id=post_id)
    return render(
        request, 'new_post.html',
        {'form': form, 'action': action, 'post': post, 'group': group, }
        )


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None,)
    action = 'new'
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('index')
    return render(request, 'new_post.html', {'form': form, 'action': action, })


@login_required
def follow_index(request):
    authors = Follow.objects.select_related('author').filter(user=request.user).values_list('author')
    post_list = Post.objects.filter(author__in=authors).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request, "follow.html",
        {'post_list': post_list, 'page': page, 'paginator': paginator}
        )


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    if not Follow.objects.filter(user=user, author=author).exists() and author != user:
        Follow.objects.create(user=request.user, author=author)
    return redirect('profile', username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('profile', username)


@login_required
def add_comment(request, username, post_id):
    form = CommentForm(request.POST)
    if form.is_valid():
        add_comment = form.save(commit=False)
        add_comment.post = get_object_or_404(Post, id=post_id)
        add_comment.author = request.user
        add_comment.save()
    return redirect('post', username=username, post_id=post_id,)


def year(request):
    date = dt.datetime.now().year
    return {'year': date}


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
