from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .constants import PAGINATE_PAGE_COUNT
from .forms import CommentForm, PostCreateForm, UserCreateForm
from .models import Category, Comment, Post
from .utils import (get_object_from_query, get_query_all_posts,
                    get_query_published_posts)

User = get_user_model()


class SuccessURLMixin:
    def get_success_url(self):
        username = self.request.user
        return reverse('blog:profile', kwargs={'username': username})


class UserListView(ListView):
    model = Post
    author = None
    template_name = 'blog/profile.html'
    paginate_by = PAGINATE_PAGE_COUNT
    slug_url_kwargs = 'username'
    queryset = get_query_all_posts(model.objects)

    def get_object(self):
        return get_object_from_query(
            User,
            username=self.kwargs[self.slug_url_kwargs])

    def get_queryset(self):
        self.author = self.get_object()
        if self.author == self.request.user:
            return self.queryset.filter(author=self.author)
        return super().get_queryset().filter(
            author=self.author, is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_object()
        return context


class UserUpdateViews(SuccessURLMixin, LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserCreateForm
    template_name = 'blog/user.html'

    def get_object(self):
        return self.request.user


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    ordering = '-created_at'
    paginate_by = PAGINATE_PAGE_COUNT
    queryset = get_query_published_posts(model.objects)

    def get_queryset(self):
        return self.queryset


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = get_object_from_query(
            Post,
            id=self.kwargs[self.pk_url_kwarg]
        )
        if post.author != self.request.user:
            if not (post.is_published
                    and post.category.is_published
                    and post.pub_date <= timezone.now()):
                raise Http404('Page not published')
        context['comments'] = post.comments.select_related(
            'author')
        context['form'] = CommentForm()
        return context


class CategoryListView(ListView):
    model = Category
    template_name = 'blog/category.html'
    slug_url_kwarg = 'category_slug'
    category = None
    paginate_by = PAGINATE_PAGE_COUNT

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.category = get_object_from_query(
            self.model,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True
        )
        context['category'] = self.category
        return context

    def get_queryset(self, *args, **kwargs):
        self.category = get_object_from_query(
            self.model,
            slug=self.kwargs[self.slug_url_kwarg],
            is_published=True
        )
        return get_query_published_posts(self.category.posts)


class PostCreateView(SuccessURLMixin, LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'id'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'id': self.kwargs[self.pk_url_kwarg]})

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_from_query(
            Post, id=self.kwargs[self.pk_url_kwarg])

        if instance.author != request.user:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = PostCreateForm
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_from_query(Post, id=kwargs[self.pk_url_kwarg])
        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.object)
        return context


class CommentMixin(LoginRequiredMixin):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_from_query(Comment, id=kwargs[self.pk_url_kwarg])

        if instance.author != request.user:
            return redirect('blog:index')
        return super().dispatch(request, *args, **kwargs)


class CommentUpdateView(CommentMixin, UpdateView):
    """Редактирование комментария."""


class CommentDeleteView(CommentMixin, DeleteView):
    """Удаление комментария."""


@login_required
def add_comment(request, post_id):
    post = get_object_from_query(Post, id=post_id)

    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)
