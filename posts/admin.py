from django.contrib import admin
from .models import Post, PostMedia, Hashtag

admin.site.register(Post)
admin.site.register(PostMedia)
admin.site.register(Hashtag)
