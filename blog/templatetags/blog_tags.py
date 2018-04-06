from django import template
from django.db.models.aggregates import Count
from ..models import Post, Category, Tag


register = template.Library()
@register.simple_tag
def get_recent_posts(num=5):
    """获得最新5篇文章"""
    return Post.objects.all().order_by('-created_time')[:num]


@register.simple_tag
def archives():
    """归档"""
    return Post.objects.dates('created_time', 'month', order='DESC')


@register.simple_tag
def get_categories():
    """分类模版"""
    return Category.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)


@register.simple_tag
def get_tags():
    return Tag.objects.annotate(num_posts=Count('post')).filter(num_posts__gt=0)
