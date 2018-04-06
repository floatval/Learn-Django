import markdown
from django.db import models
from django.contrib.auth.models import User
# from django.core.urlresolvers import reverse
from django.urls import reverse
from django.utils.html import strip_tags


class Category(models.Model):
    """文章分类"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """标签分类"""
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    """文章"""
    # 文章标题
    title = models.CharField(max_length=70)
    # 文章主题
    body = models.TextField()
    # 文章创建时间
    created_time = models.DateTimeField()
    # 文章最后一次修改时间
    modified_time = models.DateTimeField()
    # 文章摘要
    excerpt = models.CharField(max_length=200, blank=True)

    # 文章与分类的对应关系
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    # 文章与标签的对应关系(文章标签可以为空)
    tags = models.ManyToManyField(Tag, blank=True)
    # 文章与作者的对应关系(一对一)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    # 文章的阅读次数统计
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:detail', kwargs={'pk': self.pk})

    def Meta(self):
        ordering = ['-created_time', 'title']

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def save(self, *args, **kwargs):
        if not self.excerpt:
            # 首先实例化一个 MarkDown 类, 用于渲染 body 文本
            md = markdown.Markdown(extensions=[
                'markdown.extensions.extra',
                'markdown.extensions.codehilite',
                ])
            # 先将 MarkDown 文本渲染成 HTML 文本
            # strip_tags 去掉 HTML 文本的全部 HTML 标签
            # 从文本摘取前 54 个字符赋给 excerpt
            self.excerpt = strip_tags(md.convert(self.body))[:54]

        # 调用父类的 save 方法将数据保存到数据库中
        super(Post, self).save(*args, **kwargs)
