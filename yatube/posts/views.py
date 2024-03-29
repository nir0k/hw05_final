from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import pagi


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    post_list = group.posts.all()
    context = {
        'title': group.title,
        'page_obj': pagi(request, post_list, POSTS_PER_PAGE),
        'description': group.description,
    }
    return render(
        request,
        template,
        context,
    )


@cache_page(20)
def index(request):
    template = 'posts/index.html'
    title = 'Последние обновления на сайте'
    post_list = Post.objects.all()
    context = {
        'title': title,
        'page_obj': pagi(request, post_list, POSTS_PER_PAGE),
    }
    return render(
        request,
        template,
        context
    )


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if not User.objects.filter(pk=request.user.id).exists():
        post_list = author.author_posts.all()
        title = 'Профайл пользователя'
        context = {
            'title': title,
            'page_obj': pagi(request, post_list, POSTS_PER_PAGE),
            'author': author,
            'posts_count': post_list.count(),
        }
        return render(request, 'posts/profile.html', context)
    curent_user = get_object_or_404(User, username=request.user.username)
    following = curent_user.follower.filter(author=author)
    follower = following.exists()
    post_list = author.author_posts.all()
    title = 'Профайл пользователя'
    if request.method == 'POST':
        profile_follow(data=request.POST)
    context = {
        'title': title,
        'page_obj': pagi(request, post_list, POSTS_PER_PAGE),
        'author': author,
        'curent_user': curent_user,
        'posts_count': post_list.count(),
        'following': follower,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    comments = post.comments.all()
    if request.method == 'POST':
        form = post_create(data=request.POST)
    else:
        form = CommentForm()
    context = {
        'post': post,
        'posts_count': posts_count,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    if request.method != 'POST':
        form = PostForm()
        return render(
            request,
            template,
            {'form': form},
        )
    form = PostForm(
        request.POST or None,
        files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.text = form.cleaned_data['text']
        post.save()
        return redirect('posts:profile', request.user)
    return render(
        request,
        template,
        {'form': form},
    )


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post,)
    context = {
        'post': post,
        'form': form,
        'is_edit': True,
    }
    if request.method != 'POST':
        return render(request, 'posts/create_post.html', context)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.text = form.cleaned_data['text']
        post.group = form.cleaned_data['group']
        post.image = form.cleaned_data['image']
        post.save()
        return redirect('posts:post_detail', post_id=post_id)
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.text = form.cleaned_data['text']
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = 'Последние обновления в подписках'
    user = get_object_or_404(User, username=request.user)
    following = user.follower.values_list('author')
    post_list = Post.objects.filter(author__in=following)
    context = {
        'title': title,
        'page_obj': pagi(request, post_list, POSTS_PER_PAGE),
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    curent_user = get_object_or_404(User, username=request.user.username)
    if author == curent_user:
        return redirect(template, author)
    following = curent_user.follower.filter(author=author)
    if not following.exists():
        Follow.objects.create(user=curent_user, author=author)
    return redirect(template, author)


@login_required
def profile_unfollow(request, username):
    template = 'posts:profile'
    author = get_object_or_404(User, username=username)
    curent_user = get_object_or_404(User, username=request.user.username)
    if author == curent_user:
        return redirect(template, author)
    following = curent_user.follower.filter(author=author)
    if following.exists():
        Follow.objects.get(user=curent_user, author=author).delete()
    return redirect(template, author)
