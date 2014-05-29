from django.contrib import admin
from .models import Author, Post, Comment

admin.site.register(Author)
admin.site.register(Post)
admin.site.register(Comment)
