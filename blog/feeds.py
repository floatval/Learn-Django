from django.contrib.syndication.views import Feed

from .models import Post


class AllPostsRssFeed(Feed):
    # 显示在聚合阅读器上的标题
    title = "Django 博客学习项目"

    # 通过聚合阅读器跳转到网站的网址
    link = "/"

    # 显示在聚合阅读器上的描述信息
    description = "Django 博客测试文章"

    # 需要显示的内容条目
    def item(self):
        return Post.objects.all()

    # 聚合器中显示的内容条目的标题
    def item_title(self, item):
        return '[%s] %s' % (item.category, item.title)

    # 聚合器中显示的条目的描述
    def item_description(self, item):
        return item.body
