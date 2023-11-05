from datetime import date
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404
from blog.models import Post, Category, Comment
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from .forms import CommentForm, PostForm
from django.views.generic import DetailView


POST_LIMIT = 5

User = get_user_model()


def get_posts_qs(**filter_fields):
    return Post.objects.all().filter(
        is_published=True, category__is_published=True,
        pub_date__lte=date.today(), **filter_fields)


def index(request):
    # posts = get_posts_qs()[:POST_LIMIT]
    # context = {'posts': posts, }
    posts = Post.objects.order_by('id')
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    template = 'blog/index.html'
    return render(request, template, context)


def post_detail(request, id):
    template = 'blog/detail.html'
    post = get_object_or_404(
        get_posts_qs(),
        id=id)
    form = CommentForm(request.POST)
    context = {'post': post, 'form': form, }
    return render(request, template, context)


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category.objects.filter(is_published=True), slug=category_slug)
    posts = get_posts_qs(category__title=category)
    context = {'category': category, 'posts': posts, }
    return render(request, template, context)


@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user  # Привязываем автора поста к текущему пользователю.
            post.save()
            return redirect('blog:post_detail', id=post.id)  # После создания перенаправляем на страницу с подробностями поста.
    else:
        form = PostForm()  # Создаем пустую форму для создания поста.

    context = {'form': form}
    return render(request, 'blog/create.html', context)


@login_required
def profile(request, username):
    try:
        user = User.objects.get(username=username)
        template = 'blog/profile.html'
        return render(request, template, {'username': user})
    except User.DoesNotExist:
        raise Http404("Пользователь не найден")


@login_required
def simple_view(request):
    return HttpResponse('Страница для залогиненных пользователей!')



def post_edit(request, post_id):
    template = 'blog/create.html'
    post = get_object_or_404(
        get_posts_qs(),
        id=post_id)
    context = {'post': post, }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    # context = {'form': form }
    return redirect('blog:post_detail', id=post_id)


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context

    def get_object(self, queryset=None):
        # Извлекаем значение параметра 'id' из URL.
        id = self.kwargs.get('id')
        queryset = self.get_queryset()
        obj = queryset.get(id=id)
        return obj


@login_required
def edit_comment(request, post_id, comment_id):
    # Получаем комментарий, который нужно отредактировать
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        # Если запрос методом POST, значит, пользователь отправил форму с изменениями.
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            # Если форма валидна, сохраняем изменения.
            form.save()
            return redirect('blog:post_detail', post_id)  # Перенаправляем пользователя на страницу с постом.

    else:
        # Если запрос не методом POST, значит, это GET-запрос, и мы отображаем форму для редактирования комментария.
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {'form': form})


def confirm_delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'blog/comment.html', {'object': post})


def confirm_delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    return render(request, 'blog/comment.html', {'object': comment})


