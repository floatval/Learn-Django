from django.contrib import admin
from blog.feeds import AllPostsRssFeed
from django.urls import include, path
from django.conf.urls import url

urlpatterns = [
    path('admin/', admin.site.urls),
    path(r'', include('blog.urls', namespace='blog')),
    path(r'', include('comments.urls', namespace='comments')),
    url(r'^all/rss/$', AllPostsRssFeed(), name='rss'),
    url(r'^search/', include('haystack.urls')),
]
