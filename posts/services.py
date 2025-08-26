from django.db import transaction
from django.db.models import F
from django.utils.text import slugify
from .models import Post, PostMedia, Hashtag


def _extract_hashtags(caption: str) -> set[str]:
    if not caption:
        return set()
    raw = {w[1:] for w in caption.split() if w.startswith("#") and len(w) > 1}
    cleaned = {slugify(x).replace("-", "") for x in raw}
    return {x for x in cleaned if x}


@transaction.atomic
def create_post_with_media(
    *,
    user,
    caption: str = "",
    location: str = "",
    visibility: str = Post.VIS_PUBLIC,
    files: list[dict] | None = None
) -> Post:
    """
    files: list of dicts -> [{'file': <InMemoryUploadedFile>, 'media_type': 'image'|'video', 'order': 0}, ...]
    """
    post = Post.objects.create(
        user=user, caption=caption or "", location=location or "", visibility=visibility
    )
    # hashtags
    tags = _extract_hashtags(caption)
    if tags:
        hashtag_objs = [Hashtag(name=t) for t in tags]
        # upsert-like: get existing then create missing
        existing = set(
            Hashtag.objects.filter(name__in=tags).values_list("name", flat=True)
        )
        to_create = [h for h in hashtag_objs if h.name not in existing]
        if to_create:
            Hashtag.objects.bulk_create(to_create, ignore_conflicts=True)
        post.hashtags.add(*Hashtag.objects.filter(name__in=tags))
        Hashtag.objects.filter(name__in=tags).update(usage_count=F("usage_count") + 1)

    # media
    if files:
        media_objs = [
            PostMedia(
                post=post,
                file=item["file"],
                media_type=item["media_type"],
                order=item.get("order", 0),
            )
            for item in files
        ]
        PostMedia.objects.bulk_create(media_objs)

    return post


@transaction.atomic
def increment_post_comment_count(post_id):
    from .models import Post

    Post.objects.filter(id=post_id).update(comment_count=F("comment_count") + 1)


@transaction.atomic
def decrement_post_comment_count(post_id):
    from .models import Post

    Post.objects.filter(id=post_id, comment_count__gt=0).update(
        comment_count=F("comment_count") - 1
    )
