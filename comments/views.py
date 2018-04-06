from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post

from .models import Comment
from .forms import CommentForm


def post_comment(request, post_pk):
    """先获取被评论的文章,由于后面需要把评论和被评论的文章关联起来.
       这里我们使用了　Django　提供的一个快捷函数　get_object_or_404,
       这个函数的作用是当获取的文章(Post)存在时,则获取,否则返回404"""

    post = get_object_or_404(Post, pk=post_pk)

    if request.method == 'POST':
        form = CommentForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.save()
            return redirect(post)
    else:
        comment_list = post.comment_set.all()
        context = {'post': post,
                   'form': form,
                   'comment_list': comment_list}
        return render(request, 'blog/detail.html', context=context)
    return redirect(post)
