from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.index, name='index'),
    path('posts/<int:id>/', views.PostDetailView.as_view(),
         name='post_detail'),
    path('category/<slug:category_slug>/', views.category_posts,
         name='category_posts'),
    path('posts/create/', views.create_post, name='create_post'),
    path('blog/profile/<str:username>/', views.profile, name='profile'),
    path('login_only/', views.simple_view),
    path('posts/<int:post_id>/edit/', views.post_edit, name='edit_post'),
    path('posts/<post_id>/comment/', views.add_comment, name='add_comment'),
    path('posts/<post_id>/edit_comment/<comment_id>/', views.edit_comment, name='edit_comment'),
    path('posts/<post_id>/delete/', views.confirm_delete_post, name='delete_post'),
    path('posts/<post_id>/delete_comment/<comment_id>/', views.confirm_delete_comment, name='delete_comment'),
]
