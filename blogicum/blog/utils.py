from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.utils import timezone


def get_query_all_posts(model):
    return model.select_related(
        'category',
        'location',
        'author'
    ).annotate(
        comment_count=Count('comments')
    ).order_by('-pub_date')


def get_query_published_posts(model):
    return get_query_all_posts(model).filter(
        is_published=True,
        pub_date__lt=timezone.now(),
        category__is_published=True
    )


def get_object_from_query(model, **kwargs):
    return get_object_or_404(model, **kwargs)
