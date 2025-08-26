from django.db import transaction
from django.db.models import F
from django.shortcuts import get_object_or_404
from posts.models import Post
from .models import PostLike, Comment


@transaction.atomic
def toggle_like(*, user, post_id) -> bool:
    """
    Returns True if liked after toggle, False if unliked.
    """
    post = get_object_or_404(Post.objects.only("id"), id=post_id)
    like, created = PostLike.objects.get_or_create(user=user, post=post)
    if created:
        Post.objects.filter(id=post.id).update(like_count=F("like_count") + 1)
        return True
    # unlike
    PostLike.objects.filter(id=like.id).delete()
    Post.objects.filter(id=post.id, like_count__gt=0).update(
        like_count=F("like_count") - 1
    )
    return False


@transaction.atomic
def add_comment(*, user, post_id, content: str, parent_id=None) -> Comment:
    post = get_object_or_404(Post, id=post_id)
    comment = Comment.objects.create(
        user=user, post=post, content=content, parent_id=parent_id
    )
    Post.objects.filter(id=post.id).update(comment_count=F("comment_count") + 1)
    return comment


@transaction.atomic
def delete_comment(*, user, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=user)
    comment.is_deleted = True
    comment.save(update_fields=["is_deleted"])
    Post.objects.filter(id=comment.post_id, comment_count__gt=0).update(
        comment_count=F("comment_count") - 1
    )
