from django import template
from django.db.models import Count
from ..models import Post
from django.utils.safestring import mark_safe
import markdown

register = template.Library()

@register.simple_tag
def total_posts() -> int :
    return Post.published.count()

@register.inclusion_tag('blog/post/latest_posts.html')
def show_latest_posts(count=5) -> dict:
    latest_posts = Post.published.order_by("-publish")[:count]
    return {'latest_posts': latest_posts}

@register.simple_tag
def get_most_commented_posts(count=5) -> list[ Post ]:
    return Post.published.annotate(
        total_comments=Count('comments')
    ).order_by('-total_comments')[:count]

@register.filter(name='markdown')
def markdown_format(text) -> str:
    return mark_safe(markdown.markdown(text))