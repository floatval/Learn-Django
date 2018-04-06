import markdown

from markdown.extensions.toc import TocExtension

from django.views.generic import ListView, DetailView
from django.utils.text import slugify
from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Post, Category, Tag
from comments.forms import CommentForm


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        # 覆写 get 方法的目的是因为每当文章被访问一次,就得将文章阅读量 +1
        # get 方法返回的是一个 HttpResponse 实例
        # 之所以需要先调用父类的 get 方法, 是因为当 get 方法被调用后
        # 才有 self.object 属性, 其值为 Post 模型实例, 即被访问的文章 Post
        response = super(PostDetailView, self).get(request, *args, **kwargs)

        # 将文章阅读量 +1
        # 注意 self.object 的值就是被访问的文章 post
        self.object.increase_views()

        # 视图必须返回一个 HttpResponse 对象
        return response

    def get_object(self, queryset=None):
        # 覆写 get_object 方法的目的是因为需要对 post 的 body 值进行渲染
        post = super(PostDetailView, self).get_object(queryset=None)
        md = markdown.Markdown(extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            TocExtension(slugify=slugify),
        ])
        post.body = md.convert(post.body)
        post.toc = md.toc
        return post

    def get_context_data(self, **kwargs):                                   
       # 覆写 get_context_data 的目的是因为除了将 post 传递给模板外（Detail    View 已经帮我们完成），
       # 还要把评论表单、post 下的评论列表传递给模板。                 
        context = super(PostDetailView, self).get_context_data(**kwargs)
        form = CommentForm()                                           
        comment_list = self.object.comment_set.all()                   
        context.update({                                               
            'form': form,     
            'comment_list': comment_list                               
        })                                                             
        return context 


class IndexView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    # 制定 paginate_by 属性后开启分页功能, 其值代表每一页包含多少文章
    paginate_by = 2
    
    def get_context_data(self, **kwargs):
        # 覆写 get_context_date 的原因是除了将 post 传递给模版外 (DetailView 已经帮我们完成), 
        # 还需要评论表单 post 下的评论列表传递给模版.
        # 在类视图中, 需要传递给模版变量的字典是通过这个函数进行传递的.
        # 覆写该方法,以便插入自定义的模版变量
        # context = super(PostDetailView, self).get_context_data(**kwargs)

        # 获得父类生成的传递给模版的字典
        context = super().get_context_data(**kwargs)
        paginator = context.get('paginator')
        page = context.get('page_obj')
        is_paginated = context.get('is_paginated')

        # 调用自己写的 pagination_data 方法获得显示分页导航所需的数据,见下方
        pagination_data = self.pagination_data(paginator, page, is_paginated)

        # 将分页导航条的模版变量更新到 context 中, 注意 pagination_data 方法返回值也是字典
        context.update(pagination_data)

        # 将更新后的 context 返回,以便 ListView 使用这个字典中的模版变量去渲染模版
        # 注意此时 context 字典中已经有了显示分页导航条所需的数据
        return context

    def pagination_data(self, paginator, page, is_paginated):
        if not is_paginated:
        # 如果没有分页,则无需显示分页导航条,不用任何分页导航条的数据,因此返回一个空的字典
             return {}

        # 当前页左边连续的页码号,初始值为空
        left = []

        # 当前页右边连续的页码号,初始值为空
        right = []

        # 标示第 1 页页码后是否需要显示省略号
        left_has_more = False

        # 标示最后一页前是否需要显示省略号
        right_has_more = False

        # 标示是否需要显示第 1 页的页码号
        # 因为如果当前左侧的连续页码中,包含第 1 页的页码, 则无需显示第 1 页的页码号
        # 其他情况均需要显示
        # 初始值为 False
        first = False

        # 标示是否需要显示最后一页的页码
        # 判断条件同上
        last = False

        # 获得用户当前请求的页码
        page_number = page.number

        # 获取分页后的总页数
        total_pages = paginator.num_pages

        # 获取整个分页页码列表,例如分了四页,那么即[1,2,3,4]
        page_range = paginator.page_range

        if page_number == 1:
            # 此时左侧无需数据,且 left已默认为空
            # 获取右侧的处去最后一页的连续页码
            # 下面获取的连续页码的数字可以修改成需要的值
            right = page_range[page_number:page_number + 2]

            # 当前最右侧的页码比最后一页的页码 -1 还小的话,则需要添加省略号
            # 标示为 right_has_more
            if right[-1] < total_pages -1:
                right_has_more = True

            # 最右侧的页码比最后一页页码小, 说明当前右侧连续页码不包含最后一页的页码
            # 需要显示最后一页的页码, 标示为 last
            if right[-1] < total_pages:
                last = True

        elif page_number == total_pages:
                        # 用户访问的为最后一页,则右侧无需数据, 令ringh=[](默认为空)
            # 此时只需获取左侧的连续页码
            # 例如分页页码为[1, 2, 3, 4], 那么获取的就是 left=[2, 3]
            # 这里只获取当前页码前连续两个页码, 可以更改数字获取更多页码
            left = page_range[(page_number -3) if (page_number -3) > 0 else 0:page_number -1 ]

            # 若最左侧的页码比第 2 页页码大,则需要省略号
            # 表示为 left_has_more
            if left[0] > 2:
                left_has_more = True

            # 若最左侧的页码比第 1 页的页码大, 则需显示第一页的页码
            # 标示为 first
            if left[0] > 1:
                first = True
        else:
            # 用户请求的页码不是第一页或最后一页
            # 需要获取当前页的左右两边的连续页码
            # 这里只获取两页,可以通过修改数字来改变获得的连续页码数
            left = page_range[(page_number -3 ) if (page_number - 3) > 0 else 0:page_number -1]
            right = page_range[page_number:page_number + 2]

            # 最后一页及其之前的省略号是否需要显示
            if right[-1] < total_pages -1:
                right_has_more = True
            if right[-1] < total_pages:
                last = True

            # 第一页及其后的省略号是否需要显示
            if left[0] > 2:
                left_has_more = True
            if left[0] > 1:
                first = True

        data = {
            'left':left,
            'right': right,
            'left_has_more': left_has_more,
            'right_has_more': right_has_more,
            'first': first,
            'last': last,
       }
        return data
def index(request):
    """主页函数"""
    post_list = Post.objects.all().order_by('-created_time')
    return render(request, 'blog/index.html', {'post_list': post_list})


def detail(request, pk):
    """文章详情页面"""
    post = get_object_or_404(Post, pk=pk)

    # 阅读量自动+1 
    post.increase_views()

    post.body = markdown.markdown(post.body,
                                  extensions=[
                                      'markdown.extensions.extra',
                                      'markdown.extensions.codehilite',
                                      'markdown.extensions.toc',
                                      ])
    form = CommentForm()
    comment_list = post.comment_set.all()
    context = {
            'post': post,
            'form': form,
            'comment_list': comment_list}
    return render(request, 'blog/detail.html', context=context)


class CategoryViews(IndexView):
    """分类"""
    def get_queryset(self):
        cate = get_object_or_404(Category, pk=self.kwargs.get('pk'))
        return super(CategoryViews, self).get_queryset().filter(category=cate)


def archives(request, year, month):
    post_list = Post.objects.filter(created_time__year=year,
                                    created_time__month=month
                                    )
    return render(request, 'blog/index.html', context={'post_list': post_list})

class ArchivesView(ListView):
    """月份排序"""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        return super(ArchivesView, self).get_queryset().filter(
                created_time__year=year,
                created_time__month=month)


class TagView(ListView):
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'post_list'

    def get_queryset(self):
        tag = get_object_or_404(Tag, pk=self.kwargs.get('pk'))
        return super(TagView, self).get_queryset().filter(tags=tag)


def search(request):
    q = request.GET.get('q')
    error_msg = ''

    if not q:
        error_msg = "请输入关键词"
        return render(request, 'blog/index.html', {'error_msg': error_msg})

    post_list = Post.objects.filter(Q(title__icontains=q) | Q(body__icontains=q))
    return render(request, 'blog/index.html', {'error_msg': error_msg,
        'post_list': post_list})
